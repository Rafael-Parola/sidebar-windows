import os
import subprocess
import threading
import time

def launch_app(app_data):
    """
    Launches an application based on its dictionary metadata.
    Returns (success: bool, message: str).
    """
    raw_path = app_data.get("path", "").strip()
    arguments = app_data.get("arguments", "").strip()

    if not raw_path:
        return False, "Caminho do aplicativo não informado."

    # Expand environment variables if any (e.g. %APPDATA%, %LOCALAPPDATA%, %WINDIR%)
    path = os.path.expandvars(raw_path)

    try:
        if arguments:
            # When arguments are passed, use subprocess
            cmd = f'"{path}" {arguments}'
            subprocess.Popen(
                cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            )
        else:
            # Standard Windows file/shortcut/executable launch
            if os.path.exists(path) or path.startswith("http://") or path.startswith("https://") or path.endswith(".exe"):
                os.startfile(path)
            else:
                # Try shell execution (e.g. 'calc.exe', 'explorer.exe', or custom alias)
                subprocess.Popen(
                    path,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                )
        return True, "Aplicativo iniciado com sucesso!"
    except Exception as e:
        return False, f"Falha ao iniciar: {str(e)}"

def run_auto_start_sequence(config_manager, on_app_launch=None, on_finish=None):
    """
    Runs in a background thread to launch all apps marked with auto_start=True.
    Applies stagger delay to prevent boot lag.
    """
    def worker():
        apps = config_manager.get_apps()
        auto_apps = [a for a in apps if a.get("auto_start", False)]
        delay = config_manager.get("stagger_delay_seconds", 2)

        launched = 0
        for i, app in enumerate(auto_apps):
            success, msg = launch_app(app)
            if success:
                launched += 1
            if on_app_launch:
                on_app_launch(i + 1, len(auto_apps), app["name"], success)
            if i < len(auto_apps) - 1 and delay > 0:
                time.sleep(delay)

        if on_finish:
            on_finish(launched, len(auto_apps))

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t
