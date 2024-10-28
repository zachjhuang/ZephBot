import pyautogui
import pydirectinput

from configs.config import config
from modules.menu_nav import (
    restart_check,
    toggle_menu,
    wait_for_menu_load,
    wait_overworld_load,
)
from modules.task_bot import TaskBot
from modules.utilities import (
    check_image_on_screen,
    find_and_click_image,
    find_image_center,
    left_click_at_position,
    mouse_move_to,
    random_sleep,
)

SCREEN_CENTER_REGION = (685, 280, 600, 420)


class UnaBot(TaskBot):
    def __init__(self, roster) -> None:
        super().__init__(roster)
        for char in self.roster:
            if not char["unas"]:
                self.remaining_tasks.append(0)
            elif 'lopang' in char["unas"]:
                self.remaining_tasks.append(3)
            else:
                self.remaining_tasks.append(len(char["unas"]))

    def do_tasks(self) -> None:
        """
        Accepts favorited daily unas and completes according to roster configuration.
        """
        if self.done_on_curr_char():
            return
        random_sleep(1000, 2000)
        print("accepting dailies")
        accept_dailies()
        restart_check()
        unas = self.roster[self.curr]["unas"]
        if "lopang" in unas:
            restart_check()
            if go_to_bifrost("lopangIsland"):
                self.remaining_tasks[self.curr] -= doLopang()

        if "mokomoko" in unas:
            restart_check()
            if go_to_bifrost("mokomoko"):
                do_mokokmoko()
                self.remaining_tasks[self.curr] -= 1

        if "bleakNightFog" in unas:
            restart_check()
            if go_to_bifrost("bleakNightFog"):
                do_bleak_night_fog()
                self.remaining_tasks[self.curr] -= 1

        if "prehilia" in unas:
            restart_check()
            if go_to_bifrost("prehilia"):
                do_prehilia()
                self.remaining_tasks[self.curr] -= 1

        if "hesteraGarden" in unas:
            restart_check()
            if go_to_bifrost("hesteraGarden"):
                do_hestera_garden()
                self.remaining_tasks[self.curr] -= 1

        if "writersLife" in unas:
            restart_check()
            if go_to_bifrost("writersLife"):
                do_writers_life()
                self.remaining_tasks[self.curr] -= 1

        if "sageTower" in unas:
            restart_check()
            if go_to_bifrost("sageTower"):
                do_sage_tower()
                self.remaining_tasks[self.curr] -= 1

        if "ghostStory" in unas:
            restart_check()
            if go_to_bifrost("ghostStory"):
                do_ghost_story()
                self.remaining_tasks[self.curr] -= 1

        if "southKurzan" in unas:
            restart_check()
            if go_to_bifrost("southKurzan"):
                do_south_kurzan()
                self.remaining_tasks[self.curr] -= 1

        print("unas completed")


def accept_dailies() -> None:
    """
    Open una menu and accept all favorited dailies.
    """
    toggle_menu("unas")
    wait_for_menu_load("unas")
    # switch to daily tab
    if not check_image_on_screen("./screenshots/dailyTabActive.png", confidence=0.95):
        mouse_move_to(x=550, y=255)
        random_sleep(100, 200)
        pydirectinput.click(button="left")
        random_sleep(500, 600)
    # toggle dropdown and swap to favorites
    if not check_image_on_screen("./screenshots/addedToFavorites.png", confidence=0.95):
        mouse_move_to(x=632, y=316)
        random_sleep(100, 200)
        pydirectinput.click(button="left")
        random_sleep(1000, 1100)
        mouse_move_to(x=634, y=337)
        random_sleep(100, 200)
        pydirectinput.click(button="left")
        random_sleep(500, 600)
        pydirectinput.click(button="left")
        random_sleep(500, 600)
        pydirectinput.click(button="left")
        random_sleep(500, 600)
        mouse_move_to(x=548, y=404)
        random_sleep(100, 200)
        pydirectinput.click(button="left")
        random_sleep(500, 600)
    # if 3x completed unas detected, skip and return false
    random_sleep(500, 600)
    # if checkImageOnScreen("./screenshots/unasCompleted.png", confidence=0.75):
    #     print("character has already ran unas")
    #     toggleMenu("unas")
    #     return False

    # click all accept buttons
    accept_buttons = list(
        pyautogui.locateAllOnScreen(
            "./screenshots/acceptUna.png", region=(1165, 380, 80, 330), confidence=0.85
        )
    )
    for region in accept_buttons:
        left_click_at_position((region.left, region.top))
        random_sleep(400, 500)

    toggle_menu("unas")
    random_sleep(800, 900)


def doLopang() -> int:
    """Does 3 lopang dailies (Shushire -> Arthetine -> Vern)."""
    walk_lopang()
    completed = 0
    for lopangLocation in ["Shushire", "Arthetine", "Vern"]:
        random_sleep(1500, 1600)
        if go_to_bifrost("lopang" + lopangLocation):
            spam_interact(6000)
            completed += 1
    return completed


def do_bleak_night_fog() -> None:
    pydirectinput.press("f5")
    random_sleep(800, 900)
    pydirectinput.press("f6")
    random_sleep(1800, 1900)
    claim_completed_quest()


def do_prehilia() -> None:
    toggle_menu("unaTaskCombatPreset")

    pydirectinput.press(config["prehiliaEmoteSlot"])
    spam_interact(8000)

    toggle_menu("defaultCombatPreset")


def do_hestera_garden() -> None:
    toggle_menu("unaTaskCombatPreset")

    pydirectinput.press(config["hesteraGardenEmoteSlot"])
    random_sleep(140000, 141000)
    claim_completed_quest()
    random_sleep(300, 400)

    toggle_menu("defaultCombatPreset")


def do_writers_life() -> None:
    random_sleep(5000, 5100)
    toggle_menu("unaTaskCombatPreset")
    spam_interact(4000)
    pydirectinput.click(x=1100, y=750, button=config["move"])
    random_sleep(1500, 1600)
    pydirectinput.click(x=1100, y=750, button=config["move"])
    random_sleep(1500, 1600)
    pydirectinput.press(config["writersLifeEmoteSlot"])
    random_sleep(9000, 9100)
    pydirectinput.click(x=800, y=600, button=config["move"])
    random_sleep(1500, 1600)
    spam_interact(10000)
    pydirectinput.click(x=880, y=250, button=config["move"])
    random_sleep(1500, 1600)
    pydirectinput.click(x=880, y=250, button=config["move"])
    random_sleep(1500, 1600)
    spam_interact(4000)
    random_sleep(300, 400)
    toggle_menu("defaultCombatPreset")


def do_sage_tower() -> None:
    for _ in range(10):
        spam_interact(1000)
        if check_image_on_screen(
            "./screenshots/sageTowerCompleted.png",
            region=(1700, 220, 100, 150),
            confidence=0.65,
        ):
            break
    mouse_move_to(x=1560, y=540)
    random_sleep(500, 600)
    pydirectinput.click(x=1560, y=540, button=config["move"])
    random_sleep(500, 600)
    spam_interact(3000)


def do_ghost_story() -> None:
    for _ in range(15):
        spam_interact(1000)
        if check_image_on_screen(
            "./screenshots/ghostStoryF5.png",
            region=(1575, 440, 80, 450),
            confidence=0.85,
        ):
            break
    pydirectinput.press("f5")
    random_sleep(200, 300)
    pydirectinput.press("f6")
    random_sleep(200, 300)
    claim_completed_quest()
    random_sleep(300, 400)


def do_south_kurzan() -> None:
    toggle_menu("unaTaskCombatPreset")

    pydirectinput.press(config["southKurzanPoseSlot"])
    random_sleep(14000, 14100)

    toggle_menu("defaultCombatPreset")

    mouse_move_to(x=650, y=180)
    random_sleep(500, 600)
    pydirectinput.click(x=650, y=180, button="left")
    random_sleep(2500, 2600)
    pydirectinput.click(x=650, y=180, button="left")
    random_sleep(2500, 2600)
    spam_interact(4000)


def do_mokokmoko() -> None:
    spam_interact(4000)
    mouse_move_to(x=416, y=766)
    random_sleep(500, 600)
    pydirectinput.click(x=416, y=766, button="left")
    random_sleep(5500, 5600)

    mouse_move_to(x=960, y=770)
    random_sleep(500, 600)
    pydirectinput.click(x=960, y=770, button=config["move"])
    random_sleep(1500, 1600)
    pydirectinput.press(config["interact"])
    random_sleep(5500, 5600)

    mouse_move_to(x=1360, y=900)
    random_sleep(500, 600)
    pydirectinput.click(x=1360, y=900, button=config["move"])
    random_sleep(1500, 1600)
    pydirectinput.press(config["interact"])
    random_sleep(5500, 5600)

    mouse_move_to(x=960, y=330)
    random_sleep(1500, 1600)
    pydirectinput.click(x=980, y=280, button=config["move"])
    random_sleep(1500, 1600)
    pydirectinput.click(x=980, y=280, button=config["move"])
    random_sleep(1500, 1600)
    spam_interact(4000)
    random_sleep(1500, 1600)


def walk_lopang() -> None:
    """Interacts with and walks to all 3 lopang terminals."""
    random_sleep(1000, 2000)
    print("walking lopang")
    # right terminal
    spam_interact(2000)
    # walk to middle terminal
    walk_to(315, 473, 1500)
    walk_to(407, 679, 1300)
    walk_to(584, 258, 1000)
    walk_to(1043, 240, 1200)
    walk_to(1339, 246, 1300)
    walk_to(1223, 406, 800)
    walk_to(1223, 406, 800)
    walk_to(1263, 404, 1300)
    # middle terminal
    spam_interact(500)
    # walk to left terminal
    walk_to(496, 750, 1200)
    walk_to(496, 750, 1200)
    walk_to(496, 750, 1200)
    walk_to(753, 687, 800)
    walk_to(753, 687, 800)
    walk_to(674, 264, 800)
    walk_to(573, 301, 1200)
    walk_to(820, 240, 1300)
    # left terminal
    spam_interact(500)
    random_sleep(1000, 2000)


def claim_completed_quest() -> None:
    left_click_at_position((1700, 430))
    random_sleep(1000, 1100)
    find_and_click_image("completeQuest", confidence=0.85)


def go_to_bifrost(location: str) -> bool:
    """
    Attempts to bifrost to location.

    Return false if bifrost not found or on cooldown.

    Return true if bifrost to location is successful.
    """
    print(f"bifrost to: {location}")
    if not check_image_on_screen(
        "./screenshots/menus/bifrostMenu.png", confidence=0.85
    ):
        toggle_menu("bifrost")
    wait_for_menu_load("bifrost")
    bifrost = find_image_center(
        f"./screenshots/bifrosts/{location}Bifrost.png", confidence=0.80
    )
    if bifrost is None:
        print(f"{location} bifrost not found, skipping")
        toggle_menu("bifrost")
        return False
    x, y = bifrost
    mouse_move_to(x=(x + 280), y=(y - 25))
    random_sleep(300, 400)
    pydirectinput.click(button="left")
    random_sleep(500, 600)
    pydirectinput.click(button="left")
    random_sleep(1500, 1600)

    # return false if bifrost on cooldown
    if check_bifrost_on_cooldown():
        pydirectinput.press("esc")
        random_sleep(1500, 1600)
        pydirectinput.press("esc")
        random_sleep(1500, 1600)
        return False
    else:
        while True:
            ok_button = find_image_center(
                "./screenshots/ok.png",
                confidence=0.75,
                region=SCREEN_CENTER_REGION,
            )
            if ok_button is not None:
                x, y = ok_button
                mouse_move_to(x=x, y=y)
                random_sleep(2000, 2100)
                pydirectinput.click(x=x, y=y, button="left")
                random_sleep(2000, 2100)
                break
            random_sleep(300, 400)
    random_sleep(10000, 12000)

    # wait until loaded
    wait_overworld_load()
    return True


def check_bifrost_on_cooldown() -> bool:
    """Return false if bifrost move confirmation costs silver."""
    silver_1k = find_image_center(
        "./screenshots/silver1k.png",
        confidence=0.75,
        region=SCREEN_CENTER_REGION,
    )
    return silver_1k is None


def walk_to(x: int, y: int, ms: int) -> None:
    """Move to specified pixel coordinate with millisecond delay."""
    mouse_move_to(x=x, y=y)
    random_sleep(100, 100)
    pydirectinput.click(x=x, y=y, button=config["move"])
    random_sleep(ms, ms)


def spam_interact(msDuration: int) -> None:
    """Presses interact key for approximately the given duration in milliseconds."""
    count = msDuration / 100
    while count != 0:
        pydirectinput.press(config["interact"])
        random_sleep(90, 120)
        count = count - 1
