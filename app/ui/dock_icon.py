import tkinter as tk
import customtkinter as ctk
from PIL import Image

from app.icon_extractor import get_app_icon
from app.launcher import launch_app
from app.ui.tooltip import ModernTooltip

class DockIcon(ctk.CTkFrame):
    def __init__(
        self,
        master,
        app_data,
        config_manager,
        dock_position="right",
        on_launch=None,
        on_edit=None,
        on_delete=None,
        on_toggle_auto=None,
        **kwargs
    ):
        super().__init__(
            master,
            width=46,
            height=46,
            corner_radius=12,
            fg_color="#181b25",
            border_width=1,
            border_color="#272d3e",
            **kwargs
        )
        self.pack_propagate(False)

        self.app_data = app_data
        self.config_manager = config_manager
        self.dock_position = dock_position
        self.on_launch = on_launch
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle_auto = on_toggle_auto

        self._build_ui()
        self._setup_events()

    def _build_ui(self):
        # 1. App Icon
        icon_pil = get_app_icon(
            self.app_data.get("path", ""),
            app_name=self.app_data.get("name", "App"),
            cache_dir=self.config_manager.cache_dir,
            app_id=self.app_data.get("id", "temp"),
            size=30,
            custom_icon=self.app_data.get("custom_icon", "")
        )
        self.icon_ctk = ctk.CTkImage(light_image=icon_pil, dark_image=icon_pil, size=(28, 28))

        # Main clickable button/label
        self.icon_lbl = ctk.CTkLabel(
            self,
            image=self.icon_ctk,
            text="",
            width=38,
            height=38,
            corner_radius=10,
            fg_color="transparent"
        )
        self.icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # 2. Auto-Start Indicator Dot
        # Green dot in bottom-right if auto_start is active
        self.dot = ctk.CTkFrame(
            self,
            width=8,
            height=8,
            corner_radius=4,
            fg_color="#10b981",
            border_width=1,
            border_color="#064e3b"
        )
        is_auto = self.app_data.get("auto_start", False)
        if is_auto:
            self.dot.place(relx=0.82, rely=0.82, anchor="center")

        # 3. Modern Tooltip (Appears on hover with app name & auto-start info)
        tip_side = "left" if self.dock_position == "right" else "right"
        self.tooltip = ModernTooltip(
            self,
            title=self.app_data.get("name", "Aplicativo"),
            is_auto_start=is_auto,
            category=self.app_data.get("category", "Geral"),
            position=tip_side
        )
        self.tooltip.bind_widget(self.icon_lbl)
        self.tooltip.bind_widget(self.dot)

    def _setup_events(self):
        # Hover animations
        def on_enter(e):
            self.configure(fg_color="#252c3d", border_color="#4f46e5")

        def on_leave(e):
            self.configure(fg_color="#181b25", border_color="#272d3e")

        for widget in (self, self.icon_lbl, self.dot):
            widget.bind("<Enter>", on_enter, add="+")
            widget.bind("<Leave>", on_leave, add="+")
            widget.bind("<Button-1>", lambda e: self._handle_click())
            widget.bind("<Button-3>", lambda e: self._show_context_menu(e))

    def _handle_click(self):
        self.tooltip.hide_tip()
        # Brief click animation
        self.configure(fg_color="#4f46e5")
        self.after(120, lambda: self.configure(fg_color="#252c3d"))

        success, msg = launch_app(self.app_data)
        if self.on_launch:
            self.on_launch(self.app_data, success, msg)

    def _toggle_auto_start(self):
        new_state = self.config_manager.toggle_auto_start(self.app_data["id"])
        self.app_data["auto_start"] = new_state

        if new_state:
            self.dot.configure(fg_color="#10b981", border_width=1, border_color="#064e3b")
            self.dot.place(relx=0.82, rely=0.82, anchor="center")
        else:
            self.dot.place_forget()

        self.tooltip.update_info(is_auto_start=new_state)

        if self.on_toggle_auto:
            self.on_toggle_auto(self.app_data, new_state)

    def _show_context_menu(self, event=None):
        self.tooltip.hide_tip()
        menu = tk.Menu(
            self,
            tearoff=0,
            bg="#181b26",
            fg="#f1f5f9",
            activebackground="#4f46e5",
            activeforeground="#ffffff",
            relief="flat",
            bd=1,
            font=("Segoe UI", 9)
        )
        menu.add_command(label=f"▶ Abrir {self.app_data.get('name', '')}", command=self._handle_click)
        menu.add_separator()

        is_auto = self.app_data.get("auto_start", False)
        auto_label = "✓ Início Automático (Ativo)" if is_auto else "○ Início Automático (Desativado)"
        menu.add_command(label=auto_label, command=self._toggle_auto_start)

        menu.add_separator()
        if self.on_edit:
            menu.add_command(label="✏ Editar Aplicativo", command=lambda: self.on_edit(self.app_data))
        if self.on_delete:
            menu.add_command(label="🗑 Remover da Barra", command=lambda: self.on_delete(self.app_data))

        try:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            if self.dock_position == "right":
                x = max(10, x - 130)
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
