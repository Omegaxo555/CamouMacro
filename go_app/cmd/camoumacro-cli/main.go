package main

import (
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/omegaxo555/camoumacro/go_app/internal/config"
	"github.com/omegaxo555/camoumacro/go_app/internal/orchestrator"
)

func main() {
	cfg := config.LoadDefaultConfig()

	algoFlag := flag.String("algo", cfg.SelectedAlgo, "ID del algoritmo a ejecutar")
	torPortFlag := flag.Int("tor-port", cfg.TorPort, "Puerto inicial de Tor SOCKS5")
	headlessFlag := flag.Bool("headless", cfg.Headless, "Ejecutar en modo headless")
	speedFlag := flag.Float64("speed", cfg.SpeedFactor, "Factor multiplicador de velocidad")
	loopFlag := flag.Bool("loop", true, "Ejecutar en bucle continuo con rotación")
	flag.Parse()

	cfg.SelectedAlgo = *algoFlag
	cfg.TorPort = *torPortFlag
	cfg.Headless = *headlessFlag
	cfg.SpeedFactor = *speedFlag

	fmt.Println("=======================================================")
	fmt.Println("   CamouMacro CLI Orchestrator (Go + Python Hybrid)   ")
	fmt.Println("=======================================================")
	fmt.Printf("Algoritmo: %s | Puerto Tor: %d | Headless: %t | Speed: %.2fx\n\n",
		cfg.SelectedAlgo, cfg.TorPort, cfg.Headless, cfg.SpeedFactor)

	orch := orchestrator.NewOrchestrator(cfg, func(line string) {
		fmt.Println(line)
	}, nil)

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-sigChan
		fmt.Println("\n[signal] Deteniendo orquestador...")
		orch.Stop()
		os.Exit(0)
	}()

	if err := orch.Start(*loopFlag); err != nil {
		fmt.Printf("[ERROR] %v\n", err)
		os.Exit(1)
	}

	// Mantener el proceso vivo hasta que se interrumpa
	select {}
}
