// Package tor provee utilidades para verificar conectividad de puertos Tor.
package tor

import (
	"net"
	"time"
)

// IsPortOpen intenta una conexión TCP a host:port con el timeout dado.
// Equivalente a is_port_open() de main.py.
func IsPortOpen(host string, port int, timeoutSec float64) bool {
	address := net.JoinHostPort(host, portStr(port))
	timeout := time.Duration(timeoutSec * float64(time.Second))
	conn, err := net.DialTimeout("tcp", address, timeout)
	if err != nil {
		return false
	}
	_ = conn.Close()
	return true
}

// IsTorAvailable comprueba si Tor está escuchando en 127.0.0.1:port.
func IsTorAvailable(port int) bool {
	return IsPortOpen("127.0.0.1", port, 1.0)
}

// portStr convierte un entero a string para usarlo en net.JoinHostPort.
func portStr(port int) string {
	return net.JoinHostPort("", intToStr(port))[1:] // quita el host vacío
}
