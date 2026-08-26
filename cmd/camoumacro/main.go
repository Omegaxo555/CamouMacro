// CamouMacro — Punto de entrada principal en Go.
// Equivalente al main.py de Python.
//
// Ciclo de vida:
//  1. Leer configuración desde env vars
//  2. Mostrar menú de selección de algoritmo
//  3. Iniciar Tor + navegador
//  4. Ejecutar algoritmo seleccionado
//  5. Al finalizar, rotar puerto Tor y reiniciar (loop infinito)
//  6. Capturar Ctrl+C para apagado graceful
package main

import (
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/omegaxo555/camoumacro/internal/algorithms"
	"github.com/omegaxo555/camoumacro/internal/algorithms/allfeellove"
	"github.com/omegaxo555/camoumacro/internal/browser"
	"github.com/omegaxo555/camoumacro/internal/tor"
	"github.com/omegaxo555/camoumacro/internal/ui"
)

func init() {
	// Registrar todos los algoritmos disponibles
	algorithms.Register(algorithms.Algorithm{
		ID:      "allfeellove_auto",
		Label:   "Allfeellove Auto",
		Handler: allfeellove.Run,
	})
	algorithms.Register(algorithms.Algorithm{
		ID:    "exit",
		Label: "Salir",
		Handler: func(_ *browser.Handler) error {
			ui.Warning("Saliendo del menú...")
			return nil
		},
	})
}

func main() {
	setupLogger()

	// ── Configuración desde env vars ────────────────────────────────────────
	torPort := envInt("TOR_PORT", 9050)
	headless := os.Getenv("HEADLESS") == "true"
	autoAlgoID := os.Getenv("ALGO")

	// ── Manejador de señales para apagado graceful ───────────────────────────
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

	// ── Selección de algoritmo ───────────────────────────────────────────────
	var selected *algorithms.Algorithm

	if autoAlgoID != "" {
		selected = algorithms.FindByID(autoAlgoID)
		if selected == nil {
			ui.Warning(fmt.Sprintf("Algoritmo '%s' no encontrado, mostrando menú...", autoAlgoID))
		}
	}

	if selected == nil {
		idx := ui.SelectOption("=== CamouMacro — Selección de algoritmo ===", algorithms.Labels(), 0)
		s := algorithms.Registry[idx]
		selected = &s
	}

	// Salir inmediato si se eligió "exit"
	if selected.ID == "exit" {
		_ = selected.Handler(nil)
		return
	}

	// ── Ciclo de vida principal ──────────────────────────────────────────────
	torManager := tor.NewManager()
	restartCount := 0

	for {
		// Comprobar señal de interrupción
		select {
		case <-sigCh:
			ui.Warning("\n[lifecycle] Proceso detenido por el usuario.")
			_ = torManager.Stop()
			return
		default:
		}

		ui.Tag("lifecycle", "fg_cyan", fmt.Sprintf("Inicializando instancia en puerto %d...", torPort))

		// Iniciar Tor
		if err := torManager.Start(torPort); err != nil {
			ui.Tag("tor", "fg_red", fmt.Sprintf("Error iniciando Tor: %v", err))
		}

		// Crear y configurar el handler de navegador
		driver := browser.NewHandler(
			tor.ProxyURL(torPort),
			"templates/perfil_base.tar.gz",
			headless,
			560, 420,
		)

		restartReason := "finalización del algoritmo"

		if err := driver.Initialize(); err != nil {
			ui.Tag("lifecycle", "fg_red", fmt.Sprintf("Error inicializando navegador: %v", err))
			restartReason = "fallo al inicializar el navegador"
		} else {
			// Ejecutar algoritmo
			ui.Tag("debug", "fg_cyan", fmt.Sprintf("Iniciando algoritmo: %s", selected.ID))
			err := runWithRecovery(driver, selected)
			if err != nil {
				ui.Tag("debug", "fg_red", fmt.Sprintf("ERROR en algoritmo: %s — %v", selected.ID, err))
				restartReason = "error fatal del algoritmo"
			} else {
				ui.Tag("debug", "fg_green", fmt.Sprintf("Finalizó el algoritmo: %s", selected.ID))
			}
		}

		// Cerrar todo y rotar
		restartCount++
		ui.Tag("lifecycle", "fg_yellow", fmt.Sprintf(
			"Reinicio #%d por '%s': cerrando navegador y rotando puerto Tor.",
			restartCount, restartReason,
		))

		driver.Close()
		_ = torManager.Stop()

		torPort = torManager.RotatePort()
		ui.Tag("lifecycle", "fg_cyan", fmt.Sprintf("Próxima instancia: puerto %d.", torPort))
		time.Sleep(1 * time.Second)
	}
}

// runWithRecovery ejecuta el handler del algoritmo y captura panics.
func runWithRecovery(driver *browser.Handler, algo *algorithms.Algorithm) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("panic en algoritmo %s: %v", algo.ID, r)
		}
	}()
	return algo.Handler(driver)
}

// setupLogger configura slog para salida estructurada en stdout.
func setupLogger() {
	slog.SetDefault(slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	})))
}

// envInt lee una variable de entorno como entero con un valor por defecto.
func envInt(key string, def int) int {
	if v := os.Getenv(key); v != "" {
		var n int
		if _, err := fmt.Sscan(v, &n); err == nil {
			return n
		}
	}
	return def
}
