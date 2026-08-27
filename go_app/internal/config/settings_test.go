package config

import (
	"testing"
)

func TestLoadDefaultConfig(t *testing.T) {
	cfg := LoadDefaultConfig()
	if cfg.PythonEngineDir == "" {
		t.Fatalf("expected PythonEngineDir to not be empty")
	}
	if cfg.RunnerScript == "" {
		t.Fatalf("expected RunnerScript to not be empty")
	}
}
