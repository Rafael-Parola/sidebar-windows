import tkinter as tk
import customtkinter as ctk
from PIL import Image
from app.icon_extractor import get_app_icon
from app.launcher import launch_app

class AppCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        app_data,
        config_manager,
        on_launch=None,
        on_edit=None,
        on_delete=None,
        on_toggle_auto=None,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=12,
            fg_color="#181b24",
            border_width=1,
            border_color="#262b3a",
            **kwargs
        )
        self.app_data = app_data
        self.config_manager = config_manager
        self.on_launch = on_launch
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle_auto = on_toggle_auto

        self._build_ui()
        self._bind_hover_effects()

    def _build_ui(self):
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)

        # 1. App Icon
        icon_pil = get_app_icon(
            self.app_data.get("path", ""),
            app_name=self.app_data.get("name", "App"),
            cache_dir=self.config_manager.cache_dir,
            app_id=self.app_data.get("id", "temp"),
            size=36
        )
        self.icon_ctk = ctk.CTkImage(light_image=icon_pil, dark_image=icon_pil, size=(34, 34))
        self.icon_label = ctk.CTkLabel(self, image=self.icon_ctk, text="", width=40, height=40)
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(10, 6), pady=8, sticky="w")
        self.icon_label.bind("<Button-1>", lambda e: self._handle_launch())

        # 2. Text Info (Name & Subtitle)
        name_text = self.app_data.get("name", "Sem Nome")
        if len(name_text) > 20:
            name_text = name_text[:18] + "..."

        self.title_label = ctk.CTkLabel(
            self,
            text=name_text,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#f1f5f9",
            anchor="w"
        )
        self.title_label.grid(row=0, column=1, padx=(2, 6), pady=(8, 0), sticky="ew")
        self.title_label.bind("<Button-1>", lambda e: self._handle_launch())

        cat_text = self.app_data.get("category", "Geral")
        self.sub_label = ctk.CTkLabel(
            self,
            text=cat_text,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#94a3b8",
            anchor="w"
        )
        self.sub_label.grid(row=1, column=1, padx=(2, 6), pady=(0, 8), sticky="ew")
        self.sub_label.bind("<Button-1>", lambda e: self._handle_launch())

        # 3. Actions Container
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=2, rowspan=2, padx=(4, 10), pady=6, sticky="e")

        # Auto-Start Toggle Badge
        self.auto_btn = ctk.CTkButton(
            self.actions_frame,
            text="⚡ Auto" if self.app_data.get("auto_start", False) else "Auto",
            width=54,
            height=26,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#065f46" if self.app_data.get("auto_start", False) else "#272e3f",
            hover_color="#047857" if self.app_data.get("auto_start", False) else "#333d52",
            text_color="#34d399" if self.app_data.get("auto_start", False) else "#94a3b8",
            border_width=1,
            border_color="#059669" if self.app_data.get("auto_start", False) else "#3b4459",
            command=self._handle_toggle_auto
        )
        self.auto_btn.pack(side="left", padx=(0, 4))

        # Launch Button
        self.launch_btn = ctk.CTkButton(
            self.actions_frame,
            text="▶",
            width=30,
            height=26,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#4f46e5",
            hover_color="#6366f1",
            text_color="#ffffff",
            command=self._handle_launch
        )
        self.launch_btn.pack(side="left", padx=(0, 4))

        # Menu Button (More options)
        self.more_btn = ctk.CTkButton(
            self.actions_frame,
            text="⋮",
            width=22,
            height=26,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color="#2d3548",
            text_color="#94a3b8",
            command=self._show_options_menu
        )
        self.more_btn.pack(side="left")

    def _bind_hover_effects(self):
        def on_enter(e):
            self.configure(fg_color="#202534", border_color="#3b435c")

        def on_leave(e):
            self.configure(fg_color="#181b24", border_color="#262b3a")

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)

    def _handle_launch(self):
        success, msg = launch_app(self.app_data)
        if self.on_launch:
            self.on_launch(self.app_data, success, msg)

    def _handle_toggle_auto(self):
        new_state = self.config_manager.toggle_auto_start(self.app_data["id"])
        self.app_data["auto_start"] = new_state

        if new_state:
            self.auto_btn.configure(
                text="⚡ Auto",
                fg_color="#065f46",
                hover_color="#047857",
                text_color="#34d399",
                border_color="#059669"
            )
        else:
            self.auto_btn.configure(
                text="Auto",
                fg_color="#272e3f",
                hover_color="#333d52",
                text_color="#94a3b8",
                border_color="#3b4459"
            )

        if self.on_toggle_auto:
            self.on_toggle_auto(self.app_data, new_state)

    def _show_options_menu(self):
        menu = tk.Menu(self, tearoff=0, bg="#1e2230", fg="#f1f5f9", activebackground="#4f46e5", activeforeground="#ffffff", relief="flat", bd=1)
        menu.add_command(label="▶ Iniciar Agora", command=self._handle_launch)
        menu.add_command(
            label="⚡ Alternar Início Automático",
            command=self._handle_toggle_auto
        )
        menu.add_separator()
        if self.on_edit:
            menu.add_command(label="✏ Editar Aplicativo", command=lambda: self.on_edit(self.app_data))
        if self.on_delete:
            menu.add_command(label="🗑 Remover da Barra", command=lambda: self.on_delete(self.app_data))

        # Position menu next to button
        try:
            x = self.more_btn.winfo_rootx()
            y = self.more_btn.winfo_rooty() + self.more_btn.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
