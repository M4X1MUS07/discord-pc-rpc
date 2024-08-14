import time
import psutil
from pypresence import Presence
import humanize
import keyboard
import mouse
import pygetwindow as gw
import json

with open("config.json") as f:
    config = json.load(f)

client_id = config["client_id"]
large_image_key = config["large_image_key"]
url_link = config["url_link"]

RPC = Presence(client_id)
RPC.connect()

def update_rpc(details, state, large_image_text, button_label=None):
    buttons = [{"label": button_label, "url": url_link}] if button_label else None
    RPC.update(
        details=details,
        state=state,
        large_image=large_image_key,
        large_text=large_image_text,
        buttons=buttons
    )

def get_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    return humanize.precisedelta(uptime_seconds)

def get_active_window(is_active):
    active_window = gw.getActiveWindow()
    if active_window:
        if "Counter-Strike 2" in active_window.title:
            app_name = "Counter-Strike 2"
        else:
            title_parts = active_window.title.split("-")
            if len(title_parts) > 1:
                if is_active:
                    app_name = f"Active: {title_parts[-1].strip()}"
                else:
                    app_name = f"AFK: {title_parts[-1].strip()}"
            else:
                app_name = f"Active: {title_parts[0].strip()}" if is_active else f"AFK: {title_parts[0].strip()}"
        app_name = app_name[:32]
        return app_name
    else:
        return "No window is open"

def on_input_event(e):
    global last_input_time, afk_start_time, active_pc_start_time
    last_input_time = time.time()
    afk_start_time = None
    if not active_pc_start_time:
        active_pc_start_time = last_input_time

def check_activity():
    global last_input_time, afk_start_time, active_pc_start_time
    current_time = time.time()
    time_difference = current_time - last_input_time if last_input_time else 0

    if time_difference < 300:
        active_duration = current_time - active_pc_start_time if active_pc_start_time else 0
        return f"👨‍💻 Using PC for {humanize.precisedelta(int(active_duration))}", True
    else:
        if not afk_start_time:
            afk_start_time = current_time
        afk_duration = current_time - afk_start_time
        active_pc_start_time = None
        return f"🌙 AFK for {humanize.precisedelta(int(afk_duration))}", False

def get_resource_usage():
    cpu_percent = round(psutil.cpu_percent(interval=1))
    ram_percent = round(psutil.virtual_memory().percent)
    return f"CPU: {cpu_percent}% RAM: {ram_percent}%"

def minimize_to_tray(icon, item):
    gw.getActiveWindow().minimize()

def show_window(icon, item):
    gw.getActiveWindow().restore()

last_input_time = time.time()
afk_start_time = None
active_pc_start_time = None

keyboard.hook(on_input_event)
mouse.hook(on_input_event)

print("Your PC discord RPC is now running...")

try:
    while True:
        pc_uptime_str = get_uptime()
        resource_usage_str = get_resource_usage()
        activity_str, is_active = check_activity()
        hover_text = f"{resource_usage_str}"
        active_window = get_active_window(is_active)
        update_rpc(details=f"💻 PC Uptime: {pc_uptime_str}", state=activity_str, large_image_text=hover_text, button_label=f"{active_window}")
        time.sleep(10)

except KeyboardInterrupt:
    pass

finally:
    RPC.close()