import random
import time

import pyautogui
import pydirectinput

from configs.config import config
from configs.skills import skills
from modules.menu_nav import restart_check, toggle_menu, wait_overworld_load
from modules.task_bot import TaskBot
from modules.utilities import (
    check_image_on_screen,
    find_and_click_image,
    mouse_move_to,
    random_sleep,
    TimeoutException,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

CLICKABLE_REGION = (460, 290, 1000, 500)
LEAVE_MENU_REGION = (0, 154, 250, 300)

CHARACTER_SPECIALTY_REGION = (900, 800, 120, 940)
CHARACTER_BUFFS_REGION = (625, 780, 300, 60)
CHARACTER_DEBUFFS_REGION = (1040, 810, 90, 40)


class DungeonBot(TaskBot):
    def __init__(self, roster):
        super().__init__(roster)

        self.skills: dict[list[dict]] = skills
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
        x = int(690 + 180 * config["healthPotAtPercent"])
        r1, g, b = pyautogui.pixel(x, 855)
        r2, g, b = pyautogui.pixel(x - 2, 855)
        r3, g, b = pyautogui.pixel(x + 2, 855)
        if r1 < 30 or r2 < 30 or r3 < 30:
            print("health pot pressed")
            pydirectinput.press(config["healthPot"])
            self.health_pot_count += 1

    def died_check(self) -> None:
        """
        Checks if death menu on screen and clicks revive.
        """
        if check_image_on_screen(
            "./screenshots/chaos/died.png", grayscale=True, confidence=0.8
        ):
            print("died")
            self.death_count += 1
            random_sleep(5000, 5500)
            res_ready = check_image_on_screen(
                "./screenshots/chaos/resReady.png", confidence=0.7
            )
            if res_ready:
                mouse_move_to(x=1275, y=400)
                random_sleep(1600, 1800)
                pydirectinput.click(button="left")
                random_sleep(600, 800)
                mouse_move_to(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                random_sleep(600, 800)
                restart_check()
                self.timeout_check()

    def timeout_check(self) -> None:
        """
        Raise timeoutException if total time elapsed in chaos exceeds limit.
        """
        curr_time = int(time.time())
        if curr_time - self.run_start_time > config["timeLimit"]:
            print("timeout triggered")
            timeout = pyautogui.screenshot()
            timeout.save(f"./debug/timeout_{curr_time}.png")
            self.timeout_count += 1
            raise TimeoutException

    def update_print_metrics(self, int):
        """
        Updates bot statistics and prints summary.
        """
        print("-------------------------------------")
        print(f"run completed in {int}s")
        self.completed_count += 1
        self.total_time += int
        self.fastest_clear = min(int, self.fastest_clear)
        self.slowest_clear = max(int, self.slowest_clear)
        print("-------------------------------------")
        print(f"total timeouts: {self.timeout_count}")
        print(f"total deaths: {self.death_count}")
        print(f"total low hp: {self.health_pot_count}")
        print("-------------------------------------")
        avg_time = self.total_time / self.completed_count
        print(
            f"average: {avg_time}, fastest: {self.fastest_clear}, slowest: {self.slowest_clear}"
        )
        print("-------------------------------------")


def cast_ability(ability: dict) -> None:
    """
    Casts the given ability in the specified direction.
    """
    # mouse_move_to(x=x, y=y)
    # if ability["directional"]:
    #     mouseMoveTo(x=x, y=y)
    # else:
    #     mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)

    if ability["castTime"] is not None:
        pydirectinput.press(ability["key"])
        random_sleep(100, 150)
        pydirectinput.press(ability["key"])
        random_sleep(ability["castTime"], (ability["castTime"] + 100))
    elif ability["holdTime"] is not None:
        pydirectinput.keyDown(ability["key"])
        random_sleep(ability["holdTime"], (ability["holdTime"] + 100))
        pydirectinput.keyUp(ability["key"])
    else:
        pydirectinput.press(ability["key"])
        random_sleep(100, 150)


def perform_class_specialty(char_class: str, i: int, abilities: list[dict]) -> None:
    """
    Performs custom class behavior (activating identity, using specialty, stance swapping, etc.).
    """
    match char_class:
        case "arcanist":
            pydirectinput.press(config["specialty1"])
            pydirectinput.press(config["specialty2"])
        case "souleater":
            soul_snatch = check_image_on_screen(
                "./screenshots/classSpecialties/soulSnatch.png",
                region=CHARACTER_DEBUFFS_REGION,
                confidence=0.85,
            )
            # if soulSnatch:
            #     castAbility(960, 540, abilities[0])
            #     random_sleep(300, 400)
            #     castAbility(960, 540, abilities[1])
            #     random_sleep(300, 400)
            #     castAbility(960, 540, abilities[5])
            #     random_sleep(300, 400)
        case "slayer":
            slayer_specialty = check_image_on_screen(
                "./screenshots/classSpecialties/slayerSpecialty.png",
                region=CHARACTER_SPECIALTY_REGION,
                confidence=0.85,
            )
            if slayer_specialty:
                pydirectinput.press(config["specialty1"])
                random_sleep(150, 160)
        case "deathblade":
            deathblade_three_orbs = check_image_on_screen(
                "./screenshots/classSpecialties/deathTrance.png",
                region=CHARACTER_SPECIALTY_REGION,
                confidence=0.80,
            )
            if deathblade_three_orbs:
                pydirectinput.press(config["specialty1"])
                random_sleep(150, 160)
        case "gunslinger":
            pistol_stance = check_image_on_screen(
                "./screenshots/classSpecialties/pistolStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            )
            shotgun_stance = check_image_on_screen(
                "./screenshots/classSpecialties/shotgunStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            )
            sniper_stance = check_image_on_screen(
                "./screenshots/classSpecialties/sniperStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            )
            # swap to shotgun
            if i == 0 and not shotgun_stance:
                if pistol_stance:
                    pydirectinput.press(config["specialty1"])
                    random_sleep(150, 160)
                if sniper_stance:
                    pydirectinput.press(config["specialty2"])
                    random_sleep(150, 160)
            # swap to sniper
            elif i < 3 and not sniper_stance:
                if pistol_stance:
                    pydirectinput.press(config["specialty2"])
                    random_sleep(150, 160)
                if shotgun_stance:
                    pydirectinput.press(config["specialty1"])
                    random_sleep(150, 160)
            # swap to pistol
            elif not pistol_stance:
                if shotgun_stance:
                    pydirectinput.press(config["specialty2"])
                    random_sleep(150, 160)
                if sniper_stance:
                    pydirectinput.press(config["specialty1"])
                    random_sleep(150, 160)
        case "artist":
            artist_orb = check_image_on_screen(
                "./screenshots/classSpecialties/artistOrb.png",
                region=CHARACTER_SPECIALTY_REGION,
                confidence=0.85,
            )
            if artist_orb:
                mouse_move_to(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                random_sleep(150, 160)
                pydirectinput.press(config["specialty2"])
                random_sleep(1500, 1600)
                pydirectinput.press(config["interact"])
        case "aeromancer":
            aero_specialty = check_image_on_screen(
                "./screenshots/classSpecialties/aeroSpecialty.png",
                region=CHARACTER_SPECIALTY_REGION,
                confidence=0.95,
            )
            if aero_specialty:
                random_sleep(150, 160)
                pydirectinput.press(config["specialty1"])
        case "scrapper":
            scrapper_specialty = check_image_on_screen(
                "./screenshots/classSpecialties/scrapperSpecialty.png",
                region=CHARACTER_SPECIALTY_REGION,
                confidence=0.85,
            )
            if scrapper_specialty:
                random_sleep(150, 160)
                pydirectinput.press(config["specialty1"])
        case "bard":
            courage_buff = check_image_on_screen(
                "./screenshots/classSpecialties/bardCourage120.png",
                region=CHARACTER_BUFFS_REGION,
                confidence=0.75,
            )
            rZ, gZ, bZ = pyautogui.pixel(920, 866)
            rX, gX, bX = pyautogui.pixel(1006, 875)
            if rZ - gZ > 80 and courage_buff:
                pydirectinput.press(config["specialty1"])
                random_sleep(50, 60)
                pydirectinput.press(config["specialty1"])
                random_sleep(150, 160)
            elif bX - gX > 70 and not courage_buff:
                mouse_move_to(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                random_sleep(150, 160)
                pydirectinput.press(config["specialty2"])
                random_sleep(50, 60)
                pydirectinput.press(config["specialty2"])
                random_sleep(150, 160)


def do_aura_repair(forced: bool) -> None:
    """
    Repair through pet menu if forced or yellow/red armor icon detected.
    """
    if forced or check_image_on_screen(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        toggle_menu("pet")
        mouse_move_to(x=1142, y=661)
        random_sleep(2500, 2600)
        pydirectinput.click(button="left")
        random_sleep(5500, 5600)
        mouse_move_to(x=1054, y=455)
        random_sleep(2500, 2600)
        pydirectinput.click(button="left")
        random_sleep(2500, 2600)
        pydirectinput.press("esc")
        random_sleep(2500, 2600)
        pydirectinput.press("esc")
        random_sleep(2500, 2600)


def move_in_direction(x: int, y: int, duration: int) -> None:
    """
    Moves to (x, y) across duration.
    """
    if x == SCREEN_CENTER_X and y == SCREEN_CENTER_Y:
        return
    halfstep = int(duration / 2)
    for _ in range(2):
        pydirectinput.click(x=x, y=y, button=config["move"])
        random_sleep(halfstep - 20, halfstep + 20)


def random_move() -> None:
    """
    Randomly moves by clicking in the clickable region.
    """
    left, top, width, height = CLICKABLE_REGION
    x = random.randint(left, left + width)
    y = random.randint(top, top + height)

    print(f"random move to x: {x} y: {y}")
    pydirectinput.click(x=x, y=y, button=config["move"])
    random_sleep(200, 250)
    pydirectinput.click(x=x, y=y, button=config["move"])
    random_sleep(200, 250)


def wait_dungeon_load() -> None:
    """
    Sleeps until exit button of dungeon is on screen.
    ALT F4 if loading times out.
    """
    black_screen_start_time = int(time.time_ns() / 1000000)
    while True:
        restart_check()
        curr_time = int(time.time_ns() / 1000000)
        if curr_time - black_screen_start_time > config["blackScreenTimeLimit"]:
            print("alt f4")
            pydirectinput.keyDown("alt")
            random_sleep(350, 400)
            pydirectinput.keyDown("f4")
            random_sleep(350, 400)
            pydirectinput.keyUp("alt")
            random_sleep(350, 400)
            pydirectinput.keyUp("f4")
            random_sleep(350, 400)
            random_sleep(10000, 15000)
            return
        leave_button = check_image_on_screen(
            "./screenshots/chaos/exit.png",
            grayscale=True,
            confidence=0.7,
            region=LEAVE_MENU_REGION,
        )
        if leave_button:
            return
        random_sleep(100, 150)


def quit_dungeon() -> None:
    """
    Quit dungeon after finishing a run.
    """
    print("quitting dungeon")
    find_and_click_image("chaos/exit", region=LEAVE_MENU_REGION, confidence=0.7)
    random_sleep(800, 900)
    find_and_click_image("ok", region=CLICKABLE_REGION, confidence=0.75)
    random_sleep(5000, 7000)
    wait_overworld_load()
    return
