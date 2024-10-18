import argparse
import os
import platform
import time

import keyboard
import pydirectinput
import pywintypes
import win32api
import win32con

from modules.botmanager import BotManager
from modules.menuNav import restartGame, waitForOverworldLoaded
from modules.utilities import (
    Position,
    leftClickAtPosition,
    randSleep,
    resetException,
    restartException,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

pydirectinput.PAUSE = 0.05


def abortScript():
    os._exit(1)


def main():
    # set_resolution(1920, 1080)
    keyboard.add_hotkey("ctrl+page down", abortScript)

    # Instantiate the parser
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument(
        "--chaos", action="store_true", help="Enables 2x chaos on entire roster"
    )
    parser.add_argument(
        "--kurzanfront",
        action="store_true",
        help="Enables Kurzan Front on entire roster",
    )
    parser.add_argument(
        "--unas", action="store_true", help="Enables unas on entire roster"
    )
    parser.add_argument(
        "--guild",
        action="store_true",
        help="Enables guild donation/support on entire roster",
    )
    # parser.add_argument("--cubes", action="store_true", help="testing cubes")
    parser.add_argument("--delay", type=int, help="Delay start of program in seconds")
    args = parser.parse_args()

    if args.delay is not None:
        print(f"randSleeping for {args.delay} seconds")
        randSleep(args.delay * 1000, (args.delay + 1) * 1000)

    print(f"script starting at {time.asctime(time.localtime())}")
    startTime = time.time()

    leftClickAtPosition(SCREEN_CENTER_POS)

    botManager = BotManager(
        doChaos=args.chaos,
        doKurzanFront=args.kurzanfront,
        doUnas=args.unas,
        doGuild=args.guild,
    )

    # stay invis in friends list
    # if config["invisible"] == True:
    #     goInvisible()

    # save bot start time
    # states["botStartTime"] = int(time.time_ns() / 1000000)
    while True:
        try:
            botManager.run()
            print(f"script finished at {time.asctime(time.localtime())}")
            runtime = time.time() - startTime
            h, rem = divmod(runtime, 3600)
            m, s = divmod(rem, 60)
            print(f"time elapsed: {int(h)}h {int(m)}m {int(s)}s")
            break
        except restartException:
            randSleep(10000, 12200)
            restartGame()
            waitForOverworldLoaded()
        except resetException:
            botManager = BotManager(args.chaos, args.unas, args.guild)


# def saveAbilitiesScreenshots() -> None:
#     for ability in abilities[config["characters"][states["currentCharacter"]]["class"]]:
#         if ability["abilityType"] not in ["specialty1", "specialty2"]:
#             ability.update({"image": pyautogui.screenshot(region=ability["position"])})
#             randSleep(100, 150)


# def cleanInventory():
#     toggleMenu("pet")
#     pydirectinput.click(1143, 630, button="left")  # pet
#     randSleep(3000, 3000)
#     pydirectinput.click(560, 765, button="left")  # roster deposit
#     randSleep(1500, 1600)
#     pydirectinput.click(560, 765, button="left")  # roster deposit
#     randSleep(1500, 1600)
#     pydirectinput.click(880, 765, button="left")  # character deposit
#     randSleep(1500, 1600)
#     pydirectinput.click(880, 765, button="left")  # character deposit
#     randSleep(1500, 1600)

#     for _ in range(2):
#         pydirectinput.press("esc")
#         randSleep(100, 200)


def set_resolution(width: int, height: int):
    if platform.system() == "Windows":
        # adapted from [Win | dP] Dragonback
        # adapted from Peter Wood: https://stackoverflow.com/a/54262365
        devmode = pywintypes.DEVMODEType()
        devmode.PelsWidth = width
        devmode.PelsHeight = height
        devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

        win32api.ChangeDisplaySettings(devmode, 0)


if __name__ == "__main__":
    main()
