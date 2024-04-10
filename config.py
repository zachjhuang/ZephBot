# python .\bot.py --lunshua

"""
    IMPORTANT #1:
    Please change game settings to EXACTLY these numbers:
    desktop resolution: 1920x1080
    In-game Video settings:

    Resolution: 1920x1080
    Screen: Borderless
    Force 21:9 Aspect Ratio checked
    In-game Gameplay -> Controls and Display -> HUD size: 110%
    minimap transparency (at top right corner): 100%
    minimap zoom-in (at top right corner): 65%

    IMPORTANT #2: 
    config must be set up correctly in order for the bot to work properly on your machine.
    Refer to the inline comments below:

    For Lopang enjoyers: https://github.com/any-other-guy/LostArk-Endless-Chaos/issues/15
    Set your first bifrost point to be at lopang island.
    Exact location to be right in front of the NPC machine which stands farthest to the entrance.
    Then set your 2/4/5 (because i dont have no3 unlocked) bifrost location to be right in front of those three lopang quest hand-in NPCs.
    Set your lopang quests as your ONLY 3 favourite quests
"""
from characters import characters

config = {
    "mainCharacter": 4,  # must be in number 0 to 5 (0 is the first character)
    "resetHour": 5,
    "GFN": True,  # set True for Geforce Now users
    "enableMultiCharacterMode": True,  # this is lit
    "enableLopang": True,  # NOTE: you need to setup bifrost locations properly for this, at very specific locations. Look up ^
    "enableGuildDonation": True,  # please make sure all your characters have a guild
    "enableRapport": False,  # NOTE: you need to setup bifrost no3 infront of a rapport NPC
    "floor3Mode": False,  # only enable if you ONLY want to run infinite floor3 clearing
    # Setup your characters below:
    # can setup UP TO 18(0 to 17) characters for daily chaos/lopang/guild stuff
    # however your main must be in character 0 to 5 (just for re-connect back after disconnection happens)
    # ilvl-endless is the dungeon which you want to run infinitely
    # ilvl-aor is the daily aura of resonance dungeon you only want to run TWICE per day
    # IMPORTANT: dungeon ilvl choices are only limited to 1475, 1445, 1370, 1110 for now. I will add more later when brel comes out
    "characters": characters,
    "performance": False,  # set True for lower-end PCs


    # keybinds
    "interact": "g",  # change this if you have binded it to something else eg.mouse button
    "move": "left",  # or "right"
    "blink": "space",
    "meleeAttack": "c",
    "awakening": "v",
    "specialty1": "z",
    "specialty2": "`",
    "healthPot": "f1",  # important to put your regen potion on this button
    "friends": "u",
    # menus
    "chaos": "alt q",
    "bifrost": "alt w",
    "pet": "alt f",
    "guild": "alt a",
    "unas": "alt r",
    "map": "alt d",
    "defaultCombatPreset": "ctrl q",
    "hesteraGardenCombatPreset": "ctrl r",
    "hesteraGardenEmoteSlot": "8",



    "invisible": False,
    "healthPotAtPercent": 0.20,  # health threshold to trigger potion
    "useAwakening": True, # not checking this for now
    "useSpeciality1": True, # not checking this for now
    "useSpeciality2": True, # not checking this for now
    "auraRepair": True,  # True if you have aura, if not then for non-aura users: MUST have your character parked near a repairer in city before starting the script
    "shortcutEnterChaos": True,  # you want to use True
    "useHealthPot": True,  # you want to use True
    # You might not want to touch anything below, because I assume you have your game setup same as mine :) otherwise something might not work properly!
    "confidenceForGFN": 0.9,
    "regions": {
        "minimap": (1655, 170, 240, 200),  # (1700, 200, 125, 120)
        "abilities": (625, 779, 300, 155),
        "leaveMenu": (0, 154, 250, 300),
        "buffs": (625, 780, 300, 60),
        "center": (685, 280, 600, 420),
        "portal": (228, 230, 1370, 570),
        "specialty": (900, 800, 120, 940),
        "debuffs": (1040, 810, 90, 40),
    },
    "screenResolutionX": 1920,
    "screenResolutionY": 1080,
    "clickableAreaX": 500,
    "clickableAreaY": 250,
    "screenCenterX": 960,
    "screenCenterY": 540,
    "minimapCenterX": 1772,
    "minimapCenterY": 272,
    "timeLimit": 450000,  # to prevent unexpected amount of time spent in a chaos dungeon, a tiem limit is set here, will quit after this amount of seconds
    "timeLimitAor": 510000,  # to prevent unexpected amount of time spent in a chaos dungeon, a tiem limit is set here, will quit after this amount of seconds
    "blackScreenTimeLimit": 30000,  # if stuck in nothing for this amount of time, alt f4 game, restart and resume.
    "delayedStart": 1000,
    "portalPause": 700,
    "healthCheckX": 690,
    "healthCheckY": 854,
    "charSwitchX": 540,
    "charSwitchY": 683,
    "charPositionsAtCharSelect": [
        [500, 827],
        [681, 827],
        [874, 827],
        [1050, 827],
        [1237, 827],
        [1425, 827],
    ],
    "charPositions": [
        [760, 440], # 1
        [960, 440], # 2
        [1160, 440], # 3
        [760, 530], # 4
        [960, 530], # 5
        [1160, 530], # 6
        [760, 620], # 7
        [960, 620], # 8
        [1160, 620], # 9
        [760, 620], # 10
        [960, 620], # 11
        [1160, 620], # 12
        [760, 620], # 13
        [960, 620], # 14
        [1160, 620], # 15
    ],
    "charSelectConnectX": 1030,
    "charSelectConnectY": 684,
    "charSelectOkX": 920,
    "charSelectOkY": 590,
}
