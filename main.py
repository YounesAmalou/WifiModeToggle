import logging
import os
import subprocess
import sys
import time
import winreg
import pystray
from PIL import Image, ImageDraw
from elevate import elevate
from pystray import MenuItem as item

# Registry constants
ADAPTER_KEY_PATH = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0000'
VALUE_NAME = 'WirelessMode'
VALUE_5GHZ = 17
VALUE_24GHZ = 34
ADAPTER_NAME = 'Intel(R) Wi-Fi 6E AX211 160MHz'

# Scheduled Task constant
TASK_NAME = "WiFiToggle Startup"

# Global flag to prevent multiple toggles simultaneously
toggling = False

# Configure logging
logging.basicConfig(
    filename="wifi_toggle.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------- Registry and Adapter Functions ---------------

def read_mode():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ADAPTER_KEY_PATH, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, VALUE_NAME)
            return int(val)
    except Exception as exc:
        logging.error(f"Registry read error: {exc}")
        raise


def write_mode(value):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ADAPTER_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, str(value))
    except Exception as exc:
        logging.error(f"Registry write error: {exc}")
        raise


def restart_adapter():
    try:
        subprocess.call(f'netsh interface set interface "{ADAPTER_NAME}" admin=disable', shell=True)
        time.sleep(2)  # Delay to ensure adapter disable
        subprocess.call(f'netsh interface set interface "{ADAPTER_NAME}" admin=enable', shell=True)
    except Exception as exc:
        logging.error(f"Error restarting adapter: {exc}")
        raise


def create_image(color: str = 'blue') -> 'Image.Image':
    img = Image.new('RGB', (64, 64), 'black')
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 48, 48), fill=color)
    return img


def toggle_mode(icon, *_):
    global toggling
    if toggling:
        # Ignore if already processing a toggle
        return
    toggling = True
    # Show yellow indicator during toggle process
    icon.icon = create_image("yellow")
    try:
        current = read_mode()
        new_value = VALUE_24GHZ if current == VALUE_5GHZ else VALUE_5GHZ
        write_mode(new_value)
        restart_adapter()

        if new_value == VALUE_24GHZ:
            mode_str = "2.4GHz"
            final_color = "blue"
        else:
            mode_str = "5GHz"
            final_color = "green"

        icon.title = f"Wireless Mode: {mode_str}"
        icon.icon = create_image(final_color)
    except Exception as exc:
        logging.error(f"Error toggling mode: {exc}")
    finally:
        toggling = False


# ------------- Scheduled Task Functions ---------------

def check_scheduled_task_exists() -> bool:
    """
    Returns True if the scheduled task exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", TASK_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except Exception as exc:
        logging.error(f"Error checking scheduled task: {exc}")
        return False


def install_scheduled_task():
    """
    Installs the scheduled task to run this executable at logon with highest privileges.
    """
    try:
        # Use the absolute path to this executable.
        exe_path = os.path.abspath(sys.argv[0])
        cmd = [
            "schtasks", "/create",
            "/tn", TASK_NAME,
            "/tr", exe_path,
            "/sc", "onlogon",
            "/rl", "highest",
            "/f"  # Force creation
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.error(f"Scheduled task '{TASK_NAME}' installed successfully.")
        else:
            logging.error(f"Error installing scheduled task '{TASK_NAME}': {result.stderr.strip()}")
    except Exception as exc:
        logging.error(f"Exception installing scheduled task: {exc}")


def uninstall_scheduled_task():
    """
    Uninstalls the scheduled task.
    """
    try:
        cmd = ["schtasks", "/delete", "/tn", TASK_NAME, "/f"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.error(f"Scheduled task '{TASK_NAME}' uninstalled successfully.")
        else:
            logging.error(f"Error uninstalling scheduled task '{TASK_NAME}': {result.stderr.strip()}")
    except Exception as exc:
        logging.error(f"Exception uninstalling scheduled task: {exc}")


def toggle_scheduled_task(icon, _):
    """
    Checks the current state of the scheduled task.
    If it exists, uninstall it. Otherwise, install it.
    Afterward, update the tray menu.
    """
    try:
        if check_scheduled_task_exists():
            uninstall_scheduled_task()
        else:
            install_scheduled_task()
    except Exception as exc:
        logging.error(f"Error toggling scheduled task: {exc}")
    finally:
        # Update the tray menu with the new status
        icon.menu = build_menu()
        icon.update_menu()  # This call forces a refresh (if supported)

# ------------- Tray Icon Setup ---------------

def build_menu():
    menu_items = [
        item('Toggle Wi-Fi Band', toggle_mode, default=True)
    ]
    if getattr(sys, 'frozen', False):
        schedule_status = "Installed" if check_scheduled_task_exists() else "Not Installed"
        menu_items.extend([
            item(f'Scheduled Task: {schedule_status}', None, enabled=False),
            item('Install/Uninstall Scheduled Task', toggle_scheduled_task)
        ])
    menu_items.append(item('Quit', lambda icon, item: icon.stop()))
    return pystray.Menu(*menu_items)

def setup_tray():
    try:
        current_mode = read_mode()
    except Exception as exc:
        logging.error(f"Error reading mode during tray setup: {exc}")
        current_mode = VALUE_5GHZ  # fallback value

    if current_mode == VALUE_24GHZ:
        mode_str = "2.4GHz"
        initial_color = "blue"
    else:
        mode_str = "5GHz"
        initial_color = "green"

    icon = pystray.Icon('WiFiToggle')
    icon.icon = create_image(initial_color)
    icon.title = f"Wireless Mode: {mode_str}"
    icon.menu = build_menu()
    icon.run()


if __name__ == '__main__':
    try:
        elevate(show_console=False)
        print("starting tray...")
        setup_tray()
    except Exception as e:
        logging.error(f"Error starting tray: {e}")
