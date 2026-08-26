package main

import (
	"github.com/omegaxo555/camoumacro/go_app/internal/config"
	"github.com/omegaxo555/camoumacro/go_app/internal/ui"
)

func main() {
	cfg := config.LoadDefaultConfig()
	appUI := ui.NewMainUI(cfg)
	appUI.Run()
}
