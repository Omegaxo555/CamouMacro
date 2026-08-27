package config

import (
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
)

// AppConfig contiene las configuraciones generales del orquestador y workers.
type AppConfig struct {
	PythonExecutable string
	PythonEngineDir  string
	RunnerScript     string
	TorPort          int
	Headless         bool
	SpeedFactor      float64
	SelectedAlgo     string
	WindowWidth      int
	WindowHeight     int
}

// LoadDefaultConfig inicializa la configuración buscando el interprete de Python y rutas relativas.
func LoadDefaultConfig() *AppConfig {
	exeDir := getProjectRootDir()

	pythonPath := findPythonExecutable(exeDir)
	engineDir := filepath.Join(exeDir, "python_engine")
	runnerScript := filepath.Join(engineDir, "runner.py")

	speed := 1.0
	if envSpeed := os.Getenv("SPEED_FACTOR"); envSpeed != "" {
		if s, err := strconv.ParseFloat(envSpeed, 64); err == nil {
			speed = s
		}
	}

	torPort := 9050
	if envPort := os.Getenv("TOR_PORT"); envPort != "" {
		if p, err := strconv.Atoi(envPort); err == nil {
			torPort = p
		}
	}

	headless := false
	if envHeadless := os.Getenv("HEADLESS"); envHeadless == "true" || envHeadless == "1" {
		headless = true
	}

	if envPython := os.Getenv("PYTHON_PATH"); envPython != "" {
		pythonPath = envPython
	}
	if envEngine := os.Getenv("PYTHON_ENGINE_DIR"); envEngine != "" {
		engineDir = envEngine
		runnerScript = filepath.Join(engineDir, "runner.py")
	}

	algo := "allfeellove_auto"
	if envAlgo := os.Getenv("ALGO"); envAlgo != "" {
		algo = envAlgo
	}

	return &AppConfig{
		PythonExecutable: pythonPath,
		PythonEngineDir:  engineDir,
		RunnerScript:     runnerScript,
		TorPort:          torPort,
		Headless:         headless,
		SpeedFactor:      speed,
		SelectedAlgo:     algo,
		WindowWidth:      560,
		WindowHeight:     420,
	}
}

func getProjectRootDir() string {
	var startDirs []string
	if exe, err := os.Executable(); err == nil {
		startDirs = append(startDirs, filepath.Dir(exe))
	}
	if cwd, err := os.Getwd(); err == nil {
		startDirs = append(startDirs, cwd)
	}

	for _, start := range startDirs {
		curr := start
		for i := 0; i < 6; i++ {
			if _, err := os.Stat(filepath.Join(curr, "python_engine")); err == nil {
				return curr
			}
			if _, err := os.Stat(filepath.Join(curr, "camoumacro.py")); err == nil {
				return curr
			}
			parent := filepath.Dir(curr)
			if parent == curr || parent == "." || parent == "" {
				break
			}
			curr = parent
		}
	}

	// Fallback: directorio de trabajo actual
	cwd, _ := os.Getwd()
	if filepath.Base(cwd) == "go_app" || filepath.Base(cwd) == "bin" {
		return filepath.Dir(cwd)
	}
	return cwd
}

func findPythonExecutable(projectRoot string) string {
	// 1. Probar entorno virtual local .venv en projectRoot
	var venvCandidates []string
	if runtime.GOOS == "windows" {
		venvCandidates = append(venvCandidates,
			filepath.Join(projectRoot, ".venv", "Scripts", "python.exe"),
			filepath.Join(projectRoot, "python_engine", ".venv", "Scripts", "python.exe"),
		)
	} else {
		venvCandidates = append(venvCandidates,
			filepath.Join(projectRoot, ".venv", "bin", "python"),
			filepath.Join(projectRoot, "python_engine", ".venv", "bin", "python"),
		)
	}

	for _, c := range venvCandidates {
		if _, err := os.Stat(c); err == nil {
			return c
		}
	}

	// 2. Probar PATH general del sistema
	candidates := []string{"python3", "python"}
	for _, c := range candidates {
		if path, err := exec.LookPath(c); err == nil {
			return path
		}
	}

	if runtime.GOOS == "windows" {
		return "python.exe"
	}
	return "python3"
}
