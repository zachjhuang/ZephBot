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

COMPLETED_QUEST_POS = (1700, 430)

SAGE_TOWER_COMPLETED_REGION = (1700, 220, 100, 150)
GHOST_STORY_F5_REGION = (1575, 440, 80, 450)
ACCEPT_UNAS_REGION = (1165, 380, 80, 330)

class UnaBot(TaskBot):
    """
    Taskbot child class for daily una tasks.
    """
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
        left_click_at_position((550, 255))
        random_sleep(500, 600)
    # toggle dropdown and swap to favorites
    if not check_image_on_screen("./screenshots/addedToFavorites.png", confidence=0.95):
        left_click_at_position((632, 316))
        random_sleep(1000, 1100)
        left_click_at_position((634, 337))
        random_sleep(200, 300)
        left_click_at_position((634, 337))
        random_sleep(200, 300)
        left_click_at_position((634, 337))
        random_sleep(200, 300)
        left_click_at_position((548, 404))
        random_sleep(200, 300)
    random_sleep(500, 600)

    # click all accept buttons
    accept_buttons = list(
        pyautogui.locateAllOnScreen(
            "./screenshots/acceptUna.png", region=ACCEPT_UNAS_REGION, confidence=0.85
        )
    )
    for region in accept_buttons:
        left_click_at_position((region.left, region.top))
        random_sleep(600, 700)

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
    toggle_menu("unaTaskCombatPreset")
    # accept at NPC
    spam_interact(4000)

    # emote in circle
    walk_to(x=1100, y=750, ms=1600)
    walk_to(x=1100, y=750, ms=1600)
    pydirectinput.press(config["writersLifeEmoteSlot"])
    random_sleep(9000, 9100)

    # interact with 3 NPCs
    walk_to(x=800, y=600, ms=1600)
    spam_interact(10000)

    # claim rewards at NPC
    walk_to(x=880, y=250, ms=1600)
    walk_to(x=880, y=250, ms=1600)
    spam_interact(4000)
    random_sleep(300, 400)
    toggle_menu("defaultCombatPreset")


def do_sage_tower() -> None:
    # interact with 2 points of interests
    for _ in range(10):
        spam_interact(1000)
        if check_image_on_screen(
            "./screenshots/sageTowerCompleted.png",
            region=SAGE_TOWER_COMPLETED_REGION,
            confidence=0.65,
        ):
            break
    # claim at NPC
    walk_to(x=1560, y=540, ms=700)
    spam_interact(3000)


def do_ghost_story() -> None:
    # interact with 3 NPCs
    for _ in range(15):
        spam_interact(1000)
        if check_image_on_screen(
            "./screenshots/ghostStoryF5.png",
            region=GHOST_STORY_F5_REGION,
            confidence=0.85,
        ):
            break
    # use toy
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

    walk_to(x=50, y=180, ms=2600)
    walk_to(x=650, y=180, ms=2600)
    spam_interact(4000)


def do_mokokmoko() -> None:
    spam_interact(4000)
    walk_to(x=416, y=766, ms=5600)

    walk_to(x=960, y=770, ms=1600)
    pydirectinput.press(config["interact"])
    random_sleep(5500, 5600)

    walk_to(x=1360, y=900, ms=1600)
    pydirectinput.press(config["interact"])
    random_sleep(5500, 5600)

    walk_to(x=980, y=280, ms=1600)
    walk_to(x=980, y=280, ms=1600)
    spam_interact(4000)
    random_sleep(1500, 1600)


def walk_lopang() -> None:
    """Interacts with and walks to all 3 lopang terminals."""
    random_sleep(1000, 2000)
    print("walking lopang")
    # right terminal
    spam_interact(2000)
    # walk to middle terminal
    walk_to(x=315, y=473, ms=1500)
    walk_to(x=407, y=679, ms=1300)
    walk_to(x=584, y=258, ms=1000)
    walk_to(x=1043, y=240, ms=1200)
    walk_to(x=1339, y=246, ms=1300)
    walk_to(x=1223, y=406, ms=800)
    walk_to(x=1223, y=406, ms=800)
    walk_to(x=1263, y=404, ms=1300)
    # middle terminal
    spam_interact(500)
    # walk to left terminal
    walk_to(x=496, y=750, ms=1200)
    walk_to(x=496, y=750, ms=1200)
    walk_to(x=496, y=750, ms=1200)
    walk_to(x=753, y=687, ms=800)
    walk_to(x=753, y=687, ms=800)
    walk_to(x=674, y=264, ms=800)
    walk_to(x=573, y=301, ms=1200)
    walk_to(x=820, y=240, ms=1300)
    # left terminal
    spam_interact(500)
    random_sleep(1000, 2000)


def claim_completed_quest() -> None:
    left_click_at_position(COMPLETED_QUEST_POS)
    random_sleep(1000, 1100)
    find_and_click_image("completeQuest", confidence=0.85)


def go_to_bifrost(location: str) -> bool:
    """
    Attempts to bifrost to location.

    Returns:
        False if bifrost not found or on cooldown, True otherwise.
    """
    print(f"bifrost to: {location}")
    if not check_image_on_screen(
        "./screenshots/menus/bifrostMenu.png", confidence=0.85
    ):
        toggle_menu("bifrost")
    wait_for_menu_load("bifrost")
    match find_image_center(
        f"./screenshots/bifrosts/{location}Bifrost.png", confidence=0.80
    ):
        case x, y:
            left_click_at_position((x + 280, y - 25))
            random_sleep(1500, 1600)
        case _:
            print(f"{location} bifrost not found, skipping")
            toggle_menu("bifrost")
            return False

    # return false if bifrost on cooldown
    if check_bifrost_on_cooldown():
        pydirectinput.press("esc")
        random_sleep(500, 600)
        pydirectinput.press("esc")
        random_sleep(500, 600)
        return False
    else:
        while True:
            match find_image_center(
                "./screenshots/ok.png",
                confidence=0.75,
                region=SCREEN_CENTER_REGION,
            ):
                case x, y:
                    left_click_at_position((x, y))
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


def spam_interact(duration_ms: int) -> None:
    """Presses interact key for approximately the given duration in milliseconds."""
    count = duration_ms / 100
    while count != 0:
        pydirectinput.press(config["interact"])
        random_sleep(90, 110)
        count = count - 1
