from modules.taskbot import TaskBot
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
from datetime import datetime
import random
import pydirectinput
import pyautogui

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

SCREEN_CENTER_POS = Position(960, 540)
SCREEN_CENTER_REGION = (685, 280, 600, 420)

CHAOS_CLICKABLE_REGION = (460, 290, 1000, 500)
CHAOS_PORTAL_REGION = (228, 230, 1370, 570)
CHAOS_LEAVE_MENU_REGION = (0, 154, 250, 300)

CHARACTER_SPECIALTY_REGION = (900, 800, 120, 940)
CHARACTER_BUFFS_REGION = (625, 780, 300, 60)
CHARACTER_DEBUFFS_REGION = (1040, 810, 90, 40)

PUNIKA_CHAOS_TAB_POS = Position(1020, 307)
SOUTH_VERN_CHAOS_TAB_POS = Position(1160, 307)
ELGACIA_CHAOS_TAB_POS = Position(1300, 307)
VOLDIS_CHAOS_TAB_POS = Position(1440, 307)

LEVEL_1_CHAOS_POS = Position(624, 405)
LEVEL_2_CHAOS_POS = Position(624, 457)
LEVEL_3_CHAOS_POS = Position(624, 509)
LEVEL_4_CHAOS_POS = Position(624, 561)
LEVEL_5_CHAOS_POS = Position(624, 613)
LEVEL_6_CHAOS_POS = Position(624, 665)
LEVEL_7_CHAOS_POS = Position(624, 717)
LEVEL_8_CHAOS_POS = Position(624, 769)

CHAOS_TAB_POSITION = {
    1100: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1310: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
    1325: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_3_CHAOS_POS},
    1340: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_4_CHAOS_POS},
    1355: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_5_CHAOS_POS},
    1370: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_6_CHAOS_POS},
    1385: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_7_CHAOS_POS},
    1400: {"tabPos": PUNIKA_CHAOS_TAB_POS, "levelPos": LEVEL_8_CHAOS_POS},
    1415: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1445: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
    1475: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_3_CHAOS_POS},
    1490: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_4_CHAOS_POS},
    1520: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_5_CHAOS_POS},
    1540: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_6_CHAOS_POS},
    1560: {"tabPos": SOUTH_VERN_CHAOS_TAB_POS, "levelPos": LEVEL_7_CHAOS_POS},
    1580: {"tabPos": ELGACIA_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1600: {"tabPos": ELGACIA_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
    1610: {"tabPos": VOLDIS_CHAOS_TAB_POS, "levelPos": LEVEL_1_CHAOS_POS},
    1630: {"tabPos": VOLDIS_CHAOS_TAB_POS, "levelPos": LEVEL_2_CHAOS_POS},
}


class ChaosBot(TaskBot):
    def __init__(self, roster):
        super().__init__(roster)
        self.remainingTasks = [
            2 if char["chaosItemLevel"] is not None and char["chaosItemLevel"] <= 1610 else 0 for char in self.roster
        ]
        self.skills: dict[list[dict]] = skills
        self.runStartTime: int = 0

        self.completedCount: int = 0
        self.totalTime: int = 0
        self.fastestClear: int = 500000
        self.slowestClear: int = 0

        self.healthPotCount: int = 0
        self.deathCount: int = 0
        self.timeoutCount: int = 0

    def doTasks(self) -> None:
        if self.remainingTasks[self.curr] == 0:
            return
        
        toggleMenu("defaultCombatPreset")

        enterChaos(self.roster[self.curr]["chaosItemLevel"])
        
        while self.remainingTasks[self.curr] > 0:
            try:
                self.runStartTime = int(time.time())
                self.doChaosFloor(1)
                self.doChaosFloor(2)
                self.doChaosFloor(3)
                finishTime = int(time.time())
                self.updateAndPrintMetrics(finishTime - self.runStartTime)
            except timeoutException:
                quitChaos()
                enterChaos(self.roster[self.curr]["chaosItemLevel"])
            self.remainingTasks[self.curr] -= 1
            if self.remainingTasks[self.curr] > 0:
                reenterChaos()
            if datetime.now().hour == config["resetHour"] and not self.resetOnce:
                self.resetOnce = True
                quitChaos()
                raise resetException
        quitChaos()

    def doChaosFloor(self, n: int) -> None:
        waitForChaosFloorLoading()
        print(f"floor {n} loaded")

        if config["auraRepair"]:
            doAuraRepair(False)

        leftClickAtPosition(SCREEN_CENTER_POS)
        randSleep(1500, 1600)

        self.useSkills(n)
        print(f"floor {n} cleared")

        restartCheck()
        self.timeoutCheck()

    def useSkills(self, floor) -> None:
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
        while True:
            self.diedCheck()
            self.healthCheck()
            restartCheck()
            self.timeoutCheck()

            x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()

            if floor == 1 and not awakeningUsed:
                awakeningUsed = True
                castAbility(x, y, awakeningSkill)

            # check for accident
            if floor == 1 and minimap.checkElite():
                print("accidentally entered floor 2")
                return
            elif floor == 2 and minimap.checkRiftCore():
                print("accidentally entered floor 3")
                return

            if floor == 1 and not minimap.checkMob():
                print("no floor 1 mob detected, random move")
                randomMove()
            elif floor == 2 and not minimap.checkElite() and not minimap.checkMob():
                print("no floor 2 elite/mob detected, random move")
                randomMove()
            elif floor == 3 and minimap.checkElite():
                x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                moveInDirection(x, y, moveDuration)
            elif (
                floor == 3
                and not minimap.checkRiftCore()
                and not minimap.checkElite()
                and not minimap.checkMob()
            ):
                randomMove()

            # cast sequence
            for i in range(0, len(normalSkills)):
                if floor == 3 and checkChaosFinish():
                    print("chaos finish screen")
                    return
                self.diedCheck()
                self.healthCheck()

                if (floor == 1 or floor == 2) and minimap.checkPortal():
                    pydirectinput.click(
                        x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y, button=config["move"]
                    )
                    randSleep(100, 150)
                    while True:
                        minimap.checkPortal()
                        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                        if self.enterPortal(x, y, int(moveDuration / 3)):
                            break
                        self.timeoutCheck()
                    return

                # click rift core
                if floor == 3:
                    clickRiftCore()

                # check high-priority mobs
                match floor:
                    case 1:
                        if minimap.checkMob():
                            x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                    case 2:
                        if (
                            minimap.checkBoss()
                            or minimap.checkElite()
                            or minimap.checkMob()
                        ):
                            x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                            moveInDirection(x, y, int(moveDuration / 3))
                            if minimap.checkBoss() and not awakeningUsed:
                                awakeningUsed = True
                                castAbility(x, y, awakeningSkill)
                    case 3:
                        if (
                            minimap.checkRiftCore()
                            or minimap.checkElite()
                            or minimap.checkMob()
                        ):
                            x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                            moveInDirection(x, y, int(moveDuration / 2))
                            if not minimap.checkElite() and not minimap.checkMob():
                                minimap.checkRiftCore()
                                newX, newY, _ = minimap.getGameCoordsOfMinimapTarget()
                                if (
                                    newX - 30 < x < newX + 30
                                    and newY - 20 < y < newY + 20
                                ):
                                    randomMove()

                self.performClassSpecialty(
                    self.roster[self.curr]["class"], i, normalSkills
                )
                castAbility(x, y, normalSkills[i])

    def healthCheck(self) -> None:
        """
        Press potion if under HP threshold.
        """
        x = int(690 + 180 * config["healthPotAtPercent"])
        r1, g, b = pyautogui.pixel(x, 855)
        r2, g, b = pyautogui.pixel(x - 2, 855)
        r3, g, b = pyautogui.pixel(x + 2, 855)
        if r1 < 30 or r2 < 30 or r3 < 30:
            print("health pot pressed")
            pydirectinput.press(config["healthPot"])
            self.healthPotCount += 1

    def diedCheck(self) -> None:
        """
        Checks if death menu on screen and clicks revive.
        """
        if checkImageOnScreen(
            "./screenshots/chaos/died.png",
            grayscale=True,
            confidence=0.8,
            region=(917, 145, 630, 550),
        ):
            print("died")
            self.deathCount += 1
            randSleep(5000, 5500)
            resReady = checkImageOnScreen(
                "./screenshots/chaos/resReady.png",
                confidence=0.7,
                region=(917, 145, 630, 550),
            )
            if resReady:
                mouseMoveTo(x=1275, y=400)
                randSleep(1600, 1800)
                pydirectinput.click(button="left")
                randSleep(600, 800)
                mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                randSleep(600, 800)
                restartCheck()
                self.timeoutCheck()

    def performClassSpecialty(
        self, characterClass: str, i: int, abilities: list[dict]
    ) -> None:
        """
        Performs custom class behavior (activating identity, using specialty, stance swapping, etc.).
        """
        match characterClass:
            case "arcana":
                pydirectinput.press(config["specialty1"])
                pydirectinput.press(config["specialty2"])
            case "souleater":
                soulSnatch = checkImageOnScreen(
                    "./screenshots/classSpecialties/soulSnatch.png",
                    region=CHARACTER_DEBUFFS_REGION,
                    confidence=0.85,
                )
                if soulSnatch:
                    castAbility(960, 540, abilities[0])
                    randSleep(300, 400)
                    castAbility(960, 540, abilities[1])
                    randSleep(300, 400)
                    castAbility(960, 540, abilities[5])
                    randSleep(300, 400)
            case "slayer":
                slayerSpecialty = checkImageOnScreen(
                    "./screenshots/classSpecialties/slayerSpecialty.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.85,
                )
                if slayerSpecialty:
                    pydirectinput.press(config["specialty1"])
                    randSleep(150, 160)
            case "deathblade":
                threeOrbDeathTrance = checkImageOnScreen(
                    "./screenshots/classSpecialties/deathTrance.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.80,
                )
                if threeOrbDeathTrance:
                    pydirectinput.press(config["specialty1"])
                    randSleep(150, 160)
            case "gunslinger":
                pistolStance = checkImageOnScreen(
                    "./screenshots/classSpecialties/pistolStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                shotgunStance = checkImageOnScreen(
                    "./screenshots/classSpecialties/shotgunStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                sniperStance = checkImageOnScreen(
                    "./screenshots/classSpecialties/sniperStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                # swap to shotgun
                if i == 0 and not shotgunStance:
                    if pistolStance:
                        pydirectinput.press(config["specialty1"])
                        randSleep(150, 160)
                    if sniperStance:
                        pydirectinput.press(config["specialty2"])
                        randSleep(150, 160)
                # swap to sniper
                elif i < 3 and not sniperStance:
                    if pistolStance:
                        pydirectinput.press(config["specialty2"])
                        randSleep(150, 160)
                    if shotgunStance:
                        pydirectinput.press(config["specialty1"])
                        randSleep(150, 160)
                # swap to pistol
                elif not pistolStance:
                    if shotgunStance:
                        pydirectinput.press(config["specialty2"])
                        randSleep(150, 160)
                    if sniperStance:
                        pydirectinput.press(config["specialty1"])
                        randSleep(150, 160)
            case "artist":
                artistOrb = checkImageOnScreen(
                    "./screenshots/classSpecialties/artistOrb.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.85,
                )
                if artistOrb:
                    mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                    randSleep(150, 160)
                    pydirectinput.press(config["specialty2"])
                    randSleep(1500, 1600)
                    pydirectinput.press(config["interact"])
            case "aeromancer":
                aeroSpecialty = checkImageOnScreen(
                    "./screenshots/classSpecialties/aeroSpecialty.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.95,
                )
                if aeroSpecialty:
                    randSleep(150, 160)
                    pydirectinput.press(config["specialty1"])
            case "scrapper":
                scrapperSpecialty = checkImageOnScreen(
                    "./screenshots/classSpecialties/scrapperSpecialty.png",
                    region=CHARACTER_SPECIALTY_REGION,
                    confidence=0.85,
                )
                if scrapperSpecialty:
                    randSleep(150, 160)
                    pydirectinput.press("z")
            case "bard":
                courageBuffActive = checkImageOnScreen(
                    "./screenshots/classSpecialties/bardCourage120.png",
                    region=CHARACTER_BUFFS_REGION,
                    confidence=0.75,
                )
                rZ, gZ, bZ = pyautogui.pixel(920, 866)
                rX, gX, bX = pyautogui.pixel(1006, 875)
                if rZ - gZ > 80 and courageBuffActive:
                    pydirectinput.press("z")
                    randSleep(50, 60)
                    pydirectinput.press("z")
                    randSleep(150, 160)
                elif bX - gX > 70 and not courageBuffActive:
                    mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                    randSleep(150, 160)
                    pydirectinput.press("x")
                    randSleep(50, 60)
                    pydirectinput.press("x")
                    randSleep(150, 160)

    def enterPortal(self, x: int, y: int, moveDuration: int) -> bool:
        """
        Moves to (x, y) over moveDuration milliseconds while pressing interact.

        Returns true if black loading screen reached from interacting with portal within time limit, false otherwise.
        """
        if moveDuration > 550:
            pydirectinput.click(x=x, y=y, button=config["move"])
            randSleep(100, 150)
            if self.roster[self.curr]["class"] != "gunlancer":
                pydirectinput.press(config["blink"])

        for _ in range(10):
            # try to enter portal until black screen
            im = pyautogui.screenshot(region=(1652, 168, 240, 210))
            r, g, b = im.getpixel((1772 - 1652, 272 - 168))
            if r + g + b < 30:
                mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                return True
            pydirectinput.press(config["interact"])
            randSleep(100, 120)
            pydirectinput.click(x=x, y=y, button=config["move"])
            randSleep(60, 70)
        pydirectinput.press(self.skills[self.roster[self.curr]["class"]][0])
        randSleep(100, 150)
        pydirectinput.press(config["meleeAttack"])
        randSleep(100, 150)
        return False

    def timeoutCheck(self) -> None:
        """
        Raise timeoutException if total time elapsed in chaos exceeds limit.
        """
        currentTime = int(time.time())
        if currentTime - self.runStartTime > config["timeLimit"]:
            print("timeout triggered")
            timeout = pyautogui.screenshot()
            timeout.save(f"./debug/timeout_{currentTime}.png")
            self.timeoutCount += 1
            raise timeoutException

    def updateAndPrintMetrics(self, int):
        """
        Updates bot statistics and prints summary.
        """
        print("-------------------------------------")
        print(f"run completed in {int}s")
        self.completedCount += 1
        self.totalTime += int
        self.fastestClear = min(int, self.fastestClear)
        self.slowestClear = max(int, self.slowestClear)
        print("-------------------------------------")
        print(f"total timeouts: {self.timeoutCount}")
        print(f"total deaths: {self.deathCount}")
        print(f"total low hp: {self.healthPotCount}")
        print("-------------------------------------")
        averageTime = self.totalTime / self.completedCount
        print(
            f"average: {averageTime}, fastest: {self.fastestClear}, slowest: {self.slowestClear}"
        )
        print("-------------------------------------")


def checkAuraOfResonance() -> int:
    for remainingAura in [0, 50, 100]:
        if checkImageOnScreen(
            f"./screenshots/aura{remainingAura}.png",
            region=(760, 345, 70, 30),
            confidence=0.95,
        ):
            print(f"{remainingAura} aura of resonance detected")
            return remainingAura
    return 0


def enterChaos(ilvl: int) -> None:
        """
        Enters specified chaos dungeon level.
        """
        toggleMenu("content")
        waitForMenuLoaded("content")

        # remainingAura = checkAuraOfResonance()
        # self.remainingTasks[self.curr] = remainingAura / 50
        # if remainingAura == 0:
        #     toggleMenu("content")
        #     return False

        elementPos = findImageCenter(
            "./screenshots/menus/chaosDungeonContentMenuElement.png", confidence=0.9
        )
        if elementPos is not None:
            x, y = elementPos
            leftClickAtPosition(Position(x + 300, y + 30))  # shortcut button
        else:
            leftClickAtPosition(Position(786, 315)) # edge case different UI
        randSleep(800, 900)
        isCorrectChaosDungeon = checkImageOnScreen(
            f"./screenshots/chaos/ilvls/{ilvl}.png",
            region=(1255, 380, 80, 50),
            confidence=0.95,
        )
        if not isCorrectChaosDungeon:
            print("not correct")
            selectChaosDungeon(ilvl)

        findAndClickImage("weeklyPurificationClaimAll", confidence=0.95)
        randSleep(500, 600)
        leftClickAtPosition(Position(920, 575))  # accept button
        randSleep(500, 600)

        findAndClickImage("enterButton", region=(1380, 760, 210, 60), confidence=0.75)
        randSleep(800, 900)
        findAndClickImage("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
        randSleep(800, 900)

def selectChaosDungeon(ilvl: int) -> None:
    """
    With chaos dungeon menu open, select chaos dungeon level corresponding to item level.
    """
    chaosMenuRightArrow = findImageCenter(
        f"./screenshots/chaosMenuRightArrow.png", confidence=0.95
    )
    if chaosMenuRightArrow is not None:
        x, y = chaosMenuRightArrow
        mouseMoveTo(x=x, y=y)
        randSleep(200, 250)
        pydirectinput.click(button="left")
        randSleep(200, 250)

    leftClickAtPosition(CHAOS_TAB_POSITION[ilvl]["tabPos"])
    randSleep(1000, 1100)
    leftClickAtPosition(CHAOS_TAB_POSITION[ilvl]["levelPos"])
    randSleep(1000, 1100)


def waitForChaosFloorLoading() -> None:
    """
    Sleeps until leave button of chaos button is on screen.
    ALT F4 if loading times out.
    """
    blackScreenStartTime = int(time.time_ns() / 1000000)
    while True:
        restartCheck()
        currentTime = int(time.time_ns() / 1000000)
        if currentTime - blackScreenStartTime > config["blackScreenTimeLimit"]:
            print("alt f4")
            pydirectinput.keyDown("alt")
            randSleep(350, 400)
            pydirectinput.keyDown("f4")
            randSleep(350, 400)
            pydirectinput.keyUp("alt")
            randSleep(350, 400)
            pydirectinput.keyUp("f4")
            randSleep(350, 400)
            randSleep(10000, 15000)
            return
        leaveButton = checkImageOnScreen(
            "./screenshots/chaos/leave.png",
            grayscale=True,
            confidence=0.7,
            region=CHAOS_LEAVE_MENU_REGION)
        if leaveButton:
            return
        randSleep(100, 150)


def castAbility(x: int, y: int, ability: dict) -> None:
    """
    Casts the given ability in the specified direction.
    """
    if ability["directional"]:
        mouseMoveTo(x=x, y=y)
    else:
        mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)

    if ability["castTime"] is not None:
        pydirectinput.press(ability["key"])
        randSleep(100, 150)
        pydirectinput.press(ability["key"])
        randSleep(ability["castTime"], (ability["castTime"] + 100))
    elif ability["holdTime"] is not None:
        pydirectinput.keyDown(ability["key"])
        randSleep(ability["holdTime"], (ability["holdTime"] + 100))
        pydirectinput.keyUp(ability["key"])
    else:
        pydirectinput.press(ability["key"])
        randSleep(100, 150)


def clickRiftCore() -> None:
    """
    Uses basic attacks if rift core label on screen.
    """
    for i in [1, 2]:
        riftCore = findImageCenter(
            f"./screenshots/chaos/riftcore{i}.png",
            confidence=0.6,
            region=CHAOS_PORTAL_REGION,
        )
        if riftCore is not None:
            x, y = riftCore
            if y > 650 or x < 400 or x > 1500:
                return
            pydirectinput.click(x=x, y=y + 190, button=config["move"])
            randSleep(100, 120)
            for _ in range(4):
                pydirectinput.press(config["meleeAttack"])
                randSleep(300, 360)


def moveInDirection(x: int, y: int, duration: int) -> None:
    """
    Moves to (x, y) across duration.
    """
    if x == SCREEN_CENTER_X and y == SCREEN_CENTER_Y:
        return
    halfstep = int(duration / 2)
    for _ in range(2):
        pydirectinput.click(x=x, y=y, button=config["move"])
        randSleep(halfstep - 20, halfstep + 20)


def randomMove() -> None:
    """
    Randomly moves by clicking in the clickable region.
    """
    left, top, width, height = CHAOS_CLICKABLE_REGION
    x = random.randint(left, left + width)
    y = random.randint(top, top + height)

    print(f"random move to x: {x} y: {y}")
    pydirectinput.click(x=x, y=y, button=config["move"])
    randSleep(200, 250)
    pydirectinput.click(x=x, y=y, button=config["move"])
    randSleep(200, 250)


def checkChaosFinish() -> bool:
    """
    Returns true if chaos finish screen detected and clears the finish overlay. Otherwise returns false.
    """
    clearOk = findImageCenter(
        "./screenshots/chaos/clearOk.png", confidence=0.75, region=(625, 779, 500, 155)
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


def reenterChaos() -> None:
    """
    Start new chaos dungeon after finishing.
    """
    print("reentering chaos")
    randSleep(1200, 1400)
    findAndClickImage(
        "chaos/selectLevel", region=CHAOS_LEAVE_MENU_REGION, confidence=0.7
    )
    randSleep(500,600)
    findAndClickImage("enterButton", region=(1380, 760, 210, 60), confidence=0.75)
    randSleep(800,900)
    findAndClickImage("acceptButton", region=SCREEN_CENTER_REGION, confidence=0.75)
    randSleep(2000, 3200)
    return


def doAuraRepair(forced: bool) -> None:
    """
    Repair through pet menu if forced or yellow/red armor icon detected.
    """
    if forced or checkImageOnScreen(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        toggleMenu("pet")
        mouseMoveTo(x=1142, y=661)
        randSleep(2500, 2600)
        pydirectinput.click(button="left")
        randSleep(5500, 5600)
        mouseMoveTo(x=1054, y=455)
        randSleep(2500, 2600)
        pydirectinput.click(button="left")
        randSleep(2500, 2600)
        pydirectinput.press("esc")
        randSleep(2500, 2600)
        pydirectinput.press("esc")
        randSleep(2500, 2600)
