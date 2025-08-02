import FreeSimpleGUI as sg
import threading

from items import items
from automation import run_bot

# ==========================
# Globals
# ==========================
gear_items_dict = items["gear"]
gear_items = list(gear_items_dict.values())
terminate_flag = threading.Event()
bot_thread = None
is_running = False


def get_key_by_value(d, value):
    return next((k for k, v in d.items() if v == value), None)


def run_bot_thread(selected_keys):
    global is_running
    terminate_flag.clear()
    is_running = True
    run_bot(selected_keys, terminate_flag)
    is_running = False


# ==========================
# GUI Setup
# ==========================
status_text = sg.Text('Status: Idle', key='status', font=('Segoe UI', 10), text_color='white', background_color='gray')

layout = [[
    sg.Text('Gears', font=('Segoe UI', 14)),
    sg.Push(),
    sg.Button('Select all', key='select_all', size=(10, 1), font=('Segoe UI', 8)),
]]

checkbox_size = (20, 1)

# Create 2-column checkbox layout
for i in range(0, len(gear_items), 2):
    row = []
    row.append(sg.Checkbox(
        gear_items[i],
        key=gear_items[i],
        size=checkbox_size,
        pad=(10, 5),
        enable_events=False
    ))
    if i + 1 < len(gear_items):
        row.append(sg.Checkbox(
            gear_items[i + 1],
            key=gear_items[i + 1],
            size=checkbox_size,
            pad=(30, 5),
            enable_events=False
        ))
    layout.append(row)

layout.append([
    sg.Push(),
    sg.Button('Run Automation', key='run_automation', size=(15, 1), font=('Segoe UI', 9)),
    sg.Button('Terminate', key='terminate', size=(10, 1), font=('Segoe UI', 9), button_color=('white', 'red')),
])
layout.append([status_text])

window = sg.Window('Grow A Garden Bot', layout, element_padding=(5, 10))

# ==========================
# Event Loop
# ==========================
while True:
    event, values = window.read(timeout=100)

    if event == sg.WIN_CLOSED:
        terminate_flag.set()
        break

    if event == 'select_all':
        for gear in gear_items:
            window[gear].update(True)

    if event == 'run_automation':
        selected_gear = [gear for gear in gear_items if values[gear]]
        if not selected_gear:
            sg.popup_error("Please select at least one gear to purchase.")
            continue
        selected_keys = [get_key_by_value(gear_items_dict, gear) for gear in selected_gear]

        # Disable checkboxes to prevent changes during automation
        for gear in gear_items:
            window[gear].update(disabled=True)
        window['run_automation'].update(disabled=True)
        window['select_all'].update(disabled=True)
        print("🛠️ Running automation:")
        print("Selected gears to purchase:", selected_gear)

        if bot_thread is None or not bot_thread.is_alive():
            window['status'].update('Status: Running', text_color='white', background_color='green')
            bot_thread = threading.Thread(target=run_bot_thread, args=(selected_keys,), daemon=True)
            bot_thread.start()
        else:
            print("⚠️ Automation already running!")

    if event == 'terminate':
        print("🛑 Terminating automation...")
        terminate_flag.set()
        window['status'].update('Status: Terminating...', text_color='white', background_color='red')

    if not is_running and (bot_thread is None or not bot_thread.is_alive()):
        window['status'].update('Status: Idle', text_color='white', background_color='gray')
        # Re-enable checkboxes and buttons
        for gear in gear_items:
            window[gear].update(disabled=False)
        window['run_automation'].update(disabled=False)
        window['select_all'].update(disabled=False)


window.close()
