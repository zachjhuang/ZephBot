import random
import time
from datetime import datetime

import pyautogui
import pydirectinput

from configs.config import config
from modules.dungeon_bot import (
    DungeonBot,
    cast_ability,
    do_aura_repair,
    move_in_direction,
    random_move,
    wait_dungeon_load,
)
from modules.menu_nav import quit_chaos, restart_check, toggle_menu, wait_for_menu_load
from modules.minimap import Minimap
from modules.utilities import (
    Position,
    ResetException,
    TimeoutException,
    check_image_on_screen,
    find_and_click_image,
    find_image_center,
    left_click_at_position,
    mouse_move_to,
    random_sleep,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

PORTAL_REGION = (228, 230, 1370, 570)
LEAVE_MENU_REGION = (0, 154, 250, 300)

PUNIKA_CHAOS_TAB_POS = Position(1020, 307)
SOUTH_VERN_CHAOS_TAB_POS = Position(1160, 307)
ELGACIA_CHAOS_TAB_POS = Position(1300, 307)
VOLDIS_CHAOS_TAB_POS = Position(1440, 307)

LEVEL_1_CHAOS_POS = Position(624, 405)
LEVEL_2_CHAOS_POS = Position(624, 457)
LEVEL_3_CHAOS_POS = Position(624, 509)
LEVEL_4_CHAOS_POS = Position(624, 561)
LEVEL_5_CHAOS_POS = Position(624, 613)
LEVEL_6_CHAOS_POS = Position(624, 665)
LEVEL_7_CHAOS_POS = Position(624, 717)
LEVEL_8_CHAOS_POS = Position(624, 769)

CHAOS_TAB_POSITION = {
    1100: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1310: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
    1325: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_3_CHAOS_POS},
    1340: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_4_CHAOS_POS},
    1355: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_5_CHAOS_POS},
    1370: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_6_CHAOS_POS},
    1385: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_7_CHAOS_POS},
    1400: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_8_CHAOS_POS},
    1415: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1445: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
    1475: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_3_CHAOS_POS},
    1490: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_4_CHAOS_POS},
    1520: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_5_CHAOS_POS},
    1540: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_6_CHAOS_POS},
    1560: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_7_CHAOS_POS},
    1580: {"tabPos": ELGACIA_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1600: {"tabPos": ELGACIA_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
    1610: {"tabPos": VOLDIS_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1630: {"tabPos": VOLDIS_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
}


class ChaosBot(DungeonBot):
    def __init__(self, roster):
        super().__init__(roster)
        self.remaining_tasks = [
            (
                2
                if char["chaosItemLevel"] is not None and char["chaosItemLevel"] <= 1610
                else 0
            )
            for char in self.roster
        ]

    def do_tasks(self) -> None:
        if self.done_on_curr_char():
            return

        toggle_menu("defaultCombatPreset")

        enter_chaos(self.roster[self.curr]["chaosItemLevel"])

        while self.remaining_tasks[self.curr] > 0:
            try:
                self.run_start_time = int(time.time())
                self.do_chaos_floor(1)
                self.do_chaos_floor(2)
                self.do_chaos_floor(3)
                end_time = int(time.time())
                self.update_print_metrics(end_time - self.run_start_time)
            except TimeoutException:
                quit_chaos()
                enter_chaos(self.roster[self.curr]["chaosItemLevel"])
            self.remaining_tasks[self.curr] -= 1
            if self.remaining_tasks[self.curr] > 0:
                reenter_chaos()
            # if datetime.now().hour == config["resetHour"] and not self.resetOnce:
            #     self.resetOnce = True
            #     quit_chaos()
            #     raise ResetException
        quit_chaos()

    def do_chaos_floor(self, n: int) -> None:
        wait_dungeon_load()
        print(f"floor {n} loaded")

        if config["auraRepair"]:
            do_aura_repair(False)

        left_click_at_position(SCREEN_CENTER_POS)
        random_sleep(1500, 1600)

        self.use_skills(n)
        print(f"floor {n} cleared")

        restart_check()
        self.timeout_check()

    def use_skills(self, floor) -> None:
        """
        Moves character and uses skills. Behavior changes depending on the floor.
        """
        minimap = Minimap()
        curr_class = self.roster[self.curr]["class"]
        char_skills = self.skills[curr_class]
        normal_skills = [
            skill for skill in char_skills if skill["skillType"] == "normal"
        ]
        awakening_skill = [
            skill for skill in char_skills if skill["skillType"] == "awakening"
        ][0]
        awakening_used = False
        while True:
            self.died_check()
            self.health_check()
            restart_check()
            self.timeout_check()

            x, y, move_duration = minimap.get_game_coords()

            if floor == 1 and not awakening_used:
                awakening_used = True
                cast_ability(x, y, awakening_skill)

            # check for accident
            if floor == 1 and minimap.check_elite():
                print("accidentally entered floor 2")
                return
            elif floor == 2 and minimap.check_rift_core():
                print("accidentally entered floor 3")
                return

            if floor == 1 and not minimap.check_mob():
                print("no floor 1 mob detected, random move")
                random_move()
            elif floor == 2 and not minimap.check_elite() and not minimap.check_mob():
                print("no floor 2 elite/mob detected, random move")
                random_move()
            elif floor == 3 and minimap.check_elite():
                x, y, move_duration = minimap.get_game_coords(
                    target_found=True, pathfind=True
                )
                move_in_direction(x, y, move_duration)
            elif (
                floor == 3
                and not minimap.check_rift_core()
                and not minimap.check_elite()
                and not minimap.check_mob()
            ):
                random_move()

            # cast sequence
            for i in range(0, len(normal_skills)):
                if floor == 3 and check_chaos_finish():
                    print("chaos finish screen")
                    return
                self.died_check()
                self.health_check()

                if (floor == 1 or floor == 2) and minimap.check_portal():
                    pydirectinput.click(
                        x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y, button=config["move"]
                    )
                    random_sleep(100, 150)
                    while True:
                        minimap.check_portal()
                        x, y, move_duration = minimap.get_game_coords(target_found=True)
                        if self.enter_portal(x, y, int(move_duration / 3)):
                            break
                        self.timeout_check()
                    return

                # click rift core
                if floor == 3:
                    click_rift_core()

                # check high-priority mobs
                match floor:
                    case 1:
                        x, y, move_duration = minimap.get_game_coords(
                            target_found=minimap.check_mob()
                        )
                    case 2:
                        x, y, move_duration = minimap.get_game_coords(
                            target_found=(
                                minimap.check_boss()
                                or minimap.check_elite()
                                or minimap.check_mob()
                            )
                        )
                        move_in_direction(x, y, int(move_duration / 5))
                        if minimap.check_boss() or checkBossBar() and not awakening_used:
                            cast_ability(x, y, awakening_skill)
                            awakening_used = True
                    case 3:
                        x, y, move_duration = minimap.get_game_coords(
                            target_found=(
                                minimap.check_rift_core()
                                or minimap.check_elite()
                                or minimap.check_mob()
                            ),
                            pathfind=True,
                        )
                        move_in_direction(x, y, int(move_duration / 2))
                        # if not minimap.checkElite() and not minimap.checkMob():
                        #     minimap.checkRiftCore()
                        #     newX, newY, _ = minimap.getGameCoords()
                        #     if (
                        #         newX - 30 < x < newX + 30
                        #         and newY - 20 < y < newY + 20
                        #     ):
                        #         randomMove()

                self.perform_class_specialty(
                    self.roster[self.curr]["class"], i, normal_skills
                )
                cast_ability(x, y, normal_skills[i])

    def enter_portal(self, x: int, y: int, moveDuration: int) -> bool:
        """
        Moves to (x, y) over moveDuration milliseconds while pressing interact.

        Returns true if black loading screen reached from interacting with portal within time limit, false otherwise.
        """
        if moveDuration > 550:
            pydirectinput.click(x=x, y=y, button=config["move"])
            random_sleep(100, 150)
            if self.roster[self.curr]["class"] != "gunlancer":
                pydirectinput.press(config["blink"])

        for _ in range(10):
            # try to enter portal until black screen
            im = pyautogui.screenshot(region=(1652, 168, 240, 210))
            r, g, b = im.getpixel((1772 - 1652, 272 - 168))
            if r + g + b < 30:
                mouse_move_to(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                return True
            pydirectinput.press(config["interact"])
            random_sleep(100, 120)
            pydirectinput.click(x=x, y=y, button=config["move"])
            random_sleep(60, 70)
        pydirectinput.press(self.skills[self.roster[self.curr]["class"]][0])
        random_sleep(100, 150)
        pydirectinput.press(config["meleeAttack"])
        random_sleep(100, 150)
        return False


def enter_chaos(ilvl: int) -> None:
    """
    Enters specified chaos dungeon level.
    """
    toggle_menu("content")
    wait_for_menu_load("content")

    elementPos = find_image_center(
        "./screenshots/menus/chaosDungeonContentMenuElement.png", confidence=0.9
    )
    if elementPos is not None:
        x, y = elementPos
        left_click_at_position(Position(x + 300, y + 30))  # shortcut button
    else:
        left_click_at_position(Position(786, 315))  # edge case different UI
    random_sleep(800, 900)
    wait_for_menu_load("chaosDungeon")
    isCorrectChaosDungeon = check_image_on_screen(
        f"./screenshots/chaos/ilvls/{ilvl}.png",
        region=(1255, 380, 80, 50),
        confidence=0.95,
    )
    if not isCorrectChaosDungeon:
        print("not correct")
        select_chaos_dungeon(ilvl)

    find_and_click_image("weeklyPurificationClaimAll", confidence=0.90)
    random_sleep(500, 600)
    left_click_at_position(Position(920, 575))  # accept button
    random_sleep(500, 600)

    find_and_click_image("enterButton", confidence=0.75)
    random_sleep(800, 900)
    find_and_click_image("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(800, 900)


def select_chaos_dungeon(ilvl: int) -> None:
    """
    With chaos dungeon menu open, select chaos dungeon level corresponding to item level.
    """
    chaos_menu_right_arrow = find_image_center(
        f"./screenshots/chaosMenuRightArrow.png", confidence=0.95
    )
    if chaos_menu_right_arrow is not None:
        x, y = chaos_menu_right_arrow
        mouse_move_to(x=x, y=y)
        random_sleep(200, 250)
        pydirectinput.click(button="left")
        random_sleep(200, 250)

    left_click_at_position(CHAOS_TAB_POSITION[ilvl]["tabPos"])
    random_sleep(1000, 1100)
    left_click_at_position(CHAOS_TAB_POSITION[ilvl]["levelPos"])
    random_sleep(1000, 1100)


def click_rift_core() -> None:
    """
    Uses basic attacks if rift core label on screen.
    """
    for i in [1, 2]:
        rift_core = find_image_center(
            f"./screenshots/chaos/riftcore{i}.png",
            confidence=0.6,
            region=PORTAL_REGION,
        )
        if rift_core is not None:
            x, y = rift_core
            if y > 650 or x < 400 or x > 1500:
                return
            pydirectinput.click(x=x, y=y + 190, button=config["move"])
            random_sleep(100, 120)
            for _ in range(4):
                pydirectinput.press(config["meleeAttack"])
                random_sleep(300, 360)


def check_chaos_finish() -> bool:
    """
    Returns true if chaos finish screen detected and clears the finish overlay. Otherwise returns false.
    """
    clear_ok = find_image_center(
        "./screenshots/chaos/clearOk.png", confidence=0.75, region=(625, 779, 500, 155)
    )
    if clear_ok is not None:
        x, y = clear_ok
        mouse_move_to(x=x, y=y)
        random_sleep(800, 900)
        pydirectinput.click(x=x, y=y, button="left")
        random_sleep(200, 300)
        pydirectinput.click(x=x, y=y, button="left")
        random_sleep(200, 300)
    return clear_ok is not None


def reenter_chaos() -> None:
    """
    Start new chaos dungeon after finishing.
    """
    print("reentering chaos")
    random_sleep(1200, 1400)
    find_and_click_image(
        "chaos/selectLevel", region=LEAVE_MENU_REGION, confidence=0.7
    )
    random_sleep(500, 600)
    find_and_click_image("enterButton", region=(1380, 760, 210, 60), confidence=0.75)
    random_sleep(800, 900)
    find_and_click_image("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(2000, 3200)
    return


def checkBossBar() -> bool:
    return check_image_on_screen(
        "./screenshots/chaos/bossBar.png",
        region=(406, 159, 1000, 200),
        confidence=0.8,
    )
