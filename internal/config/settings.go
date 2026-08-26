// Package config provee la configuración global de automatización y tiempos de ejecución.
// Los valores se leen desde variables de entorno; si no existen, se usan los defaults aquí definidos.
package config

import (
	"math"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
)

// AutomationConfig centraliza todos los parámetros de velocidad, delays y rutas.
type AutomationConfig struct {
	// SpeedFactor es el multiplicador global de todos los delays.
	//   1.0 = normal | 0.5 = doble rápido | 0.2 = ultra-rápido | 1.5 = más humano
	SpeedFactor float64

	// TargetsFile es la ruta al diccionario de perfiles objetivo.
	TargetsFile string

	// MaxScanPages limita cuántas páginas se escanean por sesión.
	MaxScanPages int

	// MessageCooldownSeconds es el cooldown entre envíos de mensajes (segundos).
	MessageCooldownSeconds float64

	// StickerCount es la cantidad de stickers a enviar.
	StickerCount int

	// StickerIntervalMs es el intervalo entre clics de sticker (ms).
	StickerIntervalMs int

	// TypingMinDelayMs es el retardo mínimo por carácter al escribir (ms).
	TypingMinDelayMs int

	// TypingMaxDelayMs es el retardo máximo por carácter al escribir (ms).
	TypingMaxDelayMs int

	// DefaultTimeoutMs es el timeout estándar para localizar elementos (ms).
	DefaultTimeoutMs int
}

// Default devuelve una instancia de AutomationConfig leyendo env vars.
func Default() AutomationConfig {
	return AutomationConfig{
		SpeedFactor:            envFloat("SPEED_FACTOR", 1.0),
		TargetsFile:            envStr("TARGETS_FILE", "targets/profiles_dict.txt"),
		MaxScanPages:           envInt("MAX_SCAN_PAGES", 100),
		MessageCooldownSeconds: envFloat("MESSAGE_COOLDOWN_SECONDS", 2.5),
		StickerCount:           envInt("STICKER_COUNT", 5),
		StickerIntervalMs:      envInt("STICKER_INTERVAL_MS", 400),
		TypingMinDelayMs:       envInt("TYPING_MIN_DELAY_MS", 15),
		TypingMaxDelayMs:       envInt("TYPING_MAX_DELAY_MS", 45),
		DefaultTimeoutMs:       envInt("DEFAULT_TIMEOUT_MS", 10000),
	}
}

// DelayMs devuelve base_ms escalado por SpeedFactor (mínimo 1 ms).
func (c AutomationConfig) DelayMs(baseMs float64) int {
	result := int(math.Round(baseMs * c.SpeedFactor))
	if result < 1 {
		return 1
	}
	return result
}

// DelayS devuelve base_seconds escalado por SpeedFactor (mínimo 10 ms).
func (c AutomationConfig) DelayS(baseSeconds float64) float64 {
	result := baseSeconds * c.SpeedFactor
	if result < 0.01 {
		return 0.01
	}
	return result
}

// TargetsPath devuelve la ruta absoluta al archivo de perfiles objetivo.
func (c AutomationConfig) TargetsPath() string {
	_, filename, _, _ := runtime.Caller(0)
	// Sube dos niveles desde internal/config/ hasta la raíz del proyecto
	root := filepath.Join(filepath.Dir(filename), "..", "..")
	return filepath.Join(root, filepath.FromSlash(c.TargetsFile))
}

// ──────────────────────────────────────────────────────────────
// Helpers para leer env vars con defaults
// ──────────────────────────────────────────────────────────────

func envStr(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func envInt(key string, def int) int {
	if v := os.Getenv(key); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return def
}

func envFloat(key string, def float64) float64 {
	if v := os.Getenv(key); v != "" {
		if f, err := strconv.ParseFloat(v, 64); err == nil {
			return f
		}
	}
	return def
}
