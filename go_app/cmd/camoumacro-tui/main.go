package main

import (
	"fmt"
	"os"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/omegaxo555/camoumacro/go_app/internal/config"
	"github.com/omegaxo555/camoumacro/go_app/internal/orchestrator"
)

// Estilos Lipgloss
var (
	accentColor  = lipgloss.Color("#7C6AF7")
	successColor = lipgloss.Color("#34D399")
	warningColor = lipgloss.Color("#FBBF24")
	dangerColor  = lipgloss.Color("#F87171")
	subtleColor  = lipgloss.Color("#8892A4")
	bgColor      = lipgloss.Color("#0F1117")
	panelBgColor = lipgloss.Color("#1A1D27")

	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FFFFFF")).
			Background(accentColor).
			Padding(0, 1)

	statusStyle = lipgloss.NewStyle().
			Bold(true).
			Padding(0, 1)

	cardStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(accentColor).
			Background(panelBgColor).
			Padding(0, 1)

	logBoxStyle = lipgloss.NewStyle().
			Border(lipgloss.NormalBorder()).
			BorderForeground(lipgloss.Color("#2E3350")).
			Background(bgColor).
			Padding(0, 1)
)

type logMsg string
type statusMsg orchestrator.StatusType

type model struct {
	cfg       *config.AppConfig
	orch      *orchestrator.Orchestrator
	status    orchestrator.StatusType
	logs      []string
	algos     []string
	algoIdx   int
	headless  bool
	loopMode  bool
	speed     float64
	quitting  bool
	logChan   chan string
	statChan  chan orchestrator.StatusType
	p         *tea.Program
}

func initialModel() model {
	cfg := config.LoadDefaultConfig()
	logCh := make(chan string, 100)
	statCh := make(chan orchestrator.StatusType, 10)

	orch := orchestrator.NewOrchestrator(cfg, func(msg string) {
		select {
		case logCh <- msg:
		default:
		}
	}, func(s orchestrator.StatusType) {
		select {
		case statCh <- s:
		default:
		}
	})

	return model{
		cfg:      cfg,
		orch:     orch,
		status:   orchestrator.StatusIdle,
		algos:    []string{"allfeellove_auto", "form_demo"},
		algoIdx:  0,
		headless: cfg.Headless,
		loopMode: true,
		speed:    cfg.SpeedFactor,
		logChan:  logCh,
		statChan: statCh,
	}
}

func (m model) Init() tea.Cmd {
	return tea.Batch(
		waitForLog(m.logChan),
		waitForStatus(m.statChan),
	)
}

func waitForLog(ch chan string) tea.Cmd {
	return func() tea.Msg {
		msg := <-ch
		return logMsg(msg)
	}
}

func waitForStatus(ch chan orchestrator.StatusType) tea.Cmd {
	return func() tea.Msg {
		s := <-ch
		return statusMsg(s)
	}
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case logMsg:
		t := time.Now().Format("15:04:05")
		m.logs = append(m.logs, fmt.Sprintf("[%s] %s", t, string(msg)))
		if len(m.logs) > 300 {
			m.logs = m.logs[len(m.logs)-300:]
		}
		cmds = append(cmds, waitForLog(m.logChan))

	case statusMsg:
		m.status = orchestrator.StatusType(msg)
		cmds = append(cmds, waitForStatus(m.statChan))

	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			m.orch.Stop()
			m.quitting = true
			return m, tea.Quit

		case "s", "enter":
			if m.status == orchestrator.StatusIdle || m.status == orchestrator.StatusError {
				m.cfg.SelectedAlgo = m.algos[m.algoIdx]
				m.cfg.Headless = m.headless
				m.cfg.SpeedFactor = m.speed
				_ = m.orch.Start(m.loopMode)
			}

		case "x":
			if m.status == orchestrator.StatusRunning || m.status == orchestrator.StatusStarting {
				m.orch.Stop()
			}

		case "tab":
			m.algoIdx = (m.algoIdx + 1) % len(m.algos)

		case "h":
			m.headless = !m.headless

		case "l":
			m.loopMode = !m.loopMode

		case "+", "=":
			m.speed += 0.1
			if m.speed > 3.0 {
				m.speed = 3.0
			}

		case "-", "_":
			m.speed -= 0.1
			if m.speed < 0.1 {
				m.speed = 0.1
			}

		case "c":
			m.logs = nil
		}
	}

	return m, tea.Batch(cmds...)
}

func (m model) View() string {
	if m.quitting {
		return "\n  ¡CamouMacro detenido! Hasta pronto.\n\n"
	}

	// Status Badge
	var statusBadge string
	switch m.status {
	case orchestrator.StatusRunning:
		statusBadge = statusStyle.Background(successColor).Foreground(bgColor).Render("● RUNNING")
	case orchestrator.StatusStarting:
		statusBadge = statusStyle.Background(warningColor).Foreground(bgColor).Render("◐ STARTING")
	case orchestrator.StatusRotating:
		statusBadge = statusStyle.Background(accentColor).Foreground(bgColor).Render("🔄 ROTATING")
	case orchestrator.StatusStopping:
		statusBadge = statusStyle.Background(warningColor).Foreground(bgColor).Render("◑ STOPPING")
	default:
		statusBadge = statusStyle.Background(subtleColor).Foreground(bgColor).Render("○ IDLE")
	}

	header := fmt.Sprintf("  %s  %s  %s",
		titleStyle.Render("CamouMacro Hybrid Suite"),
		statusBadge,
		lipgloss.NewStyle().Foreground(subtleColor).Render("Go Orchestrator ↔ Python Camoufox Engine"),
	)

	// Controles & Settings
	algoDisplay := fmt.Sprintf("Algoritmo [Tab]: %s", lipgloss.NewStyle().Foreground(accentColor).Bold(true).Render(m.algos[m.algoIdx]))
	headlessDisplay := fmt.Sprintf("Headless [h]: %s", boolColor(m.headless))
	loopDisplay := fmt.Sprintf("Auto-Rotación [l]: %s", boolColor(m.loopMode))
	speedDisplay := fmt.Sprintf("Velocidad [+/-]: %.1fx", m.speed)

	controls := fmt.Sprintf(
		"%s   |   %s   |   %s   |   %s\n\nAcciones: [s/Enter] Iniciar  •  [x] Detener  •  [c] Limpiar Logs  •  [q] Salir",
		algoDisplay, headlessDisplay, loopDisplay, speedDisplay,
	)

	panel := cardStyle.Width(96).Render(controls)

	// Visualizador de Logs
	visibleLogs := m.logs
	maxLines := 14
	if len(visibleLogs) > maxLines {
		visibleLogs = visibleLogs[len(visibleLogs)-maxLines:]
	}
	logContent := strings.Join(visibleLogs, "\n")
	if len(visibleLogs) == 0 {
		logContent = lipgloss.NewStyle().Foreground(subtleColor).Render("Consola en espera. Presiona [s] para iniciar la automatización...")
	}

	logsBox := logBoxStyle.Width(96).Height(16).Render(logContent)

	return fmt.Sprintf("\n%s\n\n%s\n\n%s\n", header, panel, logsBox)
}

func boolColor(b bool) string {
	if b {
		return lipgloss.NewStyle().Foreground(successColor).Bold(true).Render("ON")
	}
	return lipgloss.NewStyle().Foreground(subtleColor).Render("OFF")
}

func main() {
	m := initialModel()
	p := tea.NewProgram(m, tea.WithAltScreen())
	m.p = p
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error ejecutando TUI: %v\n", err)
		os.Exit(1)
	}
}
