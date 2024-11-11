# pylint: disable=missing-module-docstring, missing-function-docstring
import pyautogui
import pyscreeze
import pydirectinput

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
    rand_sleep,
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

    def __init__(self, roster, config) -> None:
        super().__init__(roster, config)
        for char in self.roster:
            if not char["unas"]:
                self.remaining_tasks.append(0)
            elif "lopang" in char["unas"]:
                self.remaining_tasks.append(3)
            else:
                self.remaining_tasks.append(len(char["unas"]))

    async def do_tasks(self) -> None:
        """
        Accepts favorited daily unas and completes according to roster configuration.
        """
        if self.done_on_curr_char():
            return
        await rand_sleep(1000, 2000)
        print("accepting dailies")
        await accept_dailies()
        await restart_check()
        unas = self.roster[self.curr]["unas"]
        if "lopang" in unas:
            await restart_check()
            if await go_to_bifrost("lopangIsland"):
                self.remaining_tasks[self.curr] -= await self.do_lopang()

        if "mokomoko" in unas:
            await restart_check()
            if await go_to_bifrost("mokomoko"):
                await self.do_mokokmoko()
                self.remaining_tasks[self.curr] -= 1

        if "bleakNightFog" in unas:
            await restart_check()
            if await go_to_bifrost("bleakNightFog"):
                await do_bleak_night_fog()
                self.remaining_tasks[self.curr] -= 1

        if "prehilia" in unas:
            await restart_check()
            if await go_to_bifrost("prehilia"):
                await self.do_prehilia()
                self.remaining_tasks[self.curr] -= 1

        if "hesteraGarden" in unas:
            await restart_check()
            if await go_to_bifrost("hesteraGarden"):
                await self.do_hestera_garden()
                self.remaining_tasks[self.curr] -= 1

        if "writersLife" in unas:
            await restart_check()
            if await go_to_bifrost("writersLife"):
                await self.do_writers_life()
                self.remaining_tasks[self.curr] -= 1

        if "sageTower" in unas:
            await restart_check()
            if await go_to_bifrost("sageTower"):
                await self.do_sage_tower()
                self.remaining_tasks[self.curr] -= 1

        if "ghostStory" in unas:
            await restart_check()
            if await go_to_bifrost("ghostStory"):
                await self.do_ghost_story()
                self.remaining_tasks[self.curr] -= 1

        if "southKurzan" in unas:
            await restart_check()
            if await go_to_bifrost("southKurzan"):
                await self.do_south_kurzan()
                self.remaining_tasks[self.curr] -= 1

        print("unas completed")

    async def do_lopang(self) -> int:
        """Does 3 lopang dailies (Shushire -> Arthetine -> Vern)."""
        await self.walk_lopang()
        completed = 0
        for lopang_location in ["Shushire", "Arthetine", "Vern"]:
            await rand_sleep(1500, 1600)
            if await go_to_bifrost("lopang" + lopang_location):
                await self.spam_interact(6000)
                completed += 1
        return completed

    async def do_prehilia(self) -> None:
        await toggle_menu("unaTaskCombatPreset")

        pydirectinput.press(self.config["prehiliaEmoteSlot"])
        await self.spam_interact(8000)

        await toggle_menu("defaultCombatPreset")

    async def do_hestera_garden(self) -> None:
        await toggle_menu("unaTaskCombatPreset")

        pydirectinput.press(self.config["hesteraGardenEmoteSlot"])
        await rand_sleep(140000, 141000)
        await claim_completed_quest()
        await rand_sleep(300, 400)

        await toggle_menu("defaultCombatPreset")

    async def do_writers_life(self) -> None:
        await toggle_menu("unaTaskCombatPreset")
        # accept at NPC
        await self.spam_interact(4000)

        # emote in circle
        await self.walk_to(x=1100, y=750, ms=1600)
        await self.walk_to(x=1100, y=750, ms=1600)
        pydirectinput.press(self.config["writersLifeEmoteSlot"])
        await rand_sleep(9000, 9100)

        # interact with 3 NPCs
        await self.walk_to(x=800, y=600, ms=1600)
        await self.spam_interact(10000)

        # claim rewards at NPC
        await self.walk_to(x=880, y=250, ms=1600)
        await self.walk_to(x=880, y=250, ms=1600)
        await self.spam_interact(4000)
        await rand_sleep(300, 400)
        await toggle_menu("defaultCombatPreset")

    async def do_sage_tower(self) -> None:
        # interact with 2 points of interests
        for _ in range(10):
            await self.spam_interact(1000)
            if check_image_on_screen(
                "./image_references/sageTowerCompleted.png",
                region=SAGE_TOWER_COMPLETED_REGION,
                confidence=0.65,
            ):
                break
        # claim at NPC
        await self.walk_to(x=1560, y=540, ms=700)
        await self.spam_interact(3000)

    async def do_ghost_story(self) -> None:
        # interact with 3 NPCs
        for _ in range(15):
            await self.spam_interact(1000)
            if check_image_on_screen(
                "./image_references/ghostStoryF5.png",
                region=GHOST_STORY_F5_REGION,
                confidence=0.85,
            ):
                break
        # use toy
        pydirectinput.press("f5")
        await rand_sleep(200, 300)
        pydirectinput.press("f6")
        await rand_sleep(200, 300)

        await claim_completed_quest()
        await rand_sleep(300, 400)

    async def do_south_kurzan(self) -> None:
        await toggle_menu("unaTaskCombatPreset")

        pydirectinput.press(self.config["southKurzanPoseSlot"])
        await rand_sleep(14000, 14100)

        await toggle_menu("defaultCombatPreset")

        await self.walk_to(x=650, y=180, ms=2600)
        await self.walk_to(x=650, y=180, ms=2600)
        await self.spam_interact(4000)

    async def do_mokokmoko(self) -> None:
        await self.spam_interact(4000)
        await self.walk_to(x=416, y=766, ms=5600)

        await self.walk_to(x=960, y=770, ms=1600)
        pydirectinput.press(self.config["interact"])
        await rand_sleep(5500, 5600)

        await self.walk_to(x=1360, y=900, ms=1600)
        pydirectinput.press(self.config["interact"])
        await rand_sleep(5500, 5600)

        await self.walk_to(x=980, y=280, ms=1600)
        await self.walk_to(x=980, y=280, ms=1600)
        await self.spam_interact(4000)
        await rand_sleep(1500, 1600)

    async def walk_lopang(self) -> None:
        """Interacts with and walks to all 3 lopang terminals."""
        await rand_sleep(1000, 2000)
        print("walking lopang")
        # right terminal
        await self.spam_interact(2000)
        # walk to middle terminal
        await self.walk_to(x=315, y=473, ms=1500)
        await self.walk_to(x=407, y=679, ms=1300)
        await self.walk_to(x=584, y=258, ms=1000)
        await self.walk_to(x=1043, y=240, ms=1200)
        await self.walk_to(x=1339, y=246, ms=1300)
        await self.walk_to(x=1223, y=406, ms=800)
        await self.walk_to(x=1223, y=406, ms=800)
        await self.walk_to(x=1263, y=404, ms=1300)
        # middle terminal
        await self.spam_interact(500)
        # walk to left terminal
        await self.walk_to(x=496, y=750, ms=1200)
        await self.walk_to(x=496, y=750, ms=1200)
        await self.walk_to(x=496, y=750, ms=1200)
        await self.walk_to(x=753, y=687, ms=800)
        await self.walk_to(x=753, y=687, ms=800)
        await self.walk_to(x=674, y=264, ms=800)
        await self.walk_to(x=573, y=301, ms=1200)
        await self.walk_to(x=820, y=240, ms=1300)
        # left terminal
        await self.spam_interact(500)
        await rand_sleep(1000, 2000)

    async def walk_to(self, x: int, y: int, ms: int) -> None:
        """Move to specified pixel coordinate with millisecond delay."""
        pydirectinput.moveTo(x=x, y=y)
        await rand_sleep(100, 100)
        pydirectinput.click(x=x, y=y, button=self.config["move"])
        await rand_sleep(ms, ms)

    async def spam_interact(self, duration_ms: int) -> None:
        """Presses interact key for approximately the given duration in milliseconds."""
        count = duration_ms / 100
        while count != 0:
            pydirectinput.press(self.config["interact"])
            await rand_sleep(90, 110)
            count = count - 1


async def accept_dailies() -> None:
    """
    Open una menu and accept all favorited dailies.
    """
    await toggle_menu("unas")
    await wait_for_menu_load("unas")
    # switch to daily tab
    if not check_image_on_screen(
        "./image_references/dailyTabActive.png", confidence=0.95
    ):
        await left_click_at_position((550, 255))
        await rand_sleep(500, 600)
    # toggle dropdown and swap to favorites
    if not check_image_on_screen(
        "./image_references/addedToFavorites.png", confidence=0.95
    ):
        await left_click_at_position((632, 316))
        await rand_sleep(1000, 1100)
        await left_click_at_position((634, 337))
        await rand_sleep(200, 300)
        await left_click_at_position((634, 337))
        await rand_sleep(200, 300)
        await left_click_at_position((634, 337))
        await rand_sleep(200, 300)
        await left_click_at_position((548, 404))
        await rand_sleep(200, 300)
    await rand_sleep(500, 600)

    # click all accept buttons
    # while check_image_on_screen("./image_references/acceptUna.png", region=ACCEPT_UNAS_REGION, confidence=0.85):
    #     await find_and_click_image("acceptUna", region=ACCEPT_UNAS_REGION, confidence=0.85)
    #     await rand_sleep(1700, 1800)
    try:
        accept_buttons = list(
            pyautogui.locateAllOnScreen(
                "./image_references/acceptUna.png",
                region=ACCEPT_UNAS_REGION,
                confidence=0.85,
            )
        )
        for region in accept_buttons:
            await left_click_at_position((region.left, region.top))
            await rand_sleep(600, 700)
    except pyscreeze.ImageNotFoundException:
        pass

    await toggle_menu("unas")
    await rand_sleep(800, 900)


async def do_bleak_night_fog() -> None:
    pydirectinput.press("f5")
    await rand_sleep(800, 900)
    pydirectinput.press("f6")
    await rand_sleep(1800, 1900)
    await claim_completed_quest()


async def claim_completed_quest() -> None:
    await left_click_at_position(COMPLETED_QUEST_POS)
    await rand_sleep(1000, 1100)
    await find_and_click_image("completeQuest", confidence=0.85)


async def go_to_bifrost(location: str) -> bool:
    """
    Attempts to bifrost to location.

    Returns:
        False if bifrost not found or on cooldown, True otherwise.
    """
    print(f"bifrost to: {location}")
    if not check_image_on_screen(
        "./image_references/menus/bifrostMenu.png", confidence=0.85
    ):
        await toggle_menu("bifrost")
    await wait_for_menu_load("bifrost")
    match find_image_center(
        f"./image_references/bifrosts/{location}Bifrost.png", confidence=0.80
    ):
        case x, y:
            await left_click_at_position((x + 280, y - 25))
            await rand_sleep(1500, 1600)
        case _:
            print(f"{location} bifrost not found, skipping")
            await toggle_menu("bifrost")
            return False

    # return false if bifrost on cooldown
    if check_bifrost_on_cooldown():
        pydirectinput.press("esc")
        await rand_sleep(500, 600)
        pydirectinput.press("esc")
        await rand_sleep(500, 600)
        return False
    else:
        while True:
            match find_image_center(
                "./image_references/ok.png",
                confidence=0.75,
                region=SCREEN_CENTER_REGION,
            ):
                case x, y:
                    await left_click_at_position((x, y))
                    break
            await rand_sleep(300, 400)
    await rand_sleep(10000, 12000)

    # wait until loaded
    await wait_overworld_load()
    return True


def check_bifrost_on_cooldown() -> bool:
    """Return false if bifrost move confirmation costs silver."""
    silver_1k = find_image_center(
        "./image_references/silver1k.png",
        confidence=0.75,
        region=SCREEN_CENTER_REGION,
    )
    return silver_1k is None
