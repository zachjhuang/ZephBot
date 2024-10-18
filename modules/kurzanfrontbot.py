from modules.chaosbot import (
    ChaosBot,
    castAbility,
    moveInDirection,
    doAuraRepair,
    waitForChaosFloorLoading,
)
from modules.minimap import Minimap
from configs.skills import skills
from configs.config import config

from modules.menuNav import restartCheck
from modules.menuNav import toggleMenu, waitForMenuLoaded, quitChaos

from modules.utilities import Position, resetException, timeoutException
from modules.utilities import randSleep
from modules.utilities import mouseMoveTo, leftClickAtPosition
from modules.utilities import (
    checkImageOnScreen,
    findImageCenter,
    findAndClickImage,
)

import time
import pydirectinput
import pyautogui
import statistics

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

CHAOS_CLICKABLE_REGION = (460, 290, 1000, 500)
CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)

ABIDOS_1_POS = Position(830, 670)
ABIDOS_2_POS = Position(965, 590)


class KurzanFrontBot(ChaosBot):
    def __init__(self, roster):
        super().__init__(roster)
        self.remainingTasks: list[int] = [
            (
                1
                if char["chaosItemLevel"] is not None and char["chaosItemLevel"] >= 1640
                else 0
            )
            for char in self.roster
        ]
        self.targetXs = [960]
        self.targetYs = [540]

    def doTasks(self) -> None:
        if self.remainingTasks[self.curr] == 0:
            return

        toggleMenu("defaultCombatPreset")

        enterKurzanFront(self.roster[self.curr]["chaosItemLevel"])
        waitForChaosFloorLoading()
        self.runStartTime = int(time.time())
        print(f"kurzan front loaded")

        if config["auraRepair"]:
            doAuraRepair(False)

        leftClickAtPosition(SCREEN_CENTER_POS)
        randSleep(1500, 1600)

        self.useSkills()
        finishTime = int(time.time())
        self.updateAndPrintMetrics(finishTime - self.runStartTime)

        quitChaos()

    def useSkills(self) -> None:
        """
        Moves character and uses skills. Behavior changes depending on the floor.
        """
        minimap = Minimap()
        currentClass = self.roster[self.curr]["class"]
        characterSkills = self.skills[currentClass]
        normalSkills = [
            skill for skill in characterSkills if skill["skillType"] == "normal"
        ]
        awakeningSkill = [
            skill for skill in characterSkills if skill["skillType"] == "awakening"
        ][0]
        awakeningUsed = False
        jumped = False
        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
        while True:
            self.diedCheck()
            self.healthCheck()
            restartCheck()
            self.timeoutCheck()

            # cast sequence
            for i in range(0, len(normalSkills)):
                if checkDungeonFinish():
                    print("KurzanFront finish screen")
                    return
                self.diedCheck()
                self.healthCheck()
                if not jumped and checkProgressForJump() and minimap.checkJump():
                    while not checkImageOnScreen(
                        "./screenshots/chaos/jump.png",
                        region=(940, 320, 40, 40),
                        confidence=0.85,
                    ):
                        minimap.checkJump()
                        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                        moveInDirection(x, y, int(moveDuration / 3))
                        randSleep(100, 150)
                    pydirectinput.press("g")
                    print("jumped")
                    jumped = True

                if minimap.checkBuff() or minimap.checkBoss() or minimap.checkElite():
                    print(f"x: {x}, y: {y}")
                    self.targetXs.append(x)
                    self.targetYs.append(y)
                    x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                    moveInDirection(x, y, int(moveDuration / 2))
                else:
                    meanX = int(statistics.mean(self.targetXs))
                    meanY = int(statistics.mean(self.targetYs))
                    print(f"mean x: {meanX}")
                    print(f"mean y: {meanY}")
                    moveInDirection(
                        int(statistics.mean(self.targetXs)),
                        int(statistics.mean(self.targetYs)),
                        int(moveDuration / 3),
                    )

                self.performClassSpecialty(
                    self.roster[self.curr]["class"], i, normalSkills
                )
                castAbility(x, y, normalSkills[i])


def checkProgressForJump():
    im = pyautogui.screenshot()
    r, _g, _b = im.getpixel((89, 292))
    if r > 130:
        return True


def enterKurzanFront(ilvl: int) -> None:
    """
    Enters specified Kurzan Front level.
    """
    toggleMenu("content")
    waitForMenuLoaded("kazerosWarMap")

    if ilvl == 1640:
        leftClickAtPosition(ABIDOS_1_POS)
    elif ilvl == 1660:
        leftClickAtPosition(ABIDOS_2_POS)

    randSleep(1200, 1300)
    findAndClickImage("enterButton", region=(1300, 750, 210, 40), confidence=0.75)
    randSleep(800, 900)
    findAndClickImage("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    randSleep(800, 900)


def checkDungeonFinish() -> bool:
    """
    Returns true if chaos finish screen detected and clears the finish overlay. Otherwise returns false.
    """
    clearOk = findImageCenter(
        "./screenshots/chaos/kurzanFrontClearOK.png",
        confidence=0.65,
        region=(880, 820, 150, 70),
    )
    if clearOk is not None:
        x, y = clearOk
        mouseMoveTo(x=x, y=y)
        randSleep(800, 900)
        pydirectinput.click(x=x, y=y, button="left")
        randSleep(200, 300)
        pydirectinput.click(x=x, y=y, button="left")
        randSleep(200, 300)
    return clearOk is not None
