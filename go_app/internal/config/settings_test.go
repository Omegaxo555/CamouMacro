package config

import "testing"

func TestLoadDefaultConfig(t *testing.T) {
	cfg := LoadDefaultConfig()
	if cfg.PythonEngineDir == "" {
		t.Fatalf("expected PythonEngineDir to not be empty")
	}
	if cfg.RunnerScript == "" {
		t.Fatalf("expected RunnerScript to not be empty")
	}
}

func TestLoadDefaultConfigSearchAllUsers(t *testing.T) {
	for _, test := range []struct {
		value string
		want  bool
	}{
		{value: "true", want: true},
		{value: "1", want: true},
		{value: "false", want: false},
		{value: "", want: false},
	} {
		t.Run(test.value, func(t *testing.T) {
			t.Setenv("SEARCH_ALL_USERS", test.value)
			cfg := LoadDefaultConfig()
			if cfg.SearchAllUsers != test.want {
				t.Fatalf("SearchAllUsers = %t, want %t", cfg.SearchAllUsers, test.want)
			}
		})
	}
}

func TestLoadDefaultConfigMacroCount(t *testing.T) {
	for _, test := range []struct {
		value string
		want  int
	}{
		{value: "1", want: 1},
		{value: "2", want: 2},
		{value: "3", want: 3},
		{value: "0", want: 1},
		{value: "4", want: 1},
		{value: "invalid", want: 1},
	} {
		t.Run(test.value, func(t *testing.T) {
			t.Setenv("MACRO_COUNT", test.value)
			cfg := LoadDefaultConfig()
			if cfg.MacroCount != test.want {
				t.Fatalf("MacroCount = %d, want %d", cfg.MacroCount, test.want)
			}
		})
	}
}
