"""
CamouMacro Control Panel
GUI cross-platform (Windows / Linux) para gestionar instancias del algoritmo.
Compatible con Python 3.10+ usando sólo Tkinter (stdlib).
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# ──────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = ROOT_DIR / "config" / "settings.py"
TARGETS_FILE = ROOT_DIR / "targets" / "profiles_dict.txt"
MAIN_PY = ROOT_DIR / "main.py"

IS_WINDOWS = platform.system() == "Windows"
PYTHON = sys.executable


# ──────────────────────────────────────────────────────────────
# Design tokens
# ──────────────────────────────────────────────────────────────
COLORS = {
    "bg":           "#0f1117",
    "surface":      "#1a1d27",
    "surface2":     "#22263a",
    "border":       "#2e3350",
    "accent":       "#7c6af7",
    "accent_hover": "#9d90ff",
    "accent_dim":   "#3d3580",
    "success":      "#34d399",
    "warning":      "#fbbf24",
    "danger":       "#f87171",
    "text":         "#e2e8f0",
    "text_muted":   "#8892a4",
    "text_dim":     "#4a5568",
}


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _styled_btn(parent, text, command, color=None, width=None, padx=12, pady=6):
    bg = color or COLORS["accent"]
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=COLORS["text"],
        activebackground=COLORS["accent_hover"],
        activeforeground=COLORS["text"],
        relief="flat",
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
        padx=padx,
        pady=pady,
    )
    if width:
        btn.config(width=width)

    def _on_enter(e):
        btn.config(bg=COLORS["accent_hover"])

    def _on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    return btn


def _entry(parent, textvariable, width=18):
    return tk.Entry(
        parent,
        textvariable=textvariable,
        bg=COLORS["surface2"],
        fg=COLORS["text"],
        insertbackground=COLORS["accent"],
        relief="flat",
        font=("Segoe UI", 9),
        width=width,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
    )


def _which(name: str) -> str | None:
    import shutil
    return shutil.which(name)


# ──────────────────────────────────────────────────────────────
# Instance data model
# ──────────────────────────────────────────────────────────────

class AlgoInstance:
    _counter = 0

    def __init__(self, proc: subprocess.Popen, params: dict):
        AlgoInstance._counter += 1
        self.id = AlgoInstance._counter
        self.proc = proc
        self.params = params
        self.started_at = time.time()

    @property
    def is_running(self) -> bool:
        return self.proc.poll() is None

    @property
    def status_label(self) -> str:
        return "● Running" if self.is_running else "○ Stopped"

    @property
    def status_color(self) -> str:
        return COLORS["success"] if self.is_running else COLORS["text_muted"]

    def kill(self):
        try:
            if IS_WINDOWS:
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                import signal
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        except Exception:
            pass
        try:
            self.proc.kill()
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────
# Main App Window
# ──────────────────────────────────────────────────────────────

class CamouMacroGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CamouMacro – Control Panel")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)
        self.minsize(880, 540)

        # ── Variables de configuración ──────────────────────────
        self.v_speed      = tk.StringVar(value="1.0")
        self.v_max_pages  = tk.StringVar(value="100")
        self.v_cooldown   = tk.StringVar(value="2.5")
        self.v_stickers   = tk.StringVar(value="5")
        self.v_stk_ms     = tk.StringVar(value="400")
        self.v_type_min   = tk.StringVar(value="15")
        self.v_type_max   = tk.StringVar(value="45")
        self.v_timeout    = tk.StringVar(value="10000")
        self.v_tor_port   = tk.StringVar(value="9050")
        self.v_auto_port  = tk.BooleanVar(value=True)
        self.v_headless   = tk.BooleanVar(value=False)
        self.v_algo       = tk.StringVar(value="allfeellove_auto")

        # ── Estado interno ──────────────────────────────────────
        self.instances: list[AlgoInstance] = []
        self._polling = True

        # ── Build UI ────────────────────────────────────────────
        self._build_titlebar()
        self._build_body()

        # ── Auto-update loop ────────────────────────────────────
        self._poll_instances()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Titlebar ──────────────────────────────────────────────

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=COLORS["surface"], pady=10)
        bar.pack(fill="x")

        tk.Label(bar, text="⚡ CamouMacro",
                 bg=COLORS["surface"], fg=COLORS["accent"],
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=18)

        tk.Label(bar, text="Control Panel — Multi-Instance Manager",
                 bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 9)).pack(side="left")

        tk.Label(bar, text=f"Python {sys.version.split()[0]}  |  {platform.system()}",
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 font=("Segoe UI", 8)).pack(side="right", padx=18)

    # ─── Body ──────────────────────────────────────────────────

    def _build_body(self):
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=10)

        body.columnconfigure(0, weight=2, minsize=350)
        body.columnconfigure(1, weight=3, minsize=420)
        body.rowconfigure(0, weight=1)

        self._build_config_panel(body)
        self._build_instances_panel(body)

    # ─── Config Panel ──────────────────────────────────────────

    def _build_config_panel(self, parent):
        outer = tk.Frame(parent, bg=COLORS["surface"], relief="flat",
                         highlightthickness=1, highlightbackground=COLORS["border"])
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Header
        hdr = tk.Frame(outer, bg=COLORS["accent_dim"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  Configuración", bg=COLORS["accent_dim"],
                 fg=COLORS["text"], font=("Segoe UI", 10, "bold"),
                 padx=12, pady=8).pack(side="left")

        form = tk.Frame(outer, bg=COLORS["surface"], padx=14, pady=10)
        form.pack(fill="both", expand=True)

        fields = [
            ("SPEED_FACTOR",            "Speed Factor (0.05–3.0):",  self.v_speed),
            ("MAX_SCAN_PAGES",          "Máx. páginas a escanear:",   self.v_max_pages),
            ("MESSAGE_COOLDOWN_SECONDS","Cooldown mensajes (s):",      self.v_cooldown),
            ("STICKER_COUNT",           "Cantidad de stickers:",       self.v_stickers),
            ("STICKER_INTERVAL_MS",     "Intervalo stickers (ms):",    self.v_stk_ms),
            ("TYPING_MIN_DELAY_MS",     "Typing min delay (ms):",      self.v_type_min),
            ("TYPING_MAX_DELAY_MS",     "Typing max delay (ms):",      self.v_type_max),
            ("DEFAULT_TIMEOUT_MS",      "Timeout por defecto (ms):",   self.v_timeout),
        ]

        for i, (key, label, var) in enumerate(fields):
            tk.Label(form, text=label, bg=COLORS["surface"], fg=COLORS["text_muted"],
                     font=("Segoe UI", 8), anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            e = _entry(form, var, width=14)
            e.grid(row=i, column=1, sticky="e", pady=3, padx=(8, 0))

        r = len(fields)

        # Tor Port
        tk.Label(form, text="Puerto Tor Base:", bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 8), anchor="w").grid(row=r, column=0, sticky="w", pady=3)
        _entry(form, self.v_tor_port, width=14).grid(row=r, column=1, sticky="e", pady=3, padx=(8, 0))
        r += 1

        # Headless
        tk.Label(form, text="Modo Headless:", bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 8), anchor="w").grid(row=r, column=0, sticky="w", pady=3)
        tk.Checkbutton(form, variable=self.v_headless,
                       bg=COLORS["surface"], fg=COLORS["text"],
                       activebackground=COLORS["surface"],
                       selectcolor=COLORS["accent_dim"],
                       relief="flat").grid(row=r, column=1, sticky="e", pady=3)
        r += 1

        # Algorithm selector
        tk.Label(form, text="Algoritmo:", bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 8), anchor="w").grid(row=r, column=0, sticky="w", pady=3)
        algo_combo = ttk.Combobox(form, textvariable=self.v_algo,
                                  values=["allfeellove_auto", "form_demo"],
                                  state="readonly", width=13,
                                  font=("Segoe UI", 9))
        algo_combo.grid(row=r, column=1, sticky="e", pady=3, padx=(8, 0))
        r += 1

        # Speed presets
        tk.Label(form, text="Presets de velocidad:",
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 font=("Segoe UI", 8)).grid(row=r, column=0, columnspan=2, sticky="w", pady=(8, 3))
        r += 1

        preset_frame = tk.Frame(form, bg=COLORS["surface"])
        preset_frame.grid(row=r, column=0, columnspan=2, sticky="ew")
        presets = [("🐢 Lento", "1.5"), ("🚶 Normal", "1.0"), ("🏃 Rápido", "0.5"), ("⚡ Ultra", "0.2")]
        for label, val in presets:
            btn = tk.Button(preset_frame, text=label,
                            command=lambda v=val: self.v_speed.set(v),
                            bg=COLORS["surface2"], fg=COLORS["text"],
                            activebackground=COLORS["accent_dim"],
                            relief="flat", font=("Segoe UI", 8), padx=6, pady=3,
                            cursor="hand2")
            btn.pack(side="left", padx=2)
        r += 1

        # Separator
        ttk.Separator(form, orient="horizontal").grid(
            row=r, column=0, columnspan=2, sticky="ew", pady=10)
        r += 1

        # Buttons row
        btn_frame = tk.Frame(form, bg=COLORS["surface"])
        btn_frame.grid(row=r, column=0, columnspan=2, sticky="ew")

        _styled_btn(btn_frame, "💾 Guardar Config", self._save_config,
                    color=COLORS["accent"]).pack(side="left", padx=(0, 6))
        _styled_btn(btn_frame, "↺ Recargar", self._load_config,
                    color=COLORS["surface2"]).pack(side="left")

        self._load_config()

    # ─── Instances Panel ───────────────────────────────────────

    def _build_instances_panel(self, parent):
        outer = tk.Frame(parent, bg=COLORS["surface"], relief="flat",
                         highlightthickness=1, highlightbackground=COLORS["border"])
        outer.grid(row=0, column=1, sticky="nsew")

        # Header
        hdr = tk.Frame(outer, bg=COLORS["accent_dim"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="🚀  Instancias Activas", bg=COLORS["accent_dim"],
                 fg=COLORS["text"], font=("Segoe UI", 10, "bold"),
                 padx=12, pady=8).pack(side="left")

        self._inst_count_lbl = tk.Label(hdr, text="0 running",
                                        bg=COLORS["accent_dim"], fg=COLORS["text_muted"],
                                        font=("Segoe UI", 8))
        self._inst_count_lbl.pack(side="right", padx=12)

        # Launch button bar
        launch_row = tk.Frame(outer, bg=COLORS["surface"], pady=8, padx=14)
        launch_row.pack(fill="x")

        _styled_btn(launch_row, "＋ Lanzar Nueva Instancia",
                    self._launch_instance,
                    color=COLORS["accent"]).pack(side="left")

        _styled_btn(launch_row, "✖ Terminar Todas",
                    self._kill_all,
                    color=COLORS["danger"]).pack(side="left", padx=(8, 0))

        # Scrollable list container
        list_outer = tk.Frame(outer, bg=COLORS["bg"])
        list_outer.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        canvas = tk.Canvas(list_outer, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        self._inst_frame = tk.Frame(canvas, bg=COLORS["bg"])

        self._inst_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._inst_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._inst_canvas = canvas

        # Empty label
        self._empty_lbl = tk.Label(self._inst_frame,
                                   text="No hay instancias en ejecución.\nHaz clic en «Lanzar Nueva Instancia» para comenzar.",
                                   bg=COLORS["bg"], fg=COLORS["text_dim"],
                                   font=("Segoe UI", 9), justify="center")
        self._empty_lbl.pack(pady=30)

    # ─── Config I/O ────────────────────────────────────────────

    def _save_config(self):
        """Persiste los valores en config/settings.py."""
        try:
            content = f'''"""Configuración global de automatización y tiempos de ejecución."""

import os
from pathlib import Path


class AutomationConfig:
    """Parámetros de velocidad, delays y rutas para los algoritmos."""

    SPEED_FACTOR: float = float(os.environ.get("SPEED_FACTOR", "{self.v_speed.get()}"))
    TARGETS_FILE: str = os.environ.get("TARGETS_FILE", "targets/profiles_dict.txt")
    MAX_SCAN_PAGES: int = int(os.environ.get("MAX_SCAN_PAGES", "{self.v_max_pages.get()}"))
    MESSAGE_COOLDOWN_SECONDS: float = float(os.environ.get("MESSAGE_COOLDOWN_SECONDS", "{self.v_cooldown.get()}"))
    STICKER_COUNT: int = int(os.environ.get("STICKER_COUNT", "{self.v_stickers.get()}"))
    STICKER_INTERVAL_MS: int = int(os.environ.get("STICKER_INTERVAL_MS", "{self.v_stk_ms.get()}"))
    TYPING_MIN_DELAY_MS: int = int(os.environ.get("TYPING_MIN_DELAY_MS", "{self.v_type_min.get()}"))
    TYPING_MAX_DELAY_MS: int = int(os.environ.get("TYPING_MAX_DELAY_MS", "{self.v_type_max.get()}"))
    DEFAULT_TIMEOUT_MS: int = int(os.environ.get("DEFAULT_TIMEOUT_MS", "{self.v_timeout.get()}"))

    @classmethod
    def delay_ms(cls, base_ms: int | float) -> int:
        return max(1, int(base_ms * cls.SPEED_FACTOR))

    @classmethod
    def delay_s(cls, base_seconds: float) -> float:
        return max(0.01, base_seconds * cls.SPEED_FACTOR)

    @classmethod
    def get_targets_path(cls) -> Path:
        return Path(__file__).resolve().parent.parent / cls.TARGETS_FILE
'''
            SETTINGS_FILE.write_text(content, encoding="utf-8")
            self._flash_status("✓ Configuración guardada en config/settings.py", COLORS["success"])
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{exc}")

    def _load_config(self):
        """Lee los valores actuales desde config/settings.py."""
        try:
            text = SETTINGS_FILE.read_text(encoding="utf-8")

            def extract(key, default):
                import re
                m = re.search(rf'os\.environ\.get\("{key}",\s*"([^"]+)"\)', text)
                if m:
                    return m.group(1)
                return default

            self.v_speed.set(extract("SPEED_FACTOR", "1.0"))
            self.v_max_pages.set(extract("MAX_SCAN_PAGES", "100"))
            self.v_cooldown.set(extract("MESSAGE_COOLDOWN_SECONDS", "2.5"))
            self.v_stickers.set(extract("STICKER_COUNT", "5"))
            self.v_stk_ms.set(extract("STICKER_INTERVAL_MS", "400"))
            self.v_type_min.set(extract("TYPING_MIN_DELAY_MS", "15"))
            self.v_type_max.set(extract("TYPING_MAX_DELAY_MS", "45"))
            self.v_timeout.set(extract("DEFAULT_TIMEOUT_MS", "10000"))
        except Exception:
            pass

    def _flash_status(self, msg: str, color: str = COLORS["success"]):
        """Muestra un mensaje temporal en el pie de la ventana."""
        lbl = tk.Label(self, text=msg, bg=color, fg="#fff",
                       font=("Segoe UI", 8, "bold"), padx=12, pady=4)
        lbl.place(relx=0.5, rely=0.97, anchor="s")
        self.after(2500, lbl.destroy)

    # ─── Instance management ───────────────────────────────────

    def _get_next_tor_port(self) -> int:
        """Calcula un puerto Tor libre para evitar colisiones si se corren varias instancias."""
        try:
            base_port = int(self.v_tor_port.get())
        except ValueError:
            base_port = 9050

        used_ports = set()
        for inst in self.instances:
            if inst.is_running:
                p = inst.params.get("port")
                if p:
                    try:
                        used_ports.add(int(p))
                    except ValueError:
                        pass

        port = base_port
        while port in used_ports:
            port += 2  # Tor needs port and port+1 for control
        return port

    def _build_env(self, port: int) -> dict:
        """Construye el entorno con los parámetros de configuración."""
        env = os.environ.copy()
        env["SPEED_FACTOR"]              = self.v_speed.get()
        env["MAX_SCAN_PAGES"]            = self.v_max_pages.get()
        env["MESSAGE_COOLDOWN_SECONDS"]  = self.v_cooldown.get()
        env["STICKER_COUNT"]             = self.v_stickers.get()
        env["STICKER_INTERVAL_MS"]       = self.v_stk_ms.get()
        env["TYPING_MIN_DELAY_MS"]       = self.v_type_min.get()
        env["TYPING_MAX_DELAY_MS"]       = self.v_type_max.get()
        env["DEFAULT_TIMEOUT_MS"]        = self.v_timeout.get()
        env["TOR_PORT"]                  = str(port)
        env["HEADLESS"]                  = "true" if self.v_headless.get() else "false"
        env["ALGO"]                      = self.v_algo.get()
        return env

    def _launch_instance(self):
        """Abre una nueva terminal emergente con main.py."""
        port = self._get_next_tor_port()
        env = self._build_env(port)
        algo = self.v_algo.get()
        inst_num = AlgoInstance._counter + 1
        title = f"CamouMacro #{inst_num} – {algo} (Port {port})"

        try:
            if IS_WINDOWS:
                cmd = (
                    f'title {title} && '
                    f'"{PYTHON}" "{MAIN_PY}"'
                )
                proc = subprocess.Popen(
                    ["cmd", "/K", cmd],
                    env=env,
                    cwd=str(ROOT_DIR),
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            else:
                inner_cmd = f'cd "{ROOT_DIR}" && "{PYTHON}" "{MAIN_PY}"; exec bash'
                terminal_tried = False
                for term_cmd in [
                    ["x-terminal-emulator", "-e", f"bash -c '{inner_cmd}'"],
                    ["qterminal", "-e", f"bash -c '{inner_cmd}'"],
                    ["gnome-terminal", "--", "bash", "-c", inner_cmd],
                    ["xterm", "-title", title, "-e", f"bash -c '{inner_cmd}'"],
                    ["konsole", "--noclose", "-e", "bash", "-c", inner_cmd],
                    ["xfce4-terminal", "--command", f"bash -c '{inner_cmd}'"],
                    ["mate-terminal", "-e", f"bash -c '{inner_cmd}'"],
                    ["lxterminal", "-e", f"bash -c '{inner_cmd}'"],
                ]:
                    if _which(term_cmd[0]):
                        proc = subprocess.Popen(term_cmd, env=env, cwd=str(ROOT_DIR),
                                                start_new_session=True)
                        terminal_tried = True
                        break
                if not terminal_tried:
                    messagebox.showerror("Error",
                        "No se encontró un emulador de terminal compatible.\n"
                        "Se intentó usar: x-terminal-emulator, qterminal, gnome-terminal, xterm, konsole, xfce4-terminal, mate-terminal, lxterminal.")
                    return

            inst = AlgoInstance(proc, params={
                "algo": algo,
                "speed": self.v_speed.get(),
                "pages": self.v_max_pages.get(),
                "port": str(port),
            })
            self.instances.append(inst)
            self._refresh_instance_list()
            self._flash_status(f"✓ Instancia #{inst.id} lanzada en puerto {port}", COLORS["success"])

        except Exception as exc:
            messagebox.showerror("Error al lanzar", str(exc))

    def _kill_instance(self, inst: AlgoInstance):
        inst.kill()
        self._refresh_instance_list()

    def _kill_all(self):
        if not self.instances:
            return
        if messagebox.askyesno("Confirmar", "¿Terminar TODAS las instancias activas?"):
            for inst in self.instances:
                inst.kill()
            self.instances.clear()
            self._refresh_instance_list()

    def _refresh_instance_list(self):
        """Reconstruye la lista visual de instancias."""
        for widget in self._inst_frame.winfo_children():
            widget.destroy()

        running_count = sum(1 for i in self.instances if i.is_running)
        self._inst_count_lbl.config(text=f"{running_count} running")

        if not self.instances:
            tk.Label(self._inst_frame,
                     text="No hay instancias en ejecución.\nHaz clic en «Lanzar Nueva Instancia» para comenzar.",
                     bg=COLORS["bg"], fg=COLORS["text_dim"],
                     font=("Segoe UI", 9), justify="center").pack(pady=30)
            return

        for inst in self.instances:
            self._add_instance_row(inst)

        self._inst_frame.update_idletasks()
        self._inst_canvas.configure(scrollregion=self._inst_canvas.bbox("all"))

    def _add_instance_row(self, inst: AlgoInstance):
        row = tk.Frame(self._inst_frame, bg=COLORS["surface2"],
                       highlightthickness=1,
                       highlightbackground=COLORS["border"])
        row.pack(fill="x", padx=4, pady=3)

        # Status indicator
        status_dot = tk.Label(row, text=inst.status_label,
                              bg=COLORS["surface2"], fg=inst.status_color,
                              font=("Segoe UI", 9, "bold"), padx=10, pady=8)
        status_dot.pack(side="left")

        # Info
        info_text = (
            f"#{inst.id}  {inst.params.get('algo', 'unknown')}  "
            f"|  Speed: {inst.params.get('speed')}  "
            f"|  Pages: {inst.params.get('pages')}  "
            f"|  Tor: :{inst.params.get('port')}"
        )
        tk.Label(row, text=info_text,
                 bg=COLORS["surface2"], fg=COLORS["text"],
                 font=("Segoe UI", 8), anchor="w").pack(side="left", fill="x", expand=True)

        # Kill button
        if inst.is_running:
            _styled_btn(row, "✖ Terminar",
                        lambda i=inst: self._kill_instance(i),
                        color=COLORS["danger"], padx=8, pady=4).pack(side="right", padx=8, pady=4)
        else:
            tk.Label(row, text="Finalizado", bg=COLORS["surface2"],
                     fg=COLORS["text_dim"], font=("Segoe UI", 8),
                     padx=8).pack(side="right", padx=8)

    def _poll_instances(self):
        """Actualiza el estado de las instancias cada 1.5s."""
        if self._polling:
            self._refresh_instance_list()
            self.after(1500, self._poll_instances)

    def _on_close(self):
        self._polling = False
        running = [i for i in self.instances if i.is_running]
        if running:
            if messagebox.askyesno("Salir",
                f"Hay {len(running)} instancia(s) activa(s). ¿Deseas terminarlas antes de salir?"):
                for i in running:
                    i.kill()
        self.destroy()


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CamouMacroGUI()
    app.mainloop()
