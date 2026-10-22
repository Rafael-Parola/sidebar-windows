import json
import os
import sys
import uuid
import winreg

from app.paths import get_resource_path, get_user_data_dir, get_bundle_dir
import shutil

USER_DATA_ROOT = get_user_data_dir()
CONFIG_FILE = os.path.join(USER_DATA_ROOT, "config.json")
CACHE_DIR = os.path.join(USER_DATA_ROOT, ".cache", "icons")
CUSTOM_ICONS_DIR = os.path.join(USER_DATA_ROOT, "assets", "custom_icons")

RUN_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "SydeBarWindows"

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "position": "right",          # 'right' or 'left'
    "auto_hide": True,            # Auto-retract when mouse leaves
    "height_mode": "auto",        # 'auto' (scales with apps) or 'custom'
    "custom_height": 480,         # Custom height in px when height_mode == 'custom'
    "extra_height_padding": 30,   # Extra breathing room in auto mode
    "run_at_windows_startup": False,
    "launch_auto_apps_on_start": True,
    "stagger_delay_seconds": 2,
    "apps": [
        {
            "id": "app_explorer",
            "name": "Explorador de Arquivos",
            "path": "explorer.exe",
            "arguments": "",
            "auto_start": False,
            "category": "Sistema"
        },
        {
            "id": "app_notepad",
            "name": "Bloco de Notas",
            "path": r"C:\Windows\notepad.exe",
            "arguments": "",
            "auto_start": False,
            "category": "Produtividade"
        },
        {
            "id": "app_calc",
            "name": "Calculadora",
            "path": "calc.exe",
            "arguments": "",
            "auto_start": False,
            "category": "Utilidades"
        },
        {
            "id": "app_taskmgr",
            "name": "Gerenciador de Tarefas",
            "path": r"C:\Windows\System32\Taskmgr.exe",
            "arguments": "",
            "auto_start": False,
            "category": "Sistema"
        }
    ]
}

class ConfigManager:
    def __init__(self, file_path=None):
        self.project_root = get_user_data_dir()
        self.file_path = file_path or os.path.join(self.project_root, "config.json")
        self.cache_dir = os.path.join(self.project_root, ".cache", "icons")
        self.custom_icons_dir = os.path.join(self.project_root, "assets", "custom_icons")
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.custom_icons_dir, exist_ok=True)

        # Seed initial config and default custom icons if first run in frozen mode
        if not os.path.exists(self.file_path):
            bundled_config = get_resource_path("config.json")
            if os.path.exists(bundled_config):
                try:
                    shutil.copy2(bundled_config, self.file_path)
                except Exception:
                    pass

        bundled_custom_icons = get_resource_path(os.path.join("assets", "custom_icons"))
        if os.path.exists(bundled_custom_icons):
            try:
                for icon_name in os.listdir(bundled_custom_icons):
                    src = os.path.join(bundled_custom_icons, icon_name)
                    dest = os.path.join(self.custom_icons_dir, icon_name)
                    if os.path.isfile(src) and not os.path.exists(dest):
                        shutil.copy2(src, dest)
            except Exception:
                pass

        self.data = self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge defaults for any missing keys
                    for k, v in DEFAULT_CONFIG.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception as e:
                print(f"Error reading config, using defaults: {e}")
        # If not found or error, create with defaults
        self._save_raw(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    def save(self):
        """Saves current state to config.json."""
        self._save_raw(self.data)

    def _save_raw(self, payload):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    # Settings getters and setters
    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def save_custom_icon(self, source_path, app_id):
        """
        Copies/converts an external custom icon into the local assets/custom_icons/ folder
        so external scripts or file cleanups won't break the icon.
        Returns the safe relative path, e.g. 'assets/custom_icons/app_123456.png'.
        """
        if not source_path:
            return ""

        source = os.path.expandvars(source_path.strip())
        if not os.path.exists(source):
            # Might already be a relative path
            full_test = os.path.join(self.project_root, source)
            if os.path.exists(full_test):
                return source.replace("\\", "/")
            return source_path

        dest_filename = f"{app_id}.png"
        dest_path = os.path.join(self.custom_icons_dir, dest_filename)
        rel_path = os.path.join("assets", "custom_icons", dest_filename).replace("\\", "/")

        norm_source = os.path.normpath(os.path.abspath(source))
        if norm_source == os.path.normpath(dest_path):
            return rel_path

        try:
            from PIL import Image
            with Image.open(source) as img:
                rgba = img.convert("RGBA")
                rgba.save(dest_path, "PNG")
            return rel_path
        except Exception:
            try:
                import shutil
                shutil.copy2(source, dest_path)
                return rel_path
            except Exception as e:
                print(f"Error copying custom icon: {e}")
                return source_path

    # Apps management
    def get_apps(self):
        return self.data.get("apps", [])

    def add_app(self, name, path, arguments="", auto_start=False, category="Geral", custom_icon=""):
        app_id = f"app_{uuid.uuid4().hex[:8]}"
        saved_icon = self.save_custom_icon(custom_icon, app_id) if custom_icon else ""
        new_app = {
            "id": app_id,
            "name": name.strip(),
            "path": path.strip(),
            "arguments": arguments.strip(),
            "auto_start": bool(auto_start),
            "category": category.strip() or "Geral",
            "custom_icon": saved_icon
        }
        self.data.setdefault("apps", []).append(new_app)
        self.save()
        return new_app

    def update_app(self, app_id, **kwargs):
        for app in self.data.get("apps", []):
            if app["id"] == app_id:
                if "custom_icon" in kwargs:
                    new_icon = kwargs["custom_icon"]
                    if new_icon:
                        kwargs["custom_icon"] = self.save_custom_icon(new_icon, app_id)
                    else:
                        # User cleared the custom icon - delete stored file
                        local_icon = os.path.join(self.custom_icons_dir, f"{app_id}.png")
                        if os.path.exists(local_icon):
                            try:
                                os.remove(local_icon)
                            except Exception:
                                pass
                        kwargs["custom_icon"] = ""

                app.update(kwargs)
                self.save()
                # Clean cached icon so new/updated icon takes immediate effect
                cached_icon = os.path.join(self.cache_dir, f"{app_id}.png")
                if os.path.exists(cached_icon):
                    try:
                        os.remove(cached_icon)
                    except Exception:
                        pass
                return app
        return None

    def toggle_auto_start(self, app_id):
        """Toggles the auto_start flag for a specific app."""
        for app in self.data.get("apps", []):
            if app["id"] == app_id:
                app["auto_start"] = not app.get("auto_start", False)
                self.save()
                return app["auto_start"]
        return False

    def remove_app(self, app_id):
        apps = self.data.get("apps", [])
        self.data["apps"] = [app for app in apps if app["id"] != app_id]
        self.save()
        # Clean cached icon if exists
        cached_icon = os.path.join(self.cache_dir, f"{app_id}.png")
        if os.path.exists(cached_icon):
            try:
                os.remove(cached_icon)
            except Exception:
                pass
        # Clean custom icon in assets/custom_icons/ if exists
        custom_icon = os.path.join(self.custom_icons_dir, f"{app_id}.png")
        if os.path.exists(custom_icon):
            try:
                os.remove(custom_icon)
            except Exception:
                pass

    def reorder_app(self, from_index, to_index):
        apps = self.data.get("apps", [])
        if 0 <= from_index < len(apps) and 0 <= to_index < len(apps):
            item = apps.pop(from_index)
            apps.insert(to_index, item)
            self.save()

    # Windows Startup Registry Management
    def is_run_at_startup_enabled(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
                return bool(val)
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def set_run_at_startup(self, enable: bool):
        """Adds or removes SydeBar from Windows CurrentVersion\\Run registry."""
        if getattr(sys, "frozen", False):
            cmd = f'"{sys.executable}"'
        else:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            vbs_launcher = os.path.join(project_root, "SydeBar.vbs")
            main_py = os.path.join(project_root, "main.py")

            # Command to run silently without command prompt
            if os.path.exists(vbs_launcher):
                cmd = f'wscript.exe "{vbs_launcher}"'
            else:
                # Fallback to pythonw.exe
                pyw_exe = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(pyw_exe):
                    pyw_exe = sys.executable
                cmd = f'"{pyw_exe}" "{main_py}"'

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, cmd)
                    self.set("run_at_windows_startup", True)
                else:
                    try:
                        winreg.DeleteValue(key, REG_APP_NAME)
                    except FileNotFoundError:
                        pass
                    self.set("run_at_windows_startup", False)
            return True
        except Exception as e:
            print(f"Error updating Windows Startup Registry: {e}")
            return False
