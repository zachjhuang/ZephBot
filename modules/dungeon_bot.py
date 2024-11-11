# pylint: disable=missing-module-docstring
import random
import time
import math

import pyautogui
import pydirectinput

from modules.menu_nav import restart_check, toggle_menu, wait_overworld_load
from modules.task_bot import TaskBot
from modules.utilities import (
    left_click_at_position,
    check_image_on_screen,
    find_and_click_image,
    rand_sleep,
    TimeoutException,
    get_skills,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

INSTANT_RES_POS = (1275, 400)

CLICKABLE_REGION = (460, 290, 1000, 500)
LEAVE_MENU_REGION = (0, 154, 250, 300)

CHARACTER_SPECIALTY_REGION = (900, 800, 120, 940)
CHARACTER_BUFFS_REGION = (625, 780, 300, 60)
CHARACTER_DEBUFFS_REGION = (1040, 810, 90, 40)

DAMAGED_ARMOR_REGION = (1500, 134, 100, 100)


class DungeonBot(TaskBot):
    """
    TaskBot child class that can complete combat dungeons (instances) by using skills
    and navigating based on the minimap.
    Maintains clear time statistics.
    """

    def __init__(self, roster, config):
        super().__init__(roster, config)

        self.skills: dict[str, list[dict]] = get_skills()
        self.run_start_time: int = 0

        self.completed_count: int = 0
        self.total_time: int = 0
        self.fastest_clear: int = 500000
        self.slowest_clear: int = 0

        self.health_pot_count: int = 0
        self.death_count: int = 0
        self.timeout_count: int = 0

    def health_check(self) -> None:
        """
        Press potion if under HP threshold.
        """
        x = int(690 + 180 * self.config["healthPotAtPercent"])
        r1, _g, _b = pyautogui.pixel(x, 855)
        r2, _g, _b = pyautogui.pixel(x - 2, 855)
        r3, _g, _b = pyautogui.pixel(x + 2, 855)
        if r1 < 30 or r2 < 30 or r3 < 30:
            print("health pot pressed")
            pydirectinput.press(self.config["healthPot"])
            self.health_pot_count += 1

    async def died_check(self) -> None:
        """
        Checks if death menu on screen and clicks revive.
        """
        if check_image_on_screen(
            "./image_references/chaos/died.png", grayscale=True, confidence=0.8
        ):
            print("died")
            self.death_count += 1
            await rand_sleep(5000, 5500)
            if check_image_on_screen(
                "./image_references/chaos/resReady.png", confidence=0.7
            ):
                await left_click_at_position(INSTANT_RES_POS)
                await rand_sleep(600, 800)
                await restart_check()
                self.timeout_check()

    def timeout_check(self) -> None:
        """
        Raise timeoutException if total time elapsed in chaos exceeds limit.
        """
        curr_time = int(time.time())
        if curr_time - self.run_start_time > self.config["timeLimit"]:
            print("timeout triggered")
            timeout = pyautogui.screenshot()
            timeout.save(f"./debug/timeout_{curr_time}.png")
            self.timeout_count += 1
            raise TimeoutException

    def update_print_metrics(self, clear_time: int):
        """
        Updates bot statistics and prints summary.
        """
        self.completed_count += 1
        self.total_time += clear_time
        avg_time = self.total_time / self.completed_count
        self.fastest_clear = min(clear_time, self.fastest_clear)
        self.slowest_clear = max(clear_time, self.slowest_clear)
        print(f"""
            -------------------------------------
            run completed in {clear_time}s
            -------------------------------------
            total timeouts: {self.timeout_count}
            total deaths: {self.death_count}
            total low hp: {self.health_pot_count}
            -------------------------------------
            average: {avg_time}, fastest: {self.fastest_clear}, slowest: {self.slowest_clear}
            -------------------------------------
            """)

        # print("-------------------------------------")
        # print(f"run completed in {clear_time}s")
        # print("-------------------------------------")
        # print(f"total timeouts: {self.timeout_count}")
        # print(f"total deaths: {self.death_count}")
        # print(f"total low hp: {self.health_pot_count}")
        # print("-------------------------------------")
        # print(
        #     f"average: {avg_time}, fastest: {
        #         self.fastest_clear}, slowest: {self.slowest_clear}"
        # )
        # print("-------------------------------------")

    async def perform_class_specialty(
        self, char_class: str, i: int, skills: list[dict]
    ) -> None:
        """
        Performs custom class behavior (activating identity, using specialty, stance swapping, etc.).
        """
        match char_class:
            case "arcanist":
                pydirectinput.press(self.config["specialty1"])
                pydirectinput.press(self.config["specialty2"])
            case "souleater":
                soul_snatch = check_image_on_screen(
                    "./image_references/classSpecialties/soulSnatch.png",
                    region=CHARACTER_DEBUFFS_REGION,
                    confidence=0.85,
                )
                # if soul_snatch:
                #     cast_skill(skills[0])
                #     random_sleep(300, 400)
                #     cast_skill(skills[1])
                #     random_sleep(300, 400)
                #     cast_skill(skills[5])
                #     random_sleep(300, 400)
            case "slayer":
                slayer_specialty = check_image_on_screen(
                    "./image_references/classSpecialties/slayerSpecialty.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.85,
                )
                if slayer_specialty:
                    pydirectinput.press(self.config["specialty1"])
                    await rand_sleep(150, 160)
            case "deathblade":
                deathblade_three_orbs = check_image_on_screen(
                    "./image_references/classSpecialties/deathTrance.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.80,
                )
                if deathblade_three_orbs:
                    pydirectinput.press(self.config["specialty1"])
                    await rand_sleep(150, 160)
            case "gunslinger":
                pistol_stance = check_image_on_screen(
                    "./image_references/classSpecialties/pistolStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                shotgun_stance = check_image_on_screen(
                    "./image_references/classSpecialties/shotgunStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                sniper_stance = check_image_on_screen(
                    "./image_references/classSpecialties/sniperStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                # swap to shotgun
                if i == 0 and not shotgun_stance:
                    if pistol_stance:
                        pydirectinput.press(self.config["specialty1"])
                        await rand_sleep(150, 160)
                    if sniper_stance:
                        pydirectinput.press(self.config["specialty2"])
                        await rand_sleep(150, 160)
                # swap to sniper
                elif i < 3 and not sniper_stance:
                    if pistol_stance:
                        pydirectinput.press(self.config["specialty2"])
                        await rand_sleep(150, 160)
                    if shotgun_stance:
                        pydirectinput.press(self.config["specialty1"])
                        await rand_sleep(150, 160)
                # swap to pistol
                elif not pistol_stance:
                    if shotgun_stance:
                        pydirectinput.press(self.config["specialty2"])
                        await rand_sleep(150, 160)
                    if sniper_stance:
                        pydirectinput.press(self.config["specialty1"])
                        await rand_sleep(150, 160)
            case "artist":
                artist_orb = check_image_on_screen(
                    "./image_references/classSpecialties/artistOrb.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.85,
                )
                if artist_orb:
                    pydirectinput.moveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                    await rand_sleep(150, 160)
                    pydirectinput.press(self.config["specialty2"])
                    await rand_sleep(1500, 1600)
                    pydirectinput.press(self.config["interact"])
            case "aeromancer":
                aero_specialty = check_image_on_screen(
                    "./image_references/classSpecialties/aeroSpecialty.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.95,
                )
                if aero_specialty:
                    await rand_sleep(150, 160)
                    pydirectinput.press(self.config["specialty1"])
            case "scrapper":
                scrapper_specialty = check_image_on_screen(
                    "./image_references/classSpecialties/scrapperSpecialty.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.85,
                )
                if scrapper_specialty:
                    await rand_sleep(150, 160)
                    pydirectinput.press(self.config["specialty1"])
            case "bard":
                courage_buff = check_image_on_screen(
                    "./image_references/classSpecialties/bardCourage120.png",
                    region=CHARACTER_BUFFS_REGION,
                    confidence=0.75,
                )
                rz, gz, _bz = pyautogui.pixel(920, 866)
                _rx, gx, bx = pyautogui.pixel(1006, 875)
                if rz - gz > 80 and courage_buff:
                    pydirectinput.press(self.config["specialty1"])
                    await rand_sleep(50, 60)
                    pydirectinput.press(self.config["specialty1"])
                    await rand_sleep(150, 160)
                elif bx - gx > 70 and not courage_buff:
                    pydirectinput.moveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                    await rand_sleep(150, 160)
                    pydirectinput.press(self.config["specialty2"])
                    await rand_sleep(50, 60)
                    pydirectinput.press(self.config["specialty2"])
                    await rand_sleep(150, 160)

    async def move_in_direction(self, x: int, y: int, magnitude: int) -> None:
        """
        Moves in (x, y) direction with magnitude.
        """
        if x == SCREEN_CENTER_X and y == SCREEN_CENTER_Y:
            return
        for _ in range(math.floor(magnitude / 10) + 1):
            pydirectinput.click(x=x, y=y, button=self.config["move"])
            await rand_sleep(100, 110)

    async def random_move(self) -> None:
        """
        Randomly moves by clicking in the clickable region.
        """
        left, top, width, height = CLICKABLE_REGION
        x = random.randint(left, left + width)
        y = random.randint(top, top + height)

        print(f"random move to x: {x} y: {y}")
        pydirectinput.click(x=x, y=y, button=self.config["move"])
        await rand_sleep(400, 500)


async def cast_skill(skill: dict) -> None:
    """
    Casts the given skill in the specified direction.
    """
    # mouse_move_to(x=x, y=y)
    # if ability["directional"]:
    #     mouseMoveTo(x=x, y=y)
    # else:
    #     mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)

    if skill["castTime"] is not None and skill["castTime"] > 0:
        pydirectinput.press(skill["key"])
        await rand_sleep(100, 150)
        pydirectinput.press(skill["key"])
        await rand_sleep(skill["castTime"], (skill["castTime"] + 100))
    elif skill["holdTime"] is not None and skill["holdTime"] > 0:
        pydirectinput.keyDown(skill["key"])
        await rand_sleep(skill["holdTime"], (skill["holdTime"] + 100))
        pydirectinput.keyUp(skill["key"])
    else:
        pydirectinput.press(skill["key"])
        await rand_sleep(100, 150)


async def do_aura_repair(forced: bool) -> None:
    """
    Repair through pet menu if forced or yellow/red armor icon detected.
    """
    if forced or check_image_on_screen(
        "./image_references/repair.png",
        grayscale=True,
        confidence=0.4,
        region=DAMAGED_ARMOR_REGION,
    ):
        await toggle_menu("pet")
        await left_click_at_position((1142, 661))
        await rand_sleep(2500, 2600)
        await left_click_at_position((1054, 455))
        await rand_sleep(2500, 2600)
        pydirectinput.press("esc")
        await rand_sleep(2500, 2600)
        pydirectinput.press("esc")
        await rand_sleep(2500, 2600)


async def wait_dungeon_load() -> None:
    """
    Sleeps until exit button of dungeon is on screen.
    ALT F4 if loading times out.
    """
    black_screen_start_time = int(time.time())
    while True:
        await restart_check()
        curr_time = int(time.time())
        if curr_time - black_screen_start_time > 50:
            print("alt f4")
            pydirectinput.keyDown("alt")
            await rand_sleep(350, 400)
            pydirectinput.keyDown("f4")
            await rand_sleep(350, 400)
            pydirectinput.keyUp("alt")
            await rand_sleep(350, 400)
            pydirectinput.keyUp("f4")
            await rand_sleep(350, 400)
            await rand_sleep(10000, 15000)
            return
        leave_button = check_image_on_screen(
            "./image_references/chaos/exit.png",
            grayscale=True,
            confidence=0.7,
            region=LEAVE_MENU_REGION,
        )
        if leave_button:
            return
        await rand_sleep(100, 150)


async def quit_dungeon() -> None:
    """
    Quit dungeon after finishing a run.
    """
    print("quitting dungeon")
    await find_and_click_image("chaos/exit", region=LEAVE_MENU_REGION, confidence=0.7)
    await rand_sleep(800, 900)
    await find_and_click_image("ok", region=CLICKABLE_REGION, confidence=0.75)
    await rand_sleep(5000, 7000)
    await wait_overworld_load()
    return
