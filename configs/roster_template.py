"""
Currently supported classes for chaos dungeon are:
    - 'aeromancer' (Drizzle)
    - 'slayer' (Predator)
    - 'artist' (Recurrence)
    - 'deathblade' (Remaining Energy)
    - 'arcana' (Emperor)
    - 'scrapper' (Taijutsu)
    - all other classes which do not rely on pressing specialty 
      (Reflux 'sorceress', Perfect Suppression 'shadowhunter', Hunger 'reaper', etc.)

If a class relies on pressing specialty and is not specifically listed above,
clear speed may be less than average. Please submit an issue on GitHub to suggest 
class implementations.

'chaosItemLevel' must be a valid chaos dungeon item level
'unas' is a string of up to three different task names,
separated by spaces.
Possible tasks include
    - 'lopang' (Shushire, Arthetine, Vern, silver)
    - 'mokomoko' (How to Succeed at Length, leapstones)
    - 'bleakNightFog' (Bleak Night Fog, leapstones)
    - 'hesteraGarden (Examine the Brilliant Spring, leapstones)
    - 'sageTower' (Finding Valuable Resources, leapstones)
    - 'southKurzan' (Preserve the ancient relic, leapstones)
    - 'prehilia' (Befriend the Hiliaberry Thief!, shards)
    - 'ghostStory (Birth of a Ghost Story, shards)
    - 'writersLife' (Writer's Life: Fan Meeting, shards)

MUST SET UP BIFROSTS ACCORDING TO EXAMPLE IN /unaexamples
MEMO FOR BIFROST MUST BE THE EXACT STRING (CASE SENSITIVE)
"""

roster = [
    {
        "index": 0,
        "class": "souleater",
        "chaosItemLevel": None,
        "unas": "prehilia writersLife ghostStory",
        "guildDonation": True
    },
    {
        "index": 1,
        "class": "aeromancer",
        "chaosItemLevel": None,
        "unas": None,
        "guildDonation": True
    },
        {
        "index": 2,
        "class": "sorceress",
        "chaosItemLevel": None,
        "unas": None,
        "guildDonation": True
    },
    {
        "index": 3,
        "class": "gunslinger",
        "chaosItemLevel": 1610,
        "unas": "hesteraGarden sageTower southKurzan",
        "guildDonation": True
    },
    {
        "index": 4,
        "class": "glaivier",
        "chaosItemLevel": 1600,
        "unas": "hesteraGarden sageTower southKurzan",
        "guildDonation": True
    },
    {
        "index": 5,
        "class": "artist",
        "chaosItemLevel": 1600,
        "unas": "hesteraGarden sageTower southKurzan",
        "guildDonation": True
    },
    {
        "index": 6,
        "class": "deathblade",
        "chaosItemLevel": 1560,
        "unas": "lopang",
        "guildDonation": True
    },
    {
        "index": 7,
        "class": "reaper",
        "chaosItemLevel": 1540,
        "unas": "lopang",
        "guildDonation": True
    },
    {
        "index": 8,
        "class": "arcana",
        "chaosItemLevel": 1540,
        "unas": "lopang",
        "guildDonation": True
    },
    {
        "index": 9,
        "class": "slayer",
        "chaosItemLevel": 1540,
        "unas": "lopang",
        "guildDonation": True
    },
    {
        "index": 10,
        "class": "scrapper",
        "chaosItemLevel": 1540,
        "unas": "lopang",
        "guildDonation": True
    },
    {
        "index": 11,
        "class": "shadowhunter",
        "chaosItemLevel": 1540,
        "unas": "lopang",
        "guildDonation": True
    },
    {
        "index": 12,
        "class": "souleater",
        "chaosItemLevel": 1540,
        "unas": "bleakNightFog",
        "guildDonation": True
    },
]