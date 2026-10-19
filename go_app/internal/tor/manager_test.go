package tor

import (
	"net"
	"testing"
)

func TestFindTorExecutable(t *testing.T) {
	torPath := FindTorExecutable()
	if torPath == "" {
		t.Fatalf("expected to find Tor executable in repository or system, got empty string")
	}
	t.Logf("Found Tor executable at: %s", torPath)
}

func TestStartRejectsPortAlreadyInUse(t *testing.T) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen on temporary port: %v", err)
	}
	defer listener.Close()

	port := listener.Addr().(*net.TCPAddr).Port
	manager := NewManagerWithPorts(nil, []int{port})
	if err := manager.Start(port); err == nil {
		t.Fatal("expected Start to reject a port owned by another Tor process")
	}
}
