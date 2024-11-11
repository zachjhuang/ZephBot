import math

import pydirectinput

from modules.chaos_bot import ChaosBot
from modules.guild_bot import GuildBot
from modules.kurzan_front_bot import KurzanFrontBot
from modules.menu_nav import restart_check, wait_overworld_load
from modules.task_bot import TaskBot
from modules.unabot import UnaBot
from modules.utilities import (
    check_image_on_screen,
    find_image_center,
    left_click_at_position,
    rand_sleep,
    get_roster,
    get_config,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_REGION = (685, 280, 600, 420)
CLEAR_NOTIFS_REGION = (880, 720, 160, 40)

MINIMAP_REGION = (1655, 170, 240, 200)
MINIMAP_CENTER_X = 1772
MINIMAP_CENTER_Y = 272

CHARACTER_STATUS_ICON_REGION = (1280, 440, 30, 230)
CHARACTER_SELECT_POS = [
    (760, 440),
    (960, 440),
    (1160, 440),
    (760, 530),
    (960, 530),
    (1160, 530),
    (760, 620),
    (960, 620),
    (1160, 620),
]


class BotManager:
    """
    Manages a list of bots and switches between characters,
    running each of the bots on each character.
    """

    def __init__(self, options) -> None:
        self.curr = 0
        self.roster = get_roster()
        self.config = get_config()
        self.running_bots: list[TaskBot] = []
        if options["do_chaos"]:
            self.running_bots.append(ChaosBot(self.roster, self.config))
        if options["do_kurzan_front"]:
            self.running_bots.append(KurzanFrontBot(self.roster, self.config))
        if options["do_unas"]:
            self.running_bots.append(UnaBot(self.roster, self.config))
        if options["do_guild"]:
            self.running_bots.append(GuildBot(self.roster, self.config))

    def all_bots_done(self) -> bool:
        """
        Checks if all bots have no more remaining tasks.

        Returns:
            bool: True if any bot still has remaining tasks, False otherwise.
        """
        for bot in self.running_bots:
            if not bot.is_done():
                return False
        return True

    async def run(self) -> None:
        """
        Loop through the roster.
        On each character, run all available bots.
        Stop when all bots have no remaining tasks.
        """
        await restart_check()
        await self.switch_to_char(0)

        if not self.config["auraRepair"]:
            await do_city_repair()

        while not self.all_bots_done():
            await restart_check()
            await wait_overworld_load()
            await clear_notifs()

            if not self.config["auraRepair"]:
                await do_city_repair()

            for bot in self.running_bots:
                await bot.do_tasks()

            await restart_check()
            next_char = (self.curr + 1) % len(self.roster)
            print(f"character {self.curr} is done, switching to: {next_char}")
            await self.switch_to_char(next_char)

    def update_curr_char(self, char: int) -> None:
        """
        Updates the current character for all running bots to the index supplied.

        Args:
            char (int): The index of the specified character.
        """
        for bot in self.running_bots:
            bot.set_current_char(char)

    def is_char_done(self, char: int) -> bool:
        """
        Checks if any of the running bots still have tasks to complete on the specified characters.

        Args:
            char (int): The index of the specified character.

        Returns:
            bool: True if no bots have remaining tasks for the character, otherwise False.
        """
        return sum([bot.remaining_tasks[char] for bot in self.running_bots]) == 0

    # def runCharTasks(self) -> None:
    #     for bot in self.runningBotList:
    #         bot.doTasks()

    async def switch_to_char(self, index: int) -> None:
        """
        Opens ESC menu and switches to character designated by index.
        """
        self.curr = index
        self.update_curr_char(index)
        await rand_sleep(500, 600)
        print("----------------------------")
        for bot in self.running_bots:
            print(f"{bot.__class__.__name__}: {bot.remaining_tasks}")
        print("----------------------------")
        print(f"switching to {self.roster[index]["name"]}")
        while not check_image_on_screen(
            "./image_references/menus/gameMenu.png", confidence=0.7
        ):
            pydirectinput.press("esc")
            await rand_sleep(1000, 1100)
        print("game menu detected")
        await rand_sleep(800, 900)
        await left_click_at_position((540, 700))
        await rand_sleep(800, 900)

        for _ in range(4):
            await left_click_at_position((1270, 430))
            await rand_sleep(200, 300)

        if index > 8:
            for _ in range(math.floor(index / 3) - 2):
                await left_click_at_position((1267, 638))
                await rand_sleep(200, 300)

        position_index = index if index < 9 else index - 3 * ((index - 6) // 3)
        await left_click_at_position(CHARACTER_SELECT_POS[position_index])
        await rand_sleep(1500, 1600)

        self.check_and_update_status(index)

        if self.all_bots_done():
            return
        elif self.is_char_done(index):
            print("character already done, switching to next")
            await self.switch_to_char((index + 1) % len(self.roster))
        elif check_image_on_screen(
            "./image_references/alreadyConnected.png", confidence=0.85
        ):
            print("character already connected")
            pydirectinput.press("esc")
            await rand_sleep(500, 600)
            pydirectinput.press("esc")
            await rand_sleep(500, 600)
        else:
            await left_click_at_position((1030, 700))
            await rand_sleep(1000, 1100)
            await left_click_at_position((920, 590))
            await rand_sleep(1000, 1100)

            await rand_sleep(10000, 12000)
            if self.config["GFN"]:
                await rand_sleep(8000, 9000)

    def check_and_update_status(self, index: int):
        """
        Detect what tasks have been completed based on the character
        status on the ESC menu screen and update accordingly.

        Args:
            index (int): Index of the character to update.
        """
        for bot in self.running_bots:
            if isinstance(bot, ChaosBot):
                bot.remaining_tasks[index] = max(
                    0, bot.remaining_tasks[index] - check_chaos_completed()
                )
            if isinstance(bot, KurzanFrontBot):
                bot.remaining_tasks[index] = max(
                    0, bot.remaining_tasks[index] - check_kurzan_front_completed()
                )
            if isinstance(bot, UnaBot):
                bot.remaining_tasks[index] = max(
                    0, bot.remaining_tasks[index] - check_unas_completed()
                )


async def do_city_repair() -> None:
    """
    With the character standing next to a repair NPC, repairs armor.
    """
    if check_image_on_screen(
        "./image_references/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        print("repairing")
        pydirectinput.press(get_config("interact"))
        await rand_sleep(600, 700)
        pydirectinput.moveTo(x=1057, y=455)
        await rand_sleep(600, 700)
        pydirectinput.click(button="left")
        await rand_sleep(600, 700)
        pydirectinput.press("esc")
        await rand_sleep(1500, 1900)


async def clear_notifs() -> None:
    """
    Gets rid of any quest and/or level up notifications that appear below the center of the screen.
    """
    match find_image_center(
        "./image_references/quest.png", region=CLEAR_NOTIFS_REGION, confidence=0.8
    ):
        case x, y:
            print("clear quest notification")
            await left_click_at_position((x, y))
            await rand_sleep(800, 900)
            pydirectinput.press("esc")
            await rand_sleep(800, 900)

    match find_image_center(
        "./image_references/leveledup.png", region=CLEAR_NOTIFS_REGION, confidence=0.8
    ):
        case x, y:
            print("clear level")
            await left_click_at_position((x, y))
            await rand_sleep(800, 900)
            pydirectinput.press("esc")
            await rand_sleep(800, 900)


def check_unas_completed() -> int:
    """
    When viewing character status in ESC menu, check how many una tasks have been completed.

    Does not account for task limit increases.

    Returns:
        int: The number of unas completed on the currently selected character. 0 if unas icon
            not detected.
    """
    una_icon = find_image_center(
        "./image_references/unaIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.75,
    )
    if una_icon is not None:
        x, y = una_icon
        for i in range(4):
            if check_image_on_screen(
                f"./image_references/{i}.png",
                region=(x + 180, y - 10, 25, 21),
                confidence=0.95,
            ):
                print(f"{3 - i} una(s) completed")
                return 3 - i
    print("unable to detect unas")
    return 0


def check_chaos_completed() -> int:
    """
    When viewing character status in ESC menu, check how many chaos runs have been completed.

    Returns:
        int: The number of chaos dungeons completed on the currently selected character.
            0 if chaos icon not detected.
    """
    chaos_icon = find_image_center(
        "./image_references/chaosIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.75,
    )
    if chaos_icon is not None:
        x, y = chaos_icon
        if check_image_on_screen(
            "./image_references/100.png",
            region=(x + 180, y - 10, 25, 21),
            confidence=0.75,
        ):
            print("no chaos runs completed")
            return 0
        if check_image_on_screen(
            "./image_references/50.png",
            region=(x + 180, y - 10, 25, 21),
            confidence=0.75,
        ):
            print("one chaos run completed")
            return 1
        if check_image_on_screen(
            "./image_references/0.png",
            region=(x + 180, y - 10, 25, 21),
            confidence=0.75,
        ):
            print("both chaos runs completed")
            return 2
    print("unable to detect chaos")
    return 0


def check_kurzan_front_completed() -> int:
    """
    When viewing character status in ESC menu, check if Kurzan Front has been cleared.

    Returns:
        int: The number of Kurzan Front completed on the currently selected character.
            0 if Kurzan Front icon not detected.
    """
    kurzan_front_icon = find_image_center(
        "./image_references/kurzanFrontIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.65,
    )
    if kurzan_front_icon is not None:
        x, y = kurzan_front_icon
        if check_image_on_screen(
            "./image_references/100.png",
            region=(x + 180, y - 10, 25, 21),
            confidence=0.75,
        ):
            print("kurzan front not completed")
            return 0
        if check_image_on_screen(
            "./image_references/0.png",
            region=(x + 180, y - 10, 25, 21),
            confidence=0.75,
        ):
            print("kurzan front completed")
            return 1
        print("cant detect aura")
    else:
        print("unable to detect kurzan front icon")
    return 0
