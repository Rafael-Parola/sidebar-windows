import customtkinter as ctk
from tkinter import messagebox
from app.launcher import run_auto_start_sequence

class SettingsModal(ctk.CTkToplevel):
    def __init__(self, master, config_manager, on_settings_changed=None):
        super().__init__(master)
        self.config_manager = config_manager
        self.on_settings_changed = on_settings_changed

        self.title("Configurações do SydeBar")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color="#12151d")

        self.attributes("-topmost", True)
        self._center_window()

        self._build_ui()
        self.transient(master)
        self.grab_set()

    def _center_window(self):
        self.update_idletasks()
        w = 480
        h = 560
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        title_lbl = ctk.CTkLabel(
            header,
            text="⚙ Configurações",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#f8fafc"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            header,
            text="Personalize a aparência, posição e regras de inicialização automática.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94a3b8"
        )
        sub_lbl.pack(anchor="w")

        # Scrollable Settings Container
        container = ctk.CTkScrollableFrame(self, fg_color="#181b24", corner_radius=12, border_width=1, border_color="#262b3a")
        container.pack(fill="both", expand=True, padx=24, pady=10)

        # 1. Seção: Posicionamento e Altura
        sec1_lbl = ctk.CTkLabel(container, text="POSICIONAMENTO E ALTURA DA BARRA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#6366f1")
        sec1_lbl.pack(anchor="w", padx=16, pady=(12, 6))

        pos_row = ctk.CTkFrame(container, fg_color="transparent")
        pos_row.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(pos_row, text="Lado da tela:", font=ctk.CTkFont(size=12), text_color="#e2e8f0").pack(side="left")
        self.pos_var = ctk.StringVar(value=self.config_manager.get("position", "right"))
        self.pos_menu = ctk.CTkSegmentedButton(
            pos_row,
            values=["Direita", "Esquerda"],
            selected_color="#4f46e5",
            selected_hover_color="#6366f1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_pos_toggle
        )
        self.pos_menu.set("Direita" if self.pos_var.get() == "right" else "Esquerda")
        self.pos_menu.pack(side="right")

        # Modo de Altura
        mode_row = ctk.CTkFrame(container, fg_color="transparent")
        mode_row.pack(fill="x", padx=16, pady=(8, 4))
        ctk.CTkLabel(mode_row, text="Cálculo da altura:", font=ctk.CTkFont(size=12), text_color="#e2e8f0").pack(side="left")
        self.height_mode_var = ctk.StringVar(value=self.config_manager.get("height_mode", "auto"))
        self.height_mode_btn = ctk.CTkSegmentedButton(
            mode_row,
            values=["Automático", "Personalizada"],
            selected_color="#4f46e5",
            selected_hover_color="#6366f1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_height_mode_change
        )
        self.height_mode_btn.set("Automático" if self.height_mode_var.get() == "auto" else "Personalizada")
        self.height_mode_btn.pack(side="right")

        # Container para os sliders de altura
        self.height_controls_frame = ctk.CTkFrame(container, fg_color="#131722", corner_radius=8)
        self.height_controls_frame.pack(fill="x", padx=16, pady=(4, 10))

        # Modo Automático: folga extra conforme os itens
        self.auto_frame = ctk.CTkFrame(self.height_controls_frame, fg_color="transparent")
        auto_lbl_row = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        auto_lbl_row.pack(fill="x", padx=8, pady=(6, 2))
        ctk.CTkLabel(auto_lbl_row, text="Folga extra conforme os itens:", font=ctk.CTkFont(size=11), text_color="#cbd5e1").pack(side="left")
        self.auto_pad_val_lbl = ctk.CTkLabel(auto_lbl_row, text=f"{self.config_manager.get('extra_height_padding', 30)}px", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38bdf8")
        self.auto_pad_val_lbl.pack(side="right")

        self.auto_pad_slider = ctk.CTkSlider(
            self.auto_frame,
            from_=0,
            to=100,
            number_of_steps=20,
            progress_color="#4f46e5",
            button_color="#6366f1",
            command=self._on_auto_pad_slider_change
        )
        self.auto_pad_slider.set(self.config_manager.get("extra_height_padding", 30))
        self.auto_pad_slider.pack(fill="x", padx=8, pady=(0, 6))

        # Modo Personalizado: altura fixa
        self.custom_frame = ctk.CTkFrame(self.height_controls_frame, fg_color="transparent")
        custom_lbl_row = ctk.CTkFrame(self.custom_frame, fg_color="transparent")
        custom_lbl_row.pack(fill="x", padx=8, pady=(6, 2))
        ctk.CTkLabel(custom_lbl_row, text="Altura fixa da barra:", font=ctk.CTkFont(size=11), text_color="#cbd5e1").pack(side="left")
        self.custom_h_val_lbl = ctk.CTkLabel(custom_lbl_row, text=f"{self.config_manager.get('custom_height', 480)}px", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38bdf8")
        self.custom_h_val_lbl.pack(side="right")

        self.custom_h_slider = ctk.CTkSlider(
            self.custom_frame,
            from_=300,
            to=900,
            number_of_steps=30,
            progress_color="#4f46e5",
            button_color="#6366f1",
            command=self._on_custom_h_slider_change
        )
        self.custom_h_slider.set(self.config_manager.get("custom_height", 480))
        self.custom_h_slider.pack(fill="x", padx=8, pady=(0, 6))

        self._update_height_ui()

        # 2. Seção: Início Automático com o Windows
        sec2_lbl = ctk.CTkLabel(container, text="INICIALIZAÇÃO DO SISTEMA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#6366f1")
        sec2_lbl.pack(anchor="w", padx=16, pady=(16, 6))

        # Windows Startup switch
        is_startup_active = self.config_manager.is_run_at_startup_enabled()
        self.startup_switch = ctk.CTkSwitch(
            container,
            text="Iniciar o SydeBar ao ligar o computador (Windows Startup)",
            font=ctk.CTkFont(size=12),
            progress_color="#10b981",
            text_color="#e2e8f0"
        )
        if is_startup_active:
            self.startup_switch.select()
        else:
            self.startup_switch.deselect()
        self.startup_switch.pack(anchor="w", padx=16, pady=6)

        # Launch auto apps on sidebar start
        self.auto_launch_switch = ctk.CTkSwitch(
            container,
            text="Disparar apps marcados automaticamente ao abrir o SydeBar",
            font=ctk.CTkFont(size=12),
            progress_color="#10b981",
            text_color="#e2e8f0"
        )
        if self.config_manager.get("launch_auto_apps_on_start", True):
            self.auto_launch_switch.select()
        else:
            self.auto_launch_switch.deselect()
        self.auto_launch_switch.pack(anchor="w", padx=16, pady=6)

        # Intervalo entre apps
        delay_row = ctk.CTkFrame(container, fg_color="transparent")
        delay_row.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(delay_row, text="Intervalo entre apps automáticos:", font=ctk.CTkFont(size=12), text_color="#e2e8f0").pack(side="left")
        self.delay_menu = ctk.CTkComboBox(
            delay_row,
            values=["1 segundo", "2 segundos", "3 segundos", "5 segundos"],
            fg_color="#0f1118",
            border_color="#2c3345",
            width=120,
            height=30
        )
        cur_delay = self.config_manager.get("stagger_delay_seconds", 2)
        self.delay_menu.set(f"{cur_delay} segundo{'s' if cur_delay > 1 else ''}")
        self.delay_menu.pack(side="right")

        # Botão de teste rápido de auto-start
        test_frame = ctk.CTkFrame(container, fg_color="#1f2432", corner_radius=8)
        test_frame.pack(fill="x", padx=16, pady=(12, 10))

        test_lbl = ctk.CTkLabel(
            test_frame,
            text="Deseja testar o disparo automático agora?",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        test_lbl.pack(side="left", padx=12, pady=10)

        test_btn = ctk.CTkButton(
            test_frame,
            text="⚡ Disparar Agora",
            width=110,
            height=28,
            corner_radius=6,
            fg_color="#059669",
            hover_color="#10b981",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._trigger_auto_start_now
        )
        test_btn.pack(side="right", padx=12, pady=10)

        # Footer Buttons
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(10, 20))

        cancel_btn = ctk.CTkButton(
            footer,
            text="Cancelar",
            width=90,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#1e2433",
            text_color="#94a3b8",
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            footer,
            text="Salvar Alterações",
            width=130,
            height=36,
            corner_radius=8,
            fg_color="#4f46e5",
            hover_color="#6366f1",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save_settings
        )
        save_btn.pack(side="right")

    def _on_pos_toggle(self, value):
        self.pos_var.set("right" if value == "Direita" else "left")

    def _on_height_mode_change(self, value):
        mode = "auto" if value == "Automático" else "custom"
        self.height_mode_var.set(mode)
        self._update_height_ui()

    def _update_height_ui(self):
        if self.height_mode_var.get() == "auto":
            self.custom_frame.pack_forget()
            self.auto_frame.pack(fill="x", padx=4, pady=4)
        else:
            self.auto_frame.pack_forget()
            self.custom_frame.pack(fill="x", padx=4, pady=4)

    def _on_auto_pad_slider_change(self, val):
        self.auto_pad_val_lbl.configure(text=f"{int(val)}px")

    def _on_custom_h_slider_change(self, val):
        self.custom_h_val_lbl.configure(text=f"{int(val)}px")

    def _trigger_auto_start_now(self):
        apps = self.config_manager.get_apps()
        auto_count = len([a for a in apps if a.get("auto_start", False)])
        if auto_count == 0:
            messagebox.showinfo("Aviso", "Nenhum aplicativo está marcado com o início automático (⚡ Auto).", parent=self)
            return

        def on_finish(launched, total):
            messagebox.showinfo("Início Automático", f"Processo concluído! {launched} de {total} aplicativos iniciados.", parent=self)

        run_auto_start_sequence(self.config_manager, on_finish=on_finish)

    def _save_settings(self):
        # Position
        pos = self.pos_var.get()
        self.config_manager.set("position", pos)

        # Height mode & parameters
        mode = self.height_mode_var.get()
        self.config_manager.set("height_mode", mode)
        self.config_manager.set("extra_height_padding", int(self.auto_pad_slider.get()))
        self.config_manager.set("custom_height", int(self.custom_h_slider.get()))

        # Delay
        delay_str = self.delay_menu.get().split()[0]
        try:
            delay = int(delay_str)
        except ValueError:
            delay = 2
        self.config_manager.set("stagger_delay_seconds", delay)

        # Auto launch on open
        self.config_manager.set("launch_auto_apps_on_start", bool(self.auto_launch_switch.get()))

        # Windows Startup registry
        enable_startup = bool(self.startup_switch.get())
        self.config_manager.set_run_at_startup(enable_startup)

        if self.on_settings_changed:
            self.on_settings_changed()

        self.destroy()
