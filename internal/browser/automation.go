// Package browser provee herramientas de automatización de navegador humana.
// Equivalente Go de modules/browser_automation.py.
package browser

import (
	"fmt"
	"log/slog"
	"math/rand"
	"strings"
	"time"

	"github.com/mxschmitt/playwright-go"
)

// HtmlElement representa un elemento HTML identificado por un selector CSS, XPath o texto.
// Equivalente al dataclass HtmlElement de browser_automation.py.
type HtmlElement struct {
	Selector string
	Kind     string // "css", "xpath", "text"
}

// CSS crea un HtmlElement con selector CSS.
func CSS(selector string) HtmlElement {
	return HtmlElement{Selector: selector, Kind: "css"}
}

// XPath crea un HtmlElement con selector XPath.
func XPath(selector string) HtmlElement {
	return HtmlElement{Selector: selector, Kind: "xpath"}
}

// Text crea un HtmlElement con selector de texto.
func Text(text string) HtmlElement {
	return HtmlElement{Selector: text, Kind: "text"}
}

// ToSelector convierte el HtmlElement al formato de selector de Playwright.
func (e HtmlElement) ToSelector() string {
	switch e.Kind {
	case "xpath":
		return "xpath=" + e.Selector
	case "text":
		return "text=" + e.Selector
	default:
		return e.Selector
	}
}

// String implementa fmt.Stringer para debugging.
func (e HtmlElement) String() string {
	return fmt.Sprintf("[%s: %s]", e.Kind, e.Selector)
}

// ──────────────────────────────────────────────────────────────────────────────
// BrowserAutomation
// ──────────────────────────────────────────────────────────────────────────────

// BrowserAutomation encapsula operaciones de automatización web con delays humanos.
// Equivalente a la clase BrowserAutomation de browser_automation.py.
type BrowserAutomation struct {
	Page           playwright.Page
	DefaultTimeout float64 // en ms
	Debug          bool
	SpeedFactor    float64
}

// NewAutomation crea una instancia de BrowserAutomation.
func NewAutomation(page playwright.Page, timeoutMs int, debug bool, speedFactor float64) *BrowserAutomation {
	if speedFactor < 0.05 {
		speedFactor = 0.05
	}
	return &BrowserAutomation{
		Page:           page,
		DefaultTimeout: float64(timeoutMs),
		Debug:          debug,
		SpeedFactor:    speedFactor,
	}
}

func (a *BrowserAutomation) debug(msg string) {
	if a.Debug {
		slog.Debug("[browser_automation] " + msg)
		fmt.Println("[browser_automation]", msg)
	}
}

// resolveSelector convierte un HtmlElement o string a selector Playwright.
func (a *BrowserAutomation) resolveSelector(target interface{}) string {
	switch v := target.(type) {
	case HtmlElement:
		return v.ToSelector()
	case string:
		return v
	default:
		return fmt.Sprintf("%v", v)
	}
}

// Locator devuelve un playwright.Locator para el target dado.
func (a *BrowserAutomation) Locator(target interface{}) playwright.Locator {
	sel := a.resolveSelector(target)
	if strings.HasPrefix(strings.ToLower(sel), "text=") {
		text := strings.TrimPrefix(sel, "text=")
		return a.Page.GetByText(text, playwright.PageGetByTextOptions{Exact: playwright.Bool(false)})
	}
	return a.Page.Locator(sel)
}

// ──────────────────────────────────────────────────────────────────────────────
// Espera y existencia
// ──────────────────────────────────────────────────────────────────────────────

// WaitForSelector espera a que el selector sea visible.
// Equivalente a BrowserAutomation.wait_for_visible().
func (a *BrowserAutomation) WaitForSelector(target interface{}, timeoutMs ...float64) error {
	timeout := a.DefaultTimeout
	if len(timeoutMs) > 0 {
		timeout = timeoutMs[0]
	}
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Esperando selector: %s", sel))
	return a.Page.Locator(sel).WaitFor(playwright.LocatorWaitForOptions{
		State:   playwright.WaitForSelectorStateVisible,
		Timeout: playwright.Float(timeout),
	})
}

// ElementExists verifica si un elemento existe en la página sin lanzar error.
// Equivalente a BrowserAutomation.element_exists().
func (a *BrowserAutomation) ElementExists(target interface{}) bool {
	sel := a.resolveSelector(target)
	count, err := a.Page.Locator(sel).Count()
	if err != nil {
		return false
	}
	return count > 0
}

// ──────────────────────────────────────────────────────────────────────────────
// Interacción
// ──────────────────────────────────────────────────────────────────────────────

// Click hace click en el elemento dado esperando a que sea visible.
// Equivalente a BrowserAutomation.click().
func (a *BrowserAutomation) Click(target interface{}, timeoutMs ...float64) error {
	timeout := a.DefaultTimeout
	if len(timeoutMs) > 0 {
		timeout = timeoutMs[0]
	}
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Haciendo click en: %s", sel))

	loc := a.Page.Locator(sel)
	if err := loc.WaitFor(playwright.LocatorWaitForOptions{
		State:   playwright.WaitForSelectorStateVisible,
		Timeout: playwright.Float(timeout),
	}); err != nil {
		return fmt.Errorf("elemento no visible para click (%s): %w", sel, err)
	}

	a.humanPause(50, 150)
	return loc.Click()
}

// HumanType escribe texto en un campo con delays aleatorios entre caracteres
// para simular escritura humana.
// Equivalente a BrowserAutomation.human_type() de browser_automation.py.
func (a *BrowserAutomation) HumanType(target interface{}, text string, minDelayMs, maxDelayMs int) error {
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Escribiendo en %s: %q", sel, text))

	loc := a.Page.Locator(sel)
	if err := loc.WaitFor(playwright.LocatorWaitForOptions{
		State:   playwright.WaitForSelectorStateVisible,
		Timeout: playwright.Float(a.DefaultTimeout),
	}); err != nil {
		return fmt.Errorf("campo no visible para escribir (%s): %w", sel, err)
	}

	if err := loc.Click(); err != nil {
		return fmt.Errorf("no se pudo hacer click en campo (%s): %w", sel, err)
	}

	for _, ch := range text {
		if err := loc.Type(string(ch), playwright.LocatorTypeOptions{
			Delay: playwright.Float(float64(a.scaledDelay(minDelayMs, maxDelayMs))),
		}); err != nil {
			return fmt.Errorf("error escribiendo carácter en (%s): %w", sel, err)
		}
	}
	return nil
}

// Fill rellena un campo de formulario directamente (sin delays por carácter).
func (a *BrowserAutomation) Fill(target interface{}, value string) error {
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Rellenando %s con: %q", sel, value))
	loc := a.Page.Locator(sel)
	if err := loc.WaitFor(playwright.LocatorWaitForOptions{
		State:   playwright.WaitForSelectorStateVisible,
		Timeout: playwright.Float(a.DefaultTimeout),
	}); err != nil {
		return fmt.Errorf("campo no visible para rellenar (%s): %w", sel, err)
	}
	return loc.Fill(value)
}

// GetText obtiene el texto visible de un elemento.
// Equivalente a BrowserAutomation.get_text().
func (a *BrowserAutomation) GetText(target interface{}) (string, error) {
	sel := a.resolveSelector(target)
	return a.Page.Locator(sel).InnerText(playwright.LocatorInnerTextOptions{
		Timeout: playwright.Float(a.DefaultTimeout),
	})
}

// ScrollTo hace scroll hasta el elemento dado.
// Equivalente a BrowserAutomation.scroll_to().
func (a *BrowserAutomation) ScrollTo(target interface{}) error {
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Scroll hasta: %s", sel))
	return a.Page.Locator(sel).ScrollIntoViewIfNeeded(playwright.LocatorScrollIntoViewIfNeededOptions{
		Timeout: playwright.Float(a.DefaultTimeout),
	})
}

// SelectOption selecciona una opción en un elemento <select>.
func (a *BrowserAutomation) SelectOption(target interface{}, value string) error {
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Seleccionando opción '%s' en: %s", value, sel))
	_, err := a.Page.Locator(sel).SelectOption(playwright.SelectOptionValues{
		Values: &[]string{value},
	})
	return err
}

// Hover mueve el mouse sobre el elemento.
func (a *BrowserAutomation) Hover(target interface{}) error {
	sel := a.resolveSelector(target)
	a.debug(fmt.Sprintf("Hover sobre: %s", sel))
	return a.Page.Locator(sel).Hover()
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers de delay humano
// ──────────────────────────────────────────────────────────────────────────────

// humanPause pausa un tiempo aleatorio entre min y max ms, escalado por SpeedFactor.
func (a *BrowserAutomation) humanPause(minMs, maxMs int) {
	delay := a.scaledDelay(minMs, maxMs)
	time.Sleep(time.Duration(delay) * time.Millisecond)
}

// scaledDelay devuelve un delay aleatorio en [minMs, maxMs] escalado por SpeedFactor.
func (a *BrowserAutomation) scaledDelay(minMs, maxMs int) int {
	if minMs >= maxMs {
		return int(float64(minMs) * a.SpeedFactor)
	}
	raw := minMs + rand.Intn(maxMs-minMs)
	scaled := int(float64(raw) * a.SpeedFactor)
	if scaled < 1 {
		return 1
	}
	return scaled
}

// HumanDelay es un helper público para pausas humanas aleatorias.
func HumanDelay(minMs, maxMs int) {
	if minMs >= maxMs {
		time.Sleep(time.Duration(minMs) * time.Millisecond)
		return
	}
	delay := minMs + rand.Intn(maxMs-minMs)
	time.Sleep(time.Duration(delay) * time.Millisecond)
}
