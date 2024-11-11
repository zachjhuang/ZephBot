# pylint: disable=missing-module-docstring
import pydirectinput

from modules.menu_nav import toggle_menu, wait_for_menu_load
from modules.task_bot import TaskBot
from modules.utilities import (
    check_image_on_screen,
    find_and_click_image,
    left_click_at_position,
    rand_sleep,
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

    async def do_tasks(self) -> None:
        """
        Opens guild menu and does check-in, donation, and available research.
        """
        if self.done_on_curr_char():
            return
        await toggle_menu("guild")
        await wait_for_menu_load("guild")

        await accept_checkin()
        await donate_silver()
        await support_research()

        await rand_sleep(500, 600)
        await toggle_menu("guild")
        self.remaining_tasks[self.curr] = 0


# pylint: disable=missing-function-docstring
async def accept_checkin() -> None:
    await rand_sleep(500, 600)
    await find_and_click_image("ok", region=SCREEN_CENTER_REGION, confidence=0.75)


async def donate_silver() -> None:
    await rand_sleep(500, 600)
    await left_click_at_position(DONATE_MENU_POS)
    await rand_sleep(500, 600)
    await left_click_at_position(DONATE_SILVER_POS)
    pydirectinput.press("esc")
    await rand_sleep(500, 600)


async def support_research() -> None:
    await find_and_click_image(
        "supportResearch", region=SUPPORT_RESEARCH_REGION, confidence=0.75
    )
    await rand_sleep(500, 600)
    if check_image_on_screen(
        "./image_references/canSupportResearch.png",
        region=CAN_SUPPORT_RESEARCH_REGION,
        confidence=0.75,
    ):
        await find_and_click_image(
            "canSupportResearch",
            region=CAN_SUPPORT_RESEARCH_REGION,
            confidence=0.75,
        )
        await rand_sleep(500, 600)
        await left_click_at_position(RESEARCH_CONFIRM_POS)
    elif check_image_on_screen(
        "./image_references/alreadySupportedResearch.png",
        region=CAN_SUPPORT_RESEARCH_REGION,
        confidence=0.75,
    ):
        pydirectinput.press("esc")
