import time

import pyautogui
import pydirectinput

from configs.config import config
from modules.dungeon_bot import (
    DungeonBot,
    cast_ability,
    perform_class_specialty,
    do_aura_repair,
    move_in_direction,
    wait_dungeon_load,
    random_move,
)
from modules.menu_nav import quit_chaos, restart_check, toggle_menu, wait_for_menu_load
from modules.minimap import Minimap
from modules.utilities import (
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

CHAOS_CLICKABLE_REGION = (460, 290, 1000, 500)
CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)

ABIDOS_1_POS = (830, 670)
ABIDOS_2_POS = (965, 590)


class KurzanFrontBot(DungeonBot):
    def __init__(self, roster):
        super().__init__(roster)
        self.remaining_tasks: list[int] = [
            (
                1
                if char["chaosItemLevel"] is not None and char["chaosItemLevel"] >= 1640
                else 0
            )
            for char in self.roster
        ]
        self.minimap = Minimap()

    def do_tasks(self) -> None:
        if self.done_on_curr_char():
            return

        toggle_menu("defaultCombatPreset")

        enter_kurzan_front(self.roster[self.curr]["chaosItemLevel"])
        wait_dungeon_load()
        self.run_start_time = int(time.time())
        print(f"kurzan front loaded")

        if config["auraRepair"]:
            do_aura_repair(False)

        left_click_at_position(SCREEN_CENTER_POS)
        random_sleep(1500, 1600)

        self.use_skills()
        end_time = int(time.time())
        self.update_print_metrics(end_time - self.run_start_time)
        self.remaining_tasks[self.curr] = 0
        quit_chaos()

    def use_skills(self) -> None:
        """
        Moves character and uses skills. Behavior changes depending on the floor.
        """
        self.minimap = Minimap()
        curr_class = self.roster[self.curr]["class"]
        char_skills = self.skills[curr_class]
        normal_skills = [
            skill for skill in char_skills if skill["skillType"] == "normal"
        ]
        awakeningSkill = [
            skill for skill in char_skills if skill["skillType"] == "awakening"
        ][0]
        awakeningUsed = False
        jumped = False
        x, y, magnitude = self.minimap.get_game_coords()
        while True:
            self.died_check()
            self.health_check()
            restart_check()
            self.timeout_check()
            timeout = 0
            # cast sequence
            for i in range(len(normal_skills)):
                if check_kurzan_finish():
                    print("KurzanFront finish screen")
                    return
                self.died_check()
                self.health_check()
                if not jumped and check_50_percent_progress() and self.minimap.check_jump():
                    timeout = 0
                    while True:
                        if (
                            find_image_center(
                                "./screenshots/jumpArrow.png", confidence=0.75
                            )
                            is not None
                        ):
                            print("arrow found")
                            find_and_click_image("jumpArrow", confidence=0.75)
                            random_sleep(1000, 1100)

                        if check_image_on_screen(
                            "./screenshots/chaos/jump.png",
                            confidence=0.75,
                        ):
                            left_click_at_position(SCREEN_CENTER_POS)
                            break
                        x, y, magnitude = self.minimap.get_game_coords(
                            target_found=self.minimap.check_jump(), pathfind=True
                        )
                        move_in_direction(x, y, magnitude)
                        random_sleep(100, 150)
                        left_click_at_position(SCREEN_CENTER_POS)
                        timeout += 1
                        if timeout == 10:
                            random_move()
                            random_sleep(400, 500)
                            timeout = 0

                    pydirectinput.press("g")
                    random_sleep(300, 350)
                    pydirectinput.press("g")
                    print("jumped")
                    jumped = True
                    self.minimap.targets = []

                elif (
                    self.minimap.check_buff()
                    or self.minimap.check_boss()
                    or self.minimap.check_elite()
                ):
                    x, y, magnitude = self.minimap.get_game_coords(
                        target_found=True, pathfind=True
                    )
                    move_in_direction(x, y, magnitude)
                    if check_image_on_screen(
                        "./screenshots/chaos/bossBar.png", confidence=0.75
                    ):
                        cast_ability(awakeningSkill)
                elif timeout == 5:
                    random_move()
                    timeout = 0
                else:
                    print("target not found")
                    x, y, magnitude = self.minimap.get_game_coords(
                        target_found=False, pathfind=True
                    )
                    move_in_direction(x, y, magnitude)
                    timeout += 1
                perform_class_specialty(
                    self.roster[self.curr]["class"], i, normal_skills
                )
                cast_ability(normal_skills[i])


def check_50_percent_progress():
    im = pyautogui.screenshot()
    r, _g, _b = im.getpixel((89, 292))
    return r > 130


def enter_kurzan_front(ilvl: int) -> None:
    """
    Enters specified Kurzan Front level.
    """
    toggle_menu("content")
    wait_for_menu_load("kazerosWarMap")
    random_sleep(1200, 1300)
    if ilvl == 1640:
        left_click_at_position(ABIDOS_1_POS)
    elif ilvl == 1660:
        left_click_at_position(ABIDOS_2_POS)
    wait_for_menu_load("kurzanFront")
    random_sleep(1200, 1300)
    find_and_click_image("enterButton", region=(1300, 750, 210, 40), confidence=0.75)
    random_sleep(1200, 1300)
    find_and_click_image("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(800, 900)


def check_kurzan_finish() -> bool:
    """
    Returns true if chaos finish screen detected and clears the finish overlay. Otherwise returns false.
    """
    ok_button = find_image_center(
        "./screenshots/chaos/kurzanFrontClearOK.png",
        confidence=0.65,
        region=(880, 820, 150, 70),
    )
    if ok_button is not None:
        x, y = ok_button
        mouse_move_to(x=x, y=y)
        random_sleep(800, 900)
        pydirectinput.click(x=x, y=y, button="left")
        random_sleep(200, 300)
        pydirectinput.click(x=x, y=y, button="left")
        random_sleep(200, 300)
    return ok_button is not None
