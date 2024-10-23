from configs.config import config

from modules.utilities import RestartException
from modules.utilities import random_sleep
from modules.utilities import mouse_move_to
from modules.utilities import (
    check_image_on_screen,
    find_image_center,
    find_and_click_image,
)

import os
import time
import pydirectinput
import pyautogui

SCREEN_CENTER_REGION = (685, 280, 600, 420)
SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)


def restart_check() -> None:
    """
    Raises restartException in the following cases:

    -   "Cannot connect to server" in-game pop-up.

    -   Server select screen (edge case where previous pop-up is accidentally closed)

    -   GFN session limit reached

    -   GFN inactive (rare case)

    -   General catch-all where black bars from forcing 21:9 on GFN are not detected (i.e. GFN closed)

    """
    dc = check_image_on_screen(
        "./screenshots/dc.png",
        region=SCREEN_CENTER_REGION,
        confidence=0.9,
    )
    enter_server = check_image_on_screen(
        "./screenshots/enterServer.png",
        region=(885, 801, 160, 55),
        confidence=0.9,
    )
    if dc or enter_server:
        curr_time = int(time.time_ns() / 1000000)
        dc = pyautogui.screenshot()
        dc.save(f"./debug/dc_{curr_time}.png")
        print(f"dc detected...time : {curr_time} dc:{dc} enterServer:{dc}")
        raise RestartException
    if config["GFN"] == True:
        for error_type in ["sessionLimitReached", "updateMembership", "inactiveGFN"]:
            error_presence = check_image_on_screen(
                f"./screenshots/GFN/{error_type}.png",
                region=SCREEN_CENTER_REGION,
                confidence=0.8,
            )
            if error_presence:
                curr_time = int(time.time_ns() / 1000000)
                limitshot = pyautogui.screenshot()
                limitshot.save(f"./debug/{error_type}_{curr_time}.png")
                mouse_move_to(x=1029, y=822)
                random_sleep(1300, 1400)
                pydirectinput.click(button="left")
                random_sleep(1300, 1400)
                print(error_type)
                raise RestartException
    bottom = pyautogui.screenshot(region=(600, 960, 250, 50))
    r1, g1, b1 = bottom.getpixel((0, 0))
    r2, g2, b2 = bottom.getpixel((0, 49))
    r3, g3, b3 = bottom.getpixel((249, 0))
    r4, g4, b4 = bottom.getpixel((249, 49))
    sum = r1 + g1 + b1 + r2 + g2 + b2 + r3 + g3 + b3 + r4 + g4 + b4
    if sum > 50:
        print("game crashed, restarting game client...")
        curr_time = int(time.time_ns() / 1000000)
        crash = pyautogui.screenshot()
        crash.save(f"./debug/crash_{curr_time}.png")
        raise RestartException


def boot_gfn_session() -> None:
    """
    Boots Lost Ark from the Geforce Now main page.
    """
    while True:
        match find_image_center(
            "./screenshots/GFN/loaGFNplay.png",
            confidence=0.8,
        ):
            case x, y:
                mouse_move_to(x=x, y=y)
                random_sleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked play restart on GFN")
                random_sleep(40000, 42000)
                break
        match find_image_center(
            "./screenshots/GFN/loaGFN.png",
            confidence=0.8,
        ):
            case x, y:
                mouse_move_to(x=x, y=y)
                random_sleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked image restart on GFN")
                random_sleep(40000, 42000)
                break
        match find_image_center(
            "./screenshots/GFN/closeGFN.png",
            confidence=0.75,
        ):
            case x, y:
                print("afk GFN")
                mouse_move_to(x=x, y=y)
                random_sleep(1300, 1400)
                pydirectinput.click(button="left")
                random_sleep(1300, 1400)
        random_sleep(1000, 1100)


def boot_steam_session() -> None:
    """
    Boots Lost Ark from the Steam Library page.

    WARNING: HAS NOT BEEN UPDATED
    """
    while True:
        os.system("start steam://launch/1599340/dialog")
        random_sleep(60000, 60000)
        match find_image_center("./screenshots/steamStop.png", confidence=0.75):
            case x, y:
                print("clicking stop game on steam")
                mouse_move_to(x=x, y=y)
                random_sleep(1200, 1300)
                pydirectinput.click(button="left")
                random_sleep(500, 600)
        match find_image_center("./screenshots/steamConfirm.png", confidence=0.75):
            case x, y:
                print("confirming stop game")
                mouse_move_to(x=x, y=y)
                random_sleep(1200, 1300)
                pydirectinput.click(button="left")
                random_sleep(10000, 12000)
        match find_image_center("./screenshots/steamPlay.png", confidence=0.75):
            case x, y:
                print("restarting Lost Ark game client...")
                mouse_move_to(x=x, y=y)
                random_sleep(1200, 1300)
                pydirectinput.click(button="left")
                break


def enter_server() -> None:
    """
    Selects first server and clicks enter.
    """
    while True:
        if check_image_on_screen(
            "./screenshots/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        ):
            break

        match find_image_center(
            "./screenshots/enterServer.png",
            confidence=0.9,
            region=(885, 801, 160, 55),
        ):
            case x, y:
                print("selecting first server")
                random_sleep(1000, 1200)
                mouse_move_to(x=855, y=582)
                random_sleep(1200, 1300)
                pydirectinput.click(button="left")
                print("entering server")
                random_sleep(1000, 1200)
                mouse_move_to(x=x, y=y)
                random_sleep(1200, 1300)
                pydirectinput.click(button="left")
                break
        random_sleep(1000, 1100)


def enter_character() -> None:
    """
    Enters the game on the most recently logged character.
    """
    while True:
        match find_image_center(
            "./screenshots/enterCharacter.png",
            confidence=0.75,
            region=(745, 854, 400, 80),
        ):
            case x, y:
                print("clicking enterCharacter")
                mouse_move_to(x=x, y=y)
                random_sleep(200, 300)
                pydirectinput.click(button="left")
                break
        random_sleep(2200, 3300)


def restart_game() -> None:
    print("restart game")
    # gameCrashCheck()
    random_sleep(5000, 7000)
    if config["GFN"]:
        boot_gfn_session()
    else:
        boot_steam_session()
    enter_server()
    random_sleep(5200, 6300)
    enter_character()
    mouse_move_to(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
    random_sleep(22200, 23300)


def toggle_menu(menuType: str) -> None:
    """
    Opens/closes specified menu.
    """
    keys = config[menuType].split(" ")
    if len(keys) == 2:
        pydirectinput.keyDown(keys[0])
        random_sleep(300, 400)
        pydirectinput.press(keys[1])
        random_sleep(300, 400)
        pydirectinput.keyUp(keys[0])
        random_sleep(300, 400)
    elif len(keys) == 1:
        pydirectinput.press(keys[0])
        random_sleep(300, 400)


def wait_for_menu_load(menu: str) -> None:
    """
    Sleeps until menu is detected on screen.

    ~Attempts to open menu again after ~10 seconds.~ (deprecated)

    Times out after ~20 seconds.
    """
    timeout = 0
    while not check_image_on_screen(
        f"./screenshots/menus/{menu}Menu.png", confidence=0.85
    ):
        random_sleep(180, 220)
        timeout += 1
        # if timeout == 50:
        #     toggleMenu(menu)
        if timeout == 100:
            return


def wait_overworld_load() -> None:
    """
    Sleeps until channel dropdown arrow is on screen.
    """
    while True:
        restart_check()
        if check_image_on_screen(
            "./screenshots/channelDropdownArrow.png",
            region=(1870, 133, 25, 30),
            confidence=0.75,
        ):
            print("overworld loaded")
            break
        random_sleep(1000, 1100)

        if check_image_on_screen(
            "./screenshots/inChaos.png", region=(247, 146, 222, 50), confidence=0.75
        ):
            print("still in the last chaos run, quitting")
            quit_chaos()
            random_sleep(4000, 6000)


def quit_chaos() -> None:
    """
    Quit chaos dungeon after finishing a run.
    """
    print("quitting chaos")
    find_and_click_image("chaos/exit", region=CHAOS_LEAVE_MENU_REGION, confidence=0.7)
    random_sleep(800, 900)
    find_and_click_image("ok", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(5000, 7000)
    wait_overworld_load()
    return
