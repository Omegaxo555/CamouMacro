// Package browser provee el handler de navegador usando Playwright-Go.
// Equivalente Go de core/camoufox_handler.py.
//
// NOTA: Camoufox (anti-fingerprint) no tiene binding Go. Se usa Playwright-Go
// con Firefox + inyección JS de anti-detección para mitigar fingerprinting básico.
package browser

import (
	"archive/tar"
	"compress/gzip"
	"fmt"
	"io"
	"log/slog"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/mxschmitt/playwright-go"
)

// DefaultAntiDetectionScript inyecta JS en cada página para ocultar señales de automatización.
// Equivale a las protecciones de Camoufox que no están disponibles en Playwright puro.
const DefaultAntiDetectionScript = `
Object.defineProperty(navigator, 'webdriver', { get: () => false });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
Object.defineProperty(navigator, 'languages', { get: () => ['es-ES', 'es', 'en-US', 'en'] });
window.chrome = { runtime: {} };
`

// TorPorts son los puertos Tor que se rotan en caso de bloqueo.
var TorPorts = []int{9050, 9150, 9051, 9052}

// Handler gestiona el ciclo de vida del navegador Firefox via Playwright.
// Equivalente a CamoufoxHandler de camoufox_handler.py.
type Handler struct {
	ProxyServer     string
	ProfileTemplate string
	Headless        bool
	TimeoutMs       int
	WindowSize      [2]int
	TorPorts        []int

	torPortIdx int
	pw         *playwright.Playwright
	browser    playwright.Browser
	Context    playwright.BrowserContext
	Page       playwright.Page
	tempDir    string
}

// NewHandler crea un Handler con la configuración dada.
// torProxy es la URL SOCKS5 del proxy Tor (e.g. "socks5://127.0.0.1:9050").
func NewHandler(torProxy, profileTemplate string, headless bool, width, height int) *Handler {
	proxy := torProxy
	if proxy == "" {
		proxy = "socks5://127.0.0.1:9050"
	}
	return &Handler{
		ProxyServer:     proxy,
		ProfileTemplate: profileTemplate,
		Headless:        headless,
		TimeoutMs:       30000,
		WindowSize:      [2]int{width, height},
		TorPorts:        TorPorts,
	}
}

// ──────────────────────────────────────────────────────────────────────────────
// Inicialización y cierre
// ──────────────────────────────────────────────────────────────────────────────

// Initialize arranca Firefox con Playwright y configura la sesión.
// Equivalente a CamoufoxHandler.initialize().
func (h *Handler) Initialize() error {
	if h.pw != nil && h.Page != nil {
		slog.Info("Sesión de navegador ya inicializada, se reutiliza")
		return nil
	}

	// Instalar Playwright si es necesario
	if err := playwright.Install(&playwright.RunOptions{Browsers: []string{"firefox"}}); err != nil {
		return fmt.Errorf("error instalando Playwright: %w", err)
	}

	pw, err := playwright.Run()
	if err != nil {
		return fmt.Errorf("error iniciando Playwright: %w", err)
	}
	h.pw = pw

	// Preparar perfil de usuario si existe template
	userDataDir, err := h.prepareProfile()
	if err != nil {
		slog.Warn("No se pudo preparar el perfil de usuario", "err", err)
	}

	// Configurar opciones del browser
	launchOpts := playwright.BrowserTypeLaunchOptions{
		Headless: playwright.Bool(h.Headless),
		Args: []string{
			fmt.Sprintf("--width=%d", h.WindowSize[0]),
			fmt.Sprintf("--height=%d", h.WindowSize[1]),
		},
	}

	// Configurar proxy SOCKS5 Tor si está disponible
	proxyConf := playwright.Proxy{Server: h.ProxyServer}

	if userDataDir != "" {
		// Contexto persistente (con perfil)
		ctx, err := pw.Firefox.LaunchPersistentContext(userDataDir,
			playwright.BrowserTypeLaunchPersistentContextOptions{
				Headless: playwright.Bool(h.Headless),
				Proxy:    &proxyConf,
				Viewport: &playwright.Size{
					Width:  h.WindowSize[0],
					Height: h.WindowSize[1],
				},
			},
		)
		if err != nil {
			return fmt.Errorf("error lanzando contexto persistente: %w", err)
		}
		h.Context = ctx
	} else {
		// Contexto efímero (sin perfil)
		br, err := pw.Firefox.Launch(launchOpts)
		if err != nil {
			return fmt.Errorf("error lanzando Firefox: %w", err)
		}
		h.browser = br
		ctx, err := br.NewContext(playwright.BrowserNewContextOptions{
			Proxy: &proxyConf,
			Viewport: &playwright.Size{
				Width:  h.WindowSize[0],
				Height: h.WindowSize[1],
			},
		})
		if err != nil {
			return fmt.Errorf("error creando contexto de navegador: %w", err)
		}
		h.Context = ctx
	}

	// Inyectar script anti-detección en todas las páginas
	if err := h.Context.AddInitScript(playwright.Script{
		Content: playwright.String(DefaultAntiDetectionScript),
	}); err != nil {
		slog.Warn("No se pudo inyectar script anti-detección", "err", err)
	}

	// Bloquear permisos de notificaciones para allfeellove.com
	if err := h.Context.GrantPermissions([]string{"notifications"},
		playwright.BrowserContextGrantPermissionsOptions{
			Origin: playwright.String("https://allfeellove.com"),
		}); err != nil {
		slog.Warn("No se pudieron configurar permisos de notificaciones", "err", err)
	}

	// Obtener o crear la primera página
	pages := h.Context.Pages()
	if len(pages) > 0 {
		h.Page = pages[0]
	} else {
		page, err := h.Context.NewPage()
		if err != nil {
			return fmt.Errorf("error creando página: %w", err)
		}
		h.Page = page
	}

	h.Page.SetDefaultTimeout(float64(h.TimeoutMs))

	slog.Info("BrowserHandler inicializado",
		"headless", h.Headless,
		"proxy", h.ProxyServer,
		"timeout_ms", h.TimeoutMs,
		"window", fmt.Sprintf("%dx%d", h.WindowSize[0], h.WindowSize[1]),
	)
	return nil
}

// Close cierra el navegador y elimina el perfil temporal.
// Equivalente a CamoufoxHandler.close().
func (h *Handler) Close() {
	slog.Info("Cerrando navegador y limpiando recursos...")

	if h.Context != nil {
		if err := h.Context.Close(); err != nil {
			slog.Error("Error cerrando contexto", "err", err)
		}
		h.Context = nil
		h.Page = nil
	}

	if h.browser != nil {
		if err := h.browser.Close(); err != nil {
			slog.Error("Error cerrando browser", "err", err)
		}
		h.browser = nil
	}

	if h.pw != nil {
		if err := h.pw.Stop(); err != nil {
			slog.Error("Error deteniendo Playwright", "err", err)
		}
		h.pw = nil
	}

	if h.tempDir != "" {
		if err := os.RemoveAll(h.tempDir); err != nil {
			slog.Error("Error eliminando directorio temporal", "dir", h.tempDir, "err", err)
		} else {
			slog.Info("Perfil efímero eliminado", "dir", h.tempDir)
			h.tempDir = ""
		}
	}
}

// ──────────────────────────────────────────────────────────────────────────────
// Navegación
// ──────────────────────────────────────────────────────────────────────────────

// Navigate navega a la URL dada con reintentos.
// Equivalente a CamoufoxHandler.navigate().
func (h *Handler) Navigate(url string, maxRetries int) error {
	if h.Page == nil {
		return fmt.Errorf("página no inicializada, llama Initialize() primero")
	}

	for attempt := 1; attempt <= maxRetries; attempt++ {
		slog.Info("Navegando", "url", url, "attempt", attempt, "max", maxRetries)

		resp, err := h.Page.Goto(url, playwright.PageGotoOptions{
			WaitUntil: playwright.WaitUntilStateDomcontentloaded,
			Timeout:   playwright.Float(float64(h.TimeoutMs)),
		})
		if err != nil {
			slog.Warn("Error temporal de red", "attempt", attempt, "err", err)
			continue
		}

		if resp != nil && resp.Ok() {
			slog.Info("Página cargada", "url", url, "status", resp.Status())

			if h.IsCloudflareBlocked() {
				slog.Warn("Cloudflare bloqueó la página, rotando conexión...")
				if err := h.RotateConnection(true); err != nil {
					return fmt.Errorf("no se pudo rotar la conexión: %w", err)
				}
				// Reintentar navegación tras rotación
				resp2, err2 := h.Page.Goto(url, playwright.PageGotoOptions{
					WaitUntil: playwright.WaitUntilStateDomcontentloaded,
					Timeout:   playwright.Float(float64(h.TimeoutMs)),
				})
				if err2 == nil && resp2 != nil && resp2.Ok() && !h.IsCloudflareBlocked() {
					return nil
				}
				return fmt.Errorf("sigue bloqueado por Cloudflare tras rotar conexión")
			}
			return nil
		}

		status := 0
		if resp != nil {
			status = resp.Status()
		}
		slog.Warn("Estado de respuesta no óptimo", "status", status, "attempt", attempt)
	}

	return fmt.Errorf("imposible conectar a %s tras %d intentos", url, maxRetries)
}

// ──────────────────────────────────────────────────────────────────────────────
// Cloudflare y rotación
// ──────────────────────────────────────────────────────────────────────────────

// IsCloudflareBlocked detecta si la página actual tiene la pantalla de bloqueo de Cloudflare.
// Equivalente a CamoufoxHandler._check_page_blocked_by_cloudflare().
func (h *Handler) IsCloudflareBlocked() bool {
	if h.Page == nil {
		return false
	}

	url := h.Page.URL()
	urlLower := strings.ToLower(url)
	if strings.Contains(urlLower, "cloudflare") || strings.Contains(urlLower, "attention required") {
		return true
	}

	body, err := h.Page.Locator("body").InnerText(playwright.LocatorInnerTextOptions{
		Timeout: playwright.Float(3000),
	})
	if err != nil {
		return false
	}
	bodyLower := strings.ToLower(body)
	markers := []string{
		"attention required",
		"sorry, you have been blocked",
		"verify you are human",
		"cloudflare ray id",
		"checking your browser before accessing",
		"just a moment",
	}
	for _, m := range markers {
		if strings.Contains(bodyLower, m) {
			return true
		}
	}
	return false
}

// RotateConnection cierra la sesión y la reinicia con otro puerto Tor.
// Equivalente a CamoufoxHandler.rotate_connection().
func (h *Handler) RotateConnection(useTor bool) error {
	slog.Warn("Rotando conexión para evitar bloqueo...")
	h.Close()

	if useTor {
		h.torPortIdx = (h.torPortIdx + 1) % len(h.TorPorts)
		newPort := h.TorPorts[h.torPortIdx]
		h.ProxyServer = fmt.Sprintf("socks5://127.0.0.1:%d", newPort)
		slog.Info("Nuevo proxy Tor", "proxy", h.ProxyServer)
	}

	return h.Initialize()
}

// VerifyIP navega a check.torproject.org para confirmar que el tráfico va por Tor.
// Equivalente a CamoufoxHandler.verify_ip().
func (h *Handler) VerifyIP() {
	if h.Page == nil {
		slog.Error("Page no inicializada")
		return
	}

	slog.Info("Verificando dirección IP vía Tor Project...")
	if _, err := h.Page.Goto("https://check.torproject.org/",
		playwright.PageGotoOptions{WaitUntil: playwright.WaitUntilStateDomcontentloaded}); err != nil {
		slog.Error("No se pudo verificar la IP", "err", err)
		return
	}

	isTor, err := h.Page.IsVisible("text=Congratulations. This browser is configured to use Tor.")
	if err == nil && isTor {
		slog.Info("[CONFIRMADO] La conexión pasa por la red Tor")
	} else {
		slog.Warn("[ALERTA] La página cargó pero no confirmó la red Tor")
	}
}

// ──────────────────────────────────────────────────────────────────────────────
// Preparación de perfil
// ──────────────────────────────────────────────────────────────────────────────

// prepareProfile extrae el perfil template .tar.gz a un directorio temporal.
// Equivalente a CamoufoxHandler._prepare_profile().
func (h *Handler) prepareProfile() (string, error) {
	if h.ProfileTemplate == "" {
		slog.Info("Sin plantilla de perfil, se usará perfil efímero")
		return "", nil
	}

	archivePath := h.ProfileTemplate
	if !filepath.IsAbs(archivePath) {
		// Resolver relativo a la raíz del proyecto
		_, file, _, _ := runtime.Caller(0)
		root := filepath.Join(filepath.Dir(file), "..", "..")
		archivePath = filepath.Join(root, archivePath)
	}

	if _, err := os.Stat(archivePath); os.IsNotExist(err) {
		return "", fmt.Errorf("plantilla de perfil no existe: %s", h.ProfileTemplate)
	}

	tempDir, err := os.MkdirTemp(os.TempDir(), "camoumacro_session_")
	if err != nil {
		return "", fmt.Errorf("no se pudo crear directorio temporal: %w", err)
	}
	h.tempDir = tempDir

	slog.Info("Extrayendo perfil", "archive", filepath.Base(archivePath), "dest", tempDir)

	if err := extractTarGz(archivePath, tempDir); err != nil {
		return "", fmt.Errorf("error extrayendo perfil: %w", err)
	}

	return tempDir, nil
}

// extractTarGz extrae un archivo .tar.gz al directorio dst.
// Equivalente al uso de tarfile.open() en camoufox_handler.py.
func extractTarGz(src, dst string) error {
	f, err := os.Open(src)
	if err != nil {
		return err
	}
	defer f.Close()

	gz, err := gzip.NewReader(f)
	if err != nil {
		return err
	}
	defer gz.Close()

	tr := tar.NewReader(gz)
	for {
		hdr, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}

		target := filepath.Join(dst, filepath.Clean(hdr.Name))

		// Seguridad: evitar path traversal
		if !strings.HasPrefix(target, filepath.Clean(dst)+string(os.PathSeparator)) {
			continue
		}

		switch hdr.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(target, 0o755); err != nil {
				return err
			}
		case tar.TypeReg:
			if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
				return err
			}
			out, err := os.Create(target)
			if err != nil {
				return err
			}
			if _, err := io.Copy(out, tr); err != nil {
				out.Close()
				return err
			}
			out.Close()
		}
	}
	return nil
}

// WaitFor espera un tiempo dado (helper de conveniencia).
func WaitFor(ms int) {
	time.Sleep(time.Duration(ms) * time.Millisecond)
}
