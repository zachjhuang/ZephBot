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

pydirectinput.PAUSE = 0.05
newStates = {
    "status": "inCity",
    "abilities": [],
    "abilityScreenshots": [],
    "bossBarLocated": False,
    "clearCount": 0,
    "fullClearCount": 0,
    "moveToX": config["screenCenterX"],
    "moveToY": config["screenCenterY"],
    "moveTime": 0,
    "botStartTime": None,
    "instanceStartTime": None,
    "deathCount": 0,
    "healthPotCount": 0,
    "timeoutCount": 0,
    "goldPortalCount": 0,
    "purplePortalCount": 0,
    "badRunCount": 0,
    "gameRestartCount": 0,
    "gameCrashCount": 0,
    "gameOfflineCount": 0,
    "minTime": config["timeLimit"],
    "maxTime": -1,
    "floor3Mode": True,
    "multiCharacterMode": False,
    "currentCharacter": config["mainCharacter"],
    "multiCharacterModeState": [],
    "remainingChaosRuns": [],
    "remainingUnasTasks": [],
    "remainingGuildSupport": [],
}

def abortScript():
    os._exit(1)

def main():
    # set_resolution(1920, 1080)
    keyboard.add_hotkey('ctrl+page down', abortScript)

    print("Endless Chaos starting in seconds...")
    print("Remember to turn on Auto-disassemble")

    # Instantiate the parser
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument("--chaos", action="store_true", help="Enables 2x chaos on entire roster")
    parser.add_argument("--unas", action="store_true", help="Enables unas on entire roster")
    parser.add_argument("--guild", action="store_true", help="Enables guild donation/support on entire roster")
    parser.add_argument("--endless", action="store_true", help="Enables infinite chaos on main character")
    parser.add_argument("--sailing", action="store_true", help="Enables sailing weekly on entire roster")
    parser.add_argument("--cubes", action="store_true", help="testing cubes")
    args = parser.parse_args()

    states["doChaos"] = args.chaos
    states["doUnas"] = args.unas
    states["doGuild"] = args.guild
    states["doEndless"] = args.endless
    states["doSailing"] = args.sailing
    states["cubes"] = args.cubes

    if states["doChaos"]:
        print("doing 2x chaos")
        states["remainingChaosRuns"] = [2] * len(config["characters"])
    if states["doUnas"]:
        print("doing unas")
        states["remainingUnasTasks"] = [3] * len(config["characters"])
    if states["doGuild"]:
        print("doing guild donations/research")
        states["remainingGuildSupport"] = [1] * len(config["characters"])
    if states["doEndless"]:
        print("doing infinite chaos")

    if states["doChaos"]:
        states["multiCharacterMode"] = True
        for i in range(len(config["characters"])):
            states["multiCharacterModeState"].append(2)
        print(
            "running full runs on characters: {}".format(
                states["multiCharacterModeState"]
            )
        )
    elif states["doUnas"] or states["doGuild"] or states["doSailing"] or states["cubes"]:
        states["multiCharacterMode"] = True
        for i in range(len(config["characters"])):
            states["multiCharacterModeState"].append(-1)
        print(
            "running full runs on characters: {}".format(
                states["multiCharacterModeState"]
            )
        )

    sleep(2000, 2300)
    meleeClick = "right"
    if config["move"] == "right":
        meleeClick = "left"
    mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
    sleep(200, 300)
    pydirectinput.click(button=meleeClick)
    sleep(300, 400)

    # suspend
    pydirectinput.keyDown('ctrl')
    sleep(10, 30)
    pydirectinput.keyDown('shift')
    sleep(10, 30)
    pydirectinput.press('multiply')
    sleep(10, 30)
    pydirectinput.keyUp('shift')
    sleep(10, 30)
    pydirectinput.keyUp('ctrl')
    sleep(10, 30)

    # stay invis in friends list
    if config["invisible"] == True:
        goInvisible()

    # forceing no floor3 full clear with performance mode
    if config["performance"] == True:
        states["floor3Mode"] = False

    # save bot start time
    states["botStartTime"] = int(time.time_ns() / 1000000)

    ranOnce = False
    while True:
        if states["status"] == "inCity":
            sleep(1000, 1200)
            
            if not ranOnce:
                ranOnce = True
                switchToCharacter(config["mainCharacter"])

            if offlineCheck():
                closeGameByClickingDialogue()
                continue
            if gameCrashCheck():
                states["status"] = "restart"
                continue

            # wait until loaded
            while True:
                if gameCrashCheck():
                    states["status"] = "restart"
                    break
                if offlineCheck():
                    closeGameByClickingDialogue()
                    break
                sleep(1000, 1200)
                inTown = pyautogui.locateCenterOnScreen(
                    "./screenshots/inTown.png",
                    confidence=0.75,
                    region=(1870, 133, 25, 30),
                )
                inChaos = pyautogui.locateCenterOnScreen(
                    "./screenshots/inChaos.png",
                    confidence=0.75,
                    region=(247, 146, 222, 50),
                )
                if inTown != None:
                    print("city loaded")
                    break
                if inChaos != None:
                    print("still in the last chaos run, quitting")
                    # temp = states["multiCharacterModeState"][states["currentCharacter"]]
                    # states["multiCharacterModeState"][states["currentCharacter"]] = 0
                    quitChaos()
                    # states["multiCharacterModeState"][states["currentCharacter"]] = temp - 1
                    sleep(4000, 6000)
                if states["cubes"]:
                    break
                sleep(1400, 1600)

            # battle item preset
            toggleMenu("defaultCombatPreset")

            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(100, 200)

            if offlineCheck():
                closeGameByClickingDialogue()
                continue
            if gameCrashCheck():
                states["status"] = "restart"
                continue

            # for non-aura users: MUST have your character parked near a repairer in city before starting the script
            if config["auraRepair"] == False:
                doCityRepair()

            # switch character
            if states["multiCharacterMode"] and states["multiCharacterModeState"][states["currentCharacter"]] <= 0:
                # repair
                if config["auraRepair"]:
                    doAuraRepair(True)
                sleep(1400, 1600)
                if (
                    states["cubes"]
                ):
                    doCubes()

                # guild dono
                if (
                    states["doGuild"]
                    and config["characters"][states["currentCharacter"]]["guildDonation"]
                ):
                    sleep(1400, 1600)
                    doGuildDonation()
                    sleep(1400, 1600)
                # rapport
                if (
                    config["enableRapport"]
                    and config["characters"][states["currentCharacter"]]["rapport"]
                ):
                    sleep(500, 1000)
                    print("Doing Rapport")
                    doRapport()
                    sleep(1400, 1600)
                if gameCrashCheck():
                    states["status"] = "restart"
                    continue
                if offlineCheck():
                    closeGameByClickingDialogue()
                    continue

                # sailing level 3
                if (
                    states["doSailing"]
                    and config["characters"][states["currentCharacter"]]["guildSailingWeekly"]
                ):
                    # do sailing
                    print("doing sailing on : {}".format(states["currentCharacter"]))
                    doSailingWeekly(config["characters"][states["currentCharacter"]]["guildSailingWeekly"])
                    print("sailing done on : {}".format(states["currentCharacter"]))
                    sleep(1400, 1600)
                # lopang
                if (
                    states["doUnas"]
                    and config["characters"][states["currentCharacter"]]["unas"] == "lopang"
                ):
                    print("doing lopang on : {}".format(states["currentCharacter"]))
                    doLopang()
                    print("lopang done on : {}".format(states["currentCharacter"]))
                    sleep(1400, 1600)
                # leapstones
                if (
                    states["doUnas"]
                    and "leaps" in config["characters"][states["currentCharacter"]]["unas"]
                ):
                    print("doing leapstone dailies on : {}".format(states["currentCharacter"]))
                    doLeapstoneUnas(config["characters"][states["currentCharacter"]]["unas"])
                    print("leapstone dailies done on : {}".format(states["currentCharacter"]))
                    sleep(1400, 1600)
                    
                # cleanInventory()

                if gameCrashCheck():
                    states["status"] = "restart"
                    continue
                if offlineCheck():
                    closeGameByClickingDialogue()
                    continue
                
                if sum(states["multiCharacterModeState"]) == 0:
                    states["multiCharacterMode"] = False
                    states["multiCharacterModeState"] = []
                    sleep(3400, 3600)
                    # if date.today().weekday() == 2:
                    #     print("go invis again")
                    #     # goInvisible()
                    #     sleep(3400, 3600)
                    switchToCharacter(config["mainCharacter"])
                    continue
                states["multiCharacterModeState"][states["currentCharacter"]] = 0
                nextIndex = (states["currentCharacter"] + 1) % len(
                    states["multiCharacterModeState"]
                )
                print(
                    "character: {} 's daily x2 is done, switching to next: {}".format(
                        states["currentCharacter"], nextIndex
                    )
                )
                switchToCharacter(nextIndex)

            states["floor3Mode"] = False
            # only do floor3 if user has set to do, and when aor/multi-char is presented
            if states["doEndless"] or states["multiCharacterMode"]:
                states["floor3Mode"] = True
            if (states["doEndless"]
            and not states["doChaos"]
            and not states["doGuild"]
            and not states["doUnas"]
            and not states["doSailing"]):
                states["multiCharacterMode"] = False

            sleep(500, 600)
            # clearQuest()
            if states["doChaos"] or (states["doEndless"] and not states["multiCharacterMode"]):
                enterChaos()

            # save instance start time
            states["instanceStartTime"] = int(time.time_ns() / 1000000)
            # initialize new states
            states["abilityScreenshots"] = []
            states["bossBarLocated"] = False

            if gameCrashCheck():
                states["status"] = "restart"
                continue
            if offlineCheck():
                closeGameByClickingDialogue()
                continue

        elif states["status"] == "floor1":
            print("floor1")
            sleep(1000, 1300)
            # wait for loading
            waitForLoading()
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(100, 200)
            if gameCrashCheck():
                states["status"] = "restart"
                continue
            if offlineCheck():
                closeGameByClickingDialogue()
                continue
            if checkTimeout():
                quitChaos()
                continue
            sleep(1000, 1200)
            print("floor1 loaded")

            # saving clean abilities icons

            saveAbilitiesScreenshots()

            # do floor one
            doFloor1()
        elif states["status"] == "floor2":
            print("floor2")
            sleep(1000, 1300)
            # wait for loading
            waitForLoading()
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(100, 200)
            if gameCrashCheck():
                states["status"] = "restart"
                continue
            if offlineCheck():
                closeGameByClickingDialogue()
                continue
            if checkTimeout():
                quitChaos()
                continue
            print("floor2 loaded")
            # do floor two
            doFloor2()
        elif states["status"] == "floor3":
            print("floor3")
            sleep(1000, 1300)
            # wait for loading
            waitForLoading()
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(100, 200)
            if gameCrashCheck():
                states["status"] = "restart"
                continue
            if offlineCheck():
                closeGameByClickingDialogue()
                continue
            if checkTimeout():
                quitChaos()
                continue
            print("floor3 loaded")
            # currentTime = int(time.time_ns() / 1000000)
            # aorRun = pyautogui.screenshot()
            # aorRun.save("./debug/aor_" + str(currentTime) + ".png")
            # do floor 3
            # trigger start floor 3
            if checkTimeout() or states["floor3Mode"] == False:
                if gameCrashCheck():
                    states["status"] = "restart"
                    continue
                if offlineCheck():
                    closeGameByClickingDialogue()
                    continue
                quitChaos()
                continue
            doFloor3(states["doEndless"])
        elif states["status"] == "restart":
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

            inChaos = pyautogui.locateCenterOnScreen(
                "./screenshots/inChaos.png", confidence=0.75, region=(247, 146, 222, 50)
            )
            currentTime = int(time.time_ns() / 1000000)
            restartedshot = pyautogui.screenshot()
            restartedshot.save(
                "./debug/restarted_inChaos_"
                + str(inChaos != None)
                + "_"
                + str(currentTime)
                + ".png"
            )
            if inChaos != None:
                print("still in the last chaos run, quitting")
                quitChaos()
            else:
                print("in city, going for next run")
                states["status"] = "inCity"


def enterChaos():
    blackScreenStartTime = int(time.time_ns() / 1000000)
    if config["shortcutEnterChaos"] == True:
        # wait for last run black screen
        while True:
            im = pyautogui.screenshot(region=(1652, 168, 240, 210))
            r, g, b = im.getpixel((1772 - 1652, 272 - 168))
            if r + g + b > 10:
                break
            sleep(200, 300)

            currentTime = int(time.time_ns() / 1000000)
            if currentTime - blackScreenStartTime > config["blackScreenTimeLimit"]:
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
        sleep(600, 800)
        while True:
            if gameCrashCheck():
                return
            if offlineCheck():
                closeGameByClickingDialogue()
                return
            sleep(1000, 1200)

            # check if in chaos from disconenct->restart
            inChaos = pyautogui.locateCenterOnScreen(
                "./screenshots/inChaos.png",
                confidence=0.75,
                region=(247, 146, 222, 50),
            )
            if inChaos != None:
                print("still in the last chaos run, quitting")
                quitChaos()
                sleep(5000, 6000)
                # incity check
                while True:
                    inTown = pyautogui.locateCenterOnScreen(
                        "./screenshots/inTown.png",
                        confidence=0.75,
                        region=(1870, 133, 25, 30),
                    )
                    if inTown != None:
                        print("city loaded")
                        states["status"] = "inCity"
                        break
                    sleep(5000, 6000)

            toggleMenu("chaos")
            if config["GFN"] == True and len(states["abilityScreenshots"]) < 8:
                sleep(2000, 2400)

            noAura = pyautogui.locateOnScreen(
                "./screenshots/noAuraOfResonance.png",
                confidence=0.85
            )
            if noAura == None and config["performance"] == False:
                states["floor3Mode"] = True
                # print("aor detected")
                if (
                    config["enableMultiCharacterMode"] == True
                    and states["currentCharacter"] == config["mainCharacter"]
                    and states["multiCharacterMode"] == False
                ):
                    states["multiCharacterMode"] = True
                    states["doChaos"] = True
                    states["doGuild"] = True
                    states["doUnas"] = True
                    for i in range(len(config["characters"])):
                        states["multiCharacterModeState"].append(2)
                    print(
                        "aura of resonance detected, running full runs on characters: {}".format(
                            states["multiCharacterModeState"]
                        )
                    )
            elif noAura != None and sum(states["multiCharacterModeState"]) != 0:
                states["multiCharacterModeState"][states["currentCharacter"]] = 0
                print("no remaining aor on character, still have other chaos to run")
                return

            mouseMoveTo(x=886, y=346)
            sleep(500, 600)
            pydirectinput.click(x=886, y=346, button="left")
            sleep(500, 600)
            mouseMoveTo(x=886, y=346)
            sleep(500, 600)
            pydirectinput.click(x=886, y=346, button="left")
            sleep(500, 600)

            for _ in range(2):
                pydirectinput.click(x=1480, y=310, button="left") # right arrow
                sleep(500, 600)

            # select chaos dungeon level based on current Character
            _curr = config["characters"][states["currentCharacter"]]
            punikaChaosTabLoc = [920, 307]
            svernChaosTabLoc = [1060, 307]
            elgaciaChaosTabLoc = [1200, 307]
            voldisChaosTabLoc = [1350, 307]
            chaosTabPosition = {
                # punika
                1100: [punikaChaosTabLoc, [524, 400]],
                1310: [punikaChaosTabLoc, [524, 455]],
                1325: [punikaChaosTabLoc, [524, 505]],
                1340: [punikaChaosTabLoc, [524, 555]],
                1355: [punikaChaosTabLoc, [524, 605]],
                1370: [punikaChaosTabLoc, [524, 660]],
                1385: [punikaChaosTabLoc, [524, 715]],
                1400: [punikaChaosTabLoc, [524, 770]],
                # south vern
                1415: [svernChaosTabLoc, [524, 400]],
                1445: [svernChaosTabLoc, [524, 455]],
                1475: [svernChaosTabLoc, [524, 505]],
                1490: [svernChaosTabLoc, [524, 555]],
                1520: [svernChaosTabLoc, [524, 605]],
                1540: [svernChaosTabLoc, [524, 660]],
                1560: [svernChaosTabLoc, [524, 715]],
                # elgacia
                1580: [elgaciaChaosTabLoc, [524, 400]],
                1600: [elgaciaChaosTabLoc, [524, 455]],
                # voldis
                1610: [voldisChaosTabLoc, [524, 400]],
                1630: [voldisChaosTabLoc, [524, 455]],
            }
            if states["multiCharacterMode"] or noAura == None:
                mouseMoveTo(
                    x=chaosTabPosition[_curr["ilvl-aor"]][0][0],
                    y=chaosTabPosition[_curr["ilvl-aor"]][0][1],
                )
                sleep(800, 900)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-aor"]][0][0],
                    y=chaosTabPosition[_curr["ilvl-aor"]][0][1],
                    button="left",
                )
                sleep(500, 600)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-aor"]][0][0],
                    y=chaosTabPosition[_curr["ilvl-aor"]][0][1],
                    button="left",
                )
                sleep(500, 600)
                mouseMoveTo(
                    x=chaosTabPosition[_curr["ilvl-aor"]][1][0],
                    y=chaosTabPosition[_curr["ilvl-aor"]][1][1],
                )
                sleep(800, 900)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-aor"]][1][0],
                    y=chaosTabPosition[_curr["ilvl-aor"]][1][1],
                    button="left",
                )
                sleep(500, 600)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-aor"]][1][0],
                    y=chaosTabPosition[_curr["ilvl-aor"]][1][1],
                    button="left",
                )
                sleep(500, 600)
            else:
                mouseMoveTo(
                    x=chaosTabPosition[_curr["ilvl-endless"]][0][0],
                    y=chaosTabPosition[_curr["ilvl-endless"]][0][1],
                )
                sleep(800, 900)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-endless"]][0][0],
                    y=chaosTabPosition[_curr["ilvl-endless"]][0][1],
                    button="left",
                )
                sleep(500, 600)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-endless"]][0][0],
                    y=chaosTabPosition[_curr["ilvl-endless"]][0][1],
                    button="left",
                )
                sleep(500, 600)
                mouseMoveTo(
                    x=chaosTabPosition[_curr["ilvl-endless"]][1][0],
                    y=chaosTabPosition[_curr["ilvl-endless"]][1][1],
                )
                sleep(800, 900)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-endless"]][1][0],
                    y=chaosTabPosition[_curr["ilvl-endless"]][1][1],
                    button="left",
                )
                sleep(500, 600)
                pydirectinput.click(
                    x=chaosTabPosition[_curr["ilvl-endless"]][1][0],
                    y=chaosTabPosition[_curr["ilvl-endless"]][1][1],
                    button="left",
                )
                sleep(500, 600)

            enterButton = pyautogui.locateCenterOnScreen(
                "./screenshots/enterButton.png",
                confidence=0.75,
                region=(1334, 754, 120, 60),
            )
            if enterButton != None:
                x, y = enterButton
                mouseMoveTo(x=x, y=y)
                sleep(800, 900)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(100, 200)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(100, 200)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(100, 200)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(100, 200)
                pydirectinput.click(x=x, y=y, button="left")
                break
            else:
                mouseMoveTo(x=886, y=346)
                sleep(800, 900)
                pydirectinput.click(x=886, y=346, button="left")
                sleep(200, 300)
                pydirectinput.click(x=886, y=346, button="left")
                sleep(200, 300)
                pydirectinput.click(x=886, y=346, button="left")
                sleep(1800, 1900)

    else:
        while True:
            if gameCrashCheck():
                return
            if offlineCheck():
                closeGameByClickingDialogue()
                return
            enterHand = pyautogui.locateOnScreen(
                "./screenshots/enterChaos.png", confidence=config["confidenceForGFN"]
            )
            if enterHand != None:
                print("entering chaos...")
                pydirectinput.press(config["interact"])
                break
            sleep(200, 300)
    sleep(500, 600)
    while True:
        if gameCrashCheck():
            return
        # if offlineCheck():
        #     closeGameByClickingDialogue()
        #     return
        dc = pyautogui.locateOnScreen(
            "./screenshots/dc.png",
            region=config["regions"]["center"],
            confidence=config["confidenceForGFN"],
        )
        enterServer = pyautogui.locateCenterOnScreen(
            "./screenshots/enterServer.png", confidence=0.95, region=(885, 801, 160, 55)
        )
        if dc != None or enterServer != None:
            closeGameByClickingDialogue()
            return

        acceptButton = pyautogui.locateCenterOnScreen(
            "./screenshots/acceptButton.png",
            confidence=0.75,
            region=config["regions"]["center"],
        )
        if acceptButton != None:
            x, y = acceptButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            break
        sleep(500, 600)
    states["status"] = "floor1"
    return


def doFloor1():
    # clearQuest()
    # sleep(500, 550)

    # check repair
    if config["auraRepair"]:
        doAuraRepair(False)

    # trigger start floor 1
    mouseMoveTo(x=845, y=600)
    sleep(450, 500)
    pydirectinput.click(button=config["move"])
    sleep(450, 500)

    # switch to skill 4
    # if config["characters"][states["currentCharacter"]]["class"] == "summoner":
    #     mouseMoveTo(x=1010, y=865)
    #     sleep(800, 900)
    #     pydirectinput.click(x=985, y=865, button="left")
    #     sleep(800, 900)

    # berserker z
    # if config["characters"][states["currentCharacter"]]["class"] == "berserker":
    #     pydirectinput.press("z")
    #     sleep(800, 900)

    # delayed start for better aoe abiltiy usage at floor1 beginning
    if config["delayedStart"] != None and config["performance"] == False:
        sleep(config["delayedStart"] - 100, config["delayedStart"] + 100)

    if offlineCheck():
        closeGameByClickingDialogue()
        return
    if gameCrashCheck():
        states["status"] = "restart"
        return

    while True:
        # smash available abilities
        useAbilities()

        if offlineCheck():
            closeGameByClickingDialogue()
            return
        if gameCrashCheck():
            states["status"] = "restart"
            return
        if checkTimeout():
            quitChaos()
            return

        print("floor 1 cleared")
        # 不小心进下个门但没识别到
        if states["status"] == "floor2":
            return
        calculateMinimapRelative(states["moveToX"], states["moveToY"])
        if enterPortal():
            break

    if offlineCheck():
        closeGameByClickingDialogue()
        return
    if gameCrashCheck():
        states["status"] = "restart"
        return
    if checkTimeout():
        quitChaos()
        return
    states["status"] = "floor2"
    return


def doFloor2():
    states["bossBarLocated"] = False
    # clearQuest()
    # sleep(500, 550)
    # check repair
    if config["auraRepair"]:
        doAuraRepair(False)
    # trigger start floor 2
    pydirectinput.click(x=config["screenCenterX"], y=config["screenCenterY"], button=config["move"])
    sleep(800, 900)

    while True:
        useAbilities()

        if offlineCheck():
            closeGameByClickingDialogue()
            return
        if gameCrashCheck():
            states["status"] = "restart"
            return
        if checkTimeout():
            quitChaos()
            return

        print("floor 2 cleared")
        # 不小心进下个门但没识别到
        if states["status"] == "floor3":
            # 要接着打
            if states["floor3Mode"] == True:
                return
            # 下一把
            else:
                states["clearCount"] = states["clearCount"] + 1
                quitChaos()
                return
        if states["floor3Mode"] == False:
            states["clearCount"] = states["clearCount"] + 1
        calculateMinimapRelative(states["moveToX"], states["moveToY"])
        sleep(config["portalPause"] - 50, config["portalPause"] + 50)
        if enterPortal():
            break

    if offlineCheck():
        closeGameByClickingDialogue()
        return
    if gameCrashCheck():
        states["status"] = "restart"
        return
    if checkTimeout():
        quitChaos()
        return
    states["status"] = "floor3"
    return

def doFloor3(endless):
    waitForLoading()
    mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
    sleep(100, 200)
    if offlineCheck():
        closeGameByClickingDialogue()
        return
    if gameCrashCheck():
        states["status"] = "restart"
        return
    if checkTimeout():
        quitChaos()
        return

    print("real floor 3 loaded")

    # clearQuest()
    # sleep(500, 550)
    # check repair
    if config["auraRepair"]:
        doAuraRepair(False)

    useAbilities()

    if offlineCheck():
        closeGameByClickingDialogue()
        return
    if gameCrashCheck():
        states["status"] = "restart"
        return
    if checkTimeout():
        quitChaos()
        return

    print("Chaos Dungeon Full cleared")
    if states["multiCharacterMode"] and states["multiCharacterModeState"][states["currentCharacter"]] == 2:
        restartChaos()
    elif datetime.now().hour == config["resetHour"]:
        quitChaos()
    elif endless and not states["multiCharacterMode"]:
        restartChaos()
        # quitChaos()  # to check aor, for multi-char mode
    else:
        quitChaos()
    if states["multiCharacterMode"]:
        states["multiCharacterModeState"][states["currentCharacter"]] = (
            states["multiCharacterModeState"][states["currentCharacter"]] - 1
        )
        print(
            "currentCharacter: {}, multiCharacterModeState: {}".format(
                states["currentCharacter"], states["multiCharacterModeState"]
            )
        )
    return


def quitChaos():
    checkChaosFinish()
    # quit
    print("quitting chaos")
    sleep(100, 200)
    while True:
        if offlineCheck():
            closeGameByClickingDialogue()
            return
        if gameCrashCheck():
            states["status"] = "restart"
            return
        leaveButton = pyautogui.locateCenterOnScreen(
            "./screenshots/leave.png",
            grayscale=True,
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if leaveButton != None:
            x, y = leaveButton
            mouseMoveTo(x=x, y=y)
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(200, 300)
        sleep(300, 400)
        # leave ok
        okButton = pyautogui.locateCenterOnScreen(
            "./screenshots/ok.png",
            confidence=0.75,
            region=config["regions"]["center"],
        )
        if okButton != None:
            break
        sleep(300, 400)
        """
        # incity check
        inTown = pyautogui.locateCenterOnScreen(
            "./screenshots/inTown.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if inTown != None:
            print("city loaded")
            states["status"] = "inCity"
            return
        """
    sleep(100, 200)
    checkChaosFinish()
    sleep(100, 200)
    while True:
        if gameCrashCheck():
            states["status"] = "restart"
            return
        okButton = pyautogui.locateCenterOnScreen(
            "./screenshots/ok.png",
            confidence=0.75,
            region=config["regions"]["center"],
        )
        if okButton != None:
            x, y = okButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            sleep(100, 200)
            pydirectinput.click(button="left")
            sleep(100, 200)
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(button="left")
            sleep(100, 200)
            pydirectinput.click(button="left")
            break
        sleep(300, 400)
    # this line and following if block to the top of method if select level prob
    # timeout is alright but d/c still weird
    printResult()

        # if states["multiCharacterModeState"][states["currentCharacter"]] > 0:
        #     click(60, 370, 2000) # select level
        #     click(1400, 780, 2000) # enter
        #     click(920, 600, 2000) # accept

        #     states["status"] = "floor1"
        #     states["instanceStartTime"] = int(time.time_ns() / 1000000)
        #     return
    
    states["status"] = "inCity"
    sleep(5000, 7000)
    return


# not using for now
def restartChaos():
    printResult()
    sleep(1200, 1400)
    # states["abilityScreenshots"] = []
    states["instanceStartTime"] = int(time.time_ns() / 1000000)

    while True:
        selectLevelButton = pyautogui.locateCenterOnScreen(
            "./screenshots/selectLevel.png",
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if selectLevelButton != None:
            x, y = selectLevelButton

            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            break
        sleep(100, 200)
    sleep(100, 200)
    while True:
        enterButton = pyautogui.locateCenterOnScreen(
            "./screenshots/enterButton.png",
            confidence=0.75,
            region=(1334, 754, 120, 60),
        )
        if enterButton != None:
            x, y = enterButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            break
        sleep(100, 200)
    sleep(100, 200)
    while True:
        acceptButton = pyautogui.locateCenterOnScreen(
            "./screenshots/acceptButton.png",
            confidence=0.75,
            region=config["regions"]["center"],
        )
        if acceptButton != None:
            x, y = acceptButton
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(100, 200)
            pydirectinput.click(x=x, y=y, button="left")
            break
        sleep(100, 200)
    states["status"] = "floor1"
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
    print(
        "gold portal count: {}, purple portal count: {}".format(
            states["goldPortalCount"], states["purplePortalCount"]
        )
    )


def useAbilities():
    while True:
        diedCheck()
        healthCheck()
        # windowCheck()
        if config["performance"] == False:
            clearQuest()
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        if checkTimeout():
            return

        # check for accident
        if states["status"] == "floor1" and checkFloor2Elite():
            print("accidentally entered floor 2")
            states["status"] = "floor2"
            # nowTime = int(time.time_ns() / 1000000)
            # badRun = pyautogui.screenshot()
            # badRun.save("./debug/badRun_" + str(nowTime) + ".png")
            states["badRunCount"] = states["badRunCount"] + 1
            return
        elif states["status"] == "floor2" and checkFloor3Tower():
            print("accidentally entered floor 3")
            states["status"] = "floor3"
            # nowTime = int(time.time_ns() / 1000000)
            # badRun = pyautogui.screenshot()
            # badRun.save("./debug/badRun_" + str(nowTime) + ".png")
            states["badRunCount"] = states["badRunCount"] + 1
            return

        # # check elite and mobs, lower priority cuz it only runs check once a cycle
        # if states["status"] == "floor2" and not checkFloor2Elite() and checkFloor2Mob():
        #     calculateMinimapRelative(states["moveToX"], states["moveToY"])
        #     moveToMinimapRelative(states["moveToX"], states["moveToY"], 400, 500, False)
        if (
            states["status"] == "floor2"
            and not checkFloor2Elite()
            and not checkFloor2Mob()
        ):
            # print("no elite/mob on floor 2, random move to detect portal")
            randomMove()
        elif states["status"] == "floor2" and checkFloor2Boss():
            # to avoid stuck on that 9 square map...
            randomMove()
        elif states["status"] == "floor1" and not checkFloor2Mob():
            # print("no mob on floor 1, random move to detect portal")
            randomMove()
        elif states["status"] == "floor3" and checkFloor2Elite():
            calculateMinimapRelative(states["moveToX"], states["moveToY"])
            moveToMinimapRelative(states["moveToX"], states["moveToY"], 200, 300, False)
            # pydirectinput.press(config["awakening"])
        # elif (
        #     states["status"] == "floor2"
        #     and config["performance"] == True
        #     and checkFloor2Boss()
        # ):
        #     calculateMinimapRelative(states["moveToX"], states["moveToY"])
        #     moveToMinimapRelative(states["moveToX"], states["moveToY"], 950, 1050, True)
        #     fightFloor2Boss()

        allAbilities = [*range(0, len(states["abilityScreenshots"]))]
        # add randomness to spell order
        # if config["characters"][states["currentCharacter"]]["class"] != "gunslinger":
        #     half = int(len(allAbilities) / 2)
        #     first = allAbilities[:half]
        #     second = allAbilities[len(allAbilities) - half :]
        #     random.shuffle(first)
        #     random.shuffle(second)
        #     allAbilities = first + second

        # cast sequence
        for i in allAbilities:
            if states["status"] == "floor3" and checkChaosFinish():
                print("checkChaosFinish == True")
                return
            diedCheck()
            healthCheck()

            # if states["status"] == "floor3" and checkPortal():
            #     pydirectinput.click(
            #         x=config["screenCenterX"],
            #         y=config["screenCenterY"],
            #         button=config["move"],
            #     )
            #     sleep(100, 150)
            #     checkPortal()
            #     return
            # uncomment下面如果想不打完1/2层所有怪就检测portal, when states["floor3Mode"] == False
            if (
                states["floor3Mode"] == False
                and states["status"] == "floor1"
                and checkPortal()
            ):
                pydirectinput.click(
                    x=config["screenCenterX"],
                    y=config["screenCenterY"],
                    button=config["move"],
                )
                sleep(100, 150)
                checkPortal()
                return
            elif (
                states["floor3Mode"] == False
                and states["status"] == "floor2"
                and checkPortal()
            ):
                pydirectinput.click(
                    x=config["screenCenterX"],
                    y=config["screenCenterY"],
                    button=config["move"],
                )
                sleep(100, 150)
                checkPortal()
                return

            # click rift core
            if states["status"] == "floor3":
                clickTower()

            # check high-priority mobs
            if states["status"] == "floor1":
                if checkFloor2Mob():
                    calculateMinimapRelative(states["moveToX"], states["moveToY"])
                # if nothing is on the floor1/2 on floor3Mode, then check portal
                elif (
                    states["floor3Mode"] == True
                    and states["status"] == "floor1"
                    and checkPortal()
                ):
                    pydirectinput.click(
                        x=config["screenCenterX"],
                        y=config["screenCenterY"],
                        button=config["move"],
                    )
                    sleep(100, 150)
                    checkPortal()
                    return
            elif states["status"] == "floor2":
                if config["performance"] == False and checkFloor2Boss():
                    calculateMinimapRelative(states["moveToX"], states["moveToY"])
                    moveToMinimapRelative(
                        states["moveToX"], states["moveToY"], 950, 1050, True
                    )
                    # fightFloor2Boss()
                elif (
                    config["performance"] == True
                    and (i == 3 or i == 5 or i == 7)
                    and checkFloor2Boss()
                ):
                    calculateMinimapRelative(states["moveToX"], states["moveToY"])
                    moveToMinimapRelative(
                        states["moveToX"], states["moveToY"], 950, 1050, True
                    )
                    # fightFloor2Boss()
                elif (i == 0 or i == 3 or i == 5) and checkFloor2Elite():
                    calculateMinimapRelative(states["moveToX"], states["moveToY"])
                    moveToMinimapRelative(
                        states["moveToX"], states["moveToY"], 750, 850, False
                    )
                elif (
                    states["status"] == "floor2"
                    # and not checkFloor2Elite()
                    and checkFloor2Mob()
                ):
                    calculateMinimapRelative(states["moveToX"], states["moveToY"])
                    moveToMinimapRelative(
                        states["moveToX"], states["moveToY"], 400, 500, False
                    )
                # if nothing is on the floor1/2 on floor3Mode, then check portal
                elif (
                    states["floor3Mode"] == True
                    and states["status"] == "floor2"
                    and checkPortal()
                ):
                    pydirectinput.click(
                        x=config["screenCenterX"],
                        y=config["screenCenterY"],
                        button=config["move"],
                    )
                    sleep(100, 150)
                    checkPortal()
                    return
            elif states["status"] == "floor3" and checkFloor3Tower():
                if not checkFloor2Elite() and not checkFloor2Mob():
                    randomMove()
                    checkFloor3Tower()
                calculateMinimapRelative(states["moveToX"], states["moveToY"])
                moveToMinimapRelative(
                    states["moveToX"], states["moveToY"], 1200, 1300, True
                )
                # if (
                #     config["characters"][states["currentCharacter"]]["class"]
                #     == "sorceress"
                # ):
                #     pyautogui.press("x")
                sleep(200, 220)
                clickTower()
            elif states["status"] == "floor3" and checkFloor2Mob():
                calculateMinimapRelative(states["moveToX"], states["moveToY"])
                moveToMinimapRelative(
                    states["moveToX"], states["moveToY"], 200, 300, False
                )
                # pydirectinput.press(config["awakening"])
            elif states["status"] == "floor3" and checkFloor2Boss():
                diedCheck()
                calculateMinimapRelative(states["moveToX"], states["moveToY"])
                moveToMinimapRelative(
                    states["moveToX"], states["moveToY"], 800, 900, False
                )

            
            performClassSpecialty(i, states["abilityScreenshots"])
            # cast spells
            checkCDandCast(states["abilityScreenshots"][i])

        # 防止卡先试试这样
        if (
            states["status"] == "floor3"
            and not checkFloor2Elite()
            and not checkFloor2Boss()  # no random move in purple portal
        ):
            randomMove()

def performClassSpecialty(i, abilities):
    currentCharacterClass = config["characters"][states["currentCharacter"]]["class"]

    if (currentCharacterClass == "arcana"):
        pydirectinput.press(config["specialty1"])
        pydirectinput.press(config["specialty2"])

    # elif (currentCharacterClass == "breaker"):
    #     pydirectinput.press("x")
    #     pydirectinput.press("z")

    # elif (currentCharacterClass == "summoner"):
    #     mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
    #     sleep(150, 160)
    #     pydirectinput.press("z")
    #     sleep(50, 60)
    #     pydirectinput.press("z")
    #     sleep(150, 160)
    #     pydirectinput.press("z")
    #     sleep(50, 60)
    #     pydirectinput.press("z")

    elif (currentCharacterClass == "souleater"):
        if pyautogui.locateOnScreen(
            "./screenshots/soulSnatch.png",
            region=config["regions"]["debuffs"],
            confidence=0.85,
        ) != None:
            checkCDandCast(abilities[0])
            sleep(300, 400)
            checkCDandCast(abilities[1])
            sleep(300, 400)
            checkCDandCast(abilities[5])
            sleep(300, 400)

    elif (currentCharacterClass == "slayer"):
        slayerSpecialty = pyautogui.locateOnScreen(
            "./screenshots/slayerSpecialty.png",
            region=config["regions"]["specialty"],
            confidence=0.85,
        )
        if slayerSpecialty != None:
            pydirectinput.press(config["specialty1"])
            sleep(150, 160)

    elif (currentCharacterClass == "deathblade"):
        threeOrbDeathTrance = pyautogui.locateOnScreen(
            "./screenshots/deathTrance.png",
            region=config["regions"]["specialty"],
            confidence=0.80,
        )
        if threeOrbDeathTrance != None:
            pydirectinput.press(config["specialty1"])
            sleep(150, 160)

    elif (currentCharacterClass == "gunslinger"):
        pistolStance = pyautogui.locateOnScreen(
            "./screenshots/pistolStance.png",
            region=(930, 819, 58, 56),
            confidence=0.75,
        )
        shotgunStance = pyautogui.locateOnScreen(
            "./screenshots/shotgunStance.png",
            region=(930, 819, 58, 56),
            confidence=0.75,
        )
        sniperStance = pyautogui.locateOnScreen(
            "./screenshots/sniperStance.png",
            region=(930, 819, 58, 56),
            confidence=0.75,
        )
        # swap to shotgun
        if i == 0:
            if pyautogui.locateOnScreen(
                "./screenshots/shotgunStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            ) == None:
                diedCheck()
                pistolStance = pyautogui.locateOnScreen(
                    "./screenshots/pistolStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                if pistolStance != None:
                    pydirectinput.press(config["specialty1"])
                    sleep(150, 160)

                sniperStance = pyautogui.locateOnScreen(
                    "./screenshots/sniperStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                if sniperStance != None:
                    pydirectinput.press(config["specialty2"])
                    sleep(150, 160)
        # swap to sniper
        elif i < 3:
            if pyautogui.locateOnScreen(
                "./screenshots/sniperStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            ) == None:
                diedCheck()
                pistolStance = pyautogui.locateOnScreen(
                    "./screenshots/pistolStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                if pistolStance != None:
                    pydirectinput.press(config["specialty2"])
                    sleep(150, 160)

                shotgunStance = pyautogui.locateOnScreen(
                    "./screenshots/shotgunStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                if shotgunStance != None:
                    pydirectinput.press(config["specialty1"])
                    sleep(150, 160)
        # swap to pistol
        else:
            if pyautogui.locateOnScreen(
                "./screenshots/pistolStance.png",
                region=(930, 819, 58, 56),
                confidence=0.75,
            ) == None:
                diedCheck()
                shotgunStance = pyautogui.locateOnScreen(
                    "./screenshots/shotgunStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                if shotgunStance != None:
                    pydirectinput.press(config["specialty2"])
                    sleep(150, 160)

                sniperStance = pyautogui.locateOnScreen(
                    "./screenshots/sniperStance.png",
                    region=(930, 819, 58, 56),
                    confidence=0.75,
                )
                if sniperStance != None:
                    pydirectinput.press(config["specialty1"])
                    sleep(150, 160)

    elif (currentCharacterClass == "artist"):
        artistOrb = pyautogui.locateOnScreen(
            "./screenshots/artistOrb.png",
            region=config["regions"]["specialty"],
            confidence=0.85,
        )
        if artistOrb != None:
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(150, 160)
            pydirectinput.press(config["specialty2"])
            sleep(1500, 1600)
            pydirectinput.press("g")

    elif (currentCharacterClass == "aeromancer"):
        aeroSpecialty = pyautogui.locateOnScreen(
            "./screenshots/aeroSpecialty.png",
            region=config["regions"]["specialty"],
            confidence=0.95,
        )
        if aeroSpecialty != None:
            sleep(150, 160)
            pydirectinput.press(config["specialty1"])

    elif (currentCharacterClass == "scrapper"):
        scrapperSpecialty = pyautogui.locateOnScreen(
            "./screenshots/scrapperSpecialty.png",
            region=config["regions"]["specialty"],
            confidence=0.85,
        )
        if scrapperSpecialty != None:
            sleep(150, 160)
            pydirectinput.press("z")

    # elif (
    #     currentCharacterClass == "paladin"
    # ) and (i == 1 or i == 3 or i == 5 or i == 7):
    #     paladinSpecialty = pyautogui.locateOnScreen(
    #         "./screenshots/paladinSpecialty.png",
    #         region=(904, 900, 111, 35),
    #         confidence=0.9,
    #     )
    #     if paladinSpecialty != None:
    #         pydirectinput.press("z")
    #         sleep(150, 160)

    # bard courage
    if currentCharacterClass == "bard":
        courageBuffActive = pyautogui.locateOnScreen(
            "./screenshots/bardCourage120.png",
            region=config["regions"]["buffs"],
            confidence=0.75,
        )
        rZ, gZ, bZ = pyautogui.pixel(920, 866)
        rX, gX, bX = pyautogui.pixel(1006, 875)
        if rZ - gZ > 80 and courageBuffActive == None:
            # print("bard courage Z")
            pydirectinput.press("z")
            sleep(50, 60)
            pydirectinput.press("z")
            sleep(150, 160)
            pydirectinput.press("z")
            sleep(50, 60)
            pydirectinput.press("z")
            sleep(50, 60)
            pydirectinput.press("z")
        elif bX - gX > 70 and courageBuffActive != None:
            print("bard jiaxue X")
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(150, 160)
            pydirectinput.press("x")
            sleep(50, 60)
            pydirectinput.press("x")
            sleep(150, 160)
            pydirectinput.press("x")
            sleep(50, 60)
            pydirectinput.press("x")
            sleep(50, 60)
            pydirectinput.press("x")

def checkCDandCast(ability):
    if (
        config["GFN"] == True
        or config["performance"] == True
        or pyautogui.locateOnScreen(
            ability["image"],
            region=(ability["position"]["left"],
                    ability["position"]["top"],
                    ability["position"]["width"],
                    ability["position"]["height"]),
            confidence=0.9
        )
    ):
        if ability["directional"] == True:
            mouseMoveTo(x=states["moveToX"], y=states["moveToY"])
        else:
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])

        if ability["cast"]:
            start_ms = int(time.time_ns() / 1000000)
            now_ms = int(time.time_ns() / 1000000)
            # spam until cast time before checking cd, to prevent 击倒后情况
            while now_ms - start_ms < ability["castTime"]:
                pydirectinput.press(ability["key"])
                sleep(50, 60)
                now_ms = int(time.time_ns() / 1000000)
            # while pyautogui.locateOnScreen(
            #     ability["image"], region=config["regions"]["abilities"]
            # ):
            #     pydirectinput.press(ability["key"])
        elif ability["hold"]:
            # TODO: FIXME: avoid hold for now...
            start_ms = int(time.time_ns() / 1000000)
            now_ms = int(time.time_ns() / 1000000)
            pydirectinput.keyDown(ability["key"])
            while now_ms - start_ms < ability["holdTime"]:
                # pydirectinput.keyDown(ability["key"])
                now_ms = int(time.time_ns() / 1000000)
            # while pyautogui.locateOnScreen(
            #     ability["image"], region=config["regions"]["abilities"]
            # ):
            #     pydirectinput.keyDown(ability["key"])
            pydirectinput.keyUp(ability["key"])
        else:
            # 瞬发 ability
            if config["performance"] == True or config["GFN"] == True:
                pydirectinput.press(ability["key"])
                sleep(50, 60)
                pydirectinput.press(ability["key"])
                # sleep(50, 60)
                # pydirectinput.press(ability["key"])
                return
            pydirectinput.press(ability["key"])
            start_ms = int(time.time_ns() / 1000000)
            now_ms = int(time.time_ns() / 1000000)
            while pyautogui.locateOnScreen(
                ability["image"],
                region=(ability["position"]["left"],
                        ability["position"]["top"],
                        ability["position"]["width"],
                        ability["position"]["height"]),
                confidence=0.9
            ):
                print("trying to cast " + ability["key"])
                pydirectinput.press(ability["key"])
                sleep(50, 60)
                now_ms = int(time.time_ns() / 1000000)
                if now_ms - start_ms > 2000:
                    print("unable to use spell for 15s, check if disconnected")
                    return

def checkPortal():
    if config["performance"] == False:
        # check portal image
        portal = pyautogui.locateCenterOnScreen(
            "./screenshots/portal.png",
            region=config["regions"]["minimap"],
            confidence=0.7,
        )
        portalTop = pyautogui.locateCenterOnScreen(
            "./screenshots/portalTop.png",
            region=config["regions"]["minimap"],
            confidence=0.7,
        )
        portalBot = pyautogui.locateCenterOnScreen(
            "./screenshots/portalBot.png",
            region=config["regions"]["minimap"],
            confidence=0.7,
        )
        """
        portalLeft = pyautogui.locateCenterOnScreen(
            "./screenshots/portalLeft.png",
            region=config["regions"]["minimap"],
            confidence=0.9,
        )
        portalRight = pyautogui.locateCenterOnScreen(
            "./screenshots/portalRight.png",
            region=config["regions"]["minimap"],
            confidence=0.9,
        )
        """
        if portal != None:
            x, y = portal
            states["moveToX"] = x
            states["moveToY"] = y
            print(
                "portal image x: {} y: {}".format(states["moveToX"], states["moveToY"])
            )
            return True
        elif portalTop != None:
            x, y = portalTop
            states["moveToX"] = x
            states["moveToY"] = y + 7
            print(
                "portalTop image x: {} y: {}".format(
                    states["moveToX"], states["moveToY"]
                )
            )
            return True
        elif portalBot != None:
            x, y = portalBot
            states["moveToX"] = x
            states["moveToY"] = y - 7
            print(
                "portalBot image x: {} y: {}".format(
                    states["moveToX"], states["moveToY"]
                )
            )
            return True
        # elif portalLeft != None:
        #     x, y = portalLeft
        #     states["moveToX"] = x + 3
        #     states["moveToY"] = y
        #     print(
        #         "portalLeft image x: {} y: {}".format(
        #             states["moveToX"], states["moveToY"]
        #         )
        #     )
        #     return True
        # elif portalRight != None:
        #     x, y = portalRight
        #     states["moveToX"] = x - 3
        #     states["moveToY"] = y
        #     print(
        #         "portalRight image x: {} y: {}".format(
        #             states["moveToX"], states["moveToY"]
        #         )
        #     )
        #     return True

    # only check with portal image at aor
    # if states["floor3Mode"] == True and (
    #     states["status"] == "floor2" or states["status"] == "floor3"
    # ):
    #     return False

    minimap = pyautogui.screenshot(region=config["regions"]["minimap"])  # Top Right
    width, height = minimap.size
    order = spiralSearch(width, height, math.floor(width / 2), math.floor(height / 2))
    for entry in order:
        if entry[0] >= width or entry[1] >= height:
            continue
        r, g, b = minimap.getpixel((entry[0], entry[1]))
        inRange = False
        if config["GFN"] == True:
            inRange = (
                r in range(75, 105) and g in range(140, 170) and b in range(240, 256)
            ) or (
                r in range(120, 130) and g in range(210, 240) and b in range(240, 256)
            )
        else:
            inRange = (
                r in range(75, 85) and g in range(140, 150) and b in range(250, 256)
            ) or (
                r in range(120, 130) and g in range(210, 220) and b in range(250, 256)
            )
        if inRange:
            left, top, _w, _h = config["regions"]["minimap"]
            states["moveToX"] = left + entry[0]
            states["moveToY"] = top + entry[1]
            if r in range(75, 85) and g in range(140, 150) and b in range(250, 256):
                states["moveToY"] = states["moveToY"] - 1
            elif r in range(120, 130) and g in range(210, 220) and b in range(250, 256):
                states["moveToY"] = states["moveToY"] + 1
            print(
                "portal pixel x: {} y: {}, r: {} g: {} b: {}".format(
                    states["moveToX"], states["moveToY"], r, g, b
                )
            )
            return True
    return False


def checkFloor2Elite():
    minimap = pyautogui.screenshot(region=config["regions"]["minimap"])  # Top Right
    width, height = minimap.size
    order = spiralSearch(width, height, math.floor(width / 2), math.floor(height / 2))
    for entry in order:
        if entry[0] >= width or entry[1] >= height:
            continue
        r, g, b = minimap.getpixel((entry[0], entry[1]))
        inRange = False
        if config["GFN"] == True:
            inRange = (
                r in range(185, 215)
                and g in range(125, 147)
                and b in range(60, 78)
                # or r in range(90, 110)
                # and g in range(55, 70)
                # and b in range(10, 40)
            )
        else:
            inRange = (
                r in range(190, 215) 
                and g in range(125, 150) 
                and b in range(30, 70)
            )
        if inRange:
            left, top, _w, _h = config["regions"]["minimap"]
            states["moveToX"] = left + entry[0]
            states["moveToY"] = top + entry[1]
            # print(
            #     "elite x: {} y: {}, r: {} g: {} b: {}".format(
            #         states["moveToX"], states["moveToY"], r, g, b
            #     )
            # )
            return True
    return False


def checkFloor2Mob():
    minimap = pyautogui.screenshot(region=config["regions"]["minimap"])  # Top Right
    width, height = minimap.size
    order = spiralSearch(width, height, math.floor(width / 2), math.floor(height / 2))
    if states["status"] == "floor2":
        order = reversed(order)
    for entry in order:
        if entry[0] >= width or entry[1] >= height:
            continue
        r, g, b = minimap.getpixel((entry[0], entry[1]))
        inRange = False
        if config["GFN"] == True:
            inRange = (
                (r in range(180, 215)) and (g in range(17, 35)) and (b in range(17, 55))
            )
        else:
            inRange = (
                (r in range(206, 211)) and (g in range(22, 27)) and (b in range(22, 27))
            )
        if inRange:
            left, top, _w, _h = config["regions"]["minimap"]
            states["moveToX"] = left + entry[0]
            states["moveToY"] = top + entry[1]
            # print(
            #     "mob x: {} y: {}, r: {} g: {} b: {}".format(
            #         states["moveToX"], states["moveToY"], r, g, b
            #     )
            # )
            return True
    return False

def checkFloor2Boss():
    fightFloor2Boss()
    bossLocation = pyautogui.locateCenterOnScreen(
        "./screenshots/boss.png", confidence=0.65, region=config["regions"]["minimap"]
    )
    if bossLocation != None:
        left, top = bossLocation
        states["moveToX"] = left
        states["moveToY"] = top
        # print("boss x: {} y: {}".format(states["moveToX"], states["moveToY"]))
        return True
    return False


# def checkFloor2Boss():
#     sleep(100, 200)
#     fightFloor2Boss()
#     minimap = pyautogui.screenshot(region=config["regions"]["minimap"])  # Top Right
#     width, height = minimap.size
#     order = spiralSearch(width, height, math.floor(width / 2), math.floor(height / 2))
#     for entry in order:
#         if entry[1] >= width or entry[0] >= height:
#             continue
#         r, g, b = minimap.getpixel((entry[1], entry[0]))
#         if (
#             (r in range(153, 173)) and (g in range(25, 35)) and (b in range(25, 35))
#         ):  # r == 199 and g == 28 and b == 30
#             left, top, _w, _h = config["regions"]["minimap"]
#             states["moveToX"] = left + entry[1]
#             states["moveToY"] = top + entry[0]
#             print(
#                 "Boss x: {} y: {}, r: {} g: {} b: {}".format(
#                     states["moveToX"], states["moveToY"], r, g, b
#                 )
#             )
#             return True


def clickTower():
    riftCore1 = pyautogui.locateCenterOnScreen(
        "./screenshots/riftcore1.png",
        confidence=0.6,
        region=config["regions"]["portal"],
    )
    riftCore2 = pyautogui.locateCenterOnScreen(
        "./screenshots/riftcore2.png",
        confidence=0.6,
        region=config["regions"]["portal"],
    )
    if riftCore1 != None:
        x, y = riftCore1
        if y > 650 or x < 400 or x > 1500:
            return
        states["moveToX"] = x
        states["moveToY"] = y + 190
        pydirectinput.click(
            x=states["moveToX"], y=states["moveToY"], button=config["move"]
        )
        # print("clicked rift core")
        sleep(100, 120)
        pydirectinput.press(config["meleeAttack"])
        sleep(300, 360)
        pydirectinput.press(config["meleeAttack"])
        sleep(300, 360)
        pydirectinput.press(config["meleeAttack"])
        sleep(100, 120)
        pydirectinput.press(config["meleeAttack"])
    elif riftCore2 != None:
        x, y = riftCore2
        if y > 650 or x < 400 or x > 1500:
            return
        states["moveToX"] = x
        states["moveToY"] = y + 190
        pydirectinput.click(
            x=states["moveToX"], y=states["moveToY"], button=config["move"]
        )
        # print("clicked rift core")
        sleep(100, 120)
        pydirectinput.press(config["meleeAttack"])
        sleep(300, 360)
        pydirectinput.press(config["meleeAttack"])
        sleep(300, 360)
        pydirectinput.press(config["meleeAttack"])
        sleep(100, 120)
        pydirectinput.press(config["meleeAttack"])


def checkFloor3Tower():
    tower = pyautogui.locateCenterOnScreen(
        "./screenshots/tower.png", 
        region=config["regions"]["minimap"], 
        confidence=0.7
    )
    towerTop = pyautogui.locateCenterOnScreen(
        "./screenshots/towerTop.png",
        region=config["regions"]["minimap"],
        confidence=0.7,
    )
    towerBot = pyautogui.locateCenterOnScreen(
        "./screenshots/towerBot.png",
        region=config["regions"]["minimap"],
        confidence=0.7,
    )
    if tower != None:
        x, y = tower
        states["moveToX"] = x
        states["moveToY"] = y
        print("tower image x: {} y: {}".format(states["moveToX"]-config["minimapCenterX"], 
                                                states["moveToY"]-config["minimapCenterY"]))
        return True
    elif towerTop != None:
        x, y = towerTop
        states["moveToX"] = x
        states["moveToY"] = y + 7
        print("towerTop image x: {} y: {}".format(states["moveToX"]-config["minimapCenterX"], 
                                                  states["moveToY"]-config["minimapCenterY"]))
        return True
    elif towerBot != None:
        x, y = towerBot
        states["moveToX"] = x
        states["moveToY"] = y - 7
        print("towerBot image x: {} y: {}".format(states["moveToX"]-config["minimapCenterX"], 
                                                  states["moveToY"]-config["minimapCenterY"]))
        return True

    # minimap = pyautogui.screenshot(region=config["regions"]["minimap"])  # Top Right
    # width, height = minimap.size
    # order = spiralSearch(width, height, math.floor(width / 2), math.floor(height / 2))
    # for entry in order:
    #     if entry[1] >= width or entry[0] >= height:
    #         continue
    #     r, g, b = minimap.getpixel((entry[1], entry[0]))
    #     inRange = False
    #     if config["GFN"] == True:
    #         inRange = (
    #             r in range(209, 229) and g in range(40, 60) and b in range(49, 69)
    #         ) or (
    #             r in range(245, 256) and g in range(163, 173) and b in range(179, 189)
    #         )
    #     else:
    #         inRange = (
    #             r in range(209, 229) and g in range(40, 60) and b in range(49, 69)
    #         ) or (r == 162 and g == 162 and b == 162)
    #         (r in range(245, 255) and g in range(163, 173) and b in range(179, 189))
    #     if inRange:
    #         left, top, _w, _h = config["regions"]["minimap"]
    #         states["moveToX"] = left + entry[1]
    #         states["moveToY"] = top + entry[0]
    #         # pos offset
    #         if r in range(245, 256) and g in range(163, 173) and b in range(179, 189):
    #             states["moveToY"] = states["moveToY"] + 1
    #         print(
    #             "tower pixel pos x: {} y: {}, r: {} g: {} b: {}".format(
    #                 states["moveToX"], states["moveToY"], r, g, b
    #             )
    #         )
    #         return True

    return False


def checkChaosFinish():
    clearOk = pyautogui.locateCenterOnScreen(
        "./screenshots/clearOk.png", confidence=0.75, region=(625, 779, 500, 155)
    )
    """
    selectLevelButton = pyautogui.locateCenterOnScreen(
    "./screenshots/selectLevel.png",
    confidence=0.8,
    region=config["regions"]["leaveMenu"],
    )
    """
    if clearOk != None:
        states["fullClearCount"] = states["fullClearCount"] + 1
        x, y = clearOk
        mouseMoveTo(x=x, y=y)
        sleep(800, 900)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(200, 300)
        mouseMoveTo(x=x, y=y)
        sleep(600, 800)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(200, 300)
        return True
    # elif selectLevelButton != None:
    #     # edge case clearok
    #     states["fullClearCount"] = states["fullClearCount"] + 1
    #     currentTime = int(time.time_ns() / 1000000)
    #     timeout = pyautogui.screenshot()
    #     timeout.save("./debug/timeoutSelectLevel_" + str(currentTime) + ".png")
    #     states["timeoutCount"] = states["timeoutCount"] + 1
    #     mouseMoveTo(x=959, y=851)
    #     sleep(800, 900)
    #     pydirectinput.click(button="left")
    #     sleep(200, 300)
    #     mouseMoveTo(x=959, y=851)
    #     sleep(600, 800)
    #     pydirectinput.click(button="left")
    #     sleep(200, 300)
    #     return True
    return False


def fightFloor2Boss():
    if pyautogui.locateOnScreen(
        "./screenshots/bossBar.png", confidence=0.8, region=(406, 159, 1000, 200)
    ):
        # print("boss bar located")
        mouseMoveTo(x=states["moveToX"], y=states["moveToY"])
        sleep(80, 100)
        currentCharacterClass = config["characters"][states["currentCharacter"]]["class"]
        awakening = [ability for ability in abilities[currentCharacterClass] if ability["abilityType"] == "awakening"][0]
        if awakening["directional"] == True:
            mouseMoveTo(x=states["moveToX"], y=states["moveToY"])
        else:
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])

        if awakening["cast"]:
            start_ms = int(time.time_ns() / 1000000)
            now_ms = int(time.time_ns() / 1000000)
            # spam until cast time before checking cd, to prevent 击倒后情况
            while now_ms - start_ms < awakening["castTime"]:
                pydirectinput.press(awakening["key"])
                sleep(50, 60)
                now_ms = int(time.time_ns() / 1000000)
            # while pyautogui.locateOnScreen(
            #     ability["image"], region=config["regions"]["abilities"]
            # ):
            #     pydirectinput.press(ability["key"])
        elif awakening["hold"]:
            # TODO: FIXME: avoid hold for now...
            start_ms = int(time.time_ns() / 1000000)
            now_ms = int(time.time_ns() / 1000000)
            pydirectinput.keyDown(awakening["key"])
            while now_ms - start_ms < awakening["holdTime"]:
                # pydirectinput.keyDown(ability["key"])
                now_ms = int(time.time_ns() / 1000000)
            # while pyautogui.locateOnScreen(
            #     ability["image"], region=config["regions"]["abilities"]
            # ):
            #     pydirectinput.keyDown(ability["key"])
            pydirectinput.keyUp(awakening["key"])
        else:
            # 瞬发 ability
            if config["performance"] == True or config["GFN"] == True:
                pydirectinput.press(awakening["key"])
                sleep(50, 60)
                pydirectinput.press(awakening["key"])
                # sleep(50, 60)
                # pydirectinput.press(ability["key"])
                return
            pydirectinput.press(awakening["key"])

# def fightFloor2Boss():
#     if states["status"] == "floor3" and pyautogui.locateOnScreen(
#         "./screenshots/bossBar.png", confidence=0.8, region=(406, 159, 1000, 200)
#     ):
#         print("boss bar located")
#         mouseMoveTo(x=states["moveToX"], y=states["moveToY"])
#         sleep(80, 100)
#         pydirectinput.press(config["awakening"])
#     elif states["bossBarLocated"] == False and pyautogui.locateOnScreen(
#         "./screenshots/bossBar.png", confidence=0.8, region=(406, 159, 1000, 200)
#     ):
#         mouseMoveTo(x=states["moveToX"], y=states["moveToY"])
#         sleep(80, 100)
#         print("boss bar located")
#         pydirectinput.press(config["awakening"])
#         states["bossBarLocated"] = True
#         sleep(2500, 3000)


def calculateMinimapRelative(x, y):
    selfLeft = config["minimapCenterX"]
    selfTop = config["minimapCenterY"]
    # if abs(selfLeft - x) <= 3 and abs(selfTop - y) <= 3:
    #     states["moveToX"] = config["screenCenterX"]
    #     states["moveToY"] = config["screenCenterY"]
    #     return

    x = x - selfLeft
    y = y - selfTop
    distBtwPoints = math.sqrt(x * x + y * y)
    states["moveTime"] = int(distBtwPoints * 16)

    dist = 200
    if y < 0:
        dist = -dist

    if x == 0:
        if y < 0:
            newY = y - abs(dist)
        else:
            newY = y + abs(dist)
        # print("relative to center pos newX: 0 newY: {}".format(int(newY)))
        states["moveToX"] = 0 + config["screenCenterX"]
        states["moveToY"] = int(newY) + config["screenCenterY"]
        return
    if y == 0:
        if x < 0:
            newX = x - abs(dist)
        else:
            newX = x + abs(dist)
        # print("relative to center pos newX: {} newY: 0".format(int(newX)))
        states["moveToX"] = int(newX) + config["screenCenterX"]
        states["moveToY"] = 0 + config["screenCenterY"]
        return

    k = y / x
    # newX = x + dist
    newY = y + dist
    # newY = k * (newX - x) + y
    newX = (newY - y) / k + x

    # print("before confining newX: {} newY: {}".format(int(newX), int(newY)))
    if newX < 0 and abs(newX) > config["clickableAreaX"]:
        newX = -config["clickableAreaX"]
        if newY < 0:
            newY = newY + abs(dist) * 0.25
        else:
            newY = newY - abs(dist) * 0.25
    elif newX > 0 and abs(newX) > config["clickableAreaX"]:
        newX = config["clickableAreaX"]
        if newY < 0:
            newY = newY + abs(dist) * 0.25
        else:
            newY = newY - abs(dist) * 0.25

    if newY < 0 and abs(newY) > config["clickableAreaY"]:
        newY = -config["clickableAreaY"]
        if newX < 0:
            newX = newX + abs(dist) * 0.7
        else:
            newX = newX - abs(dist) * 0.7
    elif newY > 0 and abs(newY) > config["clickableAreaY"]:
        newY = config["clickableAreaY"]
        if newX < 0:
            newX = newX + abs(dist) * 0.7
        else:
            newX = newX - abs(dist) * 0.7

    # print(
    #     "after confining relative to center pos newX: {} newY: {}".format(
    #         int(newX), int(newY)
    #     )
    # )
    states["moveToX"] = int(newX) + config["screenCenterX"]
    states["moveToY"] = int(newY) + config["screenCenterY"]
    return


def moveToMinimapRelative(x, y, timeMin, timeMax, blink):
    # move one step to direction
    if (
        states["moveToX"] == config["screenCenterX"]
        and states["moveToY"] == config["screenCenterY"]
    ):
        return

    if states["status"] == "floor1":
        mouseMoveTo(x=x, y=y)
        sleep(100, 120)
        return

    # moving in a straight line
    # if states["moveTime"] < 50:
    #     return
    # print(
    #     "moving to pos x: {} y: {} for {} ms".format(
    #         states["moveToX"], states["moveToY"], states["moveTime"]
    #     )
    # )
    # pydirectinput.keyDown("alt")
    sleep(10, 30)
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(10, 30)
    # pydirectinput.keyUp("alt")
    sleep(int(states["moveTime"] / 2) - 50, int(states["moveTime"] / 2) + 50)

    # moving in a straight line
    # pydirectinput.keyDown("alt")
    sleep(10, 30)
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(10, 30)
    # pydirectinput.keyUp("alt")
    sleep(int(states["moveTime"] / 2) - 50, int(states["moveTime"] / 2) + 50)

    # sleep(timeMin, timeMax)

    # optional blink here
    if blink or states["moveTime"] > 800:
        # print("blink")
        if states["moveTime"] > 1200:
            if config["characters"][states["currentCharacter"]]["class"] == "sorceress":
                pydirectinput.press("x")
            sleep(120, 160)
        if config["characters"][states["currentCharacter"]]["class"] != "gunlancer":
            pydirectinput.press(config["blink"])
        sleep(120, 170)

    pydirectinput.click(
        x=config["screenCenterX"], y=config["screenCenterY"], button=config["move"]
    )
    sleep(100, 120)
    return


def randomMove():
    x = random.randint(
        config["screenCenterX"] - config["clickableAreaX"],
        config["screenCenterX"] + config["clickableAreaX"],
    )
    y = random.randint(
        config["screenCenterY"] - config["clickableAreaY"],
        config["screenCenterY"] + config["clickableAreaY"],
    )
    if states["status"] == "floor1" or states["status"] == "floor2":
        mouseMoveTo(x=x, y=y)
        sleep(200, 250)
        if config["characters"][states["currentCharacter"]]["class"] != "gunlancer":
            pydirectinput.press(config["blink"])
        sleep(200, 250)
        return

    # print("random move to x: {} y: {}".format(x, y))
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(200, 250)
    pydirectinput.click(x=x, y=y, button=config["move"])
    sleep(200, 250)
    pydirectinput.click(
        x=config["screenCenterX"], y=config["screenCenterY"], button=config["move"]
    )
    sleep(100, 150)


# def isPortalFlame(image, x, y):
#     r, g, b = image.getpixel((x, y))
#     flag = False
#     dist = 5
#     blueFlag = r in range(1, 3) and g in range(1, 4) and b in range(3, 6)
#     purpleFlag = r in range(3, 6) and g in range(1, 4) and b in range(1, 3)
#     if blueFlag or purpleFlag:
#         return True
#     return flag


def enterPortal():
    # repeatedly move and press g until black screen
    # sleep(1100, 1200)
    # print("moving to portal x: {} y: {}".format(states["moveToX"], states["moveToY"]))
    # print("move for {} ms".format(states["moveTime"]))
    if states["moveTime"] > 550:
        # print("blink")
        pydirectinput.click(
            x=states["moveToX"], y=states["moveToY"], button=config["move"]
        )
        sleep(100, 150)
        if config["characters"][states["currentCharacter"]]["class"] != "gunlancer":
            pydirectinput.press(config["blink"])

    enterTime = int(time.time_ns() / 1000000)
    while True:
        # try to enter portal until black screen
        im = pyautogui.screenshot(region=(1652, 168, 240, 210))
        r, g, b = im.getpixel((1772 - 1652, 272 - 168))
        # print(r + g + b)
        if r + g + b < 30:
            # print("portal entered")
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            return True

        nowTime = int(time.time_ns() / 1000000)
        falseTime = 6000
        if nowTime - enterTime > falseTime:
            # clear mobs a bit with first spell before scanning for portal again
            pydirectinput.press(states["abilityScreenshots"][0]["key"])
            sleep(100, 150)
            pydirectinput.press(config["meleeAttack"])
            sleep(100, 150)
            return False
        # hit move and press g
        if (
            states["moveToX"] == config["screenCenterX"]
            and states["moveToY"] == config["screenCenterY"]
        ):
            pydirectinput.press(config["interact"])
            sleep(100, 120)
            # pydirectinput.press(config["interact"])
        else:
            pydirectinput.press(config["interact"])
            pydirectinput.click(
                x=states["moveToX"], y=states["moveToY"], button=config["move"]
            )
            sleep(60, 70)
            # pydirectinput.press(config["interact"])


# def enterPortal():
#     # repeatedly move and press g until black screen
#     print("moving to portal x: {} y: {}".format(states["moveToX"], states["moveToY"]))
#     turn = True
#     deflect = 80
#     while True:
#         im = pyautogui.screenshot(region=(1652, 168, 240, 210))
#         r, g, b = im.getpixel((1772 - 1652, 272 - 168))
#         if r == 0 and g == 0 and b == 0:
#             return

#         x = states["moveToX"]
#         y = states["moveToY"]
#         if x > 960 and y < 540:
#             if turn:
#                 x = x - deflect * 2.5
#                 y = y - deflect
#             else:
#                 x = x + deflect * 2.5
#                 y = y + deflect
#         elif x > 960 and y > 540:
#             if turn:
#                 x = x + deflect * 2.5
#                 y = y - deflect
#             else:
#                 x = x - deflect * 2.5
#                 y = y + deflect
#         elif x < 960 and y > 540:
#             if turn:
#                 x = x + deflect * 2.5
#                 y = y + deflect
#             else:
#                 x = x - deflect * 2.5
#                 y = y - deflect
#         elif x < 960 and y < 540:
#             if turn:
#                 x = x - deflect * 2.5
#                 y = y + deflect
#             else:
#                 x = x + deflect * 2.5
#                 y = y - deflect
#         # print('movex: {} movey: {} x:{} y: {} turn: {}'.format(states['moveToX'], states['moveToY'], x,y,turn))
#         count = 0
#         while count < 5:
#             pydirectinput.press(config["interact"])
#             im = pyautogui.screenshot(region=(1652, 168, 240, 210))
#             r, g, b = im.getpixel((1772 - 1652, 272 - 168))
#             if r == 0 and g == 0 and b == 0:
#                 return

#             if (
#                 states["moveToX"] == config["screenCenterX"]
#                 and states["moveToY"] == config["screenCenterY"]
#             ):
#                 pydirectinput.press(config["interact"])
#                 sleep(100, 120)
#             else:
#                 pydirectinput.click(x=x, y=y, button=config["move"])
#                 sleep(50, 60)
#                 pydirectinput.press(config["interact"])
#                 count = count + 1
#             turn = not turn
#     return


def waitForLoading():
    # print("loading")
    blackScreenStartTime = int(time.time_ns() / 1000000)
    while True:
        if offlineCheck():
            closeGameByClickingDialogue()
            return
        if gameCrashCheck():
            return
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
        leaveButton = pyautogui.locateOnScreen(
            "./screenshots/leave.png",
            grayscale=True,
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if leaveButton != None:
            return
        sleep(350, 400)


def saveAbilitiesScreenshots():
    for ability in abilities[config["characters"][states["currentCharacter"]]["class"]]:
        if ability["abilityType"] == "awakening":
            continue
        if ability["abilityType"] == "specialty1":
            continue
        if ability["abilityType"] == "specialty2":
            continue
        left = ability["position"]["left"]
        top = ability["position"]["top"]
        width = ability["position"]["width"]
        height = ability["position"]["height"]
        im = pyautogui.screenshot(region=(left, top, width, height))
        states["abilityScreenshots"].append(
            {
                "key": ability["key"],
                "image": im,
                "cast": ability["cast"],
                "castTime": ability["castTime"],
                "hold": ability["hold"],
                "holdTime": ability["holdTime"],
                "directional": ability["directional"],
                "position": ability["position"],
            }
        )
        sleep(200, 300)


# def windowCheck():
#     if pyautogui.locateOnScreen(
#         "./screenshots/close.png", grayscale=True, confidence=0.9
#     ):
#         pydirectinput.press("esc")
#         sleep(500, 600)


def diedCheck():  # get information about wait a few second to revive
    if pyautogui.locateOnScreen(
        "./screenshots/died.png",
        grayscale=True,
        confidence=0.8,
        region=(917, 145, 630, 550),
    ):
        print("died")
        states["deathCount"] = states["deathCount"] + 1
        sleep(5000, 5500)
        while (
            pyautogui.locateOnScreen(
                "./screenshots/resReady.png",
                confidence=0.7,
                region=(917, 145, 630, 550),
            )
            != None
        ):
            mouseMoveTo(x=1275, y=400)
            sleep(1600, 1800)
            print("rez clicked")
            pydirectinput.click(1275, 400, button="left")
            sleep(600, 800)
            mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
            sleep(600, 800)
            if gameCrashCheck():
                return
            if offlineCheck():
                return
            if checkTimeout():
                return
    return

def doCubes():
    states["status"] = "cube"
    states["currentCharacter"] = 9
    states["instanceStartTime"] = int(time.time_ns() / 1000000)
    saveAbilitiesScreenshots()
    while True:
        diedCheck()
        healthCheck()

        allAbilities = [*range(0, len(states["abilityScreenshots"]))]

        for i in allAbilities:
            if states["status"] == "floor3" and checkChaosFinish():
                print("checkChaosFinish == True")
                return
            diedCheck()
            healthCheck()
            
            performClassSpecialty(i, states["abilityScreenshots"])
            # cast spells
            checkCDandCast(states["abilityScreenshots"][i])


def doAuraRepair(forced):
    # Check if repair needed
    if forced or pyautogui.locateOnScreen(
        "./screenshots/repair.png",
        grayscale=True,
        confidence=0.4,
        region=(1500, 134, 100, 100),
    ):
        # print("repairing")
        toggleMenu("pet")
        mouseMoveTo(x=1142, y=661)
        sleep(2500, 2600)
        pydirectinput.click(1142, 661, button="left")
        sleep(5500, 5600)
        mouseMoveTo(x=1054, y=455)
        sleep(2500, 2600)
        pydirectinput.click(1054, 455, button="left")
        sleep(2500, 2600)
        pydirectinput.press("esc")
        sleep(2500, 2600)
        pydirectinput.press("esc")
        sleep(2500, 2600)


def doCityRepair():
    # for non-aura users: MUST have your character parked near a repairer in city before starting the script
    # Check if repair needed
    if pyautogui.locateOnScreen(
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
        pydirectinput.click(1057, 455, button="left")
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
        leaveButton = pyautogui.locateCenterOnScreen(
            "./screenshots/leave.png",
            grayscale=True,
            confidence=0.7,
            region=config["regions"]["leaveMenu"],
        )
        if leaveButton == None:
            return
        pydirectinput.press(config["healthPot"])
        states["healthPotCount"] = states["healthPotCount"] + 1
        return
    return


def clearQuest():
    quest = pyautogui.locateCenterOnScreen(
        "./screenshots/quest.png", confidence=0.9, region=(815, 600, 250, 200)
    )
    leveledup = pyautogui.locateCenterOnScreen(
        "./screenshots/leveledup.png", confidence=0.9, region=(815, 600, 250, 200)
    )
    gameMenu = pyautogui.locateCenterOnScreen(
        "./screenshots/gameMenu.png",
        confidence=0.95,
        region=config["regions"]["center"],
    )
    if gameMenu != None:
        print("game menu detected")
        pydirectinput.press("esc")
        sleep(1800, 1900)
    if quest != None:
        print("clear quest")
        x, y = quest
        mouseMoveTo(x=x, y=y)
        sleep(1800, 1900)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(1800, 1900)
        pydirectinput.press("esc")
        sleep(1800, 1900)
    elif leveledup != None:
        print("clear level")
        x, y = leveledup
        mouseMoveTo(x=x, y=y)
        sleep(1800, 1900)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(1800, 1900)
        pydirectinput.press("esc")
        sleep(1800, 1900)


def sleep(min, max):
    sleepTime = random.randint(min, max) / 1000.0
    if sleepTime < 0:
        return
    time.sleep(sleepTime)


def spiralSearch(rows, cols, rStart, cStart):
    ans = []  # 可以通过长度来退出返回
    end = rows * cols  # 边界扩张
    i = i1 = i2 = rStart
    # 分别是当前点,上下边界的上边界，下边界
    j = j1 = j2 = cStart  # 当前，左、右边界
    while True:
        j2 += 1
        while j < j2:
            if 0 <= j < cols and 0 <= i:  # i刚减完
                ans.append([i, j])
            j += 1
            if 0 > i:  # i超过了，跳过优化
                j = j2  # 没有答案可添加
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
        sessionLimitReached = pyautogui.locateCenterOnScreen(
            "./screenshots/sessionLimitReached.png",
            region=config["regions"]["center"],
            confidence=0.8,
        )
        if sessionLimitReached != None:
            currentTime = int(time.time_ns() / 1000000)
            limitshot = pyautogui.screenshot()
            limitshot.save("./debug/sessionLimitReached" + str(currentTime) + ".png")
            mouseMoveTo(x=1029, y=822)
            sleep(1300, 1400)
            pydirectinput.click(x=1029, y=822, button="left")
            sleep(1300, 1400)
            print("session limit...")
            states["gameCrashCount"] = states["gameCrashCount"] + 1
            return True
        inactiveGFN = pyautogui.locateCenterOnScreen(
            "./screenshots/inactiveGFN.png",
            region=config["regions"]["center"],
            confidence=0.8,
        )
        if inactiveGFN != None:
            currentTime = int(time.time_ns() / 1000000)
            inactive = pyautogui.screenshot()
            inactive.save("./debug/inactive_" + str(currentTime) + ".png")
            mouseMoveTo(x=1194, y=585)
            sleep(1300, 1400)
            pydirectinput.click(x=1194, y=585, button="left")
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


def offlineCheck():
    dc = pyautogui.locateOnScreen(
        "./screenshots/dc.png",
        region=config["regions"]["center"],
        confidence=config["confidenceForGFN"],
    )
    ok = pyautogui.locateCenterOnScreen(
        "./screenshots/ok.png", region=config["regions"]["center"], confidence=0.75
    )
    enterServer = pyautogui.locateCenterOnScreen(
        "./screenshots/enterServer.png",
        confidence=config["confidenceForGFN"],
        region=(885, 801, 160, 55),
    )
    # should put these in crash check instead? No because it requires one more click
    if config["GFN"] == True:
        sessionLimitReached = pyautogui.locateCenterOnScreen(
            "./screenshots/sessionLimitReached.png",
            region=config["regions"]["center"],
            confidence=0.8,
        )
        if sessionLimitReached != None:
            currentTime = int(time.time_ns() / 1000000)
            limitshot = pyautogui.screenshot()
            limitshot.save("./debug/sessionLimitReached" + str(currentTime) + ".png")
            mouseMoveTo(x=1029, y=822)
            sleep(1300, 1400)
            pydirectinput.click(x=1029, y=822, button="left")
            sleep(1300, 1400)
            print("session limit...")
            states["gameCrashCount"] = states["gameCrashCount"] + 1
            return True
        updateMembership = pyautogui.locateCenterOnScreen(
            "./screenshots/updateMembership.png",
            region=config["regions"]["center"],
            confidence=0.8,
        )
        if updateMembership != None:
            currentTime = int(time.time_ns() / 1000000)
            limitshot = pyautogui.screenshot()
            limitshot.save("./debug/updateMembership" + str(currentTime) + ".png")
            mouseMoveTo(x=1036, y=822)
            sleep(1300, 1400)
            pydirectinput.click(x=1036, y=822, button="left")
            sleep(1300, 1400)
            print("update Membership...")
            states["gameCrashCount"] = states["gameCrashCount"] + 1
            return True
        inactiveGFN = pyautogui.locateCenterOnScreen(
            "./screenshots/inactiveGFN.png",
            region=config["regions"]["center"],
            confidence=0.9,
        )
        if inactiveGFN != None:
            currentTime = int(time.time_ns() / 1000000)
            inactive = pyautogui.screenshot()
            inactive.save("./debug/inactive_" + str(currentTime) + ".png")
            mouseMoveTo(x=1194, y=585)
            sleep(1300, 1400)
            pydirectinput.click(x=1194, y=585, button="left")
            sleep(1300, 1400)
            print("game inactive...")
            states["gameCrashCount"] = states["gameCrashCount"] + 1
            return True
    if dc != None or ok != None or enterServer != None:
        currentTime = int(time.time_ns() / 1000000)
        dc = pyautogui.screenshot()
        dc.save("./debug/dc_" + str(currentTime) + ".png")
        print(
            "disconnection detected...currentTime : {} dc:{} ok:{} enterServer:{}".format(
                currentTime, dc, ok, enterServer
            )
        )
        states["gameOfflineCount"] = states["gameOfflineCount"] + 1
        return True
    return False


def closeGameByClickingDialogue():
    """
    # ok = pyautogui.locateCenterOnScreen(
    #     "./screenshots/ok.png",
    #     region=config["regions"]["center"],
    # )
    # if ok != None:
    #     x, y = ok
    #     mouseMoveTo(x=x, y=y)
    #     sleep(300, 400)
    #     pydirectinput.click(x=x, y=y, button="left")
    # else:
    #     mouseMoveTo(x=960, y=500)
    #     sleep(300, 400)
    #     pydirectinput.click(button="left")
    """
    while True:
        ok = pyautogui.locateCenterOnScreen(
            "./screenshots/ok.png", region=config["regions"]["center"], confidence=0.75
        )
        enterServer = pyautogui.locateCenterOnScreen(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        if ok != None:
            x, y = ok
            mouseMoveTo(x=x, y=y)
            sleep(300, 400)
            pydirectinput.click(x=x, y=y, button="left")
            print("clicked ok")
        elif enterServer != None:
            break
        else:
            break
        sleep(1300, 1400)
    states["status"] = "restart"
    sleep(12000, 13000)


def restartGame():
    print("restart game")
    gameCrashCheck()
    sleep(5000, 7000)
    # states["multiCharacterMode"] = False  # for now
    # states["multiCharacterModeState"] = []  # for now
    # states["currentCharacter"] = config["mainCharacter"]
    while True:
        if config["GFN"] == True:
            sleep(10000, 12000)
            loaGFN = pyautogui.locateCenterOnScreen(
                "./screenshots/loaGFN.png",
                confidence=0.8,
            )
            loaGFNplay = pyautogui.locateCenterOnScreen(
                "./screenshots/loaGFNplay.png",
                confidence=0.8,
            )
            if loaGFNplay != None:
                x, y = loaGFNplay
                mouseMoveTo(x=x, y=y)
                sleep(2200, 2300)
                pydirectinput.click(x=x, y=y, button="left")
                print("clicked play restart on GFN")
                sleep(40000, 42000)
                break
            if loaGFN != None:
                x, y = loaGFN
                mouseMoveTo(x=x, y=y)
                sleep(2200, 2300)
                pydirectinput.click(x=x, y=y, button="left")
                print("clicked image restart on GFN")
                sleep(40000, 42000)
                break
            afkGFN = pyautogui.locateCenterOnScreen(
                "./screenshots/afkGFN.png",
                region=config["regions"]["center"],
                confidence=0.75,
            )
            closeGFN = pyautogui.locateCenterOnScreen(
                "./screenshots/closeGFN.png",
                confidence=0.75,
            )
            if closeGFN != None:
                print("afk GFN")
                x, y = closeGFN
                mouseMoveTo(x=x, y=y)
                sleep(1300, 1400)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(1300, 1400)
                continue
        else:
            os.system('start steam://launch/1599340/dialog')
            sleep(60000, 60000)
        enterGame = pyautogui.locateCenterOnScreen(
            "./screenshots/steamPlay.png", confidence=0.75
        )
        sleep(500, 600)
        stopGame = pyautogui.locateCenterOnScreen(
            "./screenshots/steamStop.png", confidence=0.75
        )
        sleep(500, 600)
        confirm = pyautogui.locateCenterOnScreen(
            "./screenshots/steamConfirm.png", confidence=0.75
        )
        sleep(500, 600)
        enterServer = pyautogui.locateCenterOnScreen(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        sleep(500, 600)
        inTown = pyautogui.locateCenterOnScreen(
            "./screenshots/inTown.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if stopGame != None:
            print("clicking stop game on steam")
            x, y = stopGame
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(500, 600)
            confirm = pyautogui.locateCenterOnScreen(
                "./screenshots/steamConfirm.png", confidence=0.75
            )
            if confirm == None:
                continue
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(10000, 12000)
        elif confirm != None:
            print("confirming stop game")
            x, y = confirm
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(10000, 12000)
        elif enterGame != None:
            print("restarting Lost Ark game client...")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(x=x, y=y, button="left")
            break
        elif enterServer != None:
            # new eacoffline interface
            break
        elif inTown != None:
            return
            # # i think eventually GFN would restart?
            # loa = pyautogui.locateCenterOnScreen(
            #     "./screenshots/loa.png",
            #     confidence=0.8,
            # )
            # if loa != None:
            #     x, y = loa
            #     mouseMoveTo(x=x, y=y)
            #     sleep(1200, 1300)
            #     pydirectinput.click(x=x, y=y, button="left")
            #     sleep(2200, 2300)
            #     continue
        sleep(1200, 1300)
    sleep(5200, 6300)
    while True:
        enterServer = pyautogui.locateCenterOnScreen(
            "./screenshots/enterServer.png",
            confidence=config["confidenceForGFN"],
            region=(885, 801, 160, 55),
        )
        enterGame = pyautogui.locateCenterOnScreen(
            "./screenshots/steamPlay.png", confidence=0.75
        )
        if enterServer != None:
            print("clicking enterServer")
            sleep(1000, 1200)
            # click first server
            mouseMoveTo(x=855, y=582)
            sleep(1200, 1300)
            pydirectinput.click(x=855, y=582, button="left")
            sleep(1000, 1200)
            x, y = enterServer
            mouseMoveTo(x=x, y=y)
            sleep(1200, 1300)
            pydirectinput.click(x=x, y=y, button="left")
            break
        elif enterGame != None:
            print("clicking enterGame")
            x, y = enterGame
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(x=x, y=y, button="left")
            sleep(4200, 5300)
            continue
    sleep(3200, 4300)
    while True:
        enterCharacter = pyautogui.locateCenterOnScreen(
            "./screenshots/enterCharacter.png",
            confidence=0.75,
            region=(745, 854, 400, 80),
        )
        if enterCharacter != None:
            sleep(1000, 1200)
            # 点第一页
            sleep(4000, 5000)
            # mouseMoveTo(x=138, y=895)
            # sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)

            # 点main角色
            # sleep(4000, 5000)
            # print("clicking mainCharacter")
            # mouseMoveTo(
            #     x=config["charPositionsAtCharSelect"][config["mainCharacter"]][0],
            #     y=config["charPositionsAtCharSelect"][config["mainCharacter"]][1],
            # )
            # sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)

            print("clicking enterCharacter")
            x, y = enterCharacter
            mouseMoveTo(x=x, y=y)
            sleep(200, 300)
            pydirectinput.click(x=x, y=y, button="left")
            break
        sleep(2200, 3300)
    states["gameRestartCount"] = states["gameRestartCount"] + 1
    mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
    sleep(22200, 23300)


def switchToCharacter(index):
    sleep(1500, 1600)
    print("switching to {}".format(index))
    while pyautogui.locateCenterOnScreen(
        "./screenshots/gameMenu.png",
        confidence=0.7
    ) == None:
        pydirectinput.press("esc")
        sleep(1800, 1900)
    print("game menu detected")
    mouseMoveTo(x=config["charSwitchX"], y=config["charSwitchY"])
    sleep(500, 600)
    pydirectinput.click(
        x=config["charSwitchX"], 
        y=config["charSwitchY"], 
        button="left")
    sleep(500, 600)
    pydirectinput.click(
        x=config["charSwitchX"], 
        y=config["charSwitchY"], 
        button="left")
    sleep(500, 600)

    # mouseMoveTo(
    #     x=config["charPositions"][index][0], y=config["charPositions"][index][1]
    # )
    # sleep(1500, 1600)
    # pyautogui.scroll(5)  # fix character switch if you have more then 9 characters
    # sleep(1500, 1600)
    mouseMoveTo(x=1260, y=392)
    sleep(500, 600)
    pydirectinput.click(x=1260, y=392, button="left")
    sleep(500, 600)
    pydirectinput.click(x=1260, y=392, button="left")
    sleep(500, 600)
    if index > 8:
        # mouseMoveTo(
        #     x=config["charPositions"][index][0], y=config["charPositions"][index][1]
        # )
        # pyautogui.scroll(-5)
        # sleep(1500, 1600)
        mouseMoveTo(x=1260, y=638)
        sleep(500, 600)
        pydirectinput.click(x=1260, y=638, button="left")
        sleep(500, 600)
        pydirectinput.click(x=1260, y=638, button="left")
        sleep(500, 600)

    mouseMoveTo(
        x=config["charPositions"][index][0], 
        y=config["charPositions"][index][1]
    )
    sleep(300, 400)
    pydirectinput.click(
        x=config["charPositions"][index][0],
        y=config["charPositions"][index][1],
        button="left",
    )
    sleep(300, 400)
    pydirectinput.click(
        x=config["charPositions"][index][0],
        y=config["charPositions"][index][1],
        button="left",
    )
    sleep(1500, 1600)

    if pyautogui.locateCenterOnScreen(
        "./screenshots/alreadyConnected.png",
        confidence=0.85
    ) != None:
        print("character already connected")
        pydirectinput.press("esc")
        sleep(500, 600)
        pydirectinput.press("esc")
        sleep(500, 600)
        return

    mouseMoveTo(x=config["charSelectConnectX"], y=config["charSelectConnectY"])
    sleep(300, 400)
    pydirectinput.click(
        x=config["charSelectConnectX"], 
        y=config["charSelectConnectY"], 
        button="left"
    )
    sleep(300, 400)
    pydirectinput.click(
        x=config["charSelectConnectX"], 
        y=config["charSelectConnectY"], 
        button="left"
    )
    sleep(1000, 1000)

    # currentTime = int(time.time_ns() / 1000000)
    # switchToChar = pyautogui.screenshot()
    # switchToChar.save(
    #     "./debug/switchToChar_" + str(index) + "_" + str(currentTime) + ".png"
    # )

    mouseMoveTo(x=config["charSelectOkX"], y=config["charSelectOkY"])
    sleep(300, 400)
    pydirectinput.click(
        x=config["charSelectOkX"], 
        y=config["charSelectOkY"], 
        button="left"
    )
    sleep(300, 400)
    pydirectinput.click(
        x=config["charSelectOkX"], 
        y=config["charSelectOkY"], 
        button="left"
    )
    sleep(500, 600)

    states["currentCharacter"] = index
    states["abilityScreenshots"] = []
    sleep(10000, 12000)
    if config["GFN"] == True:
        sleep(8000, 9000)


def doGuildDonation():
    toggleMenu("guild")
    sleep(5000, 5000)

    ok = pyautogui.locateCenterOnScreen(
        "./screenshots/ok.png", region=config["regions"]["center"], confidence=0.75
    )

    if ok != None:
        x, y = ok
        mouseMoveTo(x=x, y=y)
        sleep(300, 400)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(300, 400)
        pydirectinput.click(x=x, y=y, button="left")
    sleep(1500, 1600)

    mouseMoveTo(x=1431, y=843)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    # pydirectinput.click(button="left")
    # sleep(500, 600)

    # dono silver
    mouseMoveTo(x=767, y=561)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(500, 600)
    # pydirectinput.click(button="left")
    # sleep(500, 600)

    pydirectinput.press("esc")
    sleep(3500, 3600)

    supportResearch = pyautogui.locateCenterOnScreen(
        "./screenshots/supportResearch.png",
        confidence=0.8,
        region=(1255, 210, 250, 600),
    )

    if supportResearch != None:
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

        canSupportResearch = pyautogui.locateCenterOnScreen(
            "./screenshots/canSupportResearch.png",
            confidence=0.8,
            region=(735, 376, 450, 350),
        )

        if canSupportResearch != None:
            mouseMoveTo(x=848, y=520)
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)

            mouseMoveTo(x=921, y=701)
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
            pydirectinput.click(button="left")
            sleep(500, 600)
            # pydirectinput.click(button="left")
            # sleep(500, 600)
        else:
            pydirectinput.press("esc")
            sleep(800, 900)

    sleep(2800, 2900)
    pydirectinput.press("esc")
    sleep(2800, 2900)


def doRapport():
    sleep(1000, 2000)
    print("doing Rapport")
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    sleep(3500, 4600)
    # dorapport
    bifrostAvailable = bifrostGoTo(2)
    if bifrostAvailable == False:
        return
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    songandemoterapport()


def songandemoterapport():
    print("song and emote for rapport")
    pydirectinput.keyDown("alt")
    sleep(800, 900)
    pydirectinput.press("w")
    sleep(800, 900)
    pydirectinput.keyUp("alt")
    sleep(800, 900)
    spamInteract(1000)
    sleep(2000, 3000)
    mouseMoveTo(x=105, y=870)
    sleep(200, 300)
    pydirectinput.click(button="left")
    sleep(200, 300)
    mouseMoveTo(x=1630, y=403)
    sleep(300, 600)
    pydirectinput.click(button="left")
    sleep(300, 600)
    mouseMoveTo(x=1676, y=551)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(30000, 31000)  # 1songduration
    mouseMoveTo(x=105, y=870)
    sleep(300, 600)
    pydirectinput.click(button="left")
    sleep(300, 600)
    mouseMoveTo(x=1676, y=452)
    sleep(300, 600)
    pydirectinput.click(button="left")
    sleep(300, 600)
    mouseMoveTo(x=1676, y=551)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(30000, 31000)  # 2songduration
    mouseMoveTo(x=118, y=904)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(300, 400)
    mouseMoveTo(x=155, y=454)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(300, 400)
    mouseMoveTo(x=203, y=595)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(17000, 20000)  # 1emoteduration
    mouseMoveTo(x=118, y=904)
    sleep(300, 400)
    pydirectinput.click(button="left")
    mouseMoveTo(x=311, y=454)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(300, 400)
    mouseMoveTo(x=203, y=595)
    sleep(300, 400)
    pydirectinput.click(button="left")
    sleep(17000, 20000)  # 2emoteduration
    mouseMoveTo(x=1832, y=900)
    sleep(300, 400)
    pydirectinput.click(button="left")


def doLopang():
    sleep(1000, 2000)
    print("accepting lopang daily")
    areDailiesAccepted = acceptDailies()
    sleep(1500, 1600)
    if areDailiesAccepted == False:
        return
    sleep(500, 600)
    if gameCrashCheck():
        return
    if offlineCheck():
        return

    sleep(1500, 1600)

    # goto lopang island
    bifrostAvailable = bifrostGoTo("lopangIsland")
    if bifrostAvailable == False:
        return
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    sleep(5500, 6600)
    spamInteract(3000)
    walkLopang()
    sleep(1500, 1600)
    bifrostGoTo("lopangShushire")
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    spamInteract(10000)
    sleep(1500, 1600)
    bifrostGoTo("lopangArthetine")
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    spamInteract(10000)
    sleep(1500, 1600)
    bifrostGoTo("lopangVern")
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    spamInteract(10000)

def doLeapstoneUnas(unas):
    sleep(1000, 2000)
    print("accepting leapstone dailies")
    areDailiesAccepted = acceptDailies()
    if areDailiesAccepted == False:
        return
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    
    if "mokomoko" in unas:
        bifrostAvailable = bifrostGoTo("mokomoko")
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        if bifrostAvailable == True:
            doMokomokoUna()

    if "bleakNight" in unas:
        bifrostAvailable = bifrostGoTo("bleakNightFog")
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        if bifrostAvailable == True:
            doBleakNightFogUna()

    if "hesteraGarden" in unas:
        bifrostAvailable = bifrostGoTo("hesteraGarden")
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        if bifrostAvailable == True:
            doHesteraGardenUna()

    if "sageTower" in unas:
        bifrostAvailable = bifrostGoTo("sageTower")
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        if bifrostAvailable == True:
            doSageTowerUna()

    if "southKurzan" in unas:
        bifrostAvailable = bifrostGoTo("southKurzan")
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        if bifrostAvailable == True:
            doSouthKurzanUna()

    print("done")

def doBleakNightFogUna():
    pydirectinput.press("f5")
    sleep(800, 900)
    pydirectinput.press("f6")
    sleep(1800, 1900)
    claimCompletedQuest()

def doHesteraGardenUna():
    toggleMenu("hesteraGardenCombatPreset")

    pydirectinput.press(config["hesteraGardenEmoteSlot"])
    sleep(140000, 141000)
    claimCompletedQuest()
    sleep(300, 400)

    toggleMenu("defaultCombatPreset")

def doSageTowerUna():
    sleep(5000,5000)
    spamInteract(15000)
    mouseMoveTo(x=1560, y=540)
    sleep(500, 600)
    pydirectinput.click(x=1560, y=540, button=config["move"])
    sleep(500, 600)
    spamInteract(4000)

def doSouthKurzanUna():
    sleep(5000,5000)
    selfieMode = pyautogui.locateCenterOnScreen("./screenshots/selfieMode.png", confidence=0.85)
    if selfieMode == None:
        print("selfie mode icon not found")
        return
    x, y = selfieMode
    mouseMoveTo(x=x, y=y)
    sleep(500, 600)
    pydirectinput.click(x=x, y=y, button="left")
    sleep(4000, 4100)
    pydirectinput.press(config["printscreenMacro"])
    sleep(5000, 6000)
    pydirectinput.press("esc")
    sleep(500, 600)
    pydirectinput.press("enter")
    sleep(500, 600)
    mouseMoveTo(x=700, y=200)
    sleep(500, 600)
    pydirectinput.click(x=650, y=180, button="left")
    sleep(2500, 2600)
    pydirectinput.click(x=650, y=180, button="left")
    sleep(2500, 2600)
    spamInteract(5000)

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

    completeQuest = pyautogui.locateCenterOnScreen("./screenshots/completeQuest.png", confidence=0.85)
    if completeQuest == None:
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
        sleep(2500, 2600)
    elif len(keys) == 1:
        pydirectinput.press(keys[0])
        sleep(300, 400)

def bifrostGoTo(location):
    # meleeClick = "right"
    # if config["move"] == "right":
    #     meleeClick = "left"
    # mouseMoveTo(x=config["screenCenterX"], y=config["screenCenterY"])
    # sleep(200, 300)
    # pydirectinput.click(button=meleeClick)
    # sleep(300, 400)

    print("bifrost to: {}".format(location))
    toggleMenu("bifrost")
    sleep(1500, 1600)
    bifrost = pyautogui.locateCenterOnScreen("./screenshots/bifrosts/" + location + "Bifrost.png", confidence=0.80)
    if bifrost == None:
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

    # potentially unnecessary check
    if checkBlueCrystal():
        pydirectinput.press("esc")
        sleep(1500, 1600)
        pydirectinput.press("esc")
        sleep(1500, 1600)
        return False
    else:
        # ok
        while True:
            okButton = pyautogui.locateCenterOnScreen(
                "./screenshots/ok.png",
                confidence=0.75,
                region=config["regions"]["center"],
            )
            if okButton != None:
                x, y = okButton
                mouseMoveTo(x=x, y=y)
                sleep(2000, 2100)
                pydirectinput.click(x=x, y=y, button="left")
                sleep(2000, 2100)
                break
            sleep(300, 400)
    sleep(10000, 12000)

    # wait until loaded
    while True:
        if gameCrashCheck():
            return
        if offlineCheck():
            return
        sleep(1000, 1200)
        inTown = pyautogui.locateCenterOnScreen(
            "./screenshots/inTown.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if inTown != None:
            # print("city loaded")
            break
        sleep(1400, 1600)
    sleep(3500, 3600)
    if gameCrashCheck():
        return
    if offlineCheck():
        return
    return True
    # sleep(4000, 5000)


def walkLopang():
    pydirectinput.PAUSE = 0.1
    sleep(1000, 2000)
    print("walking lopang")
    spamInteract(2000)
    # nowTime = int(time.time_ns() / 1000000)
    # lopangDebug = pyautogui.screenshot()
    # lopangDebug.save("./debug/lopangDebug_" + str(nowTime) + ".png")
    walkWithAlt(315, 473, 1500)
    walkWithAlt(407, 679, 1300)
    walkWithAlt(584, 258, 1000)
    walkWithAlt(1043, 240, 1200)
    walkWithAlt(1339, 246, 1300)
    walkWithAlt(1223, 406, 800)
    walkWithAlt(1223, 406, 800)
    walkWithAlt(1263, 404, 1300)
    spamInteract(500)
    # nowTime = int(time.time_ns() / 1000000)
    # lopangDebug = pyautogui.screenshot()
    # lopangDebug.save("./debug/lopangDebug_" + str(nowTime) + ".png")
    walkWithAlt(496, 750, 1200)
    walkWithAlt(496, 750, 1200)
    walkWithAlt(496, 750, 1200)
    walkWithAlt(753, 687, 800)
    walkWithAlt(753, 687, 800)
    walkWithAlt(674, 264, 800)
    walkWithAlt(573, 301, 1200)
    walkWithAlt(820, 240, 1300)
    spamInteract(500)
    # nowTime = int(time.time_ns() / 1000000)
    # lopangDebug = pyautogui.screenshot()
    # lopangDebug.save("./debug/lopangDebug_" + str(nowTime) + ".png")
    sleep(1000, 2000)
    pydirectinput.PAUSE = 0.05
    sleep(1000, 2000)


def checkBlueCrystal():
    """
    # blueCrystal = pyautogui.locateCenterOnScreen(
    #     "./screenshots/blueCrystal.png",
    #     confidence=0.75,
    #     region=config["regions"]["center"],
    # )
    """
    silver1k = pyautogui.locateCenterOnScreen(
        "./screenshots/silver1k.png",
        confidence=0.75,
        region=config["regions"]["center"],
    )

    if silver1k != None:
        return False
    else:
        return True


def acceptDailies():
    sleep(500, 600)
    toggleMenu("unas")
    sleep(5000,5100)
    mouseMoveTo(x=550, y=255)
    sleep(100, 100)
    pydirectinput.click(button="left")
    sleep(2000,2100)
    if pyautogui.locateOnScreen("./screenshots/unasCompleted.png", confidence = 0.85) != None:
        print("character has already ran unas")
        toggleMenu("unas")
        return False

    while pyautogui.locateOnScreen("./screenshots/acceptUna.png", confidence = 0.75) != None:
        x, y = pyautogui.locateCenterOnScreen("./screenshots/acceptUna.png", confidence = 0.75)
        mouseMoveTo(x=x, y=y)
        sleep(500, 500)
        pydirectinput.click(x=x, y=y, button="left")
        sleep(2500, 2500)

    pydirectinput.press("esc")
    sleep(2800, 2900)

def walkWithAlt(lopangX, lopangY, milliseconds):
    lopangX = lopangX
    lopangY = lopangY
    mouseMoveTo(x=lopangX, y=lopangY)
    sleep(100, 100)
    pydirectinput.click(x=lopangX, y=lopangY, button=config["move"])
    sleep(milliseconds, milliseconds)


def walkPressG(lopangX, lopangY, milliseconds):
    timeCount = milliseconds / 100
    while timeCount != 0:
        lopangX = lopangX
        lopangY = lopangY
        mouseMoveTo(x=lopangX, y=lopangY)
        sleep(100, 100)
        pydirectinput.click(button=config["move"])
        timeCount = timeCount - 1
        if lopangX % 2 == 0:
            pydirectinput.press(config["interact"])


def spamInteract(milliseconds):
    timeCount = milliseconds / 100
    while timeCount != 0:
        pydirectinput.press(config["interact"])
        sleep(90, 120)
        timeCount = timeCount - 1

def doSailingWeekly(n):
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
        sleep(5000,5100)
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
        # close menu
        toggleMenu("unas")
        sleep(2000,2100)
        # move to second location
        mouseMoveTo(x=763, y=427)
        sleep(100, 100)
        pydirectinput.keyDown("alt")
        sleep(200, 300)
        pydirectinput.click(button="left")
        sleep(200, 300)
        # move to second location
        if i % 2 == 0:
            mouseMoveTo(x=566, y=501)
        else: 
            mouseMoveTo(x=960, y=505)
        sleep(200, 300)
        pydirectinput.click(button="left")
        if i == (n - 1):
            sleep(200, 300)
            mouseMoveTo(x=1055, y=600)
            sleep(200, 300)
            pydirectinput.click(button="left")
        sleep(200, 300)
        pydirectinput.keyUp("alt")
        while pyautogui.locateOnScreen("./screenshots/sailingIdle.png", region=(1060, 840, 50, 40), confidence=0.9) == None:
            sleep(1000,1100)
        claimCompletedQuest()
    mouseMoveTo(x=1050, y=900)
    sleep(200, 300)
    pydirectinput.click(button="left")
    sleep(1000, 1100)
    pydirectinput.click(button="left")
    sleep(1000, 1100)
    okButton = pyautogui.locateCenterOnScreen(
            "./screenshots/ok.png",
            confidence=0.75,
        )
    if okButton != None:
        x, y = okButton
        mouseMoveTo(x=x, y=y)
        sleep(200, 300)
        pydirectinput.click(button="left")
        sleep(200, 300)
    mouseMoveTo(x=1700, y=910)
    sleep(500, 600)
    pydirectinput.click(button="left")
    sleep(15000, 16000)
    

def buyAuctionFirstFav():
    while True:
        # buying first fav item for 2g or under
        gold2 = pyautogui.locateCenterOnScreen(
            "./screenshots/gold2.png", region=(934, 415, 36, 20), confidence=0.9
        )
        gold1 = pyautogui.locateCenterOnScreen(
            "./screenshots/gold1.png", region=(934, 415, 36, 20), confidence=0.9
        )
        if gold1 != None:
            # click price input
            mouseMoveTo(x=977, y=504)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(700, 800)
            pydirectinput.press("9")
            sleep(220, 230)
            pydirectinput.press("9")
            sleep(220, 230)
            pydirectinput.press("9")
            sleep(220, 230)
            # click buy
            mouseMoveTo(x=956, y=726)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(700, 800)
            # click ok
            mouseMoveTo(x=959, y=562)
            sleep(1500, 1600)
            pydirectinput.click(button="left")
            sleep(3000, 3500)

            # click mail
            mouseMoveTo(x=304, y=144)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(1700, 1800)
            # click first mail
            mouseMoveTo(x=212, y=219)
            sleep(700, 800)
            pydirectinput.click(button="left")
            # click accept
            mouseMoveTo(x=440, y=515)
            sleep(1700, 1800)
            pydirectinput.click(button="left")
            # click delete
            mouseMoveTo(x=518, y=515)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(1000, 1500)
            # click
            mouseMoveTo(x=1320, y=355)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(700, 800)
            # click bottom right buy
            mouseMoveTo(x=1416, y=828)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(500, 600)
        else:
            # click refresh
            mouseMoveTo(x=1062, y=298)
            sleep(700, 800)
            pydirectinput.click(button="left")
            sleep(700, 800)


def mouseMoveTo(**kwargs):
    x = kwargs["x"]
    y = kwargs["y"]
    pydirectinput.moveTo(x=x, y=y)
    pydirectinput.moveTo(x=x, y=y)


def goInvisible():
    # pydirectinput.press(config["friends"])
    # sleep(2290, 2420)
    # mouseMoveTo(x=1836, y=384)
    # sleep(700, 800)
    # pydirectinput.click(x=1836, y=384, button="left")
    # sleep(500, 600)
    # mouseMoveTo(x=1836, y=448)
    # sleep(700, 800)
    # pydirectinput.click(x=1836, y=448, button="left")
    # sleep(1500, 1600)
    # pydirectinput.press("esc")
    # sleep(1500, 1600)
    return


def goOnline():
    # pydirectinput.press(config["friends"])
    # sleep(2290, 2420)
    # mouseMoveTo(x=1836, y=384)
    # sleep(700, 800)
    # pydirectinput.click(x=1836, y=384, button="left")
    # sleep(500, 600)
    # mouseMoveTo(x=1836, y=407)
    # sleep(700, 800)
    # pydirectinput.click(x=1836, y=448, button="left")
    # sleep(1500, 1600)
    # pydirectinput.press("esc")
    # sleep(1500, 1600)
    return


def waitForCityLoaded():
    while True:
        inTown = pyautogui.locateCenterOnScreen(
            "./screenshots/inTown.png",
            confidence=0.75,
            region=(1870, 133, 25, 30),
        )
        if inTown != None:
            print("city loaded")
            states["status"] = "inCity"
            break
        sleep(5000, 6000)

def cardEater():
    #consume cards
    for card in ["white", "green", "blue", "purple"]:
        while True:
            location = pyautogui.locateCenterOnScreen(
                "./screenshots/"+card+"Card.png",
                confidence=0.75)
            if location == None:
                break
            else:
                x, y = location
                mouseMoveTo(x=x, y=y)
                sleep(200, 400)
                pydirectinput.click(x=x, y=y, button="right")
                pydirectinput.click(x=x, y=y, button="right")
                sleep(700, 1100)

def cleanInventory():
    # sleep(1000,1500)
    # pydirectinput.press("i")
    # sleep(1000,2000)
    #consume cards
    # cardEater()
    
    #dismantle
    # x,y = (1557, 740)
    # mouseMoveTo(x=x, y=y)
    # sleep(300,400)
    # pydirectinput.click(x, y, button = "left")
    # sleep(500,900)
    # pydirectinput.click(x=1210, y=730, button = "left")
    # sleep(500, 800)
    # pydirectinput.click(x=1410, y=730, button = "left")
    # sleep(500, 800)
    # pydirectinput.click(x=1225, y=570, button = "left")
    # sleep(500, 800)
    
    #deposit
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
    
    #compact
    # mouseMoveTo(x=1108, y=339)
    # sleep(2500, 2600)
    # pydirectinput.click(1108, 339, button="left")
    # sleep(2500, 2600)
    
    #exit
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

if __name__ == "__main__":
    states = newStates.copy()
    main()
