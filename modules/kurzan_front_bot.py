# pylint: disable=missing-module-docstring
import time

import pyautogui
import pydirectinput

import modules.dungeon_bot as db
import modules.utilities as util
from modules.menu_nav import (
    restart_check,
    toggle_menu,
    wait_for_menu_load,
    quit_dungeon,
)
from modules.minimap import Minimap

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = (960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

CHAOS_CLICKABLE_REGION = (460, 290, 1000, 500)
CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)

ABIDOS_ICON_POS = {1640: (830, 670), 1660: (965, 590)}
MAP_NAME_REGION = (1652, 145, 112, 11)


class KurzanFrontBot(db.DungeonBot):
    """
    DungeonBot child class for completing Kurzan Front.
    """

    def __init__(self, roster, config):
        super().__init__(roster, config)
        self.remaining_tasks: list[int] = [
            (
                1
                if char["chaosItemLevel"] is not None and char["chaosItemLevel"] >= 1640
                else 0
            )
            for char in self.roster
        ]
        self.minimap = Minimap()

    async def do_tasks(self) -> None:
        if self.done_on_curr_char():
            return

        await toggle_menu("defaultCombatPreset")

        await enter_kurzan_front(self.roster[self.curr]["chaosItemLevel"])
        await db.wait_dungeon_load()
        self.run_start_time = int(time.time())
        print("kurzan front loaded")

        if util.get_config("auraRepair"):
            await db.do_aura_repair(False)

        await util.left_click_at_position(SCREEN_CENTER_POS)
        await util.rand_sleep(1500, 1600)
        try:
            await self.use_skills()
            end_time = int(time.time())
            self.update_print_metrics(end_time - self.run_start_time)
            self.remaining_tasks[self.curr] = 0
            await quit_dungeon()
        except util.TimeoutException:
            await quit_dungeon()

    async def use_skills(self) -> None:
        """
        Moves character and uses skills. Behavior changes depending on the floor.
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
        awakening_skill = [
            skill for skill in char_skills if skill["skillType"] == "awakening"
        ][0]
        # awakeningUsed = False
        should_jump = util.check_image_on_screen(
            "./image_references/jumpMapName.png",
            region=MAP_NAME_REGION,
            confidence=0.95,
        )
        if should_jump:
            print("jump mat detected")
        x, y, magnitude = self.minimap.get_game_coords()
        timeout = 0
        while True:
            await self.died_check()
            self.health_check()
            await restart_check()
            self.timeout_check()
            # cast sequence
            for i, skill in enumerate(normal_skills):
                if await check_kurzan_finish():
                    print("KurzanFront finish screen")
                    return
                await self.died_check()
                self.health_check()

                # try perform jump if needed
                if should_jump and check_50_percent_progress():
                    await self.jump()
                    should_jump = False
                    
                # update minimap target
                target_found = (
                    self.minimap.check_buff()
                    or self.minimap.check_boss()
                    or self.minimap.check_elite()
                )
                
                # move in target direction
                x, y, magnitude = self.minimap.get_game_coords(
                    target_found=target_found,
                    pathfind=True,
                )
                await self.move_in_direction(x, y, magnitude)
                
                if self.minimap.check_buff():
                    while True:
                        new_x, new_y, new_magnitude = self.minimap.get_game_coords(
                            target_found=self.minimap.check_buff(),
                            pathfind=True,
                        )
                        if new_x == x and new_y == y and new_magnitude == magnitude:
                            await self.random_move()
                        else:
                            break
                    

                # cast awakening for bosses
                if util.check_image_on_screen(
                    "./image_references/chaos/bossBar.png", confidence=0.75
                ):
                    await db.cast_skill(awakening_skill)
                
                # handle no target timeout
                if not target_found:
                    timeout += 1
                if timeout == 5:
                    await self.random_move()
                    timeout = 0
                    
                await self.perform_class_specialty(
                    self.roster[self.curr]["class"], i, normal_skills
                )
                await db.cast_skill(skill)

    async def jump(self):
        timeout = 0
        while True:
            if util.check_image_on_screen(
                "./image_references/jumpArrow.png", confidence=0.75
            ):
                print("arrow found")
                await util.find_and_click_image("jumpArrow", confidence=0.75)
                await util.rand_sleep(1000, 1100)

            if util.check_image_on_screen(
                "./image_references/jumpInteract.png",
                confidence=0.75,
            ):
                await util.left_click_at_position(SCREEN_CENTER_POS)

                pydirectinput.press(self.config["interact"])
                await util.rand_sleep(300, 350)
                pydirectinput.press(self.config["interact"])
                print("jumped")
                self.minimap.targets = []
                break
            x, y, magnitude = self.minimap.get_game_coords(
                target_found=self.minimap.check_jump(), pathfind=True
            )
            await self.move_in_direction(x, y, magnitude)
            await util.rand_sleep(100, 150)
            await util.left_click_at_position(SCREEN_CENTER_POS)
            timeout += 1
            if timeout % 4 == 0:
                await self.random_move()
                await util.rand_sleep(400, 500)


def check_50_percent_progress() -> bool:
    """
    Check if the progress meter in the top left is approximately 50% completed.

    Used to check when to perform a jump.

    Returns:
        bool: True if progress is around 50%, False otherwise.
    """
    im = pyautogui.screenshot()
    r, _g, _b = im.getpixel((89, 294))
    return r > 130


async def enter_kurzan_front(ilvl: int) -> None:
    """
    Enters specified Kurzan Front level.
    """
    await toggle_menu("content")
    await wait_for_menu_load("kazerosWarMap")
    await util.rand_sleep(1200, 1300)
    await util.left_click_at_position(ABIDOS_ICON_POS[ilvl])
    await wait_for_menu_load("kurzanFront")
    await util.rand_sleep(1200, 1300)
    await util.find_and_click_image(
        "enterButton", region=(1300, 750, 210, 40), confidence=0.75
    )
    await util.rand_sleep(1200, 1300)
    await util.find_and_click_image(
        "acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75
    )
    await util.rand_sleep(800, 900)


async def check_kurzan_finish() -> bool:
    """
    Returns true if chaos finish screen detected and clears the finish overlay.
    Otherwise returns false.
    """
    match util.find_image_center(
        "./image_references/chaos/kurzanFrontClearOK.png",
        confidence=0.65,
        region=(880, 820, 150, 70),
    ):
        case x, y:
            await util.left_click_at_position((x, y))
            await util.rand_sleep(800, 900)
            return True
        case _:
            return False
