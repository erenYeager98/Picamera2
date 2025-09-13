import pyautogui
import time

time.sleep(2)  # 2 sec delay so you can focus the right window

# Search for image on screen
location = pyautogui.locateOnScreen("button.png", confidence=0.8)

if location:
    center = pyautogui.center(location)  # get center of the found area
    pyautogui.moveTo(center)
    pyautogui.click()
    print("Clicked on image at:", center)
else:
    print("Image not found on screen!")
