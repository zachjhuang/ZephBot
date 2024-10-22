import random
import time
from datetime import datetime

import pyautogui
import pydirectinput

from configs.config import config
from configs.skills import skills
from modules.menu_nav import quit_chaos, restart_check, toggle_menu, wait_for_menu_load
from modules.minimap import Minimap
from modules.task_bot import TaskBot
from modules.utilities import (
    Position,
    check_image_on_screen,
    find_and_click_image,
    find_image_center,
    left_click_at_position,
    mouse_move_to,
    random_sleep,
    ResetException,
    TimeoutException,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

CHAOS_CLICKABLE_REGION = (460, 290, 1000, 500)
CHAOS_PORTAL_REGION = (228, 230, 1370, 570)
CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)

CHARACTER_SPECIALTY_REGION = (900, 800, 120, 940)
CHARACTER_BUFFS_REGION = (625, 780, 300, 60)
CHARACTER_DEBUFFS_REGION = (1040, 810, 90, 40)

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


class ChaosBot(TaskBot):
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
        self.skills: dict[list[dict]] = skills
        self.run_start_time: int = 0

        self.completed_count: int = 0
        self.total_time: int = 0
        self.fastest_clear: int = 500000
        self.slowest_clear: int = 0

        self.health_pot_count: int = 0
        self.death_count: int = 0
        self.timeout_count: int = 0

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
                finishTime = int(time.time())
                self.update_print_metrics(finishTime - self.run_start_time)
            except TimeoutException:
                quit_chaos()
                enter_chaos(self.roster[self.curr]["chaosItemLevel"])
            self.remaining_tasks[self.curr] -= 1
            if self.remaining_tasks[self.curr] > 0:
                reenter_chaos()
            if datetime.now().hour == config["resetHour"] and not self.resetOnce:
                self.resetOnce = True
                quit_chaos()
                raise ResetException
        quit_chaos()

    def do_chaos_floor(self, n: int) -> None:
        wait_chaos_floor_load()
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
                x, y, move_duration = minimap.get_game_coords(target_found=True, pathfind=True)
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
                        if minimap.check_boss() and not awakening_used:
                            awakening_used = True
                            cast_ability(x, y, awakening_skill)
                    case 3:
                        x, y, move_duration = minimap.get_game_coords(
                            target_found=(
                                minimap.check_rift_core()
                                or minimap.check_elite()
                                or minimap.check_mob()
                            ),
                            pathfind=True
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

    def perform_class_specialty(
        self, char_class: str, i: int, abilities: list[dict]
    ) -> None:
        """
        Performs custom class behavior (activating identity, using specialty, stance swapping, etc.).
        """
        match char_class:
            case "arcana":
                pydirectinput.press(config["specialty1"])
                pydirectinput.press(config["specialty2"])
            case "souleater":
                soulSnatch = check_image_on_screen(
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

    def timeout_check(self) -> None:
        """
        Raise timeoutException if total time elapsed in chaos exceeds limit.
        """
        currentTime = int(time.time())
        if currentTime - self.run_start_time > config["timeLimit"]:
            print("timeout triggered")
            timeout = pyautogui.screenshot()
            timeout.save(f"./debug/timeout_{currentTime}.png")
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
        averageTime = self.total_time / self.completed_count
        print(
            f"average: {averageTime}, fastest: {self.fastest_clear}, slowest: {self.slowest_clear}"
        )
        print("-------------------------------------")


def enter_chaos(ilvl: int) -> None:
    """
    Enters specified chaos dungeon level.
    """
    toggle_menu("content")
    wait_for_menu_load("content")

    # remainingAura = checkAuraOfResonance()
    # self.remainingTasks[self.curr] = remainingAura / 50
    # if remainingAura == 0:
    #     toggleMenu("content")
    #     return False

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

    find_and_click_image("weeklyPurificationClaimAll", confidence=0.95)
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


def wait_chaos_floor_load() -> None:
    """
    Sleeps until leave button of chaos button is on screen.
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
            "./screenshots/chaos/leave.png",
            grayscale=True,
            confidence=0.7,
            region=CHAOS_LEAVE_MENU_REGION,
        )
        if leave_button:
            return
        random_sleep(100, 150)


def cast_ability(x: int, y: int, ability: dict) -> None:
    """
    Casts the given ability in the specified direction.
    """
    mouse_move_to(x=x, y=y)
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


def click_rift_core() -> None:
    """
    Uses basic attacks if rift core label on screen.
    """
    for i in [1, 2]:
        rift_core = find_image_center(
            f"./screenshots/chaos/riftcore{i}.png",
            confidence=0.6,
            region=CHAOS_PORTAL_REGION,
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
    left, top, width, height = CHAOS_CLICKABLE_REGION
    x = random.randint(left, left + width)
    y = random.randint(top, top + height)

    print(f"random move to x: {x} y: {y}")
    pydirectinput.click(x=x, y=y, button=config["move"])
    random_sleep(200, 250)
    pydirectinput.click(x=x, y=y, button=config["move"])
    random_sleep(200, 250)


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
        "chaos/selectLevel", region=CHAOS_LEAVE_MENU_REGION, confidence=0.7
    )
    random_sleep(500, 600)
    find_and_click_image("enterButton", region=(1380, 760, 210, 60), confidence=0.75)
    random_sleep(800, 900)
    find_and_click_image("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    random_sleep(2000, 3200)
    return


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
