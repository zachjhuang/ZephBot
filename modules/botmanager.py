from configs.config import config
from configs.roster import roster

from .chaosbot import ChaosBot
from .unabot import UnaBot
from .guildbot import GuildBot
from .taskbot import TaskBot
from .kurzanfrontbot import KurzanFrontBot

import pydirectinput
import math

from .utilities import Position
from .utilities import mouseMoveTo, leftClickAtPosition
from .utilities import checkImageOnScreen, findImageCenter
from .utilities import randSleep

from .menuNav import restartCheck, waitForOverworldLoaded

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

MINIMAP_REGION = (1655, 170, 240, 200)
MINIMAP_CENTER_X = 1772
MINIMAP_CENTER_Y = 272

CHARACTER_STATUS_ICON_REGION = (1280, 440, 30, 230)
CHARACTER_SELECT_POS = [
    Position(760, 440),
    Position(960, 440),
    Position(1160, 440),
    Position(760, 530),
    Position(960, 530),
    Position(1160, 530),
    Position(760, 620),
    Position(960, 620),
    Position(1160, 620),
]


class BotManager:
    def __init__(self, doChaos: bool, doKurzanFront: bool, doUnas: bool, doGuild: bool) -> None:
        self.curr = 0

        self.runningBotList: list[TaskBot] = []
        if doChaos:
            self.runningBotList.append(ChaosBot(roster))
        if doKurzanFront:
            self.runningBotList.append(KurzanFrontBot(roster))
        if doUnas:
            self.runningBotList.append(UnaBot(roster))
        if doGuild:
            self.runningBotList.append(GuildBot(roster))

    def allBotsFinished(self) -> bool:
        for bot in self.runningBotList:
            if not bot.isCompleted():
                return False
        return True

    def run(self) -> None:
        restartCheck()
        self.switchToCharacter(0)

        if config["auraRepair"] == False:
            doCityRepair()

        while not self.allBotsFinished():
            restartCheck()
            waitForOverworldLoaded()

            if config["auraRepair"] == False:
                doCityRepair()

            for bot in self.runningBotList:
                bot.doTasks()

            restartCheck()
            nextIndex = (self.curr + 1) % len(roster)
            print(f"character {self.curr} is done, switching to: {nextIndex}")
            self.switchToCharacter(nextIndex)

    def updateCurrentChar(self, char: int) -> None:
        for bot in self.runningBotList:
            bot.setCurrentCharacter(char)

    def isCharacterDone(self, char: int) -> None:
        return sum([bot.remainingTasks[char] for bot in self.runningBotList]) == 0

    # def runCharTasks(self) -> None:
    #     for bot in self.runningBotList:
    #         bot.doTasks()

    def switchToCharacter(self, index: int) -> None:
        """Opens ESC menu and switches to character designated by index."""
        self.curr = index
        self.updateCurrentChar(index)
        randSleep(500, 600)
        print("----------------------------")
        for bot in self.runningBotList:
            print(f"{bot.__class__.__name__}: {bot.remainingTasks}")
        print("----------------------------")
        print("switching to {}".format(index))
        while not checkImageOnScreen(
            "./screenshots/menus/gameMenu.png", confidence=0.7
        ):
            pydirectinput.press("esc")
            randSleep(1000, 1100)
        print("game menu detected")
        randSleep(800, 900)
        leftClickAtPosition(Position(540, 700))
        randSleep(800, 900)

        for _ in range(4):
            leftClickAtPosition(Position(1270, 430))
            randSleep(200, 300)

        if index > 8:
            for i in range(math.floor(index / 3) - 2):
                leftClickAtPosition(Position(1267, 638))
                randSleep(200, 300)

        positionIndex = index if index < 9 else index - 3 * ((index - 6) // 3)
        leftClickAtPosition(CHARACTER_SELECT_POS[positionIndex])
        randSleep(1500, 1600)

        for bot in self.runningBotList:
            if isinstance(bot, ChaosBot):
                bot.remainingTasks[index] = max(
                    0, bot.remainingTasks[index] - checkChaosCompleted()
                )
            if isinstance(bot, KurzanFrontBot):
                bot.remainingTasks[index] = max(
                    0, bot.remainingTasks[index] - checkKurzanFrontCompleted()
                )
            if isinstance(bot, UnaBot):
                bot.remainingTasks[index] = max(
                    0, bot.remainingTasks[index] - checkUnasCompleted()
                )
        
        if self.allBotsFinished():
            return
        elif self.isCharacterDone(index):
            print("character already done, switching to next")
            self.switchToCharacter((index + 1) % len(roster))
        elif checkImageOnScreen("./screenshots/alreadyConnected.png", confidence=0.85):
            print("character already connected")
            pydirectinput.press("esc")
            randSleep(500, 600)
            pydirectinput.press("esc")
            randSleep(500, 600)
        else:
            leftClickAtPosition(Position(1030, 700))
            randSleep(1000, 1100)
            leftClickAtPosition(Position(920, 590))
            randSleep(1000, 1100)

            randSleep(10000, 12000)
            if config["GFN"] == True:
                randSleep(8000, 9000)


def doCityRepair() -> None:
    # for non-aura users: MUST have your character parked near a repairer in city before starting the script
    # Check if repair needed
    if checkImageOnScreen(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        print("repairing")
        pydirectinput.press(config["interact"])
        randSleep(600, 700)
        mouseMoveTo(x=1057, y=455)
        randSleep(600, 700)
        pydirectinput.click(button="left")
        randSleep(600, 700)
        pydirectinput.press("esc")
        randSleep(1500, 1900)


def clearQuest() -> None:
    quest = findImageCenter(
        "./screenshots/quest.png", region=(815, 600, 250, 200), confidence=0.9
    )
    leveledup = findImageCenter(
        "./screenshots/leveledup.png", region=(815, 600, 250, 200), confidence=0.9
    )
    gameMenu = findImageCenter(
        "./screenshots/menus/gameMenu.png", region=SCREEN_CENTER_REGION, confidence=0.95
    )
    if gameMenu is not None:
        print("game menu detected")
        pydirectinput.press("esc")
        randSleep(1800, 1900)
    if quest is not None:
        print("clear quest")
        x, y = quest
        mouseMoveTo(x=x, y=y)
        randSleep(1800, 1900)
        pydirectinput.click(button="left")
        randSleep(1800, 1900)
        pydirectinput.press("esc")
        randSleep(1800, 1900)
    elif leveledup is not None:
        print("clear level")
        x, y = leveledup
        mouseMoveTo(x=x, y=y)
        randSleep(1800, 1900)
        pydirectinput.click(button="left")
        randSleep(1800, 1900)
        pydirectinput.press("esc")
        randSleep(1800, 1900)


def checkUnasCompleted() -> int:
    unaIcon = findImageCenter(
        "./screenshots/unaIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.75,
    )
    if unaIcon is not None:
        x, y = unaIcon
        for i in range(4):
            if checkImageOnScreen(
                f"./screenshots/{i}.png",
                region=(x + 180, y - 10, 25, 21),
                confidence=0.95,
            ):
                print(f"{3 - i} una(s) completed")
                return 3 - i
    print("unable to detect unas")
    return 0


def checkChaosCompleted() -> int:
    chaosIcon = findImageCenter(
        "./screenshots/chaosIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.75,
    )
    if chaosIcon is not None:
        x, y = chaosIcon
        if checkImageOnScreen(
            "./screenshots/100.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("no chaos runs completed")
            return 0
        if checkImageOnScreen(
            "./screenshots/50.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("one chaos run completed")
            return 1
        if checkImageOnScreen(
            "./screenshots/0.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("both chaos runs completed")
            return 2
    print("unable to detect chaos")
    return 0

def checkKurzanFrontCompleted() -> int:
    kurzanFrontIcon = findImageCenter(
        "./screenshots/kurzanFrontIcon.png",
        region=CHARACTER_STATUS_ICON_REGION,
        confidence=0.65,
    )
    if kurzanFrontIcon is not None:
        x, y = kurzanFrontIcon
        if checkImageOnScreen(
            "./screenshots/100.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("kurzan front not completed")
            return 0
        if checkImageOnScreen(
            "./screenshots/0.png", region=(x + 180, y - 10, 25, 21), confidence=0.75
        ):
            print("kurzan front completed")
            return 1
        print("cant detect aura")
    else: 
        print("unable to detect kurzan front icon")
    return 0
