import os
import sys

def get_bundle_dir() -> str:
    """
    Returns base directory where application files (assets, default config, etc.) are located.
    When running as PyInstaller bundle, returns sys._MEIPASS (onefile or onedir _internal)
    or checks the _internal folder next to the executable.
    When running from source, returns the project root.
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS") and os.path.exists(sys._MEIPASS):
            return sys._MEIPASS
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        internal_dir = os.path.join(exe_dir, "_internal")
        if os.path.exists(internal_dir):
            return internal_dir
        return exe_dir
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_resource_path(relative_path: str) -> str:
    """
    Returns absolute path to a bundled read-only resource.
    First checks get_bundle_dir(), then exe_dir (if frozen).
    """
    primary = os.path.join(get_bundle_dir(), relative_path)
    if os.path.exists(primary):
        return primary
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        secondary = os.path.join(exe_dir, relative_path)
        if os.path.exists(secondary):
            return secondary
    return primary

def get_user_data_dir() -> str:
    """
    Returns writable directory for user settings, cache, and custom icons.
    In frozen/installed mode: %APPDATA%\\SydeBar.
    In development mode: project root.
    """
    if getattr(sys, "frozen", False):
        appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
        data_dir = os.path.join(appdata, "SydeBar")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    return get_bundle_dir()
