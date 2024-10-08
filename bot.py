from config import config
from abilities import abilities
import pyautogui
import pydirectinput
import time
import random
import math
import argparse
from datetime import datetime
from datetime import date
import keyboard
import os
import platform
import pywintypes, win32con, win32api

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

CHAOS_CLICKABLE_REGION = (460, 290, 1000, 500)

MINIMAP_REGION = (1655, 170, 240, 200)
MINIMAP_CENTER_X = 1772
MINIMAP_CENTER_Y = 272

MOB_RGB_RANGE_GFN = lambda r, g, b: 180 < r < 215 and 17 < g < 35 and 17 < b < 55
MOG_RGB_RANGE = lambda r, g, b: 180 < r < 215 and 17 < g < 35 and 17 < b < 55

ELITE_RGB_RANGE_GFN = lambda r, g, b: 184 < r < 215 and 124 < g < 147 and 59 < b < 78
ELITE_RGB_RANGE = lambda r, g, b: 189 < r < 215 and 124 < g < 150 and 29 < b < 70

PORTAL_RGB_RANGE_GFN = lambda r, g, b: ((75 < r < 105 and 140 < g < 170 and 240 < b < 256) or 
                                        (120 < r < 130  and 210 < g < 240 and 240 < b < 256))
PORTAL_RGB_RANGE = lambda r, g, b: ((75 < r < 85 and 140 < g < 150 and 250 < b < 256) or 
                                    (120 < r < 130  and 210 < g < 220 and 250 < b < 256))
pydirectinput.PAUSE = 0.05
newStates = {
    "status": "overworld",
    "abilities": [],
    "abilityScreenshots": [],
    "clearCount": 0,
    "fullClearCount": 0,
    "moveTime": 0,
    "botStartTime": None,
    "instanceStartTime": None,
    "deathCount": 0,
    "healthPotCount": 0,
    "timeoutCount": 0,
    "badRunCount": 0,
    "gameRestartCount": 0,
    "gameCrashCount": 0,
    "gameOfflineCount": 0,
    "minTime": config["timeLimit"],
    "maxTime": -1,
    "multiCharacterMode": False,
    "currentCharacter": 0,
    "multiCharacterModeState": [],
    "remainingChaosRuns": [],
    "remainingUnasTasks": [],
    "remainingGuildSupport": [],
    "remainingSailing": [],
}

def abortScript():
    os._exit(1)

def main():
    # set_resolution(1920, 1080)
    keyboard.add_hotkey('ctrl+page down', abortScript)

    # Instantiate the parser
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument("--chaos", action="store_true", help="Enables 2x chaos on entire roster")
    parser.add_argument("--unas", action="store_true", help="Enables unas on entire roster")
    parser.add_argument("--guild", action="store_true", help="Enables guild donation/support on entire roster")
    parser.add_argument("--sailing", action="store_true", help="Enables sailing weekly on entire roster")
    parser.add_argument("--cubes", action="store_true", help="testing cubes")
    parser.add_argument("--delay", type=int, help="Delay start of program in seconds")
    args = parser.parse_args()

    states["doChaos"] = args.chaos
    states["doUnas"] = args.unas
    states["doGuild"] = args.guild
    states["doSailing"] = args.sailing
    states["cubes"] = args.cubes
    states["delayStart"] = False if args.delay is None else True 
    states["delayDuration"] = args.delay

    if args.delay is not None:
        print("sleeping for " + str(args.delay) + " seconds")
        sleep(args.delay*1000,(args.delay+1)*1000)

    print("Chaos script starting...")
    print("Remember to turn on Auto-disassemble")

    initRosterChecklist()

    mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
    sleep(200, 300)
    pydirectinput.click(button=config["move"])
    sleep(300, 400)

    # stay invis in friends list
    # if config["invisible"] == True:
    #     goInvisible()

    # save bot start time
    states["botStartTime"] = int(time.time_ns() / 1000000)

    ranOnce = False
    while (sum(states["remainingChaosRuns"]) + 
           sum(states["remainingUnasTasks"]) +
           sum(states["remainingGuildSupport"]) +
           sum(states["remainingSailing"]) > 0):
        try:
            sleep(1000, 1200)
            restartCheck()
            if not ranOnce:
                ranOnce = True
                switchToCharacter(config["mainCharacter"])

            # wait until loaded
            while True:
                restartCheck()
                sleep(1000, 1200)
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
                    quitChaos()
                    sleep(4000, 6000)
                if states["cubes"]:
                    break
                sleep(1400, 1600)

            # battle item preset
            toggleMenu("defaultCombatPreset")

            mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
            sleep(100, 200)

            restartCheck()

            # for non-aura users: MUST have your character parked near a repairer in city before starting the script
            if config["auraRepair"] == False:
                doCityRepair()
            
            # if (
            #     states["cubes"]
            # ):
            #     doCubes()
            restartCheck()
            
            currentCharConfig = config["characters"][states["currentCharacter"]]
            # save instance start time
            states["instanceStartTime"] = int(time.time_ns() / 1000000)
            # initialize new states
            states["abilityScreenshots"] = []

            # chaos dungeon
            if states["doChaos"]:
                if currentCharConfig["chaos_ilvl"] is None:
                    print(f"skipping chaos on {states['currentCharacter']}")
                    states["remainingChaosRuns"][states["currentCharacter"]] = 0
                elif states["remainingChaosRuns"][states["currentCharacter"]] == 0:
                    print(f"chaos already completed on {states['currentCharacter']}")
                else:
                    print(f"doing chaos on : {states['currentCharacter']}")
                    doChaos()
                    print(f"chaos done on : {states['currentCharacter']}")
                    sleep(1400, 1600)

            # dailies
            if states["doUnas"]:
                if currentCharConfig["unas"] is None:
                    print(f"skipping unas on {states['currentCharacter']}")
                    states["remainingUnasTasks"][states["currentCharacter"]] = 0
                elif states["remainingUnasTasks"][states["currentCharacter"]] == 0:
                    print(f"unas already completed on {states['currentCharacter']}")
                else:
                    print("doing daily unas on : {}".format(states["currentCharacter"]))
                    doDailyUnas(currentCharConfig["unas"])
                    print("daily unas done on : {}".format(states["currentCharacter"]))
                    sleep(1400, 1600)

            # guild dono
            if states["doGuild"] and currentCharConfig["guildDonation"]:
                print("doing guild stuff on : {}".format(states["currentCharacter"]))
                doGuildDonation()
                print("guild stuff done on : {}".format(states["currentCharacter"]))
                sleep(1400, 1600)

            # sailing level 5
            if states["doSailing"] and currentCharConfig["guildSailingWeekly"]:
                print("doing sailing on : {}".format(states["currentCharacter"]))
                doSailingWeekly(currentCharConfig["guildSailingWeekly"])
                print("sailing done on : {}".format(states["currentCharacter"]))
                sleep(1400, 1600)
                    
            restartCheck()
            nextIndex = (states["currentCharacter"] + 1) % len(config["characters"])
            print("character {} is done, switching to: {}".format(states["currentCharacter"], nextIndex))
            switchToCharacter(nextIndex)

        except restartException:
            sleep(10000, 12200)
            restartGame()
            while True:
                im = pyautogui.screenshot(region=(1652, 168, 240, 210))
                r, g, b = im.getpixel((1772 - 1652, 272 - 168))
                if r + g + b > 10:
                    print("game restarted")
                    break
                sleep(200, 300)
            sleep(600, 800)

            inChaos = findImageCenter(
                "./screenshots/inChaos.png", confidence=0.75, region=(247, 146, 222, 50)
            )
            currentTime = int(time.time_ns() / 1000000)
            restartedshot = pyautogui.screenshot()
            restartedshot.save(
                "./debug/restarted_inChaos_"
                + str(inChaos is not None)
                + "_"
                + str(currentTime)
                + ".png"
            )
            if inChaos is not None:
                print("still in the last chaos run, quitting")
                quitChaos()
            else:
                print("in city, going for next run")
                states["status"] = "overworld"
        except resetException:
            print("reset detected")
            initRosterChecklist()
            ranOnce = False

def initRosterChecklist():
    print("initializing roster")
    for character in config["characters"]:
        if states["doChaos"]:
            if character["chaos_ilvl"] is not None:
                states["remainingChaosRuns"].append(2)
            else:
                states["remainingChaosRuns"].append(0)
        if states["doUnas"]:
            if character["unas"] is not None:
                if "lopang" in character["unas"]:
                    states["remainingUnasTasks"].append(3)
                else:
                    states["remainingUnasTasks"].append(len(character["unas"].split(' ')))
            else:
                states["remainingUnasTasks"].append(0)
        if states["doGuild"]:
            if character["guildDonation"] is not None:
                states["remainingGuildSupport"].append(1)
            else:
                states["remainingGuildSupport"].append(0)
        if states["doSailing"]:
            if character["guildSailingWeekly"] is not None:
                states["remainingSailing"].append(character["guildSailingWeekly"])
            else:
                states["remainingSailing"].append(0)

    if states["doChaos"]:   
        print(f"chaos: {states['remainingChaosRuns']}")
    if states["doUnas"]:
        print(f"unas: {states['remainingUnasTasks']}")
    if states["doGuild"]:
        print(f"guild: {states['remainingGuildSupport']}")
    if states["doSailing"]: 
        print(f"sailing: {states['remainingSailing']}")

def enterChaos():
    restartCheck()
    sleep(1000, 1200)

    _curr = config["characters"][states["currentCharacter"]]

    toggleMenu("content")
    waitForMenuLoaded("content")
    aura100 = findImageRegion("./screenshots/aura100.png", region = (760, 345, 70, 30), confidence = 0.95)
    aura50 = findImageRegion("./screenshots/aura50.png", region = (760, 345, 70, 30), confidence = 0.95)
    aura0 = findImageRegion("./screenshots/aura0.png", region = (760, 345, 70, 30), confidence = 0.95)
    if aura100 is not None:
        print("100 aura of resonance detected")
        states["remainingChaosRuns"][states["currentCharacter"]] = 2
    elif aura50 is not None:
        print("50 aura of resonance detected")
        states["remainingChaosRuns"][states["currentCharacter"]] = 1
    elif aura0 is not None:
        print("0 aura of resonance detected")
        states["remainingChaosRuns"][states["currentCharacter"]] = 0
        print("no remaining aor on character, still have other chaos to run")
        return False

    mouseMoveTo(x=886, y=346)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)

    weeklyPurificationClaimAll = findImageCenter("./screenshots/weeklyPurificationClaimAll.png", confidence = 0.85)
    if weeklyPurificationClaimAll is not None:
        x, y = weeklyPurificationClaimAll
        mouseMoveTo(x=x, y=y)
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(1500, 1600)
        mouseMoveTo(x=920, y=575)
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(1500, 1600)

    for _ in range(2):
        pydirectinput.click(x=1580, y=310, button="left") # right arrow
        sleep(500, 600)

    # select chaos dungeon level based on current Character
    punikaChaosTabLoc = [1020, 307]
    svernChaosTabLoc = [1160, 307]
    elgaciaChaosTabLoc = [1300, 307]
    voldisChaosTabLoc = [1440, 307]
    chaosTabPosition = {
        # punika
        1100: [punikaChaosTabLoc, [624, 400]],
        1310: [punikaChaosTabLoc, [624, 455]],
        1325: [punikaChaosTabLoc, [624, 505]],
        1340: [punikaChaosTabLoc, [624, 555]],
        1355: [punikaChaosTabLoc, [624, 605]],
        1370: [punikaChaosTabLoc, [624, 660]],
        1385: [punikaChaosTabLoc, [624, 715]],
        1400: [punikaChaosTabLoc, [624, 770]],
        # south vern
        1415: [svernChaosTabLoc, [624, 400]],
        1445: [svernChaosTabLoc, [624, 455]],
        1475: [svernChaosTabLoc, [624, 505]],
        1490: [svernChaosTabLoc, [624, 555]],
        1520: [svernChaosTabLoc, [624, 605]],
        1540: [svernChaosTabLoc, [624, 660]],
        1560: [svernChaosTabLoc, [624, 715]],
        # elgacia
        1580: [elgaciaChaosTabLoc, [624, 400]],
        1600: [elgaciaChaosTabLoc, [624, 455]],
        # voldis
        1610: [voldisChaosTabLoc, [624, 400]],
        1630: [voldisChaosTabLoc, [624, 455]],
    }
    if states["multiCharacterMode"] or aura0 is None:
        mouseMoveTo(
            x=chaosTabPosition[_curr["chaos_ilvl"]][0][0],
            y=chaosTabPosition[_curr["chaos_ilvl"]][0][1],
        )
        sleep(800, 900)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
        mouseMoveTo(
            x=chaosTabPosition[_curr["chaos_ilvl"]][1][0],
            y=chaosTabPosition[_curr["chaos_ilvl"]][1][1],
        )
        sleep(800, 900)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left",)
        sleep(500, 600)
    else:
        mouseMoveTo(
            x=chaosTabPosition[_curr["chaos_ilvl"]][0][0],
            y=chaosTabPosition[_curr["chaos_ilvl"]][0][1],
        )
        sleep(800, 900)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
        mouseMoveTo(
            x=chaosTabPosition[_curr["chaos_ilvl"]][1][0],
            y=chaosTabPosition[_curr["chaos_ilvl"]][1][1],
        )
        sleep(800, 900)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)

    enterButton = findImageCenter(
        "./screenshots/enterButton.png",
        confidence=0.75,
        region=(1380, 760, 210, 60),
    )
    if enterButton is not None:
        x, y = enterButton
        mouseMoveTo(x=x, y=y)
        sleep(200, 300)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")

    sleep(500, 600)

    acceptButton = findImageCenter(
        "./screenshots/acceptButton.png",
        confidence=0.75,
        region=config["regions"]["center"],
    )
    if acceptButton is not None:
        x, y = acceptButton
        mouseMoveTo(x=x, y=y)
        sleep(200, 300)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
    return True

def doChaos():
    if not enterChaos():
        return
    while states["remainingChaosRuns"][states["currentCharacter"]] > 0:
        doFloor(1)
        doFloor(2)
        doFloor(3)
        if states["remainingChaosRuns"][states["currentCharacter"]] == 2:
            states["remainingChaosRuns"][states["currentCharacter"]] -= 1
            restartChaos()
        elif datetime.now().hour == config["resetHour"]:
            quitChaos()
            raise resetException
        else:
            states["remainingChaosRuns"][states["currentCharacter"]] -= 1
            quitChaos()
    
def doFloor(n):
    waitForLoading()
    print(f"floor {n} loaded")
    if n == 1:  
        saveAbilitiesScreenshots()
    
    if config["auraRepair"]:
        doAuraRepair(False)

    pydirectinput.click(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y, button=config["move"])
    sleep(1000, 1100)

    useAbilities(n)
    print(f"floor {n} cleared")
    
    restartCheck()
    if checkTimeout():
        quitChaos()
        raise timeoutException


class resetException(Exception):
    pass

class timeoutException(Exception):
    pass

def quitChaos():
    checkChaosFinish()
    # quit
    print("quitting chaos")
    sleep(100, 200)
    while True:
        leaveButton = findImageCenter(
            "./screenshots/chaos/leave.png",
            grayscale=True,
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if leaveButton is not None:
            x, y = leaveButton
            mouseMoveTo(x=x, y=y)
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(200, 300)
        sleep(300, 400)
        okButton = findImageCenter(
            "./screenshots/ok.png",
            confidence=0.75,
            region=config["regions"]["center"],
        )
        if okButton is not None:
            x, y = okButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            break
        sleep(300, 400)
    sleep(5000, 7000)
    return

def restartChaos():
    sleep(1200, 1400)
    # states["abilityScreenshots"] = []
    states["instanceStartTime"] = int(time.time_ns() / 1000000)

    while True:
        selectLevelButton = findImageCenter(
            "./screenshots/chaos/selectLevel.png",
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if selectLevelButton is not None:
            x, y = selectLevelButton

            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            sleep(100, 200)
            pydirectinput.click(button="left")
            break
        sleep(100, 200)
    sleep(100, 200)
    while True:
        enterButton = findImageCenter(
            "./screenshots/enterButton.png",
            confidence=0.75,
            region=(1380, 760, 210, 60),
        )
        if enterButton is not None:
            x, y = enterButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            sleep(100, 200)
            pydirectinput.click(button="left")
            break
        sleep(100, 200)
    sleep(100, 200)
    while True:
        acceptButton = findImageCenter(
            "./screenshots/acceptButton.png",
            confidence=0.75,
            region=config["regions"]["center"],
        )
        if acceptButton is not None:
            x, y = acceptButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            sleep(100, 200)
            pydirectinput.click(button="left")
            break
        sleep(100, 200)
    sleep(2000, 3200)
    return

def printResult():
    if int(states["clearCount"] + states["fullClearCount"]) == 0:
        return
    lastRun = (int(time.time_ns() / 1000000) - states["instanceStartTime"]) / 1000
    avgTime = int(
        ((int(time.time_ns() / 1000000) - states["botStartTime"]) / 1000)
        / (states["clearCount"] + states["fullClearCount"])
    )
    if states["instanceStartTime"] != -1:
        states["minTime"] = int(min(lastRun, states["minTime"]))
        states["maxTime"] = int(max(lastRun, states["maxTime"]))
    print(
        "floor 2 runs: {}, floor 3 runs: {}, timeout runs: {}, death: {}, dc: {}, crash: {}, restart: {}, accidentalEnter: {}, lowHpCount : {}".format(
            states["clearCount"],
            states["fullClearCount"],
            states["timeoutCount"],
            states["deathCount"],
            states["gameOfflineCount"],
            states["gameCrashCount"],
            states["gameRestartCount"],
            # entered next floor by accident
            states["badRunCount"],
            # not how many pot consumed, just shows how frequent low hp happens
            states["healthPotCount"],
        )
    )
    print(
        "Average time: {}, fastest time: {}, slowest time: {}".format(
            avgTime,
            states["minTime"],
            states["maxTime"],
        )
    )

def useAbilities(floor):
    minimap = Minimap()
    characterAbilities = abilities[config["characters"][states["currentCharacter"]]["class"]]
    normalAbilities = [ability for ability in characterAbilities if ability["abilityType"] != "awakening"]
    while True:
        diedCheck()
        healthCheck()
        restartCheck()
        if checkTimeout():
            return

        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()

        # check for accident
        if floor == 1 and minimap.checkElite():
            print("accidentally entered floor 2")
            states["badRunCount"] = states["badRunCount"] + 1
            return
        elif floor == 2 and minimap.checkFloor3Tower():
            print("accidentally entered floor 3")
            states["badRunCount"] = states["badRunCount"] + 1
            return

        if floor == 1 and not minimap.checkMob():
            print("no floor 1 mob detected, random move")
            randomMove()
        elif floor == 2 and not minimap.checkElite() and not minimap.checkMob():
            print("no floor 2 elite/mob detected, random move")
            randomMove()
        elif floor == 3 and minimap.checkElite():
            x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
            moveToMinimapRelative(x, y, moveDuration)
        elif floor == 3 and not minimap.checkFloor3Tower() and not minimap.checkElite() and not minimap.checkMob():
            randomMove()

        allAbilities = [*range(0, len(normalAbilities))]

        # cast sequence
        for i in range(0, len(normalAbilities)):
            if floor == 3 and checkChaosFinish():
                print("checkChaosFinish == True")
                return
            diedCheck()
            healthCheck()

            if minimap.checkPortal() and (floor == 1 or floor == 2):
                pydirectinput.click(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y, button=config["move"])
                sleep(100, 150)
                while True:
                    minimap.checkPortal()
                    x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                    if enterPortal(x, y, moveDuration):
                        break
                    if checkTimeout():
                        raise timeoutException
                return

            # click rift core
            if floor == 3:
                clickTower()

            # check high-priority mobs
            match floor:
                case 1:
                    if minimap.checkMob():
                        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                case 2:
                    if minimap.checkFloor2Boss() or minimap.checkElite() or minimap.checkMob():
                        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                        moveToMinimapRelative(x, y, moveDuration / 2)
                        if minimap.checkFloor2Boss():
                            fightFloor2Boss(x, y)
                case 3:
                    if minimap.checkFloor3Tower() or minimap.checkElite() or minimap.checkMob():
                        x, y, moveDuration = minimap.getGameCoordsOfMinimapTarget()
                        moveToMinimapRelative(x, y, moveDuration)
                        if not minimap.checkElite() and not minimap.checkMob():
                            minimap.checkFloor3Tower()
                            newX, newY, _ = minimap.getGameCoordsOfMinimapTarget()
                            if newX - 30 < x < newX + 30 and newY - 20 < y < newY + 20:
                                randomMove()

            performClassSpecialty(i, normalAbilities)
            # cast spells
            castAbility(x, y, normalAbilities[i])

def performClassSpecialty(i, abilities):
    currentCharacterClass = config["characters"][states["currentCharacter"]]["class"]

    match currentCharacterClass:
        case "arcana":
            pydirectinput.press(config["specialty1"])
            pydirectinput.press(config["specialty2"])
        case "souleater":
            if findImageRegion(
                "./screenshots/classSpecialties/soulSnatch.png",
                region=config["regions"]["debuffs"],
                confidence=0.85,
            ) is not None:
                castAbility(abilities[0])
                sleep(300, 400)
                castAbility(abilities[1])
                sleep(300, 400)
                castAbility(abilities[5])
                sleep(300, 400)
        case "slayer":
            slayerSpecialty = findImageRegion(
                "./screenshots/classSpecialties/slayerSpecialty.png",
                region=config["regions"]["specialty"],
                confidence=0.85,
            )
            if slayerSpecialty is not None:
                pydirectinput.press(config["specialty1"])
                sleep(150, 160)
        case "deathblade":
            threeOrbDeathTrance = findImageRegion(
                "./screenshots/classSpecialties/deathTrance.png",
                region=config["regions"]["specialty"],
                confidence=0.80,
            )
            if threeOrbDeathTrance is not None:
                pydirectinput.press(config["specialty1"])
                sleep(150, 160)
        case "gunslinger":
            pistolStance = findImageRegion(
                "./screenshots/classSpecialties/pistolStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            )
            shotgunStance = findImageRegion(
                "./screenshots/classSpecialties/shotgunStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            )
            sniperStance = findImageRegion(
                "./screenshots/classSpecialties/sniperStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            )
            # swap to shotgun
            if i == 0:
                if shotgunStance is None:
                    if pistolStance is not None:
                        pydirectinput.press(config["specialty1"])
                        sleep(150, 160)
                    if sniperStance is not None:
                        pydirectinput.press(config["specialty2"])
                        sleep(150, 160)
            # swap to sniper
            elif i < 3:
                if sniperStance is None:
                    if pistolStance is not None:
                        pydirectinput.press(config["specialty2"])
                        sleep(150, 160)
                    if shotgunStance is not None:
                        pydirectinput.press(config["specialty1"])
                        sleep(150, 160)
            # swap to pistol
            else:
                if pistolStance is None:
                    if shotgunStance is not None:
                        pydirectinput.press(config["specialty2"])
                        sleep(150, 160)
                    if sniperStance is not None:
                        pydirectinput.press(config["specialty1"])
                        sleep(150, 160)
        case "artist":
            artistOrb = findImageRegion(
                "./screenshots/classSpecialties/artistOrb.png",
                region=config["regions"]["specialty"],
                confidence=0.85,
            )
            if artistOrb is not None:
                mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                sleep(150, 160)
                pydirectinput.press(config["specialty2"])
                sleep(1500, 1600)
                pydirectinput.press(config["interact"])
        case "aeromancer":
            aeroSpecialty = findImageRegion(
                "./screenshots/classSpecialties/aeroSpecialty.png",
                region=config["regions"]["specialty"],
                confidence=0.95,
            )
            if aeroSpecialty is not None:
                sleep(150, 160)
                pydirectinput.press(config["specialty1"])
        case "scrapper":
            scrapperSpecialty = findImageRegion(
                "./screenshots/classSpecialties/scrapperSpecialty.png",
                region=config["regions"]["specialty"],
                confidence=0.85,
            )
            if scrapperSpecialty is not None:
                sleep(150, 160)
                pydirectinput.press("z")
        case "bard":
            courageBuffActive = findImageRegion(
                "./screenshots/classSpecialties/bardCourage120.png",
                region=config["regions"]["buffs"],
                confidence=0.75,
            )
            rZ, gZ, bZ = pyautogui.pixel(920, 866)
            rX, gX, bX = pyautogui.pixel(1006, 875)
            if rZ - gZ > 80 and courageBuffActive is None:
                pydirectinput.press("z")
                sleep(50, 60)
                pydirectinput.press("z")
                sleep(150, 160)
            elif bX - gX > 70 and courageBuffActive is not None:
                mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
                sleep(150, 160)
                pydirectinput.press("x")
                sleep(50, 60)
                pydirectinput.press("x")
                sleep(150, 160)

def castAbility(x, y, ability):
    if ability["directional"]:
        mouseMoveTo(x=x, y=y)
    else:
        mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)

    if ability["castTime"] is not None:
        pydirectinput.press(ability["key"])
        sleep(100, 150)
        pydirectinput.press(ability["key"])
        sleep(ability["castTime"], (ability["castTime"] + 100))
    elif ability["holdTime"] is not None:
        pydirectinput.keyDown(ability["key"])
        sleep(ability["holdTime"], (ability["holdTime"] + 100))
        pydirectinput.keyUp(ability["key"])
    else:
        pydirectinput.press(ability["key"])
        sleep(100, 150)
        pydirectinput.press(ability["key"])
        sleep(100, 150)
        pydirectinput.press(ability["key"])

class Minimap():
    def __init__(self):
        self.targetX = 0
        self.targetY = 0

    def findClosestMinimapPixel(self, name, inColorRange):
        minimap = pyautogui.screenshot(region=MINIMAP_REGION)
        width, height = minimap.size
        order = spiralSearch(width, height, math.floor(width / 2), math.floor(height / 2))
        for entry in order:
            if entry[0] >= width or entry[1] >= height:
                continue
            r, g, b = minimap.getpixel((entry[0], entry[1]))
            if inColorRange(r, g, b):
                left, top, _w, _h = MINIMAP_REGION
                self.targetX = left + entry[0] - MINIMAP_CENTER_X
                self.targetY = top + entry[1] - MINIMAP_CENTER_Y
                print(f"{name} pixel at x:{self.targetX} y:{self.targetY}")
                return True
        self.targetX = 0
        self.targetY = 0
        return False
    
    def checkMob(self):
        if config["GFN"]:
            return self.findClosestMinimapPixel("mob", MOB_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("mob", MOG_RGB_RANGE)
    
    def checkElite(self):
        if config["GFN"]:
            return self.findClosestMinimapPixel("elite", ELITE_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("elite", ELITE_RGB_RANGE)
        
    def checkPortal(self):
        if config["performance"] == False:
            for portalPart in ["portal", "portalTop", "portalBot"]:
                portalCoords = findImageCenter(
                    "./screenshots/chaos/" + portalPart + ".png",
                    region=MINIMAP_REGION,
                    confidence=0.7,
                )
                match portalPart:
                    case "portal":
                        offset = 0
                    case "portalTop":
                        offset = 7
                    case "portalBot":
                        offset = -7
                    
                if portalCoords is not None:
                    x, y = portalCoords
                    self.targetX = x - MINIMAP_CENTER_X
                    self.targetY = y - MINIMAP_CENTER_Y + offset
                    print(f"{portalPart} image x: {self.targetX} y: {self.targetY}")
                    return True
        if config["GFN"]:
            return self.findClosestMinimapPixel("portal", PORTAL_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("portal", PORTAL_RGB_RANGE)
    
    def checkFloor2Boss(self):
        bossLocation = findImageCenter(
            "./screenshots/chaos/boss.png", confidence=0.65, region=MINIMAP_REGION
        )
        if bossLocation is not None:
            x, y = bossLocation
            self.targetX = x - MINIMAP_CENTER_X
            self.targetY = y - MINIMAP_CENTER_Y
            print(f"boss x: {self.targetX} y: {self.targetY}")
            return True
        bossbar = findImageRegion(
            "./screenshots/chaos/bossBar.png", confidence=0.8, region=(406, 159, 1000, 200)
        )
        if bossbar is not None:
            self.targetX = 0
            self.targetY = 0
            return True
        return False
        
    def checkFloor3Tower(self):
        for towerPart in ["tower", "towerTop", "towerBot"]:
            towerCoords = findImageCenter(
                "./screenshots/chaos/" + towerPart + ".png", 
                region=MINIMAP_REGION, 
                confidence=0.7
            )
            if towerCoords is not None:
                x, y = towerCoords
                self.targetX = x - MINIMAP_CENTER_X
                self.targetY = y - MINIMAP_CENTER_Y
                print(f"{towerPart} at x: {self.targetX} y: {self.targetY}")
                return True
        return False
    
    def getGameCoordsOfMinimapTarget(self):
        magnitude = math.sqrt(self.targetX * self.targetX + self.targetY * self.targetY)
        magnitude = max(magnitude, 1)

        unit_x = self.targetX / magnitude
        unit_y = self.targetY / magnitude

        x = int(unit_x * 360)
        y = int(unit_y * 240) # y axis not orthogonal to camera axis unlike minimap

        return x + SCREEN_CENTER_X, y + SCREEN_CENTER_Y, int(magnitude * 50)

def clickTower():
    for i in [1,2]:
        riftCore = findImageCenter(
            "./screenshots/chaos/riftcore" + str(i) + ".png",
            confidence=0.6,
            region=config["regions"]["portal"],
        )
        if riftCore is not None:
            x, y = riftCore
            if y > 650 or x < 400 or x > 1500:
                return
            pydirectinput.click(x=x, y=y+190, button=config["move"])
            sleep(100, 120)
            pydirectinput.press(config["meleeAttack"])
            sleep(300, 360)
            pydirectinput.press(config["meleeAttack"])
            sleep(300, 360)
            pydirectinput.press(config["meleeAttack"])
            sleep(100, 120)
            pydirectinput.press(config["meleeAttack"])

def checkChaosFinish():
    clearOk = findImageCenter(
        "./screenshots/chaos/clearOk.png", confidence=0.75, region=(625, 779, 500, 155)
    )
    if clearOk is not None:
        states["fullClearCount"] = states["fullClearCount"] + 1
        x, y = clearOk
        mouseMoveTo(x=x, y=y)
        sleep(800, 900)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(200, 300)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(200, 300)
    return clearOk is not None


def fightFloor2Boss(x, y):
    mouseMoveTo(x=x, y=y)
    sleep(80, 100)
    currentCharacterClass = config["characters"][states["currentCharacter"]]["class"]
    awakening = [ability for ability in abilities[currentCharacterClass] if ability["abilityType"] == "awakening"][0]
    if not awakening["directional"]:
        mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)

    if awakening["castTime"] is not None:
        pydirectinput.press(awakening["key"])
        sleep(100, 150)
        pydirectinput.press(awakening["key"])
        sleep(awakening["castTime"])
    elif awakening["holdTime"] is not None:
        pydirectinput.keyDown(awakening["key"])
        sleep(awakening["holdTime"], awakening["holdTime"] + 100)
        pydirectinput.keyUp(awakening["key"])
    else:
        pydirectinput.press(awakening["key"])
        sleep(100, 150)
        pydirectinput.press(awakening["key"])

def moveToMinimapRelative(x, y, duration):
    if x == SCREEN_CENTER_X and y == SCREEN_CENTER_Y:
        return
    halfstep = int(duration / 2)
    for _ in range(2):
        pydirectinput.click(x=x, y=y, button=config["move"])
        sleep(halfstep - 50, halfstep + 50)
    return

def randomMove():
    left, top, width, height = CHAOS_CLICKABLE_REGION
    x = random.randint(left, left + width)
    y = random.randint(top, top + height)

    print("random move to x: {} y: {}".format(x, y))
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(200, 250)
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(200, 250)

def enterPortal(x, y, moveDuration):
    # repeatedly move and press g until black screen
    # sleep(1100, 1200)
    # print("moving to portal x: {} y: {}".format(states["moveToX"], states["moveToY"]))
    # print("move for {} ms".format(states["moveTime"]))
    if moveDuration > 550:
        pydirectinput.click(x=x, y=y, button=config["move"])
        sleep(100, 150)
        if config["characters"][states["currentCharacter"]]["class"] != "gunlancer":
            pydirectinput.press(config["blink"])

    start = int(time.time_ns() / 1000000)
    while True:
        # try to enter portal until black screen
        im = pyautogui.screenshot(region=(1652, 168, 240, 210))
        r, g, b = im.getpixel((1772 - 1652, 272 - 168))
        if r + g + b < 30:
            mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
            return True

        now = int(time.time_ns() / 1000000)
        if now - start > 3000:
            # clear mobs a bit with first spell before scanning for portal again
            # TODO change q
            pydirectinput.press("q")
            sleep(100, 150)
            pydirectinput.press(config["meleeAttack"])
            sleep(100, 150)
            return False
        # hit move and press g
        if (x == SCREEN_CENTER_X and y == SCREEN_CENTER_Y):
            pydirectinput.press(config["interact"])
            sleep(100, 120)
            pydirectinput.press(config["interact"])
        else:
            pydirectinput.press(config["interact"])
            pydirectinput.click(x=x, y=y, button=config["move"])
            sleep(60, 70)
            # pydirectinput.press(config["interact"])

def waitForLoading():
    blackScreenStartTime = int(time.time_ns() / 1000000)
    while True:
        restartCheck()
        currentTime = int(time.time_ns() / 1000000)
        if currentTime - blackScreenStartTime > config["blackScreenTimeLimit"]:
            # pyautogui.hotkey("alt", "f4")
            print("alt f4")
            pydirectinput.keyDown("alt")
            sleep(350, 400)
            pydirectinput.keyDown("f4")
            sleep(350, 400)
            pydirectinput.keyUp("alt")
            sleep(350, 400)
            pydirectinput.keyUp("f4")
            sleep(350, 400)
            sleep(10000, 15000)
            return
        leaveButton = findImageRegion(
            "./screenshots/chaos/leave.png",
            grayscale=True,
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if leaveButton is not None:
            return
        sleep(350, 400)

def saveAbilitiesScreenshots():
    for ability in abilities[config["characters"][states["currentCharacter"]]["class"]]:
        if ability["abilityType"] not in ["specialty1", "specialty2"]:
            ability.update({"image": pyautogui.screenshot(region=ability["position"])})
            sleep(100, 150)

def diedCheck():  # get information about wait a few second to revive
    if findImageRegion(
        "./screenshots/chaos/died.png",
        grayscale=True,
        confidence=0.8,
        region=(917, 145, 630, 550),
    ):
        print("died")
        states["deathCount"] = states["deathCount"] + 1
        sleep(5000, 5500)
        while (
            findImageRegion(
                "./screenshots/chaos/resReady.png",
                confidence=0.7,
                region=(917, 145, 630, 550),
            )
            is not None
        ):
            mouseMoveTo(x=1275, y=400)
            sleep(1600, 1800)
            print("rez clicked")
            pydirectinput.click(button="left")
            sleep(600, 800)
            mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
            sleep(600, 800)
            restartCheck()
            if checkTimeout():
                return
    return

# def doCubes():
#     states["status"] = "cube"
#     states["currentCharacter"] = 9
#     states["instanceStartTime"] = int(time.time_ns() / 1000000)
#     saveAbilitiesScreenshots()
#     while True:
#         diedCheck()
#         healthCheck()

#         allAbilities = [*range(0, len(states["abilityScreenshots"]))]

#         for i in allAbilities:
#             if states["status"] == "floor3" and checkChaosFinish():
#                 print("checkChaosFinish == True")
#                 return
#             diedCheck()
#             healthCheck()
            
#             performClassSpecialty(i, states["abilityScreenshots"])
#             # cast spells
#             checkCDandCast(states["abilityScreenshots"][i])


def doAuraRepair(forced):
    # Check if repair needed
    if forced or findImageRegion(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        # print("repairing")
        toggleMenu("pet")
        mouseMoveTo(x=1142, y=661)
        sleep(2500, 2600)
        pydirectinput.click(button="left")
        sleep(5500, 5600)
        mouseMoveTo(x=1054, y=455)
        sleep(2500, 2600)
        pydirectinput.click(button="left")
        sleep(2500, 2600)
        pydirectinput.press("esc")
        sleep(2500, 2600)
        pydirectinput.press("esc")
        sleep(2500, 2600)


def doCityRepair():
    # for non-aura users: MUST have your character parked near a repairer in city before starting the script
    # Check if repair needed
    if findImageRegion(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        print("repairing")
        pydirectinput.press(config["interact"])
        sleep(600, 700)
        mouseMoveTo(x=1057, y=455)
        sleep(600, 700)
        pydirectinput.click(button="left")
        sleep(600, 700)
        pydirectinput.press("esc")
        sleep(1500, 1900)


def healthCheck():
    if config["useHealthPot"] == False:
        return
    x = int(
        config["healthCheckX"]
        + (870 - config["healthCheckX"]) * config["healthPotAtPercent"]
    )
    y = config["healthCheckY"]
    r1, g, b = pyautogui.pixel(x, y)
    r2, g, b = pyautogui.pixel(x - 2, y)
    r3, g, b = pyautogui.pixel(x + 2, y)
    # print(x, r, g, b)
    if r1 < 30 or r2 < 30 or r3 < 30:
        print("health pot pressed")
        # print(r1, r2, r3)
        leaveButton = findImageCenter(
            "./screenshots/chaos/leave.png",
            grayscale=True,
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if leaveButton is None:
            return
        pydirectinput.press(config["healthPot"])
        states["healthPotCount"] = states["healthPotCount"] + 1
        return
    return


def clearQuest():
    quest = findImageCenter(
        "./screenshots/quest.png", confidence=0.9, region=(815, 600, 250, 200)
    )
    leveledup = findImageCenter(
        "./screenshots/leveledup.png", confidence=0.9, region=(815, 600, 250, 200)
    )
    gameMenu = findImageCenter(
        "./screenshots/menus/gameMenu.png",
        confidence=0.95,
        region=config["regions"]["center"],
    )
    if gameMenu is not None:
        print("game menu detected")
        pydirectinput.press("esc")
        sleep(1800, 1900)
    if quest is not None:
        print("clear quest")
        x, y = quest
        mouseMoveTo(x=x, y=y)
        sleep(1800, 1900)
        pydirectinput.click(button="left")
        sleep(1800, 1900)
        pydirectinput.press("esc")
        sleep(1800, 1900)
    elif leveledup is not None:
        print("clear level")
        x, y = leveledup
        mouseMoveTo(x=x, y=y)
        sleep(1800, 1900)
        pydirectinput.click(button="left")
        sleep(1800, 1900)
        pydirectinput.press("esc")
        sleep(1800, 1900)


def sleep(min, max):
    sleepTime = random.randint(min, max) / 1000.0
    if sleepTime < 0:
        return
    time.sleep(sleepTime)


def spiralSearch(rows, cols, rStart, cStart):
    ans = []
    end = rows * cols
    i = i1 = i2 = rStart
    j = j1 = j2 = cStart
    while True:
        j2 += 1
        while j < j2:
            if 0 <= j < cols and 0 <= i:
                ans.append([i, j])
            j += 1
            if 0 > i:
                j = j2
        i2 += 1
        while i < i2:
            if 0 <= i < rows and j < cols:
                ans.append([i, j])
            i += 1
            if j >= cols:
                i = i2
        j1 -= 1
        while j > j1:
            if 0 <= j < cols and i < rows:
                ans.append([i, j])
            j -= 1
            if i >= rows:
                j = j1
        i1 -= 1
        while i > i1:
            if 0 <= i < rows and 0 <= j:
                ans.append([i, j])
            i -= 1
            if 0 > j:
                i = i1
        if len(ans) == end:
            return ans


def checkTimeout():
    currentTime = int(time.time_ns() / 1000000)
    # hacky way of quitting
    if states["instanceStartTime"] == -1:
        print("hacky timeout")
        return True
    if (
        states["multiCharacterMode"] == False
        and currentTime - states["instanceStartTime"] > config["timeLimit"]
    ):
        print("timeout triggered")
        timeout = pyautogui.screenshot()
        timeout.save("./debug/timeout_" + str(currentTime) + ".png")
        states["timeoutCount"] = states["timeoutCount"] + 1
        return True
    elif (
        states["multiCharacterMode"] == True
        and states["floor3Mode"] == True
        and currentTime - states["instanceStartTime"] > config["timeLimitAor"]
    ):
        print("timeout on aor triggered :(")
        timeout = pyautogui.screenshot()
        timeout.save("./debug/timeout_aor_" + str(currentTime) + ".png")
        states["timeoutCount"] = states["timeoutCount"] + 1
        return True
    return False


def gameCrashCheck():
    # should put these in crash check instead? No because it requires one more click
    if config["GFN"] == True:
        sessionLimitReached = findImageCenter(
            "./screenshots/GFN/sessionLimitReached.png",
            region=config["regions"]["center"],
            confidence=0.8,
        )
        if sessionLimitReached is not None:
            currentTime = int(time.time_ns() / 1000000)
            limitshot = pyautogui.screenshot()
            limitshot.save("./debug/sessionLimitReached" + str(currentTime) + ".png")
            mouseMoveTo(x=1029, y=822)
            sleep(1300, 1400)
            pydirectinput.click(button="left")
            sleep(1300, 1400)
            print("session limit...")
            states["gameCrashCount"] = states["gameCrashCount"] + 1
            return True
        inactiveGFN = findImageCenter(
            "./screenshots/GFN/inactiveGFN.png",
            region=config["regions"]["center"],
            confidence=0.8,
        )
        if inactiveGFN is not None:
            currentTime = int(time.time_ns() / 1000000)
            inactive = pyautogui.screenshot()
            inactive.save("./debug/inactive_" + str(currentTime) + ".png")
            mouseMoveTo(x=1194, y=585)
            sleep(1300, 1400)
            pydirectinput.click(button="left")
            sleep(1300, 1400)
            print("game inactive...")
            states["gameCrashCount"] = states["gameCrashCount"] + 1
            return True
    # if bottom black bar is not black, then crash
    bottom = pyautogui.screenshot(region=(600, 960, 250, 50))
    r1, g1, b1 = bottom.getpixel((0, 0))
    r2, g2, b2 = bottom.getpixel((0, 49))
    r3, g3, b3 = bottom.getpixel((249, 0))
    r4, g4, b4 = bottom.getpixel((249, 49))
    sum = r1 + g1 + b1 + r2 + g2 + b2 + r3 + g3 + b3 + r4 + g4 + b4
    if sum > 50:
        print("game crashed, restarting game client...")
        currentTime = int(time.time_ns() / 1000000)
        crash = pyautogui.screenshot()
        crash.save("./debug/crash_" + str(currentTime) + ".png")
        states["gameCrashCount"] = states["gameCrashCount"] + 1
        return True
    return False


def restartCheck():
    dc = findImageRegion(
        "./screenshots/dc.png",
        region=config["regions"]["center"],
        confidence=config["confidenceForGFN"],
    )
    ok = findImageCenter(
        "./screenshots/ok.png", region=config["regions"]["center"], confidence=0.75
    )
    enterServer = findImageCenter(
        "./screenshots/enterServer.png",
        confidence=config["confidenceForGFN"],
        region=(885, 801, 160, 55),
    )
    if dc is not None or ok is not None or enterServer is not None:
        currentTime = int(time.time_ns() / 1000000)
        dc = pyautogui.screenshot()
        dc.save("./debug/dc_" + str(currentTime) + ".png")
        print(
            "disconnection detected...currentTime : {} dc:{} ok:{} enterServer:{}".format(
                currentTime, dc, ok, enterServer
            )
        )
        states["gameOfflineCount"] = states["gameOfflineCount"] + 1
        raise restartException
    if config["GFN"] == True:
        for errorType in ["sessionLimitReached", "updateMembership", "inactiveGFN"]:
            errorPresence = findImageCenter(
                "./screenshots/GFN/"+errorType+".png",
                region=config["regions"]["center"],
                confidence=0.8,
            )
            if errorPresence is not None:
                currentTime = int(time.time_ns() / 1000000)
                limitshot = pyautogui.screenshot()
                limitshot.save("./debug/" + errorType + str(currentTime) + ".png")
                mouseMoveTo(x=1029, y=822)
                sleep(1300, 1400)
                pydirectinput.click(button="left")
                sleep(1300, 1400)
                print(errorType)
                states["gameCrashCount"] = states["gameCrashCount"] + 1
                raise restartException
    bottom = pyautogui.screenshot(region=(600, 960, 250, 50))
    r1, g1, b1 = bottom.getpixel((0, 0))
    r2, g2, b2 = bottom.getpixel((0, 49))
    r3, g3, b3 = bottom.getpixel((249, 0))
    r4, g4, b4 = bottom.getpixel((249, 49))
    sum = r1 + g1 + b1 + r2 + g2 + b2 + r3 + g3 + b3 + r4 + g4 + b4
    if sum > 50:
        print("game crashed, restarting game client...")
        currentTime = int(time.time_ns() / 1000000)
        crash = pyautogui.screenshot()
        crash.save("./debug/crash_" + str(currentTime) + ".png")
        states["gameCrashCount"] = states["gameCrashCount"] + 1
        raise restartException

class restartException(Exception):
    pass

def restartGame():
    print("restart game")
    # gameCrashCheck()
    sleep(5000, 7000)
    while True:
        if config["GFN"] == True:
            sleep(10000, 12000)
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
                sleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked play restart on GFN")
                sleep(40000, 42000)
                break
            if loaGFN is not None:
                x, y = loaGFN
                mouseMoveTo(x=x, y=y)
                sleep(2200, 2300)
                pydirectinput.click(button="left")
                print("clicked image restart on GFN")
                sleep(40000, 42000)
                break
            afkGFN = findImageCenter(
                "./screenshots/GFN/afkGFN.png",
                region=config["regions"]["center"],
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
                sleep(1300, 1400)
                pydirectinput.click(button="left")
                sleep(1300, 1400)
                continue
        else:
            os.system('start steam://launch/1599340/dialog')
            sleep(60000, 60000)
        enterGame = findImageCenter(
            "./screenshots/steamPlay.png", confidence=0.75
        )
        sleep(500, 600)
        stopGame = findImageCenter(
            "./screenshots/steamStop.png", confidence=0.75
        )
        sleep(500, 600)
        confirm = findImageCenter(
            "./screenshots/steamConfirm.png", confidence=0.75
        )
        sleep(500, 600)
        enterServer = findImageCenter(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        sleep(500, 600)
        channelDropdownArrow = findImageCenter(
            "./screenshots/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if stopGame is not None:
            print("clicking stop game on steam")
            x, y = stopGame
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(button="left")
            sleep(500, 600)
            confirm = findImageCenter(
                "./screenshots/steamConfirm.png", confidence=0.75
            )
            if confirm is None:
                continue
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(button="left")
            sleep(10000, 12000)
        elif confirm is not None:
            print("confirming stop game")
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(button="left")
            sleep(10000, 12000)
        elif enterGame is not None:
            print("restarting Lost Ark game client...")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(button="left")
            break
        elif enterServer is not None:
            break
        elif channelDropdownArrow is not None:
            return
        sleep(1200, 1300)
    sleep(5200, 6300)
    while True:
        enterServer = findImageCenter(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        enterGame = findImageCenter(
            "./screenshots/steamPlay.png", confidence=0.75
        )
        if enterServer is not None:
            print("clicking enterServer")
            sleep(1000, 1200)
            # click first server
            mouseMoveTo(x=855, y=582)
            sleep(1200, 1300)
            pydirectinput.click(button="left")
            sleep(1000, 1200)
            x, y = enterServer
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(button="left")
            break
        elif enterGame is not None:
            print("clicking enterGame")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            sleep(4200, 5300)
            continue
    sleep(3200, 4300)
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
            sleep(200, 300)
            pydirectinput.click(button="left")
            break
        sleep(2200, 3300)
    states["gameRestartCount"] = states["gameRestartCount"] + 1
    mouseMoveTo(x=SCREEN_CENTER_X, y=SCREEN_CENTER_Y)
    sleep(22200, 23300)

def switchToCharacter(index):
    sleep(1500, 1600)
    print("switching to {}".format(index))
    while findImageCenter(
        "./screenshots/menus/gameMenu.png",
        confidence=0.7
    ) is None:
        pydirectinput.press("esc")
        sleep(1800, 1900)
    print("game menu detected")
    mouseMoveTo(x=540, y=700)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)

    mouseMoveTo(x=1270, y=430)
    for _ in range(5):
        sleep(200, 300)
        pydirectinput.click(button="left")

    if index > 8:
        mouseMoveTo(x=1267, y=638)
        sleep(500, 600)
        for i in range(math.floor(index/3) - 2):
            pydirectinput.click(button="left")
            sleep(500, 600)

    mouseMoveTo(
        x=config["charPositions"][index][0], 
        y=config["charPositions"][index][1]
    )
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(1500, 1600)

    if findImageCenter(
        "./screenshots/alreadyConnected.png",
        confidence=0.85
    ) is not None:
        print("character already connected")
        pydirectinput.press("esc")
        sleep(500, 600)
        pydirectinput.press("esc")
        sleep(500, 600)
        return

    mouseMoveTo(x=1030, y=700)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(1000, 1000)

    mouseMoveTo(x=920, y=590)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(500, 600)

    states["currentCharacter"] = index
    states["abilityScreenshots"] = []
    sleep(10000, 12000)
    if config["GFN"] == True:
        sleep(8000, 9000)


def doGuildDonation():
    toggleMenu("guild")
    waitForMenuLoaded("guild")

    ok = findImageCenter(
        "./screenshots/ok.png", region=config["regions"]["center"], confidence=0.75
    )

    if ok is not None:
        x, y = ok
        mouseMoveTo(x=x, y=y)
        sleep(300, 400)
        pydirectinput.click(button="left")
        sleep(300, 400)
        pydirectinput.click(button="left")
    sleep(1500, 1600)

    mouseMoveTo(x=1431, y=843)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)

    # dono silver
    mouseMoveTo(x=767, y=561)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)

    pydirectinput.press("esc")
    sleep(3500, 3600)

    supportResearch = findImageCenter(
        "./screenshots/supportResearch.png",
        confidence=0.8,
        region=(1255, 210, 250, 600),
    )

    if supportResearch is not None:
        x, y = supportResearch
        print("supportResearch")
        mouseMoveTo(x=x, y=y)
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(1500, 1600)

        canSupportResearch = findImageCenter(
            "./screenshots/canSupportResearch.png",
            confidence=0.8,
            region=(735, 376, 450, 350),
        )

        if canSupportResearch is not None:
            mouseMoveTo(x=848, y=520)
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)

            mouseMoveTo(x=921, y=701)
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
        else:
            pydirectinput.press("esc")
            sleep(800, 900)

    sleep(2800, 2900)
    pydirectinput.press("esc")
    sleep(2800, 2900)
    states["remainingGuildSupport"][states["currentCharacter"]] = 0

def doLopang():
    walkLopang()
    for lopangLocation in ["Shushire", "Arthetine", "Vern"]:
        sleep(1500, 1600)
        bifrostGoTo("lopang" + lopangLocation)
        restartCheck()
        spamInteract(6000)

    states["remainingUnasTasks"][states["currentCharacter"]] = 0

def doDailyUnas(unas):
    sleep(1000, 2000)
    print("accepting dailies")
    if not acceptDailies():
        return
    restartCheck()
    
    if "lopang" in unas:
        restartCheck()
        if bifrostGoTo("lopangIsland"):
            doLopang()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 3

    if "mokomoko" in unas:
        restartCheck()
        if bifrostGoTo("mokomoko"):
            doMokomokoUna()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 1

    if "bleakNight" in unas:
        restartCheck()
        if bifrostGoTo("bleakNightFog"):
            doBleakNightFogUna()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 1

    if "prehilia" in unas:
        restartCheck()
        if bifrostGoTo("prehilia"):
            doPrehiliaUna()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 1

    if "hesteraGarden" in unas:
        restartCheck()
        if bifrostGoTo("hesteraGarden"):
            doHesteraGardenUna()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 1

    if "sageTower" in unas:
        restartCheck()
        if bifrostGoTo("sageTower"):
            doSageTowerUna()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 1

    if "southKurzan" in unas:
        restartCheck()
        if bifrostGoTo("southKurzan"):
            doSouthKurzanUna()
            states["remainingUnasTasks"][states["currentCharacter"]] -= 1
    print("unas completed")

def doBleakNightFogUna():
    pydirectinput.press("f5")
    sleep(800, 900)
    pydirectinput.press("f6")
    sleep(1800, 1900)
    claimCompletedQuest()

def doPrehiliaUna():
    toggleMenu("unaTaskCombatPreset")

    pydirectinput.press(config["prehiliaEmoteSlot"])
    spamInteract(8000)

    toggleMenu("defaultCombatPreset")

def doHesteraGardenUna():
    toggleMenu("unaTaskCombatPreset")

    pydirectinput.press(config["hesteraGardenEmoteSlot"])
    sleep(140000, 141000)
    claimCompletedQuest()
    sleep(300, 400)

    toggleMenu("defaultCombatPreset")

def doWritersLifeUna():
    sleep(5000,5100)
    toggleMenu("unaTaskCombatPreset")
    spamInteract(4000)
    pydirectinput.click(x=1100, y=750, button=config["move"])
    sleep(1500,1600)
    pydirectinput.click(x=1100, y=750, button=config["move"])
    sleep(1500,1600)
    pydirectinput.press(config["writersLifeEmoteSlot"])
    sleep(5000, 5100)
    pydirectinput.click(x=800, y=600, button=config["move"])
    sleep(1500,1600)
    spamInteract(10000)
    pydirectinput.click(x=880, y=250, button=config["move"])
    sleep(1500,1600)
    pydirectinput.click(x=880, y=250, button=config["move"])
    sleep(1500,1600)
    spamInteract(4000)
    sleep(300, 400)
    toggleMenu("defaultCombatPreset")

def doSageTowerUna():
    for _ in range(10):
        spamInteract(1000)
        if findImageRegion("./screenshots/sageTowerCompleted.png", region = (1700,220,100,150), confidence = 0.65) is not None:
            break
    mouseMoveTo(x=1560, y=540)
    sleep(500, 600)
    pydirectinput.click(x=1560, y=540, button=config["move"])
    sleep(500, 600)
    spamInteract(3000)

def doGhostStoryUna():
    for _ in range(15):
        spamInteract(1000)
        if findImageRegion("./screenshots/ghostStoryF5.png", region = (1575,440,80,450), confidence = 0.85) is not None:
            break
    pydirectinput.press("f5")
    sleep(200, 300)
    pydirectinput.press("f6")
    sleep(200, 300)
    claimCompletedQuest()
    sleep(300, 400)

def doSouthKurzanUna():
    toggleMenu("unaTaskCombatPreset")

    pydirectinput.press(config["southKurzanPoseSlot"])
    sleep(14000, 14100)

    toggleMenu("defaultCombatPreset")
    
    mouseMoveTo(x=650, y=180)
    sleep(500, 600)
    pydirectinput.click(x=650, y=180, button="left")
    sleep(2500, 2600)
    pydirectinput.click(x=650, y=180, button="left")
    sleep(2500, 2600)
    spamInteract(4000)

def doMokomokoUna():
    spamInteract(4000)
    mouseMoveTo(x=416, y=766)
    sleep(500, 600)
    pydirectinput.click(x=416, y=766, button="left")
    sleep(5500, 5600)

    mouseMoveTo(x=960, y=770)
    sleep(500, 600)
    pydirectinput.click(x=960, y=770, button=config["move"])
    sleep(1500, 1600)
    pydirectinput.press(config["interact"])
    sleep(5500, 5600)

    mouseMoveTo(x=1360, y=900)
    sleep(500, 600)
    pydirectinput.click(x=1360, y=900, button=config["move"])
    sleep(1500, 1600)
    pydirectinput.press(config["interact"])
    sleep(5500, 5600)

    mouseMoveTo(x=960, y=330)
    sleep(1500, 1600)
    pydirectinput.click(x=980, y=280, button=config["move"])
    sleep(1500, 1600)
    pydirectinput.click(x=980, y=280, button=config["move"])
    sleep(1500, 1600)
    spamInteract(4000)
    sleep(1500, 1600)

def claimCompletedQuest():
    mouseMoveTo(x=1700, y=430)
    sleep(1500, 1600)
    pydirectinput.click(x=1700, y=430, button="left")
    sleep(500, 600)

    completeQuest = findImageCenter("./screenshots/completeQuest.png", confidence=0.85)
    if completeQuest is None:
        return
    x, y = completeQuest
    mouseMoveTo(x=x, y=y)
    sleep(1500, 1600)
    pydirectinput.click(x=x, y=y, button="left")
    sleep(500, 600)

def toggleMenu(menuType):
    keys = config[menuType].split(' ')
    if len(keys) == 2:
        pydirectinput.keyDown(keys[0])
        sleep(300, 400)
        pydirectinput.press(keys[1])
        sleep(300, 400)
        pydirectinput.keyUp(keys[0])
        sleep(300, 400)
    elif len(keys) == 1:
        pydirectinput.press(keys[0])
        sleep(300, 400)

def bifrostGoTo(location):
    print("bifrost to: {}".format(location))
    if findImageRegion("./screenshots/menus/bifrostMenu.png", confidence = 0.85) is None:
        toggleMenu("bifrost")
    waitForMenuLoaded("bifrost")
    bifrost = findImageCenter("./screenshots/bifrosts/" + location + "Bifrost.png", confidence=0.80)
    if bifrost is None:
        print(location + " bifrost not found, skipping")
        toggleMenu("bifrost")
        return False
    x, y = bifrost
    mouseMoveTo(x=(x + 280), y=(y - 25))
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(1500, 1600)

    # return false if bifrost on cooldown
    if checkBifrostOnCooldown():
        pydirectinput.press("esc")
        sleep(1500, 1600)
        pydirectinput.press("esc")
        sleep(1500, 1600)
        return False
    else:
        while True:
            okButton = findImageCenter(
                "./screenshots/ok.png",
                confidence=0.75,
                region=config["regions"]["center"],
            )
            if okButton is not None:
                x, y = okButton
                mouseMoveTo(x=x, y=y)
                sleep(2000, 2100)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(2000, 2100)
                break
            sleep(300, 400)
    sleep(10000, 12000)

    # wait until loaded
    if not waitForOverworldLoaded():
        return False
    return True

def walkLopang():
    """Interacts with and walks to all 3 lopang terminals."""
    sleep(1000, 2000)
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
    sleep(1000, 2000)


def checkBifrostOnCooldown():
    """Return false if bifrost move confirmation costs silver."""
    silver1k = findImageCenter(
        "./screenshots/silver1k.png",
        confidence=0.75,
        region=config["regions"]["center"],
    )
    return silver1k is None

def acceptDailies():
    """Open una menu and accept all favorited dailies. Return false if 3 favorited dailies are completed."""
    toggleMenu("unas")
    waitForMenuLoaded("unas")
    # switch to daily tab
    if findImageRegion("./screenshots/dailyTabActive.png", confidence = 0.95) is None:
        mouseMoveTo(x=550, y=255)
        sleep(100, 200)
        pydirectinput.click(button="left")
        sleep(500, 600)
    # toggle dropdown and swap to favorites
    if findImageRegion("./screenshots/addedToFavorites.png", confidence = 0.95) is None:
        mouseMoveTo(x=632, y=316)
        sleep(100, 200)
        pydirectinput.click(button="left")
        sleep(1000, 1100)
        mouseMoveTo(x=634, y=337)
        sleep(100, 200)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
        pydirectinput.click(button="left")
        sleep(500, 600)
        mouseMoveTo(x=548, y=404)
        sleep(100, 200)
        pydirectinput.click(button="left")
        sleep(500, 600)
    # if 3x completed unas detected, skip and return false
    if findImageRegion("./screenshots/unasCompleted.png", confidence = 0.85) is not None:
        print("character has already ran unas")
        toggleMenu("unas")
        return False

    # click all accept buttons
    acceptButtonRegions = list(pyautogui.locateAllOnScreen("./screenshots/acceptUna.png", region = (1165, 380, 80, 330), confidence = 0.85))
    for region in acceptButtonRegions:
        mouseMoveTo(x=region.left, y=region.top)
        sleep(100, 150)
        pydirectinput.click(button="left")
        sleep(100, 150)

    toggleMenu("unas")
    sleep(800, 900)
    return True

def walkTo(x, y, ms):
    """Move to specified pixel coordinate with millisecond delay."""
    mouseMoveTo(x=x, y=y)
    sleep(100, 100)
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(ms, ms)

def spamInteract(msDuration):
    """Presses interact key for approximately the given duration in milliseconds."""
    timeCount = msDuration / 100
    while timeCount != 0:
        pydirectinput.press(config["interact"])
        sleep(90, 120)
        timeCount = timeCount - 1

def doSailingWeekly(n):
    """
    Bifrosts to rightmost point of interest of level 5 guild sailing weekly.
    Does n number of completions before docking and repairing at Bellion Ruins.
    """
    sleep(2000,2100)
    if not bifrostGoTo("sailingWeekly"):
        return
    # open map
    sleep(2000,2100)
    toggleMenu("map")
    for i in range(0, n):
        # open menu
        sleep(2000,2100)
        toggleMenu("unas")
        waitForMenuLoaded("unas")
        if i == 0:
            # select guild weekly
            mouseMoveTo(x=920, y=255)
            sleep(100, 100)
            pydirectinput.click(button="left")
            sleep(1000,1100)
            # toggle dropdown
            mouseMoveTo(x=600, y=285)
            sleep(100, 100)
            pydirectinput.click(button="left")
            sleep(1000,1100)
            # select all quests
            mouseMoveTo(x=600, y=310)
            sleep(100, 100)
            pydirectinput.click(button="left")
            sleep(1000,1100)
            # go to last page
            mouseMoveTo(x=930, y=720)
            sleep(100, 100)
            pydirectinput.click(button="left")
            sleep(1000, 1100)
        # accept quest
        mouseMoveTo(x=1200, y=500)
        sleep(100, 100)
        pydirectinput.click(button="left")
        sleep(1000, 1100)
        # close unas menu
        toggleMenu("unas")
        sleep(1000,1100)
        # plot middle stop on map
        mouseMoveTo(x=763, y=427)
        sleep(100, 100)
        pydirectinput.keyDown("alt")
        sleep(200, 300)
        pydirectinput.click(button="left")
        sleep(200, 300)
        # plot last stop on map
        if i % 2 == 0:
            mouseMoveTo(x=566, y=501)
        else: 
            mouseMoveTo(x=960, y=505)
        sleep(200, 300)
        pydirectinput.click(button="left")
        # if last completion, plot dock location for repair
        if i == (n - 1):
            sleep(200, 300)
            mouseMoveTo(x=1055, y=600)
            sleep(200, 300)
            pydirectinput.click(button="left")
        sleep(200, 300)
        pydirectinput.keyUp("alt")
        # sleep while ship is not stopped (i.e. currently sailing to destinations)
        while findImageRegion("./screenshots/sailingIdle.png", region=(1060, 840, 50, 40), confidence=0.9) is None:
            sleep(1000,1100)
        claimCompletedQuest()
    # repair ship
    mouseMoveTo(x=1050, y=900)
    sleep(200, 300)
    pydirectinput.click(button="left")
    sleep(1000, 1100)
    pydirectinput.click(button="left")
    sleep(1000, 1100)
    okButton = findImageCenter(
            "./screenshots/ok.png",
            confidence=0.75,
        )
    if okButton is not None:
        x, y = okButton
        mouseMoveTo(x=x, y=y)
        sleep(200, 300)
        pydirectinput.click(button="left")
        sleep(200, 300)
    # dock at Bellion Ruins
    mouseMoveTo(x=1700, y=910)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(15000, 16000)
    states["remainingSailing"][states["currentCharacter"]] = 0

def mouseMoveTo(**kwargs):
    x = kwargs["x"]
    y = kwargs["y"]
    pydirectinput.moveTo(x=x, y=y)
    pydirectinput.moveTo(x=x, y=y)

def waitForOverworldLoaded():
    """Sleeps until channel dropdown arrow is on screen. Changes status to 'overworld'."""
    while True:
        restartCheck()
        channelDropdownArrow = findImageCenter(
            "./screenshots/channelDropdownArrow.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if channelDropdownArrow is not None:
            print("overworld loaded")
            states["status"] = "overworld"
            break
        sleep(1000, 1100)
    return True

def waitForMenuLoaded(menu):
    """Sleeps until menu is detected on screen. Attempts to open menu again after ~10 seconds. Times out after ~20 seconds."""
    timeout = 0
    while findImageRegion("./screenshots/menus/" + menu + "Menu.png", confidence = 0.85) is None:
        sleep(180, 220)
        timeout += 1
        if timeout == 50:
            toggleMenu(menu)
        if timeout == 100:
            return

def cleanInventory():
    toggleMenu("pet")
    pydirectinput.click(1143, 630, button="left") # pet
    sleep(3000, 3000)
    pydirectinput.click(560, 765, button="left") # roster deposit
    sleep(1500, 1600)
    pydirectinput.click(560, 765, button="left") # roster deposit
    sleep(1500, 1600)
    pydirectinput.click(880, 765, button="left") # character deposit
    sleep(1500, 1600)
    pydirectinput.click(880, 765, button="left") # character deposit
    sleep(1500, 1600)

    for _ in range(2):
        pydirectinput.press("esc")
        sleep(100, 200)

def click(x, y, sleepDur):
    pydirectinput.click(x, y, button="left")
    sleep(sleepDur, sleepDur)

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))

def set_resolution(width: int, height: int):
    if platform.system() == 'Windows':
        # adapted from [Win | dP] Dragonback
        # adapted from Peter Wood: https://stackoverflow.com/a/54262365
        devmode = pywintypes.DEVMODEType()
        devmode.PelsWidth = width
        devmode.PelsHeight = height
        devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
        
        win32api.ChangeDisplaySettings(devmode, 0)

def findImageRegion(image_path, confidence=1.0, region=None, grayscale=False):
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
        return location
    except pyautogui.ImageNotFoundException:
        return None

def findImageCenter(image_path, confidence=1.0, region=None, grayscale=False):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, region=region, grayscale=grayscale)
        return location
    except pyautogui.ImageNotFoundException:
        return None

if __name__ == "__main__":
    states = newStates.copy()
    main()
