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
	cfg      *config.AppConfig
	torMgrs  map[int]*tor.Manager
	cmds     map[int]*exec.Cmd
	ctx      context.Context
	cancel   context.CancelFunc
	mu       sync.Mutex
	status   StatusType
	onLog    func(string)
	onStatus func(StatusType)
	runLoop  bool
}

// NewOrchestrator crea un nuevo orquestador.
func NewOrchestrator(cfg *config.AppConfig, onLog func(string), onStatus func(StatusType)) *Orchestrator {
	return &Orchestrator{
		cfg:      cfg,
		torMgrs:  make(map[int]*tor.Manager),
		cmds:     make(map[int]*exec.Cmd),
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
	if o.status != StatusIdle && o.status != StatusError {
		o.mu.Unlock()
		return fmt.Errorf("el orquestador ya está en ejecución")
	}
	macroCount := o.cfg.MacroCount
	if macroCount == 0 {
		macroCount = 1
	}
	if macroCount < 1 || macroCount > 3 {
		o.mu.Unlock()
		return fmt.Errorf("el número de macros debe estar entre 1 y 3")
	}
	if o.cfg.TorPort < 1 || o.cfg.TorPort+(macroCount-1)*10 > 65534 {
		o.mu.Unlock()
		return fmt.Errorf("puerto Tor base inválido para %d macros", macroCount)
	}
	o.runLoop = loopMode
	o.ctx, o.cancel = context.WithCancel(context.Background())
	o.torMgrs = make(map[int]*tor.Manager, macroCount)
	o.cmds = make(map[int]*exec.Cmd, macroCount)
	for workerID := 1; workerID <= macroCount; workerID++ {
		id := workerID
		port := o.cfg.TorPort + (workerID-1)*10
		o.torMgrs[id] = tor.NewManagerWithPorts(func(msg string) {
			o.log(fmt.Sprintf("[macro %d] %s", id, msg))
		}, []int{port})
	}
	managers := make(map[int]*tor.Manager, len(o.torMgrs))
	for workerID, manager := range o.torMgrs {
		managers[workerID] = manager
	}
	ctx := o.ctx
	o.status = StatusStarting
	o.mu.Unlock()

	if o.onStatus != nil {
		o.onStatus(StatusStarting)
	}
	go o.lifecycleLoop(ctx, managers)
	return nil
}

// Stop detiene inmediatamente el ciclo de vida y los procesos hijos.
func (o *Orchestrator) Stop() {
	o.mu.Lock()
	if o.cancel != nil {
		o.cancel()
	}
	o.runLoop = false
	managers := make([]*tor.Manager, 0, len(o.torMgrs))
	for _, manager := range o.torMgrs {
		managers = append(managers, manager)
	}
	processes := make([]*exec.Cmd, 0, len(o.cmds))
	for _, cmd := range o.cmds {
		processes = append(processes, cmd)
	}
	o.mu.Unlock()

	o.setStatus(StatusStopping)
	o.log("[lifecycle] Deteniendo orquestador...")

	for _, cmd := range processes {
		if cmd != nil && cmd.Process != nil {
			_ = cmd.Process.Kill()
		}
	}
	for _, manager := range managers {
		manager.Stop()
	}

	o.setStatus(StatusIdle)
	o.log("[lifecycle] Detenido completamente.")
}

func (o *Orchestrator) lifecycleLoop(ctx context.Context, managers map[int]*tor.Manager) {
	var workers sync.WaitGroup
	for workerID, manager := range managers {
		workers.Add(1)
		go func(workerID int, manager *tor.Manager) {
			defer workers.Done()
			o.runMacro(ctx, workerID, manager)
		}(workerID, manager)
	}
	workers.Wait()

	if ctx.Err() == nil {
		o.log("[lifecycle] Todos los workers terminaron.")
		o.setStatus(StatusIdle)
	}
}

func (o *Orchestrator) runMacro(ctx context.Context, workerID int, manager *tor.Manager) {
	for cycle := 1; ; cycle++ {
		if ctx.Err() != nil {
			return
		}

		currentPort := manager.CurrentPort()
		o.setStatus(StatusStarting)
		o.log(fmt.Sprintf("[macro %d] Iniciando ciclo #%d con Tor SOCKS 127.0.0.1:%d", workerID, cycle, currentPort))

		if err := manager.Start(currentPort); err != nil {
			o.log(fmt.Sprintf("[macro %d][ERROR] No se pudo iniciar Tor aislado: %v", workerID, err))
			return
		}

		o.setStatus(StatusRunning)
		err := o.runPythonWorker(ctx, workerID, currentPort)
		manager.Stop()

		if ctx.Err() != nil {
			return
		}
		if err != nil {
			o.log(fmt.Sprintf("[macro %d] Worker finalizó con error/reinicio: %v", workerID, err))
		} else {
			o.log(fmt.Sprintf("[macro %d] Worker completó el algoritmo con éxito.", workerID))
		}

		o.mu.Lock()
		shouldContinue := o.runLoop
		o.mu.Unlock()
		if !shouldContinue {
			o.log(fmt.Sprintf("[macro %d] Modo ciclo único completado.", workerID))
			return
		}

		o.setStatus(StatusRotating)
		o.log(fmt.Sprintf("[macro %d] Reiniciando su propio proceso Tor para el siguiente ciclo...", workerID))
		if cyclePort := manager.RotatePort(); cyclePort != currentPort {
			o.log(fmt.Sprintf("[macro %d] Puerto Tor asignado al siguiente ciclo: %d", workerID, cyclePort))
		}
		select {
		case <-ctx.Done():
			return
		case <-time.After(2 * time.Second):
		}
	}
}

func (o *Orchestrator) runPythonWorker(ctx context.Context, workerID int, torPort int) error {
	args := []string{
		o.cfg.RunnerScript,
		"--algo", o.cfg.SelectedAlgo,
		"--tor-port", strconv.Itoa(torPort),
		"--tor-ports", strconv.Itoa(torPort),
		"--speed-factor", fmt.Sprintf("%.2f", o.cfg.SpeedFactor),
		"--width", strconv.Itoa(o.cfg.WindowWidth),
		"--height", strconv.Itoa(o.cfg.WindowHeight),
	}

	o.mu.Lock()
	keepBrowserOpen := !o.runLoop
	o.mu.Unlock()
	if keepBrowserOpen {
		args = append(args, "--keep-open")
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
		fmt.Sprintf("SEARCH_ALL_USERS=%t", o.cfg.SearchAllUsers),
		fmt.Sprintf("TARGET_GENDER=%s", o.cfg.TargetGender),
		fmt.Sprintf("ACCOUNT_GENDER=%s", o.cfg.AccountGender),
		"PYTHONUNBUFFERED=1",
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
	o.cmds[workerID] = cmd
	o.mu.Unlock()
	defer func() {
		o.mu.Lock()
		delete(o.cmds, workerID)
		o.mu.Unlock()
	}()

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
