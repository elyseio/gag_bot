import pyautogui
import time

time.sleep(3)

try:
    while True:
        x, y = pyautogui.position()
        print(x, y)
except KeyboardInterrupt:
    print()