package tor

import (
	"net"
	"strconv"
	"time"
)

// IsPortOpen comprueba si un puerto TCP está abierto y aceptando conexiones.
func IsPortOpen(host string, port int, timeoutSec float64) bool {
	address := net.JoinHostPort(host, strconv.Itoa(port))
	timeout := time.Duration(timeoutSec * float64(time.Second))
	conn, err := net.DialTimeout("tcp", address, timeout)
	if err != nil {
		return false
	}
	_ = conn.Close()
	return true
}

// IsTorAvailable comprueba si Tor responde en 127.0.0.1:port.
func IsTorAvailable(port int) bool {
	return IsPortOpen("127.0.0.1", port, 1.0)
}
