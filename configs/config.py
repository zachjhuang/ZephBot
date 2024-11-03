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
    Please set up bifrost menu according to the examples bifrost_ex.png,
    depending on your Una's tasks.
    
    For Lopang Unas:
    Register exact location to be right in front of the NPC machine in the bottom right. (lopangNPC.png)
    Set the Shushire/Arthetine/Vern Lopang quests as the ONLY 3 favourite quests

    For leapstone Unas:
    Follow examples in characters_template.py for characters.py
    If running Hestera Garden, please configure "hesteraGardenCombatPreset" and "hesteraGardenEmoteSlot".
    If running Mokomoko Island, please register bifrost when bottom left of screen matches mokomokoUna_ex.png
    If running Sage's Tower, please register bifrost between two POI nearest 
    the hand-in NPC as shown in sageTowerUna_ex.png
    Set the leapstone quests as your ONLY 3 favourite quests
"""

config = {
    "resetHour": 6,
    "GFN": True,  # set True for Geforce Now users
    "performance": False,  # set True for lower-end PCs

    # keybinds
    "interact": "g",  # change this if you have binded it to something else eg.mouse button
    "move": "left",  # or "right"
    "meleeAttack": "c",
    "specialty1": "z",
    "specialty2": "`",
    "healthPot": "f1",  # important to put your regen potion on this button
    "friends": "u",
    # menus
    "content": "alt q",
    "bifrost": "alt w",
    "pet": "alt f",
    "guild": "alt a",
    "unas": "alt r",

    "defaultCombatPreset": "ctrl q",
    "unaTaskCombatPreset": "ctrl r",
    
    "hesteraGardenEmoteSlot": "8",
    "southKurzanPoseSlot": "7",
    "prehiliaEmoteSlot": "9",
    "writersLifeEmoteSlot": "9",

    "invisible": False,
    "healthPotAtPercent": 0.20,
    "auraRepair": True,  # True if you have aura, if not then for non-aura users: MUST have your character parked near a repairer in city before starting the script
    # You might not want to touch anything below, because I assume you have your game setup same as mine :) otherwise something might not work properly!
    "confidenceForGFN": 0.9,
    "timeLimit": 450, 
    "blackScreenTimeLimit": 50000,  # if stuck in nothing for this amount of time, alt f4 game, restart and resume.
}
