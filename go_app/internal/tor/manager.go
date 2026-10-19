package tor

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

// DefaultPorts lista de puertos SOCKS cuyos puertos de control no se superponen.
var DefaultPorts = []int{9050, 9052, 9054, 9056}

// Manager administra el proceso de Tor en segundo plano y la rotación de conexiones.
type Manager struct {
	process    *exec.Cmd
	currentIdx int
	ports      []int
	mu         sync.Mutex
	logFn      func(string)
}

// NewManager crea una nueva instancia de Manager.
func NewManager(logFn func(string)) *Manager {
	return NewManagerWithPorts(logFn, DefaultPorts)
}

// NewManagerWithPorts crea un manager limitado a sus propios puertos SOCKS.
func NewManagerWithPorts(logFn func(string), ports []int) *Manager {
	if len(ports) == 0 {
		ports = DefaultPorts
	}
	return &Manager{
		ports: append([]int(nil), ports...),
		logFn: logFn,
	}
}

// Ports devuelve una copia de los puertos asignados a este manager.
func (m *Manager) Ports() []int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return append([]int(nil), m.ports...)
}

func (m *Manager) log(msg string) {
	if m.logFn != nil {
		m.logFn(fmt.Sprintf("[tor] %s", msg))
	}
}

// CurrentPort devuelve el puerto Tor actualmente en uso.
func (m *Manager) CurrentPort() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.ports[m.currentIdx%len(m.ports)]
}

// RotatePort rota al siguiente puerto Tor de la lista.
func (m *Manager) RotatePort() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.currentIdx = (m.currentIdx + 1) % len(m.ports)
	return m.ports[m.currentIdx]
}

// FindTorExecutable busca el binario de Tor en rutas comunes y en el PATH.
func FindTorExecutable() string {
	if envTor := os.Getenv("TOR_PATH"); envTor != "" {
		if _, err := os.Stat(envTor); err == nil {
			return envTor
		}
	}
	if envTor := os.Getenv("TOR_BINARY"); envTor != "" {
		if _, err := os.Stat(envTor); err == nil {
			return envTor
		}
	}

	var startDirs []string
	if exe, err := os.Executable(); err == nil {
		startDirs = append(startDirs, filepath.Dir(exe))
	}
	if cwd, err := os.Getwd(); err == nil {
		startDirs = append(startDirs, cwd)
	}

	var candidates []string

	for _, start := range startDirs {
		curr := start
		for i := 0; i < 6; i++ {
			if runtime.GOOS == "windows" {
				candidates = append(candidates,
					filepath.Join(curr, "tor", "tor", "tor.exe"),
					filepath.Join(curr, "tor", "tor.exe"),
					filepath.Join(curr, "python_engine", "tor", "tor", "tor.exe"),
					filepath.Join(curr, "bin", "tor", "tor.exe"),
				)
			} else {
				candidates = append(candidates,
					filepath.Join(curr, "tor", "tor", "tor"),
					filepath.Join(curr, "tor", "tor"),
					filepath.Join(curr, "python_engine", "tor", "tor", "tor"),
					filepath.Join(curr, "bin", "tor", "tor"),
				)
			}
			parent := filepath.Dir(curr)
			if parent == curr || parent == "." || parent == "" {
				break
			}
			curr = parent
		}
	}

	if runtime.GOOS == "windows" {
		userProfile := os.Getenv("USERPROFILE")
		if userProfile != "" {
			candidates = append(candidates,
				filepath.Join(userProfile, "AppData", "Local", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
				filepath.Join(userProfile, "Desktop", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
			)
		}
		candidates = append(candidates,
			"tor.exe",
			`C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe`,
			`C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe`,
		)
	} else {
		candidates = append(candidates,
			"tor",
			"/usr/bin/tor",
			"/usr/local/bin/tor",
		)
	}

	for _, c := range candidates {
		if c == "" {
			continue
		}
		if _, err := os.Stat(c); err == nil {
			return c
		}
		if path, err := exec.LookPath(c); err == nil {
			return path
		}
	}
	return ""
}

// Start arranca Tor en el puerto especificado.
func (m *Manager) Start(port int) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	if IsTorAvailable(port) {
		return fmt.Errorf("el puerto Tor SOCKS %d ya está en uso; se rechaza compartir una instancia Tor", port)
	}

	torPath := FindTorExecutable()
	if torPath == "" {
		m.log("No se encontró el ejecutable de Tor en el sistema.")
		return fmt.Errorf("no se encontró 'tor' o 'tor.exe'")
	}

	dataDir := filepath.Join(os.TempDir(), fmt.Sprintf("camoumacro_tor_%d", port))
	_ = os.MkdirAll(dataDir, 0700)
	configPath := filepath.Join(dataDir, "torrc")

	torrcContent := strings.Join([]string{
		fmt.Sprintf("SocksPort 127.0.0.1:%d", port),
		fmt.Sprintf("ControlPort 127.0.0.1:%d", port+1),
		fmt.Sprintf("DataDirectory %s", dataDir),
		"Log notice stdout",
		"AvoidDiskWrites 1",
	}, "\n")

	if err := os.WriteFile(configPath, []byte(torrcContent), 0600); err != nil {
		return fmt.Errorf("error escribiendo torrc: %w", err)
	}

	cmd := exec.Command(torPath, "-f", configPath)
	cmd.Dir = filepath.Dir(torPath)

	if err := cmd.Start(); err != nil {
		m.log(fmt.Sprintf("Error al iniciar proceso Tor: %v", err))
		return err
	}
	m.process = cmd

	// Esperar hasta que responda en el puerto
	for i := 0; i < 30; i++ {
		if IsTorAvailable(port) {
			m.log(fmt.Sprintf("Tor arrancó correctamente en 127.0.0.1:%d", port))
			return nil
		}
		time.Sleep(500 * time.Millisecond)
	}

	m.stopInternal()
	return fmt.Errorf("Tor inició pero no respondió a tiempo en el puerto %d", port)
}

// Stop detiene el proceso Tor si fue iniciado por este manager.
func (m *Manager) Stop() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.stopInternal()
}

func (m *Manager) stopInternal() {
	if m.process == nil || m.process.Process == nil {
		return
	}

	_ = m.process.Process.Kill()
	_ = m.process.Wait()
	m.process = nil
	m.log("Tor detenido.")
}
