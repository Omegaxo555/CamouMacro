// Package tor provee gestión del proceso Tor: búsqueda, arranque, parada y rotación de puertos.
package tor

import (
	"fmt"
	"log/slog"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

// DefaultPorts son los puertos Tor que se rotan cíclicamente.
var DefaultPorts = []int{9050, 9150, 9051, 9052}

// Manager gestiona el ciclo de vida de un proceso Tor.
type Manager struct {
	process    *exec.Cmd
	currentIdx int
	ports      []int
}

// NewManager crea un Manager con los puertos por defecto.
func NewManager() *Manager {
	return &Manager{ports: DefaultPorts}
}

// CurrentPort devuelve el puerto Tor actualmente en uso.
func (m *Manager) CurrentPort() int {
	return m.ports[m.currentIdx%len(m.ports)]
}

// RotatePort avanza al siguiente puerto en la lista cíclica y devuelve el nuevo.
func (m *Manager) RotatePort() int {
	m.currentIdx = (m.currentIdx + 1) % len(m.ports)
	return m.CurrentPort()
}

// FindTorExecutable busca el binario tor/tor.exe en rutas conocidas y en $PATH.
// Equivalente a find_tor_executable() de main.py.
func FindTorExecutable() string {
	var candidates []string

	// Ruta relativa al binario bundled (tor/tor/tor.exe o tor/tor/tor)
	if exe, err := os.Executable(); err == nil {
		root := filepath.Dir(exe)
		if runtime.GOOS == "windows" {
			candidates = append(candidates, filepath.Join(root, "tor", "tor", "tor.exe"))
		} else {
			candidates = append(candidates, filepath.Join(root, "tor", "tor", "tor"))
		}
	}

	if runtime.GOOS == "windows" {
		candidates = append(candidates,
			`tor.exe`,
			`C:\Users\paulo\AppData\Local\Tor Browser\Browser\TorBrowser\Tor\tor.exe`,
			`C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe`,
			`C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe`,
		)
	} else {
		candidates = append(candidates, "tor", "/usr/bin/tor", "/usr/local/bin/tor")
	}

	for _, c := range candidates {
		if c == "" {
			continue
		}
		// Ruta absoluta que existe
		if _, err := os.Stat(c); err == nil {
			return c
		}
		// Búsqueda en $PATH
		if path, err := exec.LookPath(c); err == nil {
			return path
		}
	}
	return ""
}

// Start arranca Tor en background en el puerto dado.
// Escribe un torrc temporal y espera hasta 15 segundos a que Tor responda.
// Equivalente a start_tor_background() de main.py.
func (m *Manager) Start(port int) error {
	if IsTorAvailable(port) {
		slog.Info("Tor ya está corriendo", "port", port)
		return nil
	}

	torPath := FindTorExecutable()
	if torPath == "" {
		return fmt.Errorf("no se encontró el ejecutable de Tor en el sistema")
	}

	// Preparar directorio y torrc temporal
	dataDir := filepath.Join(os.TempDir(), fmt.Sprintf("camoumacro_tor_%d", port))
	if err := os.MkdirAll(dataDir, 0o700); err != nil {
		return fmt.Errorf("no se pudo crear el directorio temporal de Tor: %w", err)
	}

	torrcPath := filepath.Join(dataDir, "torrc")
	torrc := strings.Join([]string{
		fmt.Sprintf("SocksPort 127.0.0.1:%d", port),
		fmt.Sprintf("ControlPort 127.0.0.1:%d", port+1),
		fmt.Sprintf("DataDirectory %s", dataDir),
		"Log notice stdout",
		"AvoidDiskWrites 1",
	}, "\n")

	if err := os.WriteFile(torrcPath, []byte(torrc), 0o600); err != nil {
		return fmt.Errorf("no se pudo escribir torrc: %w", err)
	}

	// Lanzar proceso Tor
	cmd := exec.Command(torPath, "-f", torrcPath)
	cmd.Stdout = nil
	cmd.Stderr = nil
	cmd.Dir = filepath.Dir(torPath)

	if err := cmd.Start(); err != nil {
		return fmt.Errorf("error al iniciar Tor: %w", err)
	}
	m.process = cmd

	// Esperar a que Tor responda (hasta 15 s)
	for i := 0; i < 30; i++ {
		if IsTorAvailable(port) {
			slog.Info("Tor arrancó correctamente", "addr", fmt.Sprintf("127.0.0.1:%d", port))
			return nil
		}
		time.Sleep(500 * time.Millisecond)
	}

	// No respondió — matar proceso
	_ = m.Stop()
	return fmt.Errorf("Tor se inició pero no respondió en 127.0.0.1:%d", port)
}

// Stop detiene el proceso Tor gestionado por este Manager.
// Equivalente a stop_tor_background() de main.py.
func (m *Manager) Stop() error {
	if m.process == nil {
		return nil
	}
	defer func() { m.process = nil }()

	if m.process.Process == nil {
		return nil
	}

	if err := m.process.Process.Signal(os.Interrupt); err != nil {
		// Si Interrupt falla, forzar Kill
		_ = m.process.Process.Kill()
	}

	done := make(chan error, 1)
	go func() { done <- m.process.Wait() }()

	select {
	case <-done:
	case <-time.After(10 * time.Second):
		_ = m.process.Process.Kill()
		<-done
	}

	slog.Info("Tor detenido")
	return nil
}

// ProxyURL devuelve la URL del proxy SOCKS5 para el puerto dado.
func ProxyURL(port int) string {
	return fmt.Sprintf("socks5://127.0.0.1:%d", port)
}

// intToStr convierte int a string (helper interno).
func intToStr(n int) string {
	return strconv.Itoa(n)
}
