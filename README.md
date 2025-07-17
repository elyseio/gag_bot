🤖 Grow A Garden Automation Bot

Automates gear purchases and egg buying in a Grow A Garden using screen detection, input emulation, and scheduled execution.

🚀 Features

Automated gear and egg purchasing using PyAutoGUI + PyDirectInput

Runs every 5 minutes using time-based triggers

Click/image detection retries for robust automation

Console + log file output via logging

Automatic Roblox window focusing with pywinauto (auto alt tab to roblox)

🗂 File Structure
```
project/
├── automation.py               # Main automation script
├── config.json                 # Contains screen coordinates and image paths
├── automation.log              # Logs automation activity (will show after running once)
├── get_mouse_coordinate.py     # Run to view the coordinates (x, y)
├── requirements.txt            # Dependency list
└── README.md                   # This documentation
```

⚙️ Setup

Run in the terminal:
1. python -m venv .venv
2. source .venv/Scripts/activate
3. pip install -r requirements.txt
4. Configure Coordinates & Images (get the coordinates of gear_shop values based on get_mouse_coordinates.py)
Create a config.json file:
```
{
  "image_paths": {
    "gear": "sc/gear.png",
    "exit": "sc/x.png"
  },
  "gear_items_to_purchase": 8,
  "gear_shop": {
    "item_position": [968, 469],
    "buy_button_position": [774, 664]
  }
}
```

📸 Screenshots of the button are located under sc/

▶️ Running the Bot
`python automation.py`

💡 Tips

Screen resolution and UI layout must match configured positions,
run get_mouse_coordinate.py to view the coordinate of the mouse
based on the buttons.

Avoid changing themes or visual effects that might affect screen detection.

📋 Requirements

List of packages used:
```
pyautogui
pydirectinput
pywinauto
```

🧼 Exiting Safely

Press CTRL+C on the terminal to stop the bot. Log will show total cycles completed.