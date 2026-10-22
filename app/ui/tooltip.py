import tkinter as tk
import customtkinter as ctk

class ModernTooltip:
    """
    Floating dark tooltip that appears beside the dock item.
    Rock-solid multi-widget tracking and bounding-box detection to prevent flickering.
    """
    active_tip = None  # Class-level tracker to ensure only 1 tooltip is visible at a time

    def __init__(self, widget, title, is_auto_start=False, category=None, position="left"):
        self.widget = widget
        self.title = title
        self.is_auto_start = is_auto_start
        self.category = category
        self.position = position  # 'left' (dock on right) or 'right' (dock on left)
        
        self.tip_window = None
        self.show_timer = None
        self.hide_timer = None

        self.bind_widget(self.widget)

    def bind_widget(self, w):
        """Recursively binds hover events to the widget and all its inner children."""
        try:
            w.bind("<Enter>", self.schedule_show, add="+")
            w.bind("<Leave>", self.schedule_hide, add="+")
            w.bind("<Button-1>", lambda e: self.hide_tip(), add="+")
            w.bind("<Button-3>", lambda e: self.hide_tip(), add="+")
            for child in w.winfo_children():
                self.bind_widget(child)
        except Exception:
            pass

    def update_info(self, title=None, is_auto_start=None, category=None):
        if title is not None:
            self.title = title
        if is_auto_start is not None:
            self.is_auto_start = is_auto_start
        if category is not None:
            self.category = category

    def schedule_show(self, event=None):
        """Schedules showing the tooltip after a tiny delay (100ms) to ensure smooth interaction."""
        if self.hide_timer:
            try:
                self.widget.after_cancel(self.hide_timer)
            except Exception:
                pass
            self.hide_timer = None

        if not self.tip_window and not self.show_timer:
            try:
                self.show_timer = self.widget.after(100, self.show_tip)
            except Exception:
                pass

    def schedule_hide(self, event=None):
        """Debounces hiding so moving across inner child widgets doesn't flicker or dismiss prematurely."""
        if self.show_timer:
            try:
                self.widget.after_cancel(self.show_timer)
            except Exception:
                pass
            self.show_timer = None

        if self.hide_timer:
            try:
                self.widget.after_cancel(self.hide_timer)
            except Exception:
                pass

        try:
            self.hide_timer = self.widget.after(120, self._check_and_hide)
        except Exception:
            self.hide_tip()

    def _check_and_hide(self):
        """Checks if the mouse cursor is still within the widget's physical bounds."""
        self.hide_timer = None
        try:
            px, py = self.widget.winfo_pointerxy()
            wx = self.widget.winfo_rootx() - 4
            wy = self.widget.winfo_rooty() - 4
            ww = self.widget.winfo_width() + 8
            wh = self.widget.winfo_height() + 8

            # If cursor is still inside or near the icon bounds, don't hide
            if wx <= px <= wx + ww and wy <= py <= wy + wh:
                return
        except Exception:
            pass

        self.hide_tip()

    def show_tip(self, event=None):
        self.show_timer = None

        if not self.title or self.tip_window:
            return

        # Close any other active tooltip first
        if ModernTooltip.active_tip and ModernTooltip.active_tip != self:
            try:
                ModernTooltip.active_tip.hide_tip()
            except Exception:
                pass

        try:
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_attributes("-topmost", True)

            # Container frame
            frame = ctk.CTkFrame(
                tw,
                corner_radius=8,
                fg_color="#181b26",
                border_width=1,
                border_color="#333d52"
            )
            frame.pack(fill="both", expand=True)

            # Header row: Title + Auto badge
            header = ctk.CTkFrame(frame, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(6, 2))

            title_lbl = ctk.CTkLabel(
                header,
                text=self.title,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#f8fafc"
            )
            title_lbl.pack(side="left")

            if self.is_auto_start:
                badge = ctk.CTkLabel(
                    header,
                    text="⚡ Auto-Start",
                    font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                    text_color="#34d399",
                    fg_color="#064e3b",
                    corner_radius=4,
                    padx=6,
                    pady=2
                )
                badge.pack(side="left", padx=(8, 0))

            # Subtitle / Hint
            cat_text = f"{self.category} • " if self.category else ""
            hint_lbl = ctk.CTkLabel(
                frame,
                text=f"{cat_text}Clique: abrir | Dir.: opções",
                font=ctk.CTkFont(family="Segoe UI", size=9),
                text_color="#94a3b8"
            )
            hint_lbl.pack(anchor="w", padx=10, pady=(0, 6))

            tw.update_idletasks()
            tip_w = tw.winfo_reqwidth()
            tip_h = tw.winfo_reqheight()

            # Calculate screen coordinates relative to the widget
            root_x = self.widget.winfo_rootx()
            root_y = self.widget.winfo_rooty()
            widget_w = self.widget.winfo_width()
            widget_h = self.widget.winfo_height()

            if self.position == "left":
                # Dock is on right edge, tooltip appears on the left of the dock
                x = root_x - tip_w - 12
            else:
                # Dock is on left edge, tooltip appears on the right of the dock
                x = root_x + widget_w + 12

            y = root_y + (widget_h - tip_h) // 2

            # Clamp within screen bounds
            screen_h = self.widget.winfo_screenheight()
            y = max(10, min(screen_h - tip_h - 10, y))

            tw.wm_geometry(f"{tip_w}x{tip_h}+{x}+{y}")
            ModernTooltip.active_tip = self
        except Exception:
            self.hide_tip()

    def hide_tip(self, event=None):
        if self.show_timer:
            try:
                self.widget.after_cancel(self.show_timer)
            except Exception:
                pass
            self.show_timer = None

        if self.hide_timer:
            try:
                self.widget.after_cancel(self.hide_timer)
            except Exception:
                pass
            self.hide_timer = None

        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

        if ModernTooltip.active_tip == self:
            ModernTooltip.active_tip = None
