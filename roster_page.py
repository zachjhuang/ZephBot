from nicegui import ui
import sys

import importlib.util

CLASS_NAMES = {
    "aeromancer": "Aeromancer",
    "artist": "Artist",
    "berserker": "Berserker",
    "destroyer": "Destroyer",
    "gunlancer": "Gunlancer",
    "paladin": "Paladin",
    "slayer": "Slayer",
    "breaker": "Breaker",
    "glaivier": "Glaivier",
    "scrapper": "Scrapper",
    "soulfist": "Soulfist",
    "striker": "Striker",
    "wardancer": "Wardancer",
    "artillerist": "Artillerist",
    "deadeye": "Deadeye",
    "gunslinger": "Gunslinger",
    "machinist": "Machinist",
    "sharpshooter": "Sharpshooter",
    "arcanist": "Arcanist",
    "bard": "Bard",
    "sorceress": "Sorceress",
    "summoner": "Summoner",
    "deathblade": "Deathblade",
    "reaper": "Reaper",
    "shadowhunter": "Shadowhunter",
    "souleater": "Souleater",
}

DUNGEON_ITEM_LEVELS = [
    1660,
    1640,
    1610,
    1600,
    1580,
    1560,
    1540,
    1520,
    1490,
    1475,
    1445,
    1415,
    1400,
    1385,
    1370,
    1355,
    1340,
    1325,
    1295,
    1100,
]

UNA_TASK_NAMES = {
    "lopang": "Special Delivery (Lopang)",
    "mokomoko": "How to Succeed at Length",
    "bleakNightFog": "Bleak Night Fog",
    "hesteraGarden": "Examine the Brilliant Spring",
    "sageTower": "Finding Valuable Resources",
    "southKurzan": "Preserve the ancient relic",
    "prehilia": "Befriend the Hiliaberry Thief!",
    "ghostStory": "Birth of a Ghost Story",
    "writersLife": "Writer's Life: Fan Meeting",
}


def load_roster():
    spec = importlib.util.spec_from_file_location("roster", "configs/roster.py")
    roster_module = importlib.util.module_from_spec(spec)
    sys.modules["roster"] = roster_module
    spec.loader.exec_module(roster_module)
    return roster_module.roster


roster = load_roster()


def save_roster():
    global roster
    roster = sorted(roster, key=lambda char: char["index"])
    with open("configs/roster.py", "w") as f:
        f.write("roster = " + repr(roster))

    ui.notify("Roster saved successfully!")
    roster_layout.refresh()

def add_char_to_roster():
    global roster
    new_entry = {
        "index": len(roster),
        "class": None,
        "chaosItemLevel": None,
        "unas": [],
        "guildDonation": True,
    }
    roster.append(new_entry)
    roster_layout.refresh()


def reload_roster():
    global roster
    roster = load_roster()
    roster_layout.refresh()


@ui.refreshable
def roster_layout():
    with ui.grid(columns=3).classes("gap-5"):
        for i in range(len(roster)):
            character_card(roster[i])

        with ui.card():
            ui.button("Add new character", on_click=add_char_to_roster).style(
                "margin: auto"
            )


def character_card(char: dict):
    with ui.card().classes("w-auto m-auto") as card:
        with ui.row().classes("w-11/12 m-auto"):
            ui.input(label="Name").bind_value(char, "name").classes("w-8/12 m-auto")
            ui.select(options=list(range(len(roster))), label="#").bind_value(char, "index").classes("w-3/12 m-auto")
        ui.select(options=CLASS_NAMES, label="Class", with_input=True).bind_value(
            char, "class"
        ).classes("w-11/12 m-auto")
        ui.select(
            options=DUNGEON_ITEM_LEVELS,
            label="Dungeon Item Level",
            with_input=True,
            clearable=True,
        ).bind_value(char, "chaosItemLevel").classes("w-11/12 m-auto")
        ui.select(
            options=UNA_TASK_NAMES, label="Unas", with_input=True, multiple=True
        ).bind_value(char, "unas").classes("w-11/12 m-auto").props("use-chips")
        ui.switch(
            text="Guild Donation",
        ).bind_value(
            char, "guildDonation"
        ).classes("m-auto")


class CharacterDeleter:
    target = ""

    @classmethod
    def delete_character(cls):
        global roster
        roster = [char for char in roster if char["name"] != cls.target]
        roster_layout.refresh()


with ui.dialog() as delete_character_popup, ui.card():
    ui.label("Enter the character name you wish to delete.")

    ui.input("Character Name").bind_value_to(CharacterDeleter, "target")
    with ui.row().style("justify-content: flex-end;"):
        ui.button(
            "Confirm",
            on_click=lambda: [
                CharacterDeleter.delete_character(),
                delete_character_popup.close(),
            ],
        ).props("color=red")
        ui.button("Cancel", on_click=delete_character_popup.close).props("color=grey")


def roster_page():
    with ui.row():
        ui.button("Save Roster", on_click=save_roster)
        ui.button("Reload Roster", on_click=lambda: reload_roster())
        ui.button("Delete Character", on_click=delete_character_popup.open).props(
            "color=red"
        )

    roster_layout()
