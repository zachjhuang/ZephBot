# pylint: disable=missing-module-docstring
import os
import time

import pyautogui
import pydirectinput

from modules.utilities import (
    RestartException,
    check_image_on_screen,
    left_click_at_position,
    find_and_click_image,
    find_image_center,
    rand_sleep,
    get_config,
)

SCREEN_CENTER_REGION = (685, 280, 600, 420)
SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)


async def restart_check() -> None:
    """
    Raises restartException in the following cases:

    -   "Cannot connect to server" in-game pop-up.

    -   Server select screen (edge case where previous pop-up is accidentally closed)

    -   GFN session limit reached

    -   GFN inactive (rare case)

    -   General catch-all where black bars from forcing 21:9 on GFN are not detected
        (i.e. GFN closed)

    """
    dc_popup = check_image_on_screen(
        "./image_references/dc.png",
        region=SCREEN_CENTER_REGION,
        confidence=0.9,
    )
    enter_server_button = check_image_on_screen(
        "./image_references/enterServer.png",
        region=(885, 801, 160, 55),
        confidence=0.9,
    )
    if dc_popup or enter_server_button:
        curr_time = int(time.time_ns() / 1000000)
        dc_popup = pyautogui.screenshot()
        dc_popup.save(f"./debug/dc_{curr_time}.png")
        print(f"dc detected...time : {curr_time} dc:{dc_popup} enterServer:{dc_popup}")
        raise RestartException
    if get_config("GFN"):
        for error_type in ["sessionLimitReached", "updateMembership", "inactiveGFN"]:
            error_presence = check_image_on_screen(
                f"./image_references/GFN/{error_type}.png",
                region=SCREEN_CENTER_REGION,
                confidence=0.8,
            )
            if error_presence:
                curr_time = int(time.time_ns() / 1000000)
                limitshot = pyautogui.screenshot()
                limitshot.save(f"./debug/{error_type}_{curr_time}.png")
                await left_click_at_position((1029, 822))
                await rand_sleep(1300, 1400)
                print(error_type)
                raise RestartException
    bottom = pyautogui.screenshot(region=(600, 960, 250, 50))
    r1, g1, b1 = bottom.getpixel((0, 0))
    r2, g2, b2 = bottom.getpixel((0, 49))
    r3, g3, b3 = bottom.getpixel((249, 0))
    r4, g4, b4 = bottom.getpixel((249, 49))
    brightness = r1 + g1 + b1 + r2 + g2 + b2 + r3 + g3 + b3 + r4 + g4 + b4
    if brightness > 50:
        print("game crashed, restarting game client...")
        curr_time = int(time.time_ns() / 1000000)
        crash = pyautogui.screenshot()
        crash.save(f"./debug/crash_{curr_time}.png")
        raise RestartException


async def boot_gfn_session() -> None:
    """
    Boots Lost Ark from the Geforce Now main page.
    """
    while True:
        match find_image_center(
            "./image_references/GFN/loaGFNplay.png",
            confidence=0.8,
        ):
            case x, y:
                await left_click_at_position((x, y))
                print("clicked play restart on GFN")
                await rand_sleep(40000, 42000)
                break
        match find_image_center(
            "./image_references/GFN/loaGFN.png",
            confidence=0.8,
        ):
            case x, y:
                await left_click_at_position((x, y))
                print("clicked image restart on GFN")
                await rand_sleep(40000, 42000)
                break
        match find_image_center(
            "./image_references/GFN/closeGFN.png",
            confidence=0.75,
        ):
            case x, y:
                print("afk GFN")
                await left_click_at_position((x, y))
                await rand_sleep(1300, 1400)
        await rand_sleep(1000, 1100)


async def boot_steam_session() -> None:
    """
    Boots Lost Ark from the Steam Library page.

    WARNING: HAS NOT BEEN UPDATED
    """
    while True:
        os.system("start steam://launch/1599340/dialog")
        await rand_sleep(60000, 60000)
        match find_image_center("./image_references/steamStop.png", confidence=0.75):
            case x, y:
                print("clicking stop game on steam")
                await left_click_at_position((x, y))
                await rand_sleep(500, 600)
        match find_image_center("./image_references/steamConfirm.png", confidence=0.75):
            case x, y:
                print("confirming stop game")
                await left_click_at_position((x, y))
                await rand_sleep(10000, 12000)
        match find_image_center("./image_references/steamPlay.png", confidence=0.75):
            case x, y:
                print("restarting Lost Ark game client...")
                await left_click_at_position((x, y))
                break


async def enter_server() -> None:
    """
    Selects first server and clicks enter.
    """
    while True:
        if check_image_on_screen(
            "./image_references/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        ):
            break

        match find_image_center(
            "./image_references/enterServer.png",
            confidence=0.9,
            region=(885, 801, 160, 55),
        ):
            case x, y:
                print("selecting first server")
                await rand_sleep(1000, 1200)
                await left_click_at_position((855, 582))
                print("entering server")
                await rand_sleep(1000, 1200)
                await left_click_at_position((x, y))
                break
        await rand_sleep(1000, 1100)


async def enter_character() -> None:
    """
    Enters the game on the most recently logged character.
    """
    while True:
        match find_image_center(
            "./image_references/enterCharacter.png",
            confidence=0.75,
            region=(745, 854, 400, 80),
        ):
            case x, y:
                print("clicking enterCharacter")
                await left_click_at_position((x, y))
                break
        await rand_sleep(2200, 3300)


async def restart_game() -> None:
    """
    Reboots the instance from an interrupted state.
    """
    print("restart game")
    # gameCrashCheck()
    await rand_sleep(5000, 7000)
    if get_config("GFN"):
        await boot_gfn_session()
    else:
        await boot_steam_session()
    await enter_server()
    await rand_sleep(5200, 6300)
    await enter_character()
    pydirectinput.moveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
    await rand_sleep(22200, 23300)


async def toggle_menu(menu_name: str) -> None:
    """
    Opens/closes specified menu.
    """
    keys = get_config(menu_name).split(" ")
    if len(keys) == 2:
        pydirectinput.keyDown(keys[0])
        await rand_sleep(300, 400)
        pydirectinput.press(keys[1])
        await rand_sleep(300, 400)
        pydirectinput.keyUp(keys[0])
        await rand_sleep(300, 400)
    elif len(keys) == 1:
        pydirectinput.press(keys[0])
        await rand_sleep(300, 400)


async def wait_for_menu_load(menu: str) -> None:
    """
    Sleeps until menu is detected on screen.

    ~Attempts to open menu again after ~10 seconds.~ (deprecated)

    Times out after ~20 seconds.
    """
    timeout = 0
    while not check_image_on_screen(
        f"./image_references/menus/{menu}Menu.png", confidence=0.85
    ):
        await rand_sleep(180, 220)
        timeout += 1
        # if timeout == 50:
        #     toggleMenu(menu)
        if timeout == 100:
            return


async def wait_overworld_load() -> None:
    """
    Sleeps until channel dropdown arrow is on screen.
    """
    while True:
        await restart_check()
        if check_image_on_screen(
            "./image_references/channelDropdownArrow.png",
            region=(1870, 133, 25, 30),
            confidence=0.75,
        ):
            print("overworld loaded")
            break
        await rand_sleep(1000, 1100)

        if check_image_on_screen(
            "./image_references/inChaos.png",
            region=(247, 146, 222, 50),
            confidence=0.75,
        ):
            print("still in the last chaos run, quitting")
            await quit_dungeon()
            await rand_sleep(4000, 6000)


async def quit_dungeon() -> None:
    """
    Quit chaos dungeon after finishing a run.
    """
    print("quitting chaos")
    await find_and_click_image(
        "chaos/exit", region=CHAOS_LEAVE_MENU_REGION, confidence=0.7
    )
    await rand_sleep(800, 900)
    await find_and_click_image("ok", region=SCREEN_CENTER_REGION, confidence=0.75)
    await rand_sleep(5000, 7000)
    await wait_overworld_load()
    return

async def quit_game() -> None:
    """
    Quit the GFN instance with alt F4.
    """
    print("alt f4")
    pydirectinput.keyDown("alt")
    await rand_sleep(900, 1000)
    pydirectinput.press("f4")
    await rand_sleep(900, 1000)
    pydirectinput.keyUp("alt")
    await rand_sleep(900, 1000)
    pydirectinput.press("enter")
    await rand_sleep(5000, 6000)
