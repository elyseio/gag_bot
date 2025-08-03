import FreeSimpleGUI as sg
import threading

from items import items
from automation import run_bot

# ==========================
# Globals
# ==========================
gear_items_dict = items["gear"]
gear_items = list(gear_items_dict.values())

egg_items_dict = items["egg"]
egg_items = list(egg_items_dict.values())

terminate_flag = threading.Event()
bot_thread = None
is_running = False


def get_key_by_value(d, value):
    return next((k for k, v in d.items() if v == value), None)

def run_bot_thread(gear_selected_keys, egg_selected_keys):
    global is_running
    terminate_flag.clear()
    is_running = True
    run_bot(gear_selected_keys, egg_selected_keys, terminate_flag)
    is_running = False

def set_ui_enabled(enabled: bool):
    for gear in gear_items:
        window[gear].update(disabled=not enabled)
    for egg in egg_items:
        window[egg].update(disabled=not enabled)
    window['run_automation'].update(disabled=not enabled)
    window['gears_select_all'].update(disabled=not enabled)
    window['eggs_select_all'].update(disabled=not enabled)
    window['terminate'].update(disabled=enabled)

def select_all_checkboxes(items_list, state=True):
    for item in items_list:
        window[item].update(state)



# ==========================
# GUI Setup
# ==========================

status_text = sg.Text('Status: Idle', key='status', font=('Segoe UI', 10), text_color='white', background_color='gray')

layout = [[
    sg.Text('Gears', font=('Segoe UI', 14)),
    sg.Push(),
    sg.Button('Select all gears', key='gears_select_all', size=(15), font=('Segoe UI', 8)),
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
    sg.Text('Eggs', font=('Segoe UI', 14)),
    sg.Push(),
    sg.Button('Select all eggs', key='eggs_select_all', size=(15, 1), font=('Segoe UI', 8)),
])

checkbox_size = (20, 1)

# Create 2-column checkbox layout
for i in range(0, len(egg_items), 2):
    row = []
    row.append(sg.Checkbox(
        egg_items[i],
        key=egg_items[i],
        size=checkbox_size,
        pad=(10, 5),
        enable_events=False
    ))
    if i + 1 < len(egg_items):
        row.append(sg.Checkbox(
            egg_items[i + 1],
            key=egg_items[i + 1],
            size=checkbox_size,
            pad=(30, 5),
            enable_events=False
        ))
    layout.append(row)

layout.append([
    sg.Push(),
    sg.Button('Run Automation', key='run_automation', size=(15, 1), font=('Segoe UI', 9)),
    sg.Button('Terminate', key='terminate', disabled=True, size=(10, 1), font=('Segoe UI', 9), button_color=('white', 'red')),
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

    if event == 'gears_select_all':
        select_all_checkboxes(gear_items, True)

    if event == 'eggs_select_all':
        select_all_checkboxes(egg_items, True)

    if event == 'run_automation':
        selected_gear = [gear for gear in gear_items if values[gear]]
        selected_egg = [egg for egg in egg_items if values[egg]]

        if not selected_egg and not selected_gear:
            sg.popup_error("Please select at least one gear or egg to purchase.")
            continue

        gear_selected_keys = [get_key_by_value(gear_items_dict, gear) for gear in selected_gear]
        egg_selected_keys = [get_key_by_value(egg_items_dict, egg) for egg in selected_egg]

        set_ui_enabled(False)

        print("🛠️ Running automation:")
        print("Selected gears to purchase:", selected_gear)
        print("Selected eggs to purchase:", selected_egg)

        if bot_thread is None or not bot_thread.is_alive():
            window['status'].update('Status: Running', text_color='white', background_color='green')
            bot_thread = threading.Thread(target=run_bot_thread, args=(gear_selected_keys, egg_selected_keys), daemon=True)
            bot_thread.start()  # Uncomment when ready
        else:
            print("⚠️ Automation already running!")

    if event == 'terminate':
        print("🛑 Terminating automation...")
        terminate_flag.set()
        window['status'].update('Status: Terminating...', text_color='white', background_color='red')

    if not is_running and (bot_thread is None or not bot_thread.is_alive()):
        window['status'].update('Status: Idle', text_color='white', background_color='gray')
        set_ui_enabled(True)

window.close()

