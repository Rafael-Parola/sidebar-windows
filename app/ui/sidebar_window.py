import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image

from app.ui.dock_icon import DockIcon
from app.ui.tooltip import ModernTooltip
from app.ui.add_app_modal import AddAppModal
from app.ui.settings_modal import SettingsModal
from app.launcher import run_auto_start_sequence
from app.paths import get_resource_path

DOCK_WIDTH = 68
HIDDEN_SLIVER = 6

class SidebarWindow(ctk.CTk):
    def __init__(self, config_manager, on_tray_toggle=None):
        super().__init__()
        self.config_manager = config_manager
        self.on_tray_toggle = on_tray_toggle

        # Window properties
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0e1017")

        # State flags
        self.is_expanded = False # Starts hidden at edge, reveals on hover
        self.is_animating = False
        self.is_modal_open = False
        self.leave_timer = None

        # Assets
        self.logo_image = None
        self._load_assets()

        # Build UI
        self._build_ui()

        # Setup mouse tracking for auto-hide
        self._setup_auto_hide_events()

        # Calculate height and set initial position (hidden sliver against edge)
        self.reposition_window(animate=False)

        # Load app icons
        self.refresh_app_list()

    def _load_assets(self):
        logo_path = get_resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(22, 22))
            except Exception:
                self.logo_image = None

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main Dock Card Frame
        self.dock_frame = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color="#12151d",
            border_width=1,
            border_color="#2f374d"
        )
        self.dock_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=1, pady=1)

        # 1. Top Section (Add app button)
        self.top_frame = ctk.CTkFrame(self.dock_frame, fg_color="transparent", width=46)
        self.top_frame.pack(fill="x", padx=8, pady=(10, 4))

        self.add_btn = ctk.CTkButton(
            self.top_frame,
            text="+",
            width=46,
            height=38,
            corner_radius=12,
            fg_color="#1e2230",
            hover_color="#4f46e5",
            border_width=1,
            border_color="#2e3549",
            text_color="#f1f5f9",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._open_add_modal
        )
        self.add_btn.pack(pady=2)

        tip_side = "left" if self.config_manager.get("position", "right") == "right" else "right"
        ModernTooltip(self.add_btn, title="Adicionar Novo Aplicativo", position=tip_side)

        # Top separator line
        self.sep_top = ctk.CTkFrame(self.dock_frame, height=1, fg_color="#262c3d")
        self.sep_top.pack(fill="x", padx=12, pady=6)

        # 2. Middle Section (Scrollable container for app icons)
        self.icons_scroll = ctk.CTkScrollableFrame(
            self.dock_frame,
            fg_color="transparent",
            width=52,
            scrollbar_button_color="#2b3347",
            scrollbar_button_hover_color="#4f46e5"
        )
        self.icons_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # 3. Bottom separator line
        self.sep_bottom = ctk.CTkFrame(self.dock_frame, height=1, fg_color="#262c3d")
        self.sep_bottom.pack(fill="x", padx=12, pady=6)

        # 4. Bottom Section (Auto-start trigger & Settings buttons)
        self.bottom_frame = ctk.CTkFrame(self.dock_frame, fg_color="transparent", width=46)
        self.bottom_frame.pack(fill="x", padx=8, pady=(4, 10))

        # Auto-start run all button
        self.run_auto_btn = ctk.CTkButton(
            self.bottom_frame,
            text="⚡",
            width=46,
            height=36,
            corner_radius=10,
            fg_color="#064e3b",
            hover_color="#059669",
            border_width=1,
            border_color="#059669",
            text_color="#34d399",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._launch_auto_apps_now
        )
        self.run_auto_btn.pack(pady=(0, 4))
        ModernTooltip(self.run_auto_btn, title="Disparar Apps Automáticos", position=tip_side)

        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.bottom_frame,
            text="⚙",
            width=46,
            height=36,
            corner_radius=10,
            fg_color="#181b25",
            hover_color="#282f42",
            border_width=1,
            border_color="#272d3e",
            text_color="#94a3b8",
            font=ctk.CTkFont(size=14),
            command=self._open_settings_modal
        )
        self.settings_btn.pack(pady=0)
        ModernTooltip(self.settings_btn, title="Configurações", position=tip_side)

    def refresh_app_list(self):
        # Clear existing icons
        for widget in self.icons_scroll.winfo_children():
            widget.destroy()

        apps = self.config_manager.get_apps()
        pos = self.config_manager.get("position", "right")

        for app in apps:
            icon_btn = DockIcon(
                self.icons_scroll,
                app_data=app,
                config_manager=self.config_manager,
                dock_position=pos,
                on_launch=self._on_app_launched,
                on_edit=self._open_edit_modal,
                on_delete=self._on_app_delete,
                on_toggle_auto=self._on_toggle_auto
            )
            icon_btn.pack(pady=4, padx=2)

        # Adjust height based on app count
        self.reposition_window(animate=False)

    def _calc_geometry(self, expanded: bool):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        height_mode = self.config_manager.get("height_mode", "auto")
        if height_mode == "custom":
            dock_h = self.config_manager.get("custom_height", 480)
        else:
            apps_count = len(self.config_manager.get_apps())
            extra_pad = self.config_manager.get("extra_height_padding", 30)
            # Base height for header, separators, bottom controls and paddings: ~215px
            # Plus 56px for each app icon
            content_height = 215 + (max(1, apps_count) * 56) + extra_pad
            dock_h = max(300, content_height)

        # Clamp between 300px and available screen height
        dock_h = max(300, min(sh - 100, dock_h))
        y = (sh - dock_h) // 2

        pos = self.config_manager.get("position", "right")
        if pos == "right":
            target_x = sw - DOCK_WIDTH if expanded else sw - HIDDEN_SLIVER
        else:
            target_x = 0 if expanded else - (DOCK_WIDTH - HIDDEN_SLIVER)

        return DOCK_WIDTH, dock_h, target_x, y

    def reposition_window(self, animate=False):
        w, h, target_x, y = self._calc_geometry(self.is_expanded)
        if not animate:
            self.geometry(f"{w}x{h}+{target_x}+{y}")
        else:
            self._animate_slide(target_x, w, h, y)

    def _animate_slide(self, target_x, w, h, y):
        try:
            curr_x = self.winfo_x()
        except Exception:
            curr_x = target_x

        steps = 4
        diff = (target_x - curr_x) / steps

        def step_fn(step=1):
            if step >= steps:
                self.geometry(f"{w}x{h}+{target_x}+{y}")
                self.is_animating = False
            else:
                intermediate_x = int(curr_x + diff * step)
                self.geometry(f"{w}x{h}+{intermediate_x}+{y}")
                self.after(14, lambda: step_fn(step + 1))

        self.is_animating = True
        step_fn()

    # Auto-Hide Event Tracking
    def _setup_auto_hide_events(self):
        def on_enter(e):
            if self.leave_timer:
                self.after_cancel(self.leave_timer)
                self.leave_timer = None
            if not self.is_expanded:
                self.reveal_dock()

        def on_leave(e):
            if self.leave_timer:
                self.after_cancel(self.leave_timer)
            # Debounce 300ms then check if pointer is outside
            self.leave_timer = self.after(300, self._check_and_hide)

        # Bind to root window and main frame
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.dock_frame.bind("<Enter>", on_enter)
        self.dock_frame.bind("<Leave>", on_leave)

    def _check_and_hide(self):
        if self.is_modal_open:
            return

        try:
            px, py = self.winfo_pointerxy()
            wx = self.winfo_rootx()
            wy = self.winfo_rooty()
            ww = self.winfo_width()
            wh = self.winfo_height()

            # Check if mouse is within window boundaries
            if wx <= px <= wx + ww and wy <= py <= wy + wh:
                return  # Still inside!
        except Exception:
            pass

        self.hide_dock()

    def reveal_dock(self):
        if self.is_expanded:
            return
        self.is_expanded = True
        self.reposition_window(animate=True)

    def hide_dock(self):
        if not self.is_expanded or self.is_modal_open:
            return
        if ModernTooltip.active_tip:
            try:
                ModernTooltip.active_tip.hide_tip()
            except Exception:
                pass
        self.is_expanded = False
        self.reposition_window(animate=True)

    def toggle_sidebar(self):
        if self.is_expanded:
            self.hide_dock()
        else:
            self.reveal_dock()

    # App Actions
    def _on_app_launched(self, app_data, success, msg):
        pass

    def _on_toggle_auto(self, app_data, new_state):
        pass

    def _on_app_delete(self, app_data):
        self.config_manager.remove_app(app_data["id"])
        self.refresh_app_list()

    def _open_add_modal(self):
        self.is_modal_open = True
        modal = AddAppModal(self, self.config_manager, on_saved=self.refresh_app_list)
        modal.bind("<Destroy>", lambda e: self._on_modal_closed(modal, e))

    def _open_edit_modal(self, app_data):
        self.is_modal_open = True
        modal = AddAppModal(self, self.config_manager, app_to_edit=app_data, on_saved=self.refresh_app_list)
        modal.bind("<Destroy>", lambda e: self._on_modal_closed(modal, e))

    def _open_settings_modal(self):
        self.is_modal_open = True
        modal = SettingsModal(self, self.config_manager, on_settings_changed=self._on_settings_saved)
        modal.bind("<Destroy>", lambda e: self._on_modal_closed(modal, e))

    def _on_modal_closed(self, modal, event):
        if event.widget == modal:
            self.is_modal_open = False
            self.after(200, self._check_and_hide)

    def _on_settings_saved(self):
        self.refresh_app_list()

    def _launch_auto_apps_now(self):
        apps = self.config_manager.get_apps()
        auto_apps = [a for a in apps if a.get("auto_start", False)]
        if not auto_apps:
            return
        # Brief visual feedback on button
        self.run_auto_btn.configure(fg_color="#10b981")
        self.after(500, lambda: self.run_auto_btn.configure(fg_color="#064e3b"))
        run_auto_start_sequence(self.config_manager)
