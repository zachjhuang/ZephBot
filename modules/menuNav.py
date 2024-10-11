from configs.config import config

from .utilities import restartException
from .utilities import randSleep
from .utilities import mouseMoveTo
from .utilities import checkImageOnScreen, findImageCenter, findAndClickImage

import os
import time
import pydirectinput
import pyautogui

SCREEN_CENTER_REGION = (685, 280, 600, 420)
SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)


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
        confidence=0.9,
    )
    enterServer = checkImageOnScreen(
        "./screenshots/enterServer.png",
        region=(885, 801, 160, 55),
        confidence=0.9,
    )
    if dc or enterServer:
        currentTime = int(time.time_ns() / 1000000)
        dc = pyautogui.screenshot()
        dc.save(f"./debug/dc_{currentTime}.png")
        print(f"dc detected...time : {currentTime} dc:{dc} enterServer:{dc}")
        raise restartException
    if config["GFN"] == True:
        for errorType in ["sessionLimitReached", "updateMembership", "inactiveGFN"]:
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
                pydirectinput.click(button="left")
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

def restartGame() -> None:
    print("restart game")
    # gameCrashCheck()
    randSleep(5000, 7000)
    while True:
        if config["GFN"] == True:
            randSleep(10000, 12000)
            loaGFN = findImageCenter(
                "./screenshots/GFN/loaGFN.png",
                confidence=0.8,
            )
            loaGFNplay = findImageCenter(
                "./screenshots/GFN/loaGFNplay.png",
                confidence=0.8,
            )
            if loaGFNplay is not None:
                x, y = loaGFNplay
                mouseMoveTo(x=x, y=y)
                randSleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked play restart on GFN")
                randSleep(40000, 42000)
                break
            if loaGFN is not None:
                x, y = loaGFN
                mouseMoveTo(x=x, y=y)
                randSleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked image restart on GFN")
                randSleep(40000, 42000)
                break
            # afkGFN = findImageCenter(
            #     "./screenshots/GFN/afkGFN.png",
            #     region=SCREEN_CENTER_REGION,
            #     confidence=0.75,
            # )
            closeGFN = checkImageOnScreen(
                "./screenshots/GFN/closeGFN.png",
                confidence=0.75,
            )
            if closeGFN:
                print("afk GFN")
                x, y = closeGFN
                mouseMoveTo(x=x, y=y)
                randSleep(1300, 1400)
                pydirectinput.click(button="left")
                randSleep(1300, 1400)
                continue
        else:
            os.system("start steam://launch/1599340/dialog")
            randSleep(60000, 60000)
        enterGame = findImageCenter("./screenshots/steamPlay.png", confidence=0.75)
        randSleep(500, 600)
        stopGame = findImageCenter("./screenshots/steamStop.png", confidence=0.75)
        randSleep(500, 600)
        confirm = findImageCenter("./screenshots/steamConfirm.png", confidence=0.75)
        randSleep(500, 600)
        enterServer = checkImageOnScreen(
            "./screenshots/enterServer.png",
            confidence=0.9,
            region=(885, 801, 160, 55),
        )
        randSleep(500, 600)
        channelDropdownArrow = checkImageOnScreen(
            "./screenshots/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if stopGame is not None:
            print("clicking stop game on steam")
            x, y = stopGame
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(500, 600)
            confirm = findImageCenter("./screenshots/steamConfirm.png", confidence=0.75)
            if confirm is None:
                continue
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(10000, 12000)
        elif confirm is not None:
            print("confirming stop game")
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(10000, 12000)
        elif enterGame is not None:
            print("restarting Lost Ark game client...")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            break
        elif enterServer:
            break
        elif channelDropdownArrow:
            return
        randSleep(1200, 1300)
    randSleep(5200, 6300)
    while True:
        enterServer = checkImageOnScreen(
            "./screenshots/enterServer.png",
            confidence=0.9,
            region=(885, 801, 160, 55),
        )
        enterGame = checkImageOnScreen("./screenshots/steamPlay.png", confidence=0.75)
        if enterServer:
            print("clicking enterServer")
            randSleep(1000, 1200)
            # click first server
            mouseMoveTo(x=855, y=582)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(1000, 1200)
            x, y = enterServer
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            break
        elif enterGame:
            print("clicking enterGame")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            randSleep(200, 300)
            pydirectinput.click(button="left")
            randSleep(4200, 5300)
            continue
    randSleep(3200, 4300)
    while True:
        enterCharacter = checkImageOnScreen(
            "./screenshots/enterCharacter.png",
            confidence=0.75,
            region=(745, 854, 400, 80),
        )
        if enterCharacter:
            print("clicking enterCharacter")
            x, y = enterCharacter
            mouseMoveTo(x=x, y=y)
            randSleep(200, 300)
            pydirectinput.click(button="left")
            break
        randSleep(2200, 3300)
    # states["gameRestartCount"] = states["gameRestartCount"] + 1
    mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
    randSleep(22200, 23300)

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
        f"./screenshots/menus/{menu}Menu.png", confidence=0.85
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
            region=(1870, 133, 25, 30),
            confidence=0.75,
        )
        if channelDropdownArrow:
            print("overworld loaded")
            break
        randSleep(1000, 1100)

        inChaos = checkImageOnScreen(
            "./screenshots/inChaos.png", region=(247, 146, 222, 50), confidence=0.75
        )
        if inChaos:
            print("still in the last chaos run, quitting")
            quitChaos()
            randSleep(4000, 6000)


def quitChaos() -> None:
    """
    Quit chaos dungeon after finishing a run.
    """
    print("quitting chaos")
    findAndClickImage("chaos/leave", region=CHAOS_LEAVE_MENU_REGION, confidence=0.7)
    randSleep(800, 900)
    findAndClickImage("ok", region=SCREEN_CENTER_REGION, confidence=0.75)
    randSleep(5000, 7000)
    waitForOverworldLoaded()
    return