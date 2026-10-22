import os
import threading
import pystray
from PIL import Image

from app.paths import get_resource_path

def setup_tray_icon(sidebar_window, config_manager, on_quit=None):
    """
    Sets up a background system tray icon for SydeBar.
    """
    icon_path = get_resource_path(os.path.join("assets", "icon.ico"))

    if os.path.exists(icon_path):
        tray_image = Image.open(icon_path)
    else:
        # Fallback 32x32 image
        tray_image = Image.new("RGBA", (32, 32), (99, 102, 241, 255))

    def on_toggle_clicked(icon, item):
        sidebar_window.after(0, sidebar_window.toggle_sidebar)

    def on_launch_auto_clicked(icon, item):
        sidebar_window.after(0, sidebar_window._launch_auto_apps_now)

    def on_settings_clicked(icon, item):
        sidebar_window.after(0, sidebar_window._open_settings_modal)

    def on_exit_clicked(icon, item):
        icon.stop()
        if on_quit:
            sidebar_window.after(0, on_quit)
        else:
            sidebar_window.after(0, sidebar_window.destroy)

    menu = pystray.Menu(
        pystray.MenuItem("Mostrar / Ocultar Barra", on_toggle_clicked, default=True),
        pystray.MenuItem("⚡ Disparar Início Automático", on_launch_auto_clicked),
        pystray.MenuItem("⚙ Configurações", on_settings_clicked),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", on_exit_clicked)
    )

    icon = pystray.Icon("SydeBar", tray_image, "SydeBar Windows", menu)

    # Run in background daemon thread
    t = threading.Thread(target=icon.run, daemon=True)
    t.start()
    return icon
