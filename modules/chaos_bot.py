import time
from datetime import datetime

import pyautogui
import pydirectinput

from configs.config import config
from modules.dungeon_bot import (
    DungeonBot,
    cast_ability,
    perform_class_specialty,
    do_aura_repair,
    move_in_direction,
    random_move,
    wait_dungeon_load,
)
from modules.menu_nav import quit_chaos, restart_check, toggle_menu, wait_for_menu_load
from modules.minimap import Minimap
from modules.utilities import (
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

SCREEN_CENTER_POS = (960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

PORTAL_REGION = (228, 230, 1370, 570)
LEAVE_MENU_REGION = (0, 154, 250, 300)

PUNIKA_CHAOS_TAB_POS = (1020, 307)
SOUTH_VERN_CHAOS_TAB_POS = (1160, 307)
ELGACIA_CHAOS_TAB_POS = (1300, 307)
VOLDIS_CHAOS_TAB_POS = (1440, 307)

LEVEL_1_CHAOS_POS = (624, 405)
LEVEL_2_CHAOS_POS = (624, 457)
LEVEL_3_CHAOS_POS = (624, 509)
LEVEL_4_CHAOS_POS = (624, 561)
LEVEL_5_CHAOS_POS = (624, 613)
LEVEL_6_CHAOS_POS = (624, 665)
LEVEL_7_CHAOS_POS = (624, 717)
LEVEL_8_CHAOS_POS = (624, 769)

CHAOS_TAB_POSITION = {
    1100: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1295: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
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
        self.remaining_tasks: list[int] = [
            (
                2
                if char["chaosItemLevel"] is not None and char["chaosItemLevel"] <= 1610
                else 0
            )
            for char in self.roster
        ]
        self.minimap: Minimap = Minimap()

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

    def do_chaos_floor(self, floor: int) -> None:
        """
        Completes one floor of chaos dungeon.

        Args:
            floor: The specific floor of chaos to complete.
        """
        wait_dungeon_load()
        print(f"floor {floor} loaded")

        if config["auraRepair"]:
            do_aura_repair(False)

        left_click_at_position(SCREEN_CENTER_POS)
        random_sleep(1500, 1600)

        self.use_skills(floor)
        print(f"floor {floor} cleared")

        restart_check()
        self.timeout_check()

    def use_skills(self, floor) -> None:
        """
        Moves character and uses skills. Behavior changes depending on the floor.

        Args:
            floor: The floor that skills are being used on.
        """
        self.minimap = Minimap()
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

            x, y, move_duration = self.minimap.get_game_coords()

            if self.check_accidental_portal_enter(floor):
                return

            if floor == 1 and not self.minimap.check_mob():
                print("no floor 1 mob detected, random move")
                random_move()
            elif (
                floor == 2
                and not self.minimap.check_elite()
                and not self.minimap.check_mob()
            ):
                print("no floor 2 elite/mob detected, random move")
                random_move()
            elif (
                floor == 3
                and not self.minimap.check_rift_core()
                and not self.minimap.check_elite()
                and not self.minimap.check_mob()
            ):
                random_move()

            if floor == 1 and not awakening_used:
                cast_ability(awakening_skill)
            if floor == 2 and check_boss_bar() and not awakening_used:
                cast_ability(awakening_skill)
                awakening_used = True

            for i in range(len(normal_skills)):
                if floor == 3 and check_chaos_finish():
                    print("chaos finish screen")
                    return
                self.died_check()
                self.health_check()

                if (floor == 1 or floor == 2) and self.minimap.check_portal():
                    self.enter_portal()
                    return

                self.move_to_targets(floor)

                if floor == 3:
                    click_rift_core()

                perform_class_specialty(
                    self.roster[self.curr]["class"], i, normal_skills
                )
                cast_ability(normal_skills[i])

    def check_accidental_portal_enter(self, floor) -> bool:
        """
        Check if icon that's not supposed to be on floor is on minimap.

        Args:
            floor: The floor the instance should currently be on.

        Returns:
            True if on wrong floor, False otherwise.
        """
        if floor == 1 and self.minimap.check_elite():
            print("accidentally entered floor 2")
            return True
        elif floor == 2 and self.minimap.check_rift_core():
            print("accidentally entered floor 3")
            return True
        return False

    def enter_portal(self) -> None:
        """
        Moves to portal and tries to enter it.
        """
        pydirectinput.click(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y, button=config["move"])
        random_sleep(100, 150)
        while True:
            self.minimap.check_portal()
            x, y, _move_duration = self.minimap.get_game_coords(target_found=True)

            # Try to enter portal until black screen
            im = pyautogui.screenshot(region=(1652, 168, 240, 210))
            r, g, b = im.getpixel((1772 - 1652, 272 - 168))
            if r + g + b < 30:
                mouse_move_to(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                break
            pydirectinput.press(config["interact"])
            random_sleep(100, 120)
            pydirectinput.click(x=x, y=y, button=config["move"])
            random_sleep(60, 70)
            self.timeout_check()

    def move_to_targets(self, floor) -> None:
        """
        Detects targets and moves in mouse in direction. Clicks to move character
        depending on the floor.
        """
        match floor:
            case 1:
                x, y, move_duration = self.minimap.get_game_coords(
                    target_found=self.minimap.check_mob()
                )
            case 2:
                x, y, move_duration = self.minimap.get_game_coords(
                    target_found=(
                        self.minimap.check_boss()
                        or self.minimap.check_elite()
                        or self.minimap.check_mob()
                    )
                )
                move_in_direction(x, y, int(move_duration / 5))
            case 3:
                x, y, move_duration = self.minimap.get_game_coords(
                    target_found=(
                        self.minimap.check_rift_core()
                        or self.minimap.check_elite()
                        or self.minimap.check_mob()
                    ),
                    pathfind=True,
                )
                move_in_direction(x, y, int(move_duration / 4))


def enter_chaos(ilvl: int) -> None:
    """
    Opens and navigates content menu before entering specified chaos dungeon level.

    Args:
        ilvl: A valid item level entry requirement for a chaos dungeon.
    """
    toggle_menu("content")
    wait_for_menu_load("content")

    element_pos = find_image_center(
        "./screenshots/menus/chaosDungeonContentMenuElement.png", confidence=0.9
    )
    if element_pos is not None:
        x, y = element_pos
        left_click_at_position((x + 300, y + 30))  # shortcut button
    else:
        left_click_at_position((786, 315))  # edge case different UI
    random_sleep(800, 900)
    wait_for_menu_load("chaosDungeon")
    correct_chaos_dungeon = check_image_on_screen(
        f"./screenshots/chaos/ilvls/{ilvl}.png",
        region=(1255, 380, 80, 50),
        confidence=0.95,
    )
    if not correct_chaos_dungeon:
        print("correct chaos dungeon not selected")
        select_chaos_dungeon(ilvl)

    find_and_click_image("weeklyPurificationClaimAll", confidence=0.90)
    random_sleep(500, 600)
    left_click_at_position((920, 575))  # accept button
    random_sleep(500, 600)

    find_and_click_image("enterButton", confidence=0.75)
    random_sleep(800, 900)
    find_and_click_image("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(800, 900)


def select_chaos_dungeon(ilvl: int) -> None:
    """
    With chaos dungeon menu open, select chaos dungeon level corresponding to item level.

    Args:
        ilvl: A valid item level entry requirement for a chaos dungeon.
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
    Detects if completion overlay of chaos dungeon is onscreen and clears it by clicking OK.

    Returns:
        True if completion overlay detected, False otherwise.
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
    find_and_click_image("chaos/selectLevel", region=LEAVE_MENU_REGION, confidence=0.7)
    random_sleep(800, 900)
    find_and_click_image("enterButton", confidence=0.75)
    random_sleep(800, 900)
    find_and_click_image("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(2000, 3200)
    return


def check_boss_bar() -> bool:
    """
    Check if boss icon from health bar on top of screen is visible.

    Returns:
        True if found, False otherwise.
    """
    return check_image_on_screen(
        "./screenshots/chaos/bossBar.png",
        region=(406, 159, 1000, 200),
        confidence=0.8,
    )
