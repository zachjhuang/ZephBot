import pydirectinput

from modules.menu_nav import toggle_menu, wait_for_menu_load
from modules.task_bot import TaskBot
from modules.utilities import (
    check_image_on_screen,
    find_and_click_image,
    left_click_at_position,
    random_sleep,
)

SCREEN_CENTER_REGION = (685, 280, 600, 420)
SUPPORT_RESEARCH_REGION = (1164, 455, 106, 20)
CAN_SUPPORT_RESEARCH_REGION = (761, 566, 177, 29)

DONATE_MENU_POS = (1455, 350)
DONATE_SILVER_POS = (760, 542)

RESEARCH_CONFIRM_POS = (920, 705)


class GuildBot(TaskBot):
    """
    TaskBot child class for guild check-in, silver donation, and research support.
    """

    def __init__(self, roster, config) -> None:
        super().__init__(roster, config)
        self.remaining_tasks: list[int] = [
            1 if char["guildDonation"] else 0 for char in self.roster
        ]

    def do_tasks(self) -> None:
        """
        Opens guild menu and does check-in, donation, and available research.
        """
        if self.done_on_curr_char():
            return
        toggle_menu("guild")
        wait_for_menu_load("guild")

        accept_checkin()
        donate_silver()
        support_research()

        random_sleep(500, 600)
        toggle_menu("guild")
        self.remaining_tasks[self.curr] = 0


def accept_checkin() -> None:
    random_sleep(500, 600)
    find_and_click_image("ok", region=SCREEN_CENTER_REGION, confidence=0.75)


def donate_silver() -> None:
    random_sleep(500, 600)
    left_click_at_position(DONATE_MENU_POS)
    random_sleep(500, 600)
    left_click_at_position(DONATE_SILVER_POS)
    pydirectinput.press("esc")
    random_sleep(500, 600)


def support_research() -> None:
    find_and_click_image(
        "supportResearch", region=SUPPORT_RESEARCH_REGION, confidence=0.75
    )
    random_sleep(500, 600)
    if check_image_on_screen(
        "./screenshots/canSupportResearch.png",
        region=CAN_SUPPORT_RESEARCH_REGION,
        confidence=0.75,
    ):
        find_and_click_image(
            "canSupportResearch",
            region=CAN_SUPPORT_RESEARCH_REGION,
            confidence=0.75,
        )
        random_sleep(500, 600)
        left_click_at_position(RESEARCH_CONFIRM_POS)
    elif check_image_on_screen(
        "./screenshots/alreadySupportedResearch.png",
        region=CAN_SUPPORT_RESEARCH_REGION,
        confidence=0.75,
    ):
        pydirectinput.press("esc")
