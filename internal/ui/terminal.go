// Package ui provee utilidades de terminal: colores ANSI, menú navegable con flechas,
// lectura raw de teclado cross-platform, y helpers de impresión.
// Equivalente Go de core/terminal_ui.py.
package ui

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"

	"golang.org/x/term"
)

// ANSI contiene los códigos de escape para colores y estilos en terminal.
var ANSI = map[string]string{
	"reset":     "\033[0m",
	"bold":      "\033[1m",
	"dim":       "\033[2m",
	"fg_cyan":   "\033[36m",
	"fg_yellow": "\033[33m",
	"fg_green":  "\033[32m",
	"fg_red":    "\033[31m",
	"bg_blue":   "\033[44m",
	"bg_gray":   "\033[100m",
}

// ClearScreen limpia la pantalla de la terminal.
func ClearScreen() {
	var cmd *exec.Cmd
	if runtime.GOOS == "windows" {
		cmd = exec.Command("cmd", "/c", "cls")
	} else {
		cmd = exec.Command("clear")
	}
	cmd.Stdout = os.Stdout
	_ = cmd.Run()
}

// ReadKey lee una tecla en modo raw sin necesitar Enter.
// Devuelve: "up", "down", "left", "right", "enter", o el carácter leído.
// Equivalente a TerminalUI.read_key() de terminal_ui.py.
func ReadKey() string {
	fd := int(os.Stdin.Fd())

	if !term.IsTerminal(fd) {
		// Fallback si no es terminal interactiva (e.g. redireccionada)
		buf := make([]byte, 1)
		_, _ = os.Stdin.Read(buf)
		return normalizeKey(buf)
	}

	oldState, err := term.MakeRaw(fd)
	if err != nil {
		buf := make([]byte, 1)
		_, _ = os.Stdin.Read(buf)
		return normalizeKey(buf)
	}
	defer term.Restore(fd, oldState) //nolint:errcheck

	buf := make([]byte, 6)
	n, err := os.Stdin.Read(buf)
	if err != nil || n == 0 {
		return ""
	}

	return normalizeKey(buf[:n])
}

// normalizeKey convierte bytes leídos del teclado a una cadena normalizada.
func normalizeKey(buf []byte) string {
	seq := string(buf)

	// Teclas de escape (flechas)
	arrowMap := map[string]string{
		"\x1b[A": "up",
		"\x1b[B": "down",
		"\x1b[C": "right",
		"\x1b[D": "left",
	}
	if k, ok := arrowMap[seq]; ok {
		return k
	}

	// Windows: secuencias extendidas (0x00 o 0xe0 seguido de código)
	if len(buf) == 2 && (buf[0] == 0x00 || buf[0] == 0xe0) {
		winMap := map[byte]string{
			0x48: "up",
			0x50: "down",
			0x4B: "left",
			0x4D: "right",
		}
		if k, ok := winMap[buf[1]]; ok {
			return k
		}
	}

	if seq == "\r" || seq == "\n" {
		return "enter"
	}
	if seq == "\x03" { // Ctrl+C
		return "ctrl+c"
	}
	return strings.TrimRight(seq, "\x00")
}

// SelectOption muestra un menú interactivo navegable con flechas de teclado
// y devuelve el índice (0-based) de la opción seleccionada.
// Equivalente a TerminalUI.select_option() de terminal_ui.py.
func SelectOption(title string, options []string, defaultIndex int) int {
	index := defaultIndex
	if index < 0 || index >= len(options) {
		index = 0
	}

	for {
		ClearScreen()
		fmt.Printf("%s%s%s\n", ANSI["bold"], title, ANSI["reset"])
		fmt.Printf("%sUsa ↑ ↓ y Enter para confirmar.%s\n\n", ANSI["dim"], ANSI["reset"])

		for i, opt := range options {
			prefix := "   "
			color := ANSI["bg_gray"]
			if i == index {
				prefix = " > "
				color = ANSI["bg_blue"]
			}
			fmt.Printf("%s%s%s%s\n", color, prefix, opt, ANSI["reset"])
		}

		fmt.Printf("\n%sTeclas: ↑ ↓, Enter o número.%s\n", ANSI["dim"], ANSI["reset"])

		key := strings.ToLower(ReadKey())

		switch key {
		case "w", "up", "8", "a", "left":
			index = (index - 1 + len(options)) % len(options)
		case "s", "down", "2", "d", "right":
			index = (index + 1) % len(options)
		case "enter", "\r", "\n":
			return index
		case "ctrl+c":
			os.Exit(0)
		default:
			// Selección por número
			if n, err := strconv.Atoi(key); err == nil && n >= 1 && n <= len(options) {
				return n - 1
			}
		}
	}
}

// Confirm muestra un menú Sí/No y devuelve true si el usuario eligió Sí.
// Equivalente a TerminalUI.confirm() de terminal_ui.py.
func Confirm(question string, defaultYes bool) bool {
	options := []string{"Sí", "No"}
	def := 0
	if !defaultYes {
		def = 1
	}
	return SelectOption(question, options, def) == 0
}

// Prompt pide una cadena de texto al usuario con un valor por defecto.
// Equivalente a TerminalUI.prompt() de terminal_ui.py.
func Prompt(question, defaultVal string) string {
	suffix := ""
	if defaultVal != "" {
		suffix = fmt.Sprintf(" [%s]", defaultVal)
	}
	fmt.Printf("%s%s: ", question, suffix)
	var value string
	_, _ = fmt.Scanln(&value)
	value = strings.TrimSpace(value)
	if value == "" {
		return defaultVal
	}
	return value
}

// Info imprime un mensaje en cyan.
func Info(msg string) {
	fmt.Printf("%s%s%s\n", ANSI["fg_cyan"], msg, ANSI["reset"])
}

// Warning imprime un mensaje en amarillo.
func Warning(msg string) {
	fmt.Printf("%s%s%s\n", ANSI["fg_yellow"], msg, ANSI["reset"])
}

// Error imprime un mensaje en rojo.
func Error(msg string) {
	fmt.Printf("%s%s%s\n", ANSI["fg_red"], msg, ANSI["reset"])
}

// Success imprime un mensaje en verde.
func Success(msg string) {
	fmt.Printf("%s%s%s\n", ANSI["fg_green"], msg, ANSI["reset"])
}

// Tag imprime un mensaje con tag de color: "[tag] message".
func Tag(tag, color, msg string) {
	c, ok := ANSI[color]
	if !ok {
		c = ANSI["fg_cyan"]
	}
	fmt.Printf("%s[%s]%s %s\n", c, tag, ANSI["reset"], msg)
}
