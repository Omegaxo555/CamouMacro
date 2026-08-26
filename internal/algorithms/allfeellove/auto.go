// Package allfeellove implementa el algoritmo de automatización para allfeellove.com.
// Equivalente Go de modules/allfeellove_auto.py.
package allfeellove

import (
	"fmt"
	"log/slog"
	"math/rand"
	"time"

	"github.com/mxschmitt/playwright-go"

	"github.com/omegaxo555/camoumacro/internal/browser"
	"github.com/omegaxo555/camoumacro/internal/config"
	"github.com/omegaxo555/camoumacro/internal/infogen"
)

// TargetProfile representa un perfil objetivo que se busca en el sitio.
type TargetProfile struct {
	Name string
	Age  int
}

// defaultTargets son los perfiles objetivo por defecto.
// Equivalente a target_profiles en allfeellove_auto.py.
var defaultTargets = []TargetProfile{
	{Name: "Zol", Age: 41},
	{Name: "Anna", Age: 46},
	{Name: "Kathe", Age: 34},
}

// ageFilters son los filtros de edad disponibles para la búsqueda.
var ageFilters = []string{"41", "34", "46"}

// Automation ejecuta el algoritmo completo de allfeellove.
// Equivalente a AllfeelloveAuto de allfeellove_auto.py.
type Automation struct {
	driver  *browser.Handler
	auto    *browser.BrowserAutomation
	cfg     config.AutomationConfig
	profile infogen.Profile
}

// New crea una nueva instancia del algoritmo.
func New(driver *browser.Handler) *Automation {
	cfg := config.Default()
	auto := browser.NewAutomation(driver.Page, cfg.DefaultTimeoutMs, true, cfg.SpeedFactor)
	return &Automation{
		driver: driver,
		auto:   auto,
		cfg:    cfg,
	}
}

// Run ejecuta el algoritmo completo.
// Equivalente a AllfeelloveAuto.run() de allfeellove_auto.py.
func Run(driver *browser.Handler) error {
	a := New(driver)
	return a.run()
}

func (a *Automation) run() error {
	a.profile = infogen.GenerateProfile("", "", 0, 0)
	slog.Info("[allfeellove_auto] Iniciando algoritmo", "perfil", a.profile.Name)

	return a.runAlgorithm()
}

// runAlgorithm contiene la secuencia principal del algoritmo.
// Equivalente a AllfeelloveAuto._run_algorithm().
func (a *Automation) runAlgorithm() error {
	if a.driver.Page == nil {
		return fmt.Errorf("el navegador no está inicializado")
	}

	a.auto = browser.NewAutomation(a.driver.Page, a.cfg.DefaultTimeoutMs, true, a.cfg.SpeedFactor)
	slog.Info("[allfeellove_auto] Navegando a https://allfeellove.com")

	if err := a.driver.Navigate("https://allfeellove.com", 3); err != nil {
		return fmt.Errorf("no se pudo cargar la página: %w", err)
	}

	if a.driver.IsCloudflareBlocked() {
		slog.Warn("[allfeellove_auto] Cloudflare detectado, rotando conexión...")
		if err := a.driver.RotateConnection(true); err != nil {
			return fmt.Errorf("no se pudo rotar la conexión: %w", err)
		}
		if err := a.driver.Navigate("https://allfeellove.com", 3); err != nil {
			return fmt.Errorf("la página sigue bloqueada tras reinicio: %w", err)
		}
	}

	a.driver.Page.WaitForLoadState(playwright.WaitUntilStateDomcontentloaded, playwright.PageWaitForLoadStateOptions{
		Timeout: playwright.Float(float64(a.driver.TimeoutMs)),
	})
	slog.Info("[allfeellove_auto] Página cargada", "url", a.driver.Page.URL())

	// ── Selectores de formulario de registro ────────────────────────────────
	cookiesButton := browser.XPath("/html/body/div[2]/div/div/div/div/div[2]/div[1]/button[1]")
	genderButton := browser.CSS("label.gender__item.male")
	lookingForButton := browser.CSS("label.checkbox__item.woman.woman_female")
	nameInput := browser.CSS("input.input.input_name.name-container__input")
	dateInput := browser.XPath("/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/div[3]/div[2]/div[1]/input")
	termsCheckbox := browser.XPath("/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/div[4]/div[1]/div[1]/label")
	submitButton := browser.XPath("/html/body/div[1]/div/div/main/div[1]/div/div[2]/div/div/form/button")
	mailInput := browser.XPath("/html/body/div/div/div/main/div[1]/div/div/div/div/form/div[1]/div[1]/input")
	passwordInput := browser.XPath("/html/body/div/div/div/main/div[1]/div/div/div/div/form/div[2]/div[1]/div/input")
	signupButton := browser.XPath("/html/body/div/div/div/main/div[1]/div/div/div/div/form/button")

	// Verificar que los selectores principales existen
	for label, sel := range map[string]browser.HtmlElement{
		"genero":   genderButton,
		"busqueda": lookingForButton,
		"nombre":   nameInput,
		"fecha":    dateInput,
		"terminos": termsCheckbox,
		"enviar":   submitButton,
	} {
		exists := a.auto.ElementExists(sel)
		slog.Info(fmt.Sprintf("[allfeellove_auto] ¿Existe %s?", label), "resultado", exists)
		if !exists {
			slog.Warn(fmt.Sprintf("[allfeellove_auto] No existe el selector de %s", label))
		}
	}

	// ── Paso 1: Aceptar cookies ─────────────────────────────────────────────
	if a.auto.ElementExists(cookiesButton) {
		if err := a.auto.Click(cookiesButton); err != nil {
			slog.Warn("[allfeellove_auto] No se pudo hacer click en cookies", "err", err)
		}
	}

	// ── Paso 2: Seleccionar género y preferencia ────────────────────────────
	if err := a.auto.Click(genderButton); err != nil {
		slog.Warn("[allfeellove_auto] Click género fallido", "err", err)
	}
	if err := a.auto.Click(lookingForButton); err != nil {
		slog.Warn("[allfeellove_auto] Click búsqueda fallido", "err", err)
	}

	// ── Paso 3: Completar nombre y fecha ───────────────────────────────────
	if err := a.auto.HumanType(nameInput, a.profile.Name,
		a.cfg.TypingMinDelayMs, a.cfg.TypingMaxDelayMs); err != nil {
		slog.Warn("[allfeellove_auto] Error escribiendo nombre", "err", err)
	}
	if err := a.auto.HumanType(dateInput, a.profile.Birthdate,
		a.cfg.TypingMinDelayMs, a.cfg.TypingMaxDelayMs); err != nil {
		slog.Warn("[allfeellove_auto] Error escribiendo fecha", "err", err)
	}

	// ── Paso 4: Términos y envío ────────────────────────────────────────────
	if err := a.auto.Click(termsCheckbox); err != nil {
		slog.Warn("[allfeellove_auto] Error en checkbox de términos", "err", err)
	}
	if err := a.auto.Click(submitButton); err != nil {
		slog.Warn("[allfeellove_auto] Error en botón de envío", "err", err)
	}

	a.driver.Page.WaitForLoadState(playwright.WaitUntilStateDomcontentloaded, playwright.PageWaitForLoadStateOptions{
		Timeout: playwright.Float(float64(a.driver.TimeoutMs)),
	})

	// ── Paso 5: Email y contraseña ─────────────────────────────────────────
	if err := a.auto.HumanType(mailInput, a.profile.Email,
		a.cfg.TypingMinDelayMs, a.cfg.TypingMaxDelayMs); err != nil {
		slog.Warn("[allfeellove_auto] Error escribiendo email", "err", err)
	}
	if err := a.auto.HumanType(passwordInput, a.profile.Password,
		a.cfg.TypingMinDelayMs, a.cfg.TypingMaxDelayMs); err != nil {
		slog.Warn("[allfeellove_auto] Error escribiendo contraseña", "err", err)
	}
	if err := a.auto.Click(signupButton); err != nil {
		slog.Warn("[allfeellove_auto] Error en botón signup", "err", err)
	}

	// ── Paso 6: Flujo post-registro (skip onboarding + claim tokens) ────────
	slog.Info("[allfeellove_auto] Esperando inicio de sesión (~1 min)...")
	a.driver.Page.WaitForLoadState(playwright.WaitUntilStateDomcontentloaded, playwright.PageWaitForLoadStateOptions{
		Timeout: playwright.Float(float64(a.driver.TimeoutMs)),
	})

	onboardingSteps := []struct {
		label   string
		sel     browser.HtmlElement
		timeout float64
	}{
		{"nextLets", browser.CSS(`button[data-test-id="cmp:ui-button click:next Let's do it!"]`), 160000},
		{"nextStep1", browser.CSS(`button[data-test-id="cmp:ui-button click:skip skip"]`), 10000},
		{"nextStep2", browser.CSS(`button[data-test-id="cmp:ui-button click:pref-gender female"]`), 10000},
		{"nextStep3", browser.CSS(`button[data-test-id="cmp:ui-button click:skip skip"]`), 10000},
		{"skipToStep4", browser.CSS(`button[data-test-id="cmp:ui-modal click:close"]`), 10000},
		{"nextStep4", browser.CSS(`button[data-test-id="cmp:ui-button click:skip skip"]`), 10000},
		{"nextStep5", browser.CSS(`button[data-test-id="cmp:ui-button click:next Continue"]`), 10000},
		{"claimTokens", browser.CSS(`[data-test-id="cmp:button-new click:claim-welcome-bonus"]`), 10000},
		{"cancelEmail", browser.CSS(`#Close`), 10000},
	}

	for _, step := range onboardingSteps {
		if err := a.auto.WaitForSelector(step.sel, step.timeout); err != nil {
			slog.Warn(fmt.Sprintf("[allfeellove_auto] Timeout esperando %s", step.label), "err", err)
			continue
		}
		if err := a.auto.Click(step.sel); err != nil {
			slog.Warn(fmt.Sprintf("[allfeellove_auto] Error en %s", step.label), "err", err)
		} else {
			slog.Info(fmt.Sprintf("[allfeellove_auto] ✓ %s", step.label))
		}
	}
	slog.Info("----- Se han reclamado los tokens de bienvenida -----")

	// ── Paso 7: Búsqueda de perfiles ───────────────────────────────────────
	accountSearch := browser.CSS(`a[data-test-id="file:r-u-tab-bar search"], #AccountSearch, a[href="/search"]`)
	allPeopleButton := browser.CSS(`label.chip-root[data-test-id="file:extend-search click:change-online-filter-false all"]`)
	filtersButton := browser.CSS(`[data-test-id="file:extend-search click:show-filter filters"]`)
	countrySelect := browser.CSS(`div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-country select-country"]`)
	countrySearchInput := browser.CSS(`div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-country select-country"] input.multiselect__input`)
	ageFromSelect := browser.CSS(`div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-from from"]`)
	ageFromInput := browser.CSS(`div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-from from"] input.multiselect__input`)
	ageToSelect := browser.CSS(`div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-to to"]`)
	ageToInput := browser.CSS(`div.multiselect[role="combobox"][data-test-id="cmp:ui-select search-age-to to"] input.multiselect__input`)
	searchPeople := browser.CSS(`button[data-test-id="cmp:ui-button click:show-people show-people"]`)

	if err := a.auto.Click(accountSearch); err != nil {
		slog.Warn("[allfeellove_auto] Error abriendo búsqueda", "err", err)
	}
	a.driver.Page.WaitForLoadState(playwright.WaitUntilStateDomcontentloaded, playwright.PageWaitForLoadStateOptions{
		Timeout: playwright.Float(float64(a.driver.TimeoutMs)),
	})

	_ = a.auto.Click(allPeopleButton)
	time.Sleep(80 * time.Millisecond)
	_ = a.auto.Click(filtersButton)
	_ = a.auto.WaitForSelector(browser.CSS(".search-filters-form, [data-test-id=\"cmp:search-filter content\"]"), 4000)

	// Seleccionar país
	_ = a.selectMultiselect(countrySelect, countrySearchInput, "United States")

	// Seleccionar filtro de edad aleatorio
	ageFilter := ageFilters[rand.Intn(len(ageFilters))]
	_ = a.selectMultiselect(ageFromSelect, ageFromInput, ageFilter)
	_ = a.selectMultiselect(ageToSelect, ageToInput, ageFilter)

	_ = a.auto.Click(searchPeople)
	slog.Info("[allfeellove_auto] Filtros aplicados, iniciando escaneo de perfiles...")

	// ── Paso 8: Escanear y enviar mensajes ─────────────────────────────────
	targetMap := make(map[string]int)
	for _, t := range defaultTargets {
		targetMap[t.Name] = t.Age
	}

	foundProfile := a.scanProfilesUntilFound(targetMap, a.cfg.MaxScanPages)
	if foundProfile != nil {
		slog.Info("[allfeellove_auto] Perfil encontrado", "nombre", foundProfile.Name, "edad", foundProfile.Age)
		return a.sendMessages(foundProfile)
	}

	slog.Warn("[allfeellove_auto] Ningún perfil objetivo encontrado tras el escaneo completo")
	return nil
}

// selectMultiselect interactúa con un componente multiselect de Vue.js.
// Equivalente a BrowserAutomation.select_multiselect_option() de browser_automation.py.
func (a *Automation) selectMultiselect(containerSel, inputSel browser.HtmlElement, value string) error {
	if err := a.auto.Click(containerSel); err != nil {
		return fmt.Errorf("no se pudo abrir el multiselect: %w", err)
	}
	time.Sleep(300 * time.Millisecond)

	if err := a.auto.Fill(inputSel, value); err != nil {
		return fmt.Errorf("no se pudo escribir en el input del multiselect: %w", err)
	}
	time.Sleep(400 * time.Millisecond)

	// Hacer click en la primera opción de la lista desplegada
	optionSel := browser.CSS(".multiselect__option--highlight, .multiselect__element:first-child")
	if err := a.auto.Click(optionSel); err != nil {
		// Intentar con Enter como fallback
		if err2 := a.driver.Page.Keyboard().Press("Enter"); err2 != nil {
			return fmt.Errorf("no se pudo seleccionar la opción '%s': %w", value, err)
		}
	}
	return nil
}

// scanProfilesUntilFound escanea páginas de perfiles buscando los nombres objetivo.
// Equivalente a AllfeelloveAuto._scan_profiles_until_found() de allfeellove_auto.py.
func (a *Automation) scanProfilesUntilFound(targets map[string]int, maxPages int) *TargetProfile {
	for page := 0; page < maxPages; page++ {
		slog.Info(fmt.Sprintf("[allfeellove_auto] Escaneando página %d/%d", page+1, maxPages))

		// Obtener todos los nombres visibles en la página de resultados
		nameEls, err := a.driver.Page.Locator(".user-name, .profile-name, h3.name, [class*='name']").All()
		if err != nil {
			slog.Warn("[allfeellove_auto] Error obteniendo nombres", "err", err)
			break
		}

		for _, el := range nameEls {
			text, err := el.InnerText()
			if err != nil {
				continue
			}
			for name, age := range targets {
				if name == text {
					slog.Info(fmt.Sprintf("[allfeellove_auto] ✓ Perfil objetivo encontrado: %s (%d)", name, age))
					return &TargetProfile{Name: name, Age: age}
				}
			}
		}

		// Pasar a la siguiente página
		nextBtn := browser.CSS(`button[data-test-id*="next"], .pagination-next, [aria-label="Next"]`)
		if !a.auto.ElementExists(nextBtn) {
			slog.Info("[allfeellove_auto] No hay más páginas de resultados")
			break
		}
		if err := a.auto.Click(nextBtn); err != nil {
			break
		}
		a.driver.Page.WaitForLoadState(playwright.WaitUntilStateDomcontentloaded, playwright.PageWaitForLoadStateOptions{
			Timeout: playwright.Float(float64(a.driver.TimeoutMs)),
		})
		time.Sleep(time.Duration(a.cfg.DelayMs(500)) * time.Millisecond)
	}
	return nil
}

// sendMessages envía mensajes al perfil objetivo encontrado.
func (a *Automation) sendMessages(target *TargetProfile) error {
	slog.Info(fmt.Sprintf("[allfeellove_auto] Enviando mensajes a: %s", target.Name))
	msgs := infogen.BuildMessageSet(a.cfg.StickerCount, target.Name, "flirty")

	messageInput := browser.CSS(`textarea[data-test-id*="message"], .message-input, [placeholder*="message"]`)

	for i, msg := range msgs {
		if err := a.auto.WaitForSelector(messageInput, float64(a.cfg.DefaultTimeoutMs)); err != nil {
			return fmt.Errorf("input de mensaje no disponible: %w", err)
		}
		if err := a.auto.HumanType(messageInput, msg, a.cfg.TypingMinDelayMs, a.cfg.TypingMaxDelayMs); err != nil {
			slog.Warn("[allfeellove_auto] Error escribiendo mensaje", "idx", i, "err", err)
			continue
		}
		if err := a.driver.Page.Keyboard().Press("Enter"); err != nil {
			slog.Warn("[allfeellove_auto] Error enviando mensaje", "idx", i, "err", err)
		}
		cooldown := time.Duration(a.cfg.DelayMs(a.cfg.MessageCooldownSeconds*1000)) * time.Millisecond
		time.Sleep(cooldown)
		slog.Info(fmt.Sprintf("[allfeellove_auto] ✓ Mensaje %d/%d enviado", i+1, len(msgs)))
	}
	return nil
}
