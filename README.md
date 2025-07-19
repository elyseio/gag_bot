🤖 Grow A Garden Automation Bot

Automates gear purchases and egg buying in Grow A Garden using screen detection, input emulation, and scheduled execution.
Also send Discord notifications for available items.

🚀 Features

Automated gear and egg purchasing using PyAutoGUI + PyDirectInput

Send Discord notifications for available items

Runs every 5 minutes using time-based triggers

Click/image detection retries for robust automation

Console + log file output via logging

Automatic Roblox window focusing with pywinauto (auto alt tab to roblox)

🗂 File Structure
```
project/
├── sc/                         # contains the screen-shotted buttons  
├── automation.py               # Main automation script
├── config.json                 # Contains screen coordinates and image paths
├── automation.log              # Logs automation activity (will show after running once)
├── get_mouse_coordinate.py     # Run to view the coordinates (x, y)
├── requirements.txt            # Dependency list
└── README.md                   # This documentation
```

⚙️ Setup

Run in the terminal (use Git Bash for Windows OS):
```
1. python -m venv .venv
2. source .venv/Scripts/activate
3. pip install -r requirements.txt
4. touch .env
5. inside .env, add:
     DISCORD_HOOK_URL=<your discord webhook url here>
6. python automation.py
```

📸 Screenshots of the button are located under `sc/`

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
requests
python-dotenv
```

🧼 Exiting Safely

Press CTRL+C on the terminal to stop the bot. Log will show total cycles completed.