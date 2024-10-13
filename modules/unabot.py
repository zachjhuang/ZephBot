from .taskbot import TaskBot
from configs.config import config

from .menuNav import restartCheck
from .menuNav import toggleMenu, waitForMenuLoaded, waitForOverworldLoaded

from .utilities import Position
from .utilities import mouseMoveTo, leftClickAtPosition
from .utilities import checkImageOnScreen, findImageCenter, findAndClickImage
from .utilities import randSleep

import pydirectinput
import pyautogui

SCREEN_CENTER_REGION = (685, 280, 600, 420)


class UnaBot(TaskBot):
    def __init__(self, roster):
        super().__init__(roster)
        self.remainingTasks: list[int] = [
            len(char["unas"].split()) if char["unas"] is not None else 0
            for char in self.roster
        ]

    def doTasks(self) -> None:
        """
        Accepts favorited daily unas and completes according to roster configuration.
        """
        if self.doneOnCurrentChar():
            return
        randSleep(1000, 2000)
        print("accepting dailies")
        acceptDailies()
        restartCheck()
        unas = self.roster[self.curr]["unas"]
        if "lopang" in unas:
            restartCheck()
            if bifrostGoTo("lopangIsland"):
                doLopang()
                self.remainingTasks[self.curr] -= 3

        if "mokomoko" in unas:
            restartCheck()
            if bifrostGoTo("mokomoko"):
                doMokomokoUna()
                self.remainingTasks[self.curr] -= 1

        if "bleakNightFog" in unas:
            restartCheck()
            if bifrostGoTo("bleakNightFog"):
                doBleakNightFogUna()
                self.remainingTasks[self.curr] -= 1

        if "prehilia" in unas:
            restartCheck()
            if bifrostGoTo("prehilia"):
                doPrehiliaUna()
                self.remainingTasks[self.curr] -= 1

        if "hesteraGarden" in unas:
            restartCheck()
            if bifrostGoTo("hesteraGarden"):
                doHesteraGardenUna()
                self.remainingTasks[self.curr] -= 1

        if "writersLife" in unas:
            restartCheck()
            if bifrostGoTo("writersLife"):
                doWritersLifeUna()
                self.remainingTasks[self.curr] -= 1

        if "sageTower" in unas:
            restartCheck()
            if bifrostGoTo("sageTower"):
                doSageTowerUna()
                self.remainingTasks[self.curr] -= 1

        if "ghostStory" in unas:
            restartCheck()
            if bifrostGoTo("ghostStory"):
                doGhostStoryUna()
                self.remainingTasks[self.curr] -= 1

        if "southKurzan" in unas:
            restartCheck()
            if bifrostGoTo("southKurzan"):
                doSouthKurzanUna()
                self.remainingTasks[self.curr] -= 1

        print("unas completed")


def acceptDailies() -> None:
    """
    Open una menu and accept all favorited dailies.
    """
    toggleMenu("unas")
    waitForMenuLoaded("unas")
    # switch to daily tab
    if not checkImageOnScreen("./screenshots/dailyTabActive.png", confidence=0.95):
        mouseMoveTo(x=550, y=255)
        randSleep(100, 200)
        pydirectinput.click(button="left")
        randSleep(500, 600)
    # toggle dropdown and swap to favorites
    if not checkImageOnScreen("./screenshots/addedToFavorites.png", confidence=0.95):
        mouseMoveTo(x=632, y=316)
        randSleep(100, 200)
        pydirectinput.click(button="left")
        randSleep(1000, 1100)
        mouseMoveTo(x=634, y=337)
        randSleep(100, 200)
        pydirectinput.click(button="left")
        randSleep(500, 600)
        pydirectinput.click(button="left")
        randSleep(500, 600)
        pydirectinput.click(button="left")
        randSleep(500, 600)
        mouseMoveTo(x=548, y=404)
        randSleep(100, 200)
        pydirectinput.click(button="left")
        randSleep(500, 600)
    # if 3x completed unas detected, skip and return false
    randSleep(500, 600)
    # if checkImageOnScreen("./screenshots/unasCompleted.png", confidence=0.75):
    #     print("character has already ran unas")
    #     toggleMenu("unas")
    #     return False

    # click all accept buttons
    acceptButtonRegions = list(
        pyautogui.locateAllOnScreen(
            "./screenshots/acceptUna.png", region=(1165, 380, 80, 330), confidence=0.85
        )
    )
    for region in acceptButtonRegions:
        leftClickAtPosition(Position(region.left, region.top))
        randSleep(400, 500)

    toggleMenu("unas")
    randSleep(800, 900)


def doLopang() -> None:
    """Does 3 lopang dailies (Shushire -> Arthetine -> Vern)."""
    walkLopang()
    for lopangLocation in ["Shushire", "Arthetine", "Vern"]:
        randSleep(1500, 1600)
        bifrostGoTo("lopang" + lopangLocation)
        restartCheck()
        spamInteract(6000)


def doBleakNightFogUna() -> None:
    pydirectinput.press("f5")
    randSleep(800, 900)
    pydirectinput.press("f6")
    randSleep(1800, 1900)
    claimCompletedQuest()


def doPrehiliaUna() -> None:
    toggleMenu("unaTaskCombatPreset")

    pydirectinput.press(config["prehiliaEmoteSlot"])
    spamInteract(8000)

    toggleMenu("defaultCombatPreset")


def doHesteraGardenUna() -> None:
    toggleMenu("unaTaskCombatPreset")

    pydirectinput.press(config["hesteraGardenEmoteSlot"])
    randSleep(140000, 141000)
    claimCompletedQuest()
    randSleep(300, 400)

    toggleMenu("defaultCombatPreset")


def doWritersLifeUna() -> None:
    randSleep(5000, 5100)
    toggleMenu("unaTaskCombatPreset")
    spamInteract(4000)
    pydirectinput.click(x=1100, y=750, button=config["move"])
    randSleep(1500, 1600)
    pydirectinput.click(x=1100, y=750, button=config["move"])
    randSleep(1500, 1600)
    pydirectinput.press(config["writersLifeEmoteSlot"])
    randSleep(9000, 9100)
    pydirectinput.click(x=800, y=600, button=config["move"])
    randSleep(1500, 1600)
    spamInteract(10000)
    pydirectinput.click(x=880, y=250, button=config["move"])
    randSleep(1500, 1600)
    pydirectinput.click(x=880, y=250, button=config["move"])
    randSleep(1500, 1600)
    spamInteract(4000)
    randSleep(300, 400)
    toggleMenu("defaultCombatPreset")


def doSageTowerUna() -> None:
    for _ in range(10):
        spamInteract(1000)
        if checkImageOnScreen(
            "./screenshots/sageTowerCompleted.png",
            region=(1700, 220, 100, 150),
            confidence=0.65,
        ):
            break
    mouseMoveTo(x=1560, y=540)
    randSleep(500, 600)
    pydirectinput.click(x=1560, y=540, button=config["move"])
    randSleep(500, 600)
    spamInteract(3000)


def doGhostStoryUna() -> None:
    for _ in range(15):
        spamInteract(1000)
        if checkImageOnScreen(
            "./screenshots/ghostStoryF5.png",
            region=(1575, 440, 80, 450),
            confidence=0.85,
        ):
            break
    pydirectinput.press("f5")
    randSleep(200, 300)
    pydirectinput.press("f6")
    randSleep(200, 300)
    claimCompletedQuest()
    randSleep(300, 400)


def doSouthKurzanUna() -> None:
    toggleMenu("unaTaskCombatPreset")

    pydirectinput.press(config["southKurzanPoseSlot"])
    randSleep(14000, 14100)

    toggleMenu("defaultCombatPreset")

    mouseMoveTo(x=650, y=180)
    randSleep(500, 600)
    pydirectinput.click(x=650, y=180, button="left")
    randSleep(2500, 2600)
    pydirectinput.click(x=650, y=180, button="left")
    randSleep(2500, 2600)
    spamInteract(4000)


def doMokomokoUna() -> None:
    spamInteract(4000)
    mouseMoveTo(x=416, y=766)
    randSleep(500, 600)
    pydirectinput.click(x=416, y=766, button="left")
    randSleep(5500, 5600)

    mouseMoveTo(x=960, y=770)
    randSleep(500, 600)
    pydirectinput.click(x=960, y=770, button=config["move"])
    randSleep(1500, 1600)
    pydirectinput.press(config["interact"])
    randSleep(5500, 5600)

    mouseMoveTo(x=1360, y=900)
    randSleep(500, 600)
    pydirectinput.click(x=1360, y=900, button=config["move"])
    randSleep(1500, 1600)
    pydirectinput.press(config["interact"])
    randSleep(5500, 5600)

    mouseMoveTo(x=960, y=330)
    randSleep(1500, 1600)
    pydirectinput.click(x=980, y=280, button=config["move"])
    randSleep(1500, 1600)
    pydirectinput.click(x=980, y=280, button=config["move"])
    randSleep(1500, 1600)
    spamInteract(4000)
    randSleep(1500, 1600)


def walkLopang() -> None:
    """Interacts with and walks to all 3 lopang terminals."""
    randSleep(1000, 2000)
    print("walking lopang")
    # right terminal
    spamInteract(2000)
    # walk to middle terminal
    walkTo(315, 473, 1500)
    walkTo(407, 679, 1300)
    walkTo(584, 258, 1000)
    walkTo(1043, 240, 1200)
    walkTo(1339, 246, 1300)
    walkTo(1223, 406, 800)
    walkTo(1223, 406, 800)
    walkTo(1263, 404, 1300)
    # middle terminal
    spamInteract(500)
    # walk to left terminal
    walkTo(496, 750, 1200)
    walkTo(496, 750, 1200)
    walkTo(496, 750, 1200)
    walkTo(753, 687, 800)
    walkTo(753, 687, 800)
    walkTo(674, 264, 800)
    walkTo(573, 301, 1200)
    walkTo(820, 240, 1300)
    # left terminal
    spamInteract(500)
    randSleep(1000, 2000)


def claimCompletedQuest() -> None:
    leftClickAtPosition(Position(x=1700, y=430))
    randSleep(1000, 1100)
    findAndClickImage("completeQuest", confidence=0.85)


def bifrostGoTo(location: str) -> bool:
    """
    Attempts to bifrost to location.

    Return false if bifrost not found or on cooldown.

    Return true if bifrost to location is successful.
    """
    print(f"bifrost to: {location}")
    if not checkImageOnScreen("./screenshots/menus/bifrostMenu.png", confidence=0.85):
        toggleMenu("bifrost")
    waitForMenuLoaded("bifrost")
    bifrost = findImageCenter(
        f"./screenshots/bifrosts/{location}Bifrost.png", confidence=0.80
    )
    if bifrost is None:
        print(f"{location} bifrost not found, skipping")
        toggleMenu("bifrost")
        return False
    x, y = bifrost
    mouseMoveTo(x=(x + 280), y=(y - 25))
    randSleep(300, 400)
    pydirectinput.click(button="left")
    randSleep(500, 600)
    pydirectinput.click(button="left")
    randSleep(1500, 1600)

    # return false if bifrost on cooldown
    if checkBifrostOnCooldown():
        pydirectinput.press("esc")
        randSleep(1500, 1600)
        pydirectinput.press("esc")
        randSleep(1500, 1600)
        return False
    else:
        while True:
            okButton = findImageCenter(
                "./screenshots/ok.png",
                confidence=0.75,
                region=SCREEN_CENTER_REGION,
            )
            if okButton is not None:
                x, y = okButton
                mouseMoveTo(x=x, y=y)
                randSleep(2000, 2100)
                pydirectinput.click(x=x, y=y, button="left")
                randSleep(2000, 2100)
                break
            randSleep(300, 400)
    randSleep(10000, 12000)

    # wait until loaded
    waitForOverworldLoaded()
    return True


def checkBifrostOnCooldown() -> bool:
    """Return false if bifrost move confirmation costs silver."""
    silver1k = findImageCenter(
        "./screenshots/silver1k.png",
        confidence=0.75,
        region=SCREEN_CENTER_REGION,
    )
    return silver1k is None


def walkTo(x: int, y: int, ms: int) -> None:
    """Move to specified pixel coordinate with millisecond delay."""
    mouseMoveTo(x=x, y=y)
    randSleep(100, 100)
    pydirectinput.click(x=x, y=y, button=config["move"])
    randSleep(ms, ms)


def spamInteract(msDuration: int) -> None:
    """Presses interact key for approximately the given duration in milliseconds."""
    timeCount = msDuration / 100
    while timeCount != 0:
        pydirectinput.press(config["interact"])
        randSleep(90, 120)
        timeCount = timeCount - 1
