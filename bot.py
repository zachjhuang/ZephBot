from config import config
from characters import characters as roster

from chaosbot import ChaosBot
from unabot import UnaBot
from guildbot import GuildBot
from taskbot import TaskBot

import pyautogui
import pydirectinput
import time
import math
import argparse
import keyboard
import os
import platform
import pywintypes, win32con, win32api

from utilities import Position, restartException, resetException
from utilities import mouseMoveTo, leftClickAtPosition
from utilities import checkImageOnScreen, findImageCenter
from utilities import randSleep

from menuNav import restartCheck, toggleMenu

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

CHARACTER_STATUS_ICON_REGION = (1280, 440, 30, 230)

pydirectinput.PAUSE = 0.05

def abortScript():
    os._exit(1)


def main():
    # set_resolution(1920, 1080)
    keyboard.add_hotkey("ctrl+page down", abortScript)

    # Instantiate the parser
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument(
        "--chaos", 
        action="store_true", 
        help="Enables 2x chaos on entire roster"
    )
    parser.add_argument(
        "--unas", 
        action="store_true", 
        help="Enables unas on entire roster"
    )
    parser.add_argument(
        "--guild",
        action="store_true",
        help="Enables guild donation/support on entire roster",
    )
    # parser.add_argument("--cubes", action="store_true", help="testing cubes")
    parser.add_argument("--delay", type=int, help="Delay start of program in seconds")
    args = parser.parse_args()

    if args.delay is not None:
        print(f"randSleeping for {args.delay} seconds")
        randSleep(args.delay * 1000, (args.delay + 1) * 1000)

    print("Chaos script starting...")
    print("Remember to turn on Auto-disassemble")
    
    leftClickAtPosition(SCREEN_CENTER_POS)

    botManager = BotManager(args.chaos, args.unas, args.guild)

    # stay invis in friends list
    # if config["invisible"] == True:
    #     goInvisible()

    # save bot start time
    # states["botStartTime"] = int(time.time_ns() / 1000000)

    ranOnce = False
    curr = 0

    while not botManager.allBotsFinished():
        try:
            randSleep(1000, 1200)
            restartCheck()
            if not ranOnce:
                ranOnce = True
                botManager.switchToCharacter(0)

            # wait until loaded
            while True:
                restartCheck()
                randSleep(1000, 1200)
                channelDropdownArrow = findImageCenter(
                    "./screenshots/channelDropdownArrow.png",
                    confidence=0.75,
                    region=(1870, 133, 25, 30),
                )
                inChaos = findImageCenter(
                    "./screenshots/inChaos.png",
                    confidence=0.75,
                    region=(247, 146, 222, 50),
                )
                if channelDropdownArrow is not None:
                    print("overworld loaded")
                    break
                if inChaos is not None:
                    print("still in the last chaos run, quitting")
                    ChaosBot.quitChaos()
                    randSleep(4000, 6000)
                # if states["cubes"]:
                #     break
                randSleep(1400, 1600)

            mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
            randSleep(100, 200)

            restartCheck()

            # for non-aura users: MUST have your character parked near a repairer in city before starting the script
            if config["auraRepair"] == False:
                doCityRepair()

            # if (
            #     states["cubes"]
            # ):
            #     doCubes()
            restartCheck()
            clearQuest()
            botManager.runCharTasks()
            restartCheck()
            nextIndex = (curr + 1) % len(roster)
            print(f"character {curr} is done, switching to: {nextIndex}")
            botManager.switchToCharacter(nextIndex)
            botManager.updateCurrentChar(nextIndex)
            curr = nextIndex

        except restartException:
            randSleep(10000, 12200)
            restartGame()
            while True:
                im = pyautogui.screenshot(region=(1652, 168, 240, 210))
                r, g, b = im.getpixel((1772 - 1652, 272 - 168))
                if r + g + b > 10:
                    print("game restarted")
                    break
                randSleep(200, 300)
            randSleep(600, 800)

            inChaos = findImageCenter(
                "./screenshots/inChaos.png", confidence=0.75, region=(247, 146, 222, 50)
            )
            currentTime = int(time.time_ns() / 1000000)
            restartedshot = pyautogui.screenshot()
            restartedshot.save(
                f"./debug/restarted_inChaos_{inChaos is not None}_{currentTime}.png"
            )
            if inChaos is not None:
                print("still in the last chaos run, quitting")
                # ChaosBot.quitChaos()
            else:
                print("in city, going for next run")
        except resetException:
            print("reset detected")
            botManager = BotManager()
            ranOnce = False

class BotManager():
    def __init__(self, doChaos: bool, doUnas: bool, doGuild: bool) -> None:
        self.doChaos = doChaos
        self.doUnas = doUnas
        self.doGuild = doGuild

        self.runningBotList: list[TaskBot] = []
        if self.doChaos:
            self.runningBotList.append(ChaosBot())
        if self.doUnas:
            self.runningBotList.append(UnaBot())
        if self.doGuild:
            self.runningBotList.append(GuildBot())

    def allBotsFinished(self) -> bool:
        for bot in self.runningBotList:
            if not bot.isCompleted():
                return False
        return True

    def run(self) -> None:
        self.switchToCharacter(0)

        if config["auraRepair"] == False:
            doCityRepair()
        curr = 0
        while not self.allBotsFinished():
            restartCheck()
            self.runCharTasks()
            restartCheck()
            nextIndex = (curr + 1) % len(roster)
            print(f"character {curr} is done, switching to: {nextIndex}")
            self.switchToCharacter(nextIndex)
            self.updateCurrentChar(nextIndex)
            curr = nextIndex
    
    def updateCurrentChar(self, char: int) -> None:
        for bot in self.runningBotList:
            bot.setCurrentCharacter(char)

    def runCharTasks(self) -> None:
        for bot in self.runningBotList:
            bot.doTasks()

    def switchToCharacter(self, index: int) -> None:
        """Opens ESC menu and switches to character designated by index."""
        randSleep(500, 600)
        print("switching to {}".format(index))
        while not checkImageOnScreen("./screenshots/menus/gameMenu.png", confidence=0.7):
            pydirectinput.press("esc")
            randSleep(1000, 1100)
        print("game menu detected")
        leftClickAtPosition(Position(540, 700))
        randSleep(500, 600)

        for _ in range(5):
            leftClickAtPosition(Position(1270, 430))
            randSleep(200, 300)

        if index > 8:
            for i in range(math.floor(index / 3) - 2):
                leftClickAtPosition(Position(1267, 638))
                randSleep(200, 300)

        mouseMoveTo(
            x=config["charPositions"][index][0], y=config["charPositions"][index][1]
        )
        randSleep(300, 400)
        pydirectinput.click(button="left")
        randSleep(300, 400)
        pydirectinput.click(button="left")
        randSleep(1500, 1600)

        for bot in self.runningBotList:
            if isinstance(bot, ChaosBot):
                bot.remainingTasks[index] -= checkChaosCompleted()
            if isinstance(bot, UnaBot):
                bot.remainingTasks[index] -= checkUnasCompleted()

        if checkImageOnScreen("./screenshots/alreadyConnected.png", confidence=0.85):
            print("character already connected")
            pydirectinput.press("esc")
            randSleep(500, 600)
            pydirectinput.press("esc")
            randSleep(500, 600)
            return

        leftClickAtPosition(Position(1030, 700))
        randSleep(1000, 1000)
        leftClickAtPosition(Position(920, 590))
        randSleep(1000, 1000)

        randSleep(10000, 12000)
        if config["GFN"] == True:
            randSleep(8000, 9000)


# def saveAbilitiesScreenshots() -> None:
#     for ability in abilities[config["characters"][states["currentCharacter"]]["class"]]:
#         if ability["abilityType"] not in ["specialty1", "specialty2"]:
#             ability.update({"image": pyautogui.screenshot(region=ability["position"])})
#             randSleep(100, 150)


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
        "./screenshots/quest.png", 
        region=(815, 600, 250, 200),
        confidence=0.9
    )
    leveledup = findImageCenter(
        "./screenshots/leveledup.png", 
        region=(815, 600, 250, 200),
        confidence=0.9
    )
    gameMenu = findImageCenter(
        "./screenshots/menus/gameMenu.png",
        region=SCREEN_CENTER_REGION,
        confidence=0.95
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


def restartGame() -> None:
    print("restart game")
    # gameCrashCheck()
    randSleep(5000, 7000)
    while True:
        if config["GFN"] == True:
            randSleep(10000, 12000)
            loaGFN = findImageCenter(
                "./screenshots/GFN/loaGFN.png",
                confidence=0.8,
            )
            loaGFNplay = findImageCenter(
                "./screenshots/GFN/loaGFNplay.png",
                confidence=0.8,
            )
            if loaGFNplay is not None:
                x, y = loaGFNplay
                mouseMoveTo(x=x, y=y)
                randSleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked play restart on GFN")
                randSleep(40000, 42000)
                break
            if loaGFN is not None:
                x, y = loaGFN
                mouseMoveTo(x=x, y=y)
                randSleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked image restart on GFN")
                randSleep(40000, 42000)
                break
            afkGFN = findImageCenter(
                "./screenshots/GFN/afkGFN.png",
                region=SCREEN_CENTER_REGION,
                confidence=0.75,
            )
            closeGFN = findImageCenter(
                "./screenshots/GFN/closeGFN.png",
                confidence=0.75,
            )
            if closeGFN is not None:
                print("afk GFN")
                x, y = closeGFN
                mouseMoveTo(x=x, y=y)
                randSleep(1300, 1400)
                pydirectinput.click(button="left")
                randSleep(1300, 1400)
                continue
        else:
            os.system("start steam://launch/1599340/dialog")
            randSleep(60000, 60000)
        enterGame = findImageCenter("./screenshots/steamPlay.png", confidence=0.75)
        randSleep(500, 600)
        stopGame = findImageCenter("./screenshots/steamStop.png", confidence=0.75)
        randSleep(500, 600)
        confirm = findImageCenter("./screenshots/steamConfirm.png", confidence=0.75)
        randSleep(500, 600)
        enterServer = findImageCenter(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        randSleep(500, 600)
        channelDropdownArrow = findImageCenter(
            "./screenshots/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if stopGame is not None:
            print("clicking stop game on steam")
            x, y = stopGame
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(500, 600)
            confirm = findImageCenter("./screenshots/steamConfirm.png", confidence=0.75)
            if confirm is None:
                continue
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(10000, 12000)
        elif confirm is not None:
            print("confirming stop game")
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(10000, 12000)
        elif enterGame is not None:
            print("restarting Lost Ark game client...")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            break
        elif enterServer is not None:
            break
        elif channelDropdownArrow is not None:
            return
        randSleep(1200, 1300)
    randSleep(5200, 6300)
    while True:
        enterServer = findImageCenter(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        enterGame = findImageCenter("./screenshots/steamPlay.png", confidence=0.75)
        if enterServer is not None:
            print("clicking enterServer")
            randSleep(1000, 1200)
            # click first server
            mouseMoveTo(x=855, y=582)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            randSleep(1000, 1200)
            x, y = enterServer
            mouseMoveTo(x=x, y=y)
            randSleep(1200, 1300)
            pydirectinput.click(button="left")
            break
        elif enterGame is not None:
            print("clicking enterGame")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            randSleep(200, 300)
            pydirectinput.click(button="left")
            randSleep(4200, 5300)
            continue
    randSleep(3200, 4300)
    while True:
        enterCharacter = findImageCenter(
            "./screenshots/enterCharacter.png",
            confidence=0.75,
            region=(745, 854, 400, 80),
        )
        if enterCharacter is not None:
            print("clicking enterCharacter")
            x, y = enterCharacter
            mouseMoveTo(x=x, y=y)
            randSleep(200, 300)
            pydirectinput.click(button="left")
            break
        randSleep(2200, 3300)
    # states["gameRestartCount"] = states["gameRestartCount"] + 1
    mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
    randSleep(22200, 23300)

def checkUnasCompleted() -> int:
    unaIcon = findImageCenter(
        "./screenshots/unaIcon.png", 
        region=CHARACTER_STATUS_ICON_REGION, 
        confidence=0.75
        )
    if unaIcon is not None:
        x, y = unaIcon
        if checkImageOnScreen(
            "./screenshots/3.png", 
            region=(x+180, y-10, 25, 21), 
            confidence = 0.75
            ):
            print("no unas completed")
            return 0
        if checkImageOnScreen(
            "./screenshots/0.png", 
            region=(x+180, y-10, 25, 21), 
            confidence = 0.75
            ):
            print("all unas completed")
            return 3
    print("unable to detect")
    return 0
        
def checkChaosCompleted() -> int:
    chaosIcon = findImageCenter(
        "./screenshots/chaosIcon.png", 
        region=CHARACTER_STATUS_ICON_REGION, 
        confidence=0.75
        )
    if chaosIcon is not None:
        x, y = chaosIcon
        print(f"chaos icon detected at {x} {y}")
        if checkImageOnScreen(
            "./screenshots/100.png", 
            region=(x+180, y-10, 25, 21), 
            confidence = 0.75
            ):
            print("no chaos runs completed")
            return 0
        if checkImageOnScreen(
            "./screenshots/50.png", 
            region=(x+180, y-10, 25, 21), 
            confidence = 0.75
            ):
            print("one chaos run completed")
            return 1
        if checkImageOnScreen(
            "./screenshots/0.png", 
            region=(x+180, y-10, 25, 21), 
            confidence = 0.75
            ):
            print("both chaos runs completed")
            return 2
    print("unable to detect")
    return 0

def cleanInventory():
    toggleMenu("pet")
    pydirectinput.click(1143, 630, button="left")  # pet
    randSleep(3000, 3000)
    pydirectinput.click(560, 765, button="left")  # roster deposit
    randSleep(1500, 1600)
    pydirectinput.click(560, 765, button="left")  # roster deposit
    randSleep(1500, 1600)
    pydirectinput.click(880, 765, button="left")  # character deposit
    randSleep(1500, 1600)
    pydirectinput.click(880, 765, button="left")  # character deposit
    randSleep(1500, 1600)

    for _ in range(2):
        pydirectinput.press("esc")
        randSleep(100, 200)


def click(x, y, sleepDur):
    pydirectinput.click(x, y, button="left")
    randSleep(sleepDur, sleepDur)


def set_resolution(width: int, height: int):
    if platform.system() == "Windows":
        # adapted from [Win | dP] Dragonback
        # adapted from Peter Wood: https://stackoverflow.com/a/54262365
        devmode = pywintypes.DEVMODEType()
        devmode.PelsWidth = width
        devmode.PelsHeight = height
        devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

        win32api.ChangeDisplaySettings(devmode, 0)


if __name__ == "__main__":
    main()
