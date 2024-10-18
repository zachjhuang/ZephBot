import pydirectinput

from modules.menuNav import toggleMenu, waitForMenuLoaded
from modules.taskbot import TaskBot
from modules.utilities import (
    Position,
    checkImageOnScreen,
    findAndClickImage,
    leftClickAtPosition,
    randSleep,
)

SCREEN_CENTER_REGION = (685, 280, 600, 420)
SUPPORT_RESEARCH_REGION = (1164, 455, 106, 20)
CAN_SUPPORT_RESEARCH_REGION = (761, 566, 177, 29)

DONATE_MENU_POS = Position(1455, 350)
DONATE_SILVER_POS = Position(760, 542)

RESEARCH_CONFIRM_POS = Position(920, 705)


class GuildBot(TaskBot):
    def __init__(self, roster) -> None:
        super().__init__(roster)
        self.remainingTasks: list[int] = [
            1 if char["guildDonation"] else 0 for char in self.roster
        ]

    def doTasks(self) -> None:
        """
        Opens guild menu and does check-in, donation, and available research.
        """
        if self.doneOnCurrentChar():
            return
        toggleMenu("guild")
        waitForMenuLoaded("guild")

        randSleep(500, 600)
        findAndClickImage("ok", region=SCREEN_CENTER_REGION, confidence=0.75)
        randSleep(500, 600)
        leftClickAtPosition(DONATE_MENU_POS)
        randSleep(500, 600)
        leftClickAtPosition(DONATE_SILVER_POS)

        pydirectinput.press("esc")
        randSleep(500, 600)

        findAndClickImage(
            "supportResearch", region=SUPPORT_RESEARCH_REGION, confidence=0.75
        )
        randSleep(500, 600)
        if checkImageOnScreen(
            "./screenshots/canSupportResearch.png",
            region=CAN_SUPPORT_RESEARCH_REGION,
            confidence=0.75,
        ):
            findAndClickImage(
                "canSupportResearch",
                region=CAN_SUPPORT_RESEARCH_REGION,
                confidence=0.75,
            )
            randSleep(500, 600)
            leftClickAtPosition(RESEARCH_CONFIRM_POS)
        elif checkImageOnScreen(
            "./screenshots/alreadySupportedResearch.png",
            region=CAN_SUPPORT_RESEARCH_REGION,
            confidence=0.75,
        ):
            pydirectinput.press("esc")
        randSleep(500, 600)
        toggleMenu("guild")
        self.remainingTasks[self.curr] = 0
