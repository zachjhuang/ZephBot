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


def load_skills():
    spec = importlib.util.spec_from_file_location("skills", "configs/skills.py")
    skills_module = importlib.util.module_from_spec(spec)
    sys.modules["skills"] = skills_module
    spec.loader.exec_module(skills_module)
    return skills_module.skills


skills = load_skills()


def save_skills():
    with open("configs/skills.py", "w") as f:
        f.write("skills = " + repr(skills))

    ui.notify("Skills saved successfully!")


def add_skill():
    new_entry = {
        "key": None,
        "skillType": "Normal",
        "castTime": None,
        "holdTime": None,
    }
    skills[SkillManager.curr_class].append(new_entry)
    skills_layout.refresh()


def reload_skills():
    global skills
    skills = load_skills()
    skills_layout.refresh()


class SkillManager:
    curr_class = ""
    target_keybind = ""

    @classmethod
    def delete_skill(cls):
        global skills
        skills[cls.curr_class] = [
            skill
            for skill in skills[cls.curr_class]
            if skill["key"] != cls.target_keybind
        ]
        skills_layout.refresh()


def class_select():
    ui.select(
        options=CLASS_NAMES,
        label="Class",
        with_input=True,
        on_change=skills_layout.refresh,
    ).bind_value(SkillManager, "curr_class").classes("w-11/12 m-auto")


@ui.refreshable
def skills_layout():
    if not SkillManager.curr_class:
        ui.label(text="No class selected.")
        return
    elif SkillManager.curr_class in skills.keys():
        with ui.row().classes("gap-5"):
            for i in range(len(skills[SkillManager.curr_class])):
                with ui.card().classes("w-56 m-auto") as card:
                    with ui.row():
                        ui.input(label="Key").bind_value(
                            skills[SkillManager.curr_class][i], "key"
                        ).classes("w-1/6 m-auto")
                        ui.select(
                            options={"awakening": "Awakening", "normal": "Normal"},
                            label="Skill Type",
                            with_input=True,
                        ).bind_value(
                            skills[SkillManager.curr_class][i], "skillType"
                        ).classes(
                            "w-3/6 m-auto"
                        )
                    ui.label(text="Hold Time (ms)")
                    ui.slider(
                        min=None,
                        max=3000,
                    ).bind_value(
                        skills[SkillManager.curr_class][i], "holdTime"
                    ).classes("w-11/12 m-auto").props("label-always")
                    ui.label(text="Cast Time (ms)")
                    ui.slider(
                        min=None,
                        max=5000,
                    ).bind_value(
                        skills[SkillManager.curr_class][i], "castTime"
                    ).classes("w-11/12 m-auto").props("label-always")
    else:
        ui.label(text="Skills for class not found. Click the + in the bottom left corner to add a skill.")

    with ui.page_sticky(position="bottom-left", x_offset=20, y_offset=20):
        ui.button(on_click=add_skill, icon="add").props("fab")


with ui.dialog() as confirmation_dialog, ui.card():
    ui.label("Enter the keybind of the skill you wish to delete.")

    ui.input("Skill Keybind").bind_value_to(SkillManager, "target_keybind")
    with ui.row().style("justify-content: flex-end;"):
        ui.button(
            "Confirm",
            on_click=lambda: [
                SkillManager.delete_skill(),
                confirmation_dialog.close(),
            ],
        ).props("color=red")
        ui.button("Cancel", on_click=confirmation_dialog.close).props("color=grey")


def skills_page():
    class_select()
    with ui.row():
        ui.button("Save Skills", on_click=save_skills)
        ui.button("Reload Skills", on_click=lambda: reload_skills())
        ui.button("Delete Skill", on_click=confirmation_dialog.open).props("color=red")
    skills_layout()
