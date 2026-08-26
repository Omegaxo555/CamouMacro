package orchestrator

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"strconv"
	"sync"
	"time"

	"github.com/omegaxo555/camoumacro/go_app/internal/config"
	"github.com/omegaxo555/camoumacro/go_app/internal/tor"
)

// StatusType representa el estado actual de la automatización.
type StatusType string

const (
	StatusIdle     StatusType = "IDLE"
	StatusStarting StatusType = "STARTING"
	StatusRunning  StatusType = "RUNNING"
	StatusRotating StatusType = "ROTATING"
	StatusStopping StatusType = "STOPPING"
	StatusError    StatusType = "ERROR"
)

// Orchestrator gestiona el ciclo de vida continuo de Tor y el worker Python.
type Orchestrator struct {
	cfg        *config.AppConfig
	torMgr     *tor.Manager
	cmd        *exec.Cmd
	ctx        context.Context
	cancel     context.CancelFunc
	mu         sync.Mutex
	status     StatusType
	onLog      func(string)
	onStatus   func(StatusType)
	runLoop    bool
	iteration  int
}

// NewOrchestrator crea un nuevo orquestador.
func NewOrchestrator(cfg *config.AppConfig, onLog func(string), onStatus func(StatusType)) *Orchestrator {
	torMgr := tor.NewManager(onLog)
	return &Orchestrator{
		cfg:      cfg,
		torMgr:   torMgr,
		status:   StatusIdle,
		onLog:    onLog,
		onStatus: onStatus,
	}
}

// GetStatus devuelve el estado actual.
func (o *Orchestrator) GetStatus() StatusType {
	o.mu.Lock()
	defer o.mu.Unlock()
	return o.status
}

func (o *Orchestrator) setStatus(s StatusType) {
	o.mu.Lock()
	o.status = s
	o.mu.Unlock()
	if o.onStatus != nil {
		o.onStatus(s)
	}
}

func (o *Orchestrator) log(msg string) {
	if o.onLog != nil {
		o.onLog(msg)
	}
}

// Start inicia la ejecución continua de la automatización en una goroutine.
func (o *Orchestrator) Start(loopMode bool) error {
	o.mu.Lock()
	if o.status == StatusRunning || o.status == StatusStarting {
		o.mu.Unlock()
		return fmt.Errorf("el orquestador ya está en ejecución")
	}
	o.runLoop = loopMode
	o.ctx, o.cancel = context.WithCancel(context.Background())
	o.iteration = 0
	o.mu.Unlock()

	go o.lifecycleLoop()
	return nil
}

// Stop detiene inmediatamente el ciclo de vida y los procesos hijos.
func (o *Orchestrator) Stop() {
	o.mu.Lock()
	if o.cancel != nil {
		o.cancel()
	}
	o.runLoop = false
	o.mu.Unlock()

	o.setStatus(StatusStopping)
	o.log("[lifecycle] Deteniendo orquestador...")

	o.killCurrentWorker()
	o.torMgr.Stop()

	o.setStatus(StatusIdle)
	o.log("[lifecycle] Detenido completamente.")
}

func (o *Orchestrator) killCurrentWorker() {
	o.mu.Lock()
	defer o.mu.Unlock()
	if o.cmd != nil && o.cmd.Process != nil {
		_ = o.cmd.Process.Kill()
		_ = o.cmd.Wait()
		o.cmd = nil
	}
}

func (o *Orchestrator) lifecycleLoop() {
	currentPort := o.cfg.TorPort

	for {
		o.mu.Lock()
		ctx := o.ctx
		o.iteration++
		iter := o.iteration
		o.mu.Unlock()

		select {
		case <-ctx.Done():
			return
		default:
		}

		o.setStatus(StatusStarting)
		o.log(fmt.Sprintf("\n========== CICLO #%d | Puerto Tor: %d ==========", iter, currentPort))

		// 1. Iniciar Tor
		if err := o.torMgr.Start(currentPort); err != nil {
			o.log(fmt.Sprintf("[ERROR] Fallo al iniciar Tor: %v", err))
		}

		// 2. Ejecutar Worker Python
		o.setStatus(StatusRunning)
		err := o.runPythonWorker(ctx, currentPort)

		select {
		case <-ctx.Done():
			return
		default:
		}

		if err != nil {
			o.log(fmt.Sprintf("[lifecycle] Worker finalizó con error/reinicio: %v", err))
		} else {
			o.log("[lifecycle] Worker completó el algoritmo con éxito.")
		}

		o.mu.Lock()
		shouldContinue := o.runLoop
		o.mu.Unlock()

		if !shouldContinue {
			o.log("[lifecycle] Modo ciclo único completado.")
			o.Stop()
			return
		}

		// 3. Rotar puerto y preparar siguiente ciclo
		o.setStatus(StatusRotating)
		o.log("[lifecycle] Rotando puerto Tor y limpiando sesión...")
		o.torMgr.Stop()
		currentPort = o.torMgr.RotatePort()

		time.Sleep(2 * time.Second)
	}
}

func (o *Orchestrator) runPythonWorker(ctx context.Context, torPort int) error {
	args := []string{
		o.cfg.RunnerScript,
		"--algo", o.cfg.SelectedAlgo,
		"--tor-port", strconv.Itoa(torPort),
		"--speed-factor", fmt.Sprintf("%.2f", o.cfg.SpeedFactor),
		"--width", strconv.Itoa(o.cfg.WindowWidth),
		"--height", strconv.Itoa(o.cfg.WindowHeight),
	}

	if o.cfg.Headless {
		args = append(args, "--headless")
	}

	cmd := exec.CommandContext(ctx, o.cfg.PythonExecutable, args...)
	cmd.Dir = o.cfg.PythonEngineDir

	// Inyectar variables de entorno heredadas
	cmd.Env = append(os.Environ(),
		fmt.Sprintf("TOR_PORT=%d", torPort),
		fmt.Sprintf("SPEED_FACTOR=%.2f", o.cfg.SpeedFactor),
		fmt.Sprintf("HEADLESS=%t", o.cfg.Headless),
	)

	stdoutPipe, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	stderrPipe, err := cmd.StderrPipe()
	if err != nil {
		return err
	}

	o.mu.Lock()
	o.cmd = cmd
	o.mu.Unlock()

	if err := cmd.Start(); err != nil {
		return fmt.Errorf("error al iniciar Python worker: %w", err)
	}

	// Escuchar stdout y stderr en tiempo real
	var wg sync.WaitGroup
	wg.Add(2)

	go o.streamOutput(stdoutPipe, &wg)
	go o.streamOutput(stderrPipe, &wg)

	wg.Wait()
	err = cmd.Wait()

	o.mu.Lock()
	o.cmd = nil
	o.mu.Unlock()

	return err
}

func (o *Orchestrator) streamOutput(r io.Reader, wg *sync.WaitGroup) {
	defer wg.Done()
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		text := scanner.Text()
		o.log(text)
	}
}
