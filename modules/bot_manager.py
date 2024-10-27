import math

import pydirectinput

from configs.config import config
from configs.roster import roster
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
    mouse_move_to,
    random_sleep,
)

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_REGION = (685, 280, 600, 420)
CLEAR_NOTIFS_REGION = (880, 720, 16, 40)

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
    def __init__(
        self, do_chaos: bool, do_kurzan_front: bool, do_unas: bool, do_guild: bool
    ) -> None:
        self.curr = 0

        self.running_bots: list[TaskBot] = []
        if do_chaos:
            self.running_bots.append(ChaosBot(roster))
        if do_kurzan_front:
            self.running_bots.append(KurzanFrontBot(roster))
        if do_unas:
            self.running_bots.append(UnaBot(roster))
        if do_guild:
            self.running_bots.append(GuildBot(roster))

    def all_bots_done(self) -> bool:
        for bot in self.running_bots:
            if not bot.is_done():
                return False
        return True

    def run(self) -> None:
        restart_check()
        self.switch_to_char(0)

        if config["auraRepair"] == False:
            do_city_repair()

        while not self.all_bots_done():
            restart_check()
            wait_overworld_load()

            if config["auraRepair"] == False:
                do_city_repair()

            for bot in self.running_bots:
                bot.do_tasks()

            restart_check()
            next = (self.curr + 1) % len(roster)
            print(f"character {self.curr} is done, switching to: {next}")
            self.switch_to_char(next)

    def update_curr_char(self, char: int) -> None:
        for bot in self.running_bots:
            bot.set_current_char(char)

    def is_char_done(self, char: int) -> None:
        return sum([bot.remaining_tasks[char] for bot in self.running_bots]) == 0

    # def runCharTasks(self) -> None:
    #     for bot in self.runningBotList:
    #         bot.doTasks()

    def switch_to_char(self, index: int) -> None:
        """Opens ESC menu and switches to character designated by index."""
        self.curr = index
        self.update_curr_char(index)
        random_sleep(500, 600)
        print("----------------------------")
        for bot in self.running_bots:
            print(f"{bot.__class__.__name__}: {bot.remaining_tasks}")
        print("----------------------------")
        print("switching to {}".format(index))
        while not check_image_on_screen(
            "./screenshots/menus/gameMenu.png", confidence=0.7
        ):
            pydirectinput.press("esc")
            random_sleep(1000, 1100)
        print("game menu detected")
        random_sleep(800, 900)
        left_click_at_position((540, 700))
        random_sleep(800, 900)

        for _ in range(4):
            left_click_at_position((1270, 430))
            random_sleep(200, 300)

        if index > 8:
            for i in range(math.floor(index / 3) - 2):
                left_click_at_position((1267, 638))
                random_sleep(200, 300)

        position_index = index if index < 9 else index - 3 * ((index - 6) // 3)
        left_click_at_position(CHARACTER_SELECT_POS[position_index])
        random_sleep(1500, 1600)

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

        if self.all_bots_done():
            return
        elif self.is_char_done(index):
            print("character already done, switching to next")
            self.switch_to_char((index + 1) % len(roster))
        elif check_image_on_screen(
            "./screenshots/alreadyConnected.png", confidence=0.85
        ):
            print("character already connected")
            pydirectinput.press("esc")
            random_sleep(500, 600)
            pydirectinput.press("esc")
            random_sleep(500, 600)
        else:
            left_click_at_position((1030, 700))
            random_sleep(1000, 1100)
            left_click_at_position((920, 590))
            random_sleep(1000, 1100)

            random_sleep(10000, 12000)
            if config["GFN"] == True:
                random_sleep(8000, 9000)


def do_city_repair() -> None:
    # for non-aura users: MUST have your character parked near a repairer in city before starting the script
    # Check if repair needed
    if check_image_on_screen(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        print("repairing")
        pydirectinput.press(config["interact"])
        random_sleep(600, 700)
        mouse_move_to(x=1057, y=455)
        random_sleep(600, 700)
        pydirectinput.click(button="left")
        random_sleep(600, 700)
        pydirectinput.press("esc")
        random_sleep(1500, 1900)


def clear_notifs() -> None:
    match find_image_center(
        "./screenshots/quest.png", region=CLEAR_NOTIFS_REGION, confidence=0.8
    ):
        case x, y:
            print("clear quest notification")
            left_click_at_position((x, y))
            random_sleep(800, 900)
            pydirectinput.press("esc")
            random_sleep(800, 900)

    match find_image_center(
        "./screenshots/leveledup.png", region=CLEAR_NOTIFS_REGION, confidence=0.8
    ):
        case x, y:
            print("clear level")
            left_click_at_position((x, y))
            random_sleep(800, 900)
            pydirectinput.press("esc")
            random_sleep(800, 900)


def check_unas_completed() -> int:
    una_icon = find_image_center(
        "./screenshots/unaIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.75,
    )
    if una_icon is not None:
        x, y = una_icon
        for i in range(4):
            if check_image_on_screen(
                f"./screenshots/{i}.png",
                region=(x + 180, y - 10, 25, 21),
                confidence=0.95,
            ):
                print(f"{3 - i} una(s) completed")
                return 3 - i
    print("unable to detect unas")
    return 0


def check_chaos_completed() -> int:
    chaos_icon = find_image_center(
        "./screenshots/chaosIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.75,
    )
    if chaos_icon is not None:
        x, y = chaos_icon
        if check_image_on_screen(
            "./screenshots/100.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("no chaos runs completed")
            return 0
        if check_image_on_screen(
            "./screenshots/50.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("one chaos run completed")
            return 1
        if check_image_on_screen(
            "./screenshots/0.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("both chaos runs completed")
            return 2
    print("unable to detect chaos")
    return 0


def check_kurzan_front_completed() -> int:
    kurzan_front_icon = find_image_center(
        "./screenshots/kurzanFrontIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.65,
    )
    if kurzan_front_icon is not None:
        x, y = kurzan_front_icon
        if check_image_on_screen(
            "./screenshots/100.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("kurzan front not completed")
            return 0
        if check_image_on_screen(
            "./screenshots/0.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("kurzan front completed")
            return 1
        print("cant detect aura")
    else:
        print("unable to detect kurzan front icon")
    return 0
