from config import config

from utilities import restartException
from utilities import randSleep
from utilities import mouseMoveTo
from utilities import checkImageOnScreen
import time
import pydirectinput
import pyautogui

SCREEN_CENTER_REGION = (685, 280, 600, 420)


def restartCheck() -> None:
    """
    Raises restartException in the following cases:

    -   "Cannot connect to server" in-game pop-up.

    -   Server select screen (edge case where previous pop-up is accidentally closed)

    -   GFN session limit reached

    -   GFN inactive (rare case)

    -   General catch-all where black bars from forcing 21:9 on GFN are not detected (i.e. GFN closed)

    """
    dc = checkImageOnScreen(
        "./screenshots/dc.png",
        region=SCREEN_CENTER_REGION,
        confidence=config["confidenceForGFN"],
    )
    enterServer = checkImageOnScreen(
        "./screenshots/enterServer.png",
        region=(885, 801, 160, 55),
        confidence=config["confidenceForGFN"],
    )
    if dc or enterServer:
        currentTime = int(time.time_ns() / 1000000)
        dc = pyautogui.screenshot()
        dc.save(f"./debug/dc_{currentTime}.png")
        print(f"dc detected...time : {currentTime} dc:{dc} enterServer:{dc}")
        raise restartException
    if config["GFN"] == True:
        for errorType in ['sessionLimitReached', 'updateMembership', 'inactiveGFN']:
            errorPresence = checkImageOnScreen(
                f"./screenshots/GFN/{errorType}.png",
                region=SCREEN_CENTER_REGION,
                confidence=0.8,
            )
            if errorPresence:
                currentTime = int(time.time_ns() / 1000000)
                limitshot = pyautogui.screenshot()
                limitshot.save(f"./debug/{errorType}_{currentTime}.png")
                mouseMoveTo(x=1029, y=822)
                randSleep(1300, 1400)
                pydirectinput.click(button='left')
                randSleep(1300, 1400)
                print(errorType)
                raise restartException
    bottom = pyautogui.screenshot(region=(600, 960, 250, 50))
    r1, g1, b1 = bottom.getpixel((0, 0))
    r2, g2, b2 = bottom.getpixel((0, 49))
    r3, g3, b3 = bottom.getpixel((249, 0))
    r4, g4, b4 = bottom.getpixel((249, 49))
    sum = r1 + g1 + b1 + r2 + g2 + b2 + r3 + g3 + b3 + r4 + g4 + b4
    if sum > 50:
        print("game crashed, restarting game client...")
        currentTime = int(time.time_ns() / 1000000)
        crash = pyautogui.screenshot()
        crash.save(f"./debug/crash_{currentTime}.png")
        raise restartException


def toggleMenu(menuType: str) -> None:
    """
    Opens/closes specified menu.
    """
    keys = config[menuType].split(" ")
    if len(keys) == 2:
        pydirectinput.keyDown(keys[0])
        randSleep(300, 400)
        pydirectinput.press(keys[1])
        randSleep(300, 400)
        pydirectinput.keyUp(keys[0])
        randSleep(300, 400)
    elif len(keys) == 1:
        pydirectinput.press(keys[0])
        randSleep(300, 400)


def waitForMenuLoaded(menu: str) -> None:
    """
    randSleeps until menu is detected on screen.

    Attempts to open menu again after ~10 seconds.

    Times out after ~20 seconds.
    """
    timeout = 0
    while not checkImageOnScreen(
        "./screenshots/menus/" + menu + "Menu.png", confidence=0.85
    ):
        randSleep(180, 220)
        timeout += 1
        if timeout == 50:
            toggleMenu(menu)
        if timeout == 100:
            return


def waitForOverworldLoaded() -> None:
    """randSleeps until channel dropdown arrow is on screen. Changes status to 'overworld'."""
    while True:
        restartCheck()
        channelDropdownArrow = checkImageOnScreen(
            "./screenshots/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if channelDropdownArrow:
            print("overworld loaded")
            break
        randSleep(1000, 1100)
