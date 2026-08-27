package tor

import (
	"testing"
)

func TestFindTorExecutable(t *testing.T) {
	torPath := FindTorExecutable()
	if torPath == "" {
		t.Fatalf("expected to find Tor executable in repository or system, got empty string")
	}
	t.Logf("Found Tor executable at: %s", torPath)
}
