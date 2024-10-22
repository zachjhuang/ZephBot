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

    IMPORTANT #3:
    Please set up bifrost menu according to the examples bifrost_ex.png in unaexamples
    depending on your Una's tasks.
"""

config = {
    "resetHour": 6,
    "GFN": True,  # set True for Geforce Now users
    "performance": False,  # set True for lower-end PCs

    # keybinds
    "interact": "g",  
    "move": "left",  # or "right"
    "blink": "space",
    "meleeAttack": "c",
    "awakening": "v",
    "specialty1": "z",
    "specialty2": "x",
    "healthPot": "f1",  # important to put your regen potion on this button
    "friends": "u",
    # menus
    "content": "alt q",
    "bifrost": "alt w",
    "pet": "p",
    "guild": "alt u",
    "unas": "alt j",

    "defaultCombatPreset": "ctrl q",
    "unaTaskCombatPreset": "ctrl r", # preset with the following 4 emotes

    "hesteraGardenEmoteSlot": "8", # /sit, /kneel, /drinktea
    "southKurzanPoseSlot": "7", # /PicturePose6
    "prehiliaEmoteSlot": "9", # /cute, /joy, /greet
    "writersLifeEmoteSlot": "9", # /cute, /wave, /polite

    "invisible": False,
    "healthPotAtPercent": 0.20,
    "auraRepair": True,  # True if you have aura, if not then for non-aura users: MUST have your character parked near a repairer in city before starting the script
    
    # DO NOT EDIT
    "confidenceForGFN": 0.9,
    "timeLimit": 450, 
    "blackScreenTimeLimit": 50000,  # if stuck in nothing for this amount of time, alt f4 game, restart and resume.
}
