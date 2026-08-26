package ui

import (
	"fmt"
	"strconv"
	"strings"
	"sync"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"

	"github.com/omegaxo555/camoumacro/go_app/internal/config"
	"github.com/omegaxo555/camoumacro/go_app/internal/orchestrator"
)

// MainUI estructura que controla la GUI de Fyne.
type MainUI struct {
	fyneApp fyne.App
	window  fyne.Window
	cfg     *config.AppConfig
	orch    *orchestrator.Orchestrator

	// Widgets UI
	statusBadge   *widget.Label
	torPortLabel  *widget.Label
	algoSelect    *widget.Select
	headlessCheck *widget.Check
	loopCheck     *widget.Check
	speedSlider   *widget.Slider
	speedLabel    *widget.Label

	logEntry    *widget.Entry
	logMu       sync.Mutex
	logMessages []string

	startBtn *widget.Button
	stopBtn  *widget.Button
}

// NewMainUI inicializa y construye la aplicación gráfica.
func NewMainUI(cfg *config.AppConfig) *MainUI {
	a := app.NewWithID("com.camoumacro.orchestrator")
	a.Settings().SetTheme(&DarkCustomTheme{})

	w := a.NewWindow("CamouMacro Control Panel (Go + Python Hybrid)")
	w.Resize(fyne.NewSize(880, 580))
	w.CenterOnScreen()

	ui := &MainUI{
		fyneApp: a,
		window:  w,
		cfg:     cfg,
	}

	ui.orch = orchestrator.NewOrchestrator(cfg, ui.AppendLog, ui.UpdateStatus)
	ui.buildUI()

	w.SetOnClosed(func() {
		ui.orch.Stop()
	})

	return ui
}

// Run ejecuta el bucle de eventos de la GUI.
func (ui *MainUI) Run() {
	ui.window.ShowAndRun()
}

// AppendLog añade una línea a la consola de logs de forma segura para concurrencia.
func (ui *MainUI) AppendLog(line string) {
	ui.logMu.Lock()
	defer ui.logMu.Unlock()

	timestamp := time.Now().Format("15:04:05")
	formatted := fmt.Sprintf("[%s] %s", timestamp, line)
	ui.logMessages = append(ui.logMessages, formatted)

	// Mantener máximo 1000 líneas en buffer
	if len(ui.logMessages) > 1000 {
		ui.logMessages = ui.logMessages[len(ui.logMessages)-1000:]
	}

	fullText := strings.Join(ui.logMessages, "\n")
	ui.window.Canvas().Refresh(ui.logEntry)
	ui.logEntry.SetText(fullText)
	ui.logEntry.CursorRow = len(ui.logMessages)
}

// UpdateStatus actualiza el badge de estado visual.
func (ui *MainUI) UpdateStatus(status orchestrator.StatusType) {
	if ui.statusBadge == nil {
		return
	}

	switch status {
	case orchestrator.StatusRunning:
		ui.statusBadge.SetText("● EN EJECUCIÓN")
		ui.startBtn.Disable()
		ui.stopBtn.Enable()
	case orchestrator.StatusStarting:
		ui.statusBadge.SetText("◐ INICIANDO")
		ui.startBtn.Disable()
		ui.stopBtn.Enable()
	case orchestrator.StatusRotating:
		ui.statusBadge.SetText("🔄 ROTANDO SALIDA")
	case orchestrator.StatusStopping:
		ui.statusBadge.SetText("◑ DETENIENDO")
	case orchestrator.StatusIdle:
		ui.statusBadge.SetText("○ DETENIDO (IDLE)")
		ui.startBtn.Enable()
		ui.stopBtn.Disable()
	case orchestrator.StatusError:
		ui.statusBadge.SetText("✖ ERROR")
		ui.startBtn.Enable()
		ui.stopBtn.Disable()
	}
}

func (ui *MainUI) buildUI() {
	// ── 1. Header Superior con Status Badge ──────────────────────────────
	titleLabel := widget.NewLabelWithStyle("CamouMacro Hybrid Suite", fyne.TextAlignLeading, fyne.TextStyle{Bold: true})
	ui.statusBadge = widget.NewLabelWithStyle("○ DETENIDO (IDLE)", fyne.TextAlignTrailing, fyne.TextStyle{Bold: true})

	header := container.NewBorder(nil, nil, titleLabel, ui.statusBadge)

	// ── 2. Vista Dashboard / Control Principal ──────────────────────────
	dashboardView := ui.buildDashboardTab()

	// ── 3. Vista Logs en Vivo ───────────────────────────────────────────
	logsView := ui.buildLogsTab()

	// ── 4. Vista Configuración Avanzada ─────────────────────────────────
	settingsView := ui.buildSettingsTab()

	// ── 5. Tabs Layout ──────────────────────────────────────────────────
	tabs := container.NewAppTabs(
		container.NewTabItemWithIcon("Dashboard", theme.HomeIcon(), dashboardView),
		container.NewTabItemWithIcon("Consola de Logs", theme.DocumentIcon(), logsView),
		container.NewTabItemWithIcon("Configuración", theme.SettingsIcon(), settingsView),
	)

	// Contenedor principal
	mainContent := container.NewBorder(
		container.NewVBox(header, widget.NewSeparator()),
		nil, nil, nil,
		tabs,
	)

	ui.window.SetContent(container.NewPadded(mainContent))
	ui.AppendLog("Sistema inicializado. CamouMacro listo en arquitectura híbrida.")
}

func (ui *MainUI) buildDashboardTab() fyne.CanvasObject {
	// Selector de Algoritmo
	ui.algoSelect = widget.NewSelect([]string{"allfeellove_auto", "form_demo"}, func(selected string) {
		ui.cfg.SelectedAlgo = selected
		ui.AppendLog(fmt.Sprintf("[config] Algoritmo seleccionado: %s", selected))
	})
	ui.algoSelect.SetSelected(ui.cfg.SelectedAlgo)

	// Switches y Opciones
	ui.headlessCheck = widget.NewCheck("Modo Headless (Ocultar ventana del navegador)", func(checked bool) {
		ui.cfg.Headless = checked
	})
	ui.headlessCheck.SetChecked(ui.cfg.Headless)

	ui.loopCheck = widget.NewCheck("Bucle Continuo con Rotación Automática", nil)
	ui.loopCheck.SetChecked(true)

	// Slider de Velocidad
	ui.speedLabel = widget.NewLabel(fmt.Sprintf("Multiplicador de Velocidad: %.2fx", ui.cfg.SpeedFactor))
	ui.speedSlider = widget.NewSlider(0.1, 3.0)
	ui.speedSlider.SetValue(ui.cfg.SpeedFactor)
	ui.speedSlider.Step = 0.1
	ui.speedSlider.OnChanged = func(val float64) {
		ui.cfg.SpeedFactor = val
		ui.speedLabel.SetText(fmt.Sprintf("Multiplicador de Velocidad: %.2fx", val))
	}

	// Botones Start / Stop
	ui.startBtn = widget.NewButtonWithIcon("INICIAR AUTOMATIZACIÓN", theme.MediaPlayIcon(), func() {
		err := ui.orch.Start(ui.loopCheck.Checked)
		if err != nil {
			dialog.ShowError(err, ui.window)
		}
	})
	ui.startBtn.Importance = widget.HighImportance

	ui.stopBtn = widget.NewButtonWithIcon("DETENER", theme.MediaStopIcon(), func() {
		ui.orch.Stop()
	})
	ui.stopBtn.Disable()

	buttonsGrid := container.NewGridWithColumns(2, ui.startBtn, ui.stopBtn)

	// Tarjeta informativa de Arquitectura
	archCard := widget.NewCard("Arquitectura Híbrida Activa", "Go + Fyne (Frontend/Orchestrator) ↔ Python + Camoufox (Engine)",
		widget.NewLabel("• Evasión y Fingerprints: Camoufox nativo en Python\n• GUI y Control de Procesos: Go 1.22 + Fyne v2\n• Proxy: Red Tor SOCKS5 con rotación dinámica de puertos"),
	)

	formGroup := container.NewVBox(
		widget.NewLabelWithStyle("Selección de Algoritmo:", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		ui.algoSelect,
		widget.NewSeparator(),
		ui.headlessCheck,
		ui.loopCheck,
		widget.NewSeparator(),
		ui.speedLabel,
		ui.speedSlider,
		widget.NewSeparator(),
		buttonsGrid,
	)

	return container.NewVBox(
		archCard,
		widget.NewCard("Panel de Control", "", formGroup),
	)
}

func (ui *MainUI) buildLogsTab() fyne.CanvasObject {
	ui.logEntry = widget.NewMultiLineEntry()
	ui.logEntry.Wrapping = fyne.TextWrapWord
	ui.logEntry.TextStyle = fyne.TextStyle{Monospace: true}

	clearBtn := widget.NewButtonWithIcon("Limpiar Consola", theme.DeleteIcon(), func() {
		ui.logMu.Lock()
		ui.logMessages = nil
		ui.logMu.Unlock()
		ui.logEntry.SetText("")
	})

	topBar := container.NewBorder(nil, nil, widget.NewLabelWithStyle("Salida de Procesos y Workers en Tiempo Real:", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}), clearBtn)

	return container.NewBorder(topBar, nil, nil, nil, ui.logEntry)
}

func (ui *MainUI) buildSettingsTab() fyne.CanvasObject {
	pythonExeEntry := widget.NewEntry()
	pythonExeEntry.SetText(ui.cfg.PythonExecutable)
	pythonExeEntry.OnChanged = func(s string) { ui.cfg.PythonExecutable = s }

	engineDirEntry := widget.NewEntry()
	engineDirEntry.SetText(ui.cfg.PythonEngineDir)
	engineDirEntry.OnChanged = func(s string) { ui.cfg.PythonEngineDir = s }

	torPortEntry := widget.NewEntry()
	torPortEntry.SetText(strconv.Itoa(ui.cfg.TorPort))
	torPortEntry.OnChanged = func(s string) {
		if p, err := strconv.Atoi(s); err == nil {
			ui.cfg.TorPort = p
		}
	}

	form := widget.NewForm(
		widget.NewFormItem("Ejecutable de Python:", pythonExeEntry),
		widget.NewFormItem("Directorio de Python Engine:", engineDirEntry),
		widget.NewFormItem("Puerto Base de Tor:", torPortEntry),
	)

	return container.NewVBox(
		widget.NewCard("Rutas y Entorno del Sistema", "Configuración de conexión entre Go y Python", form),
	)
}
