import sys
import os
import customtkinter as ctk

# Ensure app directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config_manager import ConfigManager
from app.ui.sidebar_window import SidebarWindow
from app.tray import setup_tray_icon

def main():
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Initialize configuration
    config = ConfigManager()

    # Create and setup sidebar window
    app = SidebarWindow(config)

    # Setup Windows system tray icon in background
    tray_icon = setup_tray_icon(app, config, on_quit=app.destroy)

    # Check if auto-launch apps should run upon startup
    if config.get("launch_auto_apps_on_start", True):
        # Trigger after 1.5s so window is fully rendered
        app.after(1500, app._launch_auto_apps_now)

    # Run application
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            tray_icon.stop()
        except Exception:
            pass

if __name__ == "__main__":
    main()
