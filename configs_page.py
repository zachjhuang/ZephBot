from nicegui import ui
import sys

import importlib.util


def load_configs():
    spec = importlib.util.spec_from_file_location("configs", "configs/config.py")
    configs_module = importlib.util.module_from_spec(spec)
    sys.modules["configs"] = configs_module
    spec.loader.exec_module(configs_module)
    return configs_module.config


configs = load_configs()


def save_configs():
    with open("configs/configs.py", "w") as f:
        f.write("configs = " + repr(configs))

    ui.notify("configs saved successfully!")


def reload_configs():
    global configs
    configs = load_configs()
    configs_layout.refresh()


@ui.refreshable
def configs_layout():
    with ui.element().classes('w-11/12 divide-y-2 m-auto'):
        with ui.row().classes("m-auto h-16"):
            ui.label(text="System").classes("w-1/6 m-auto text-3xl font-bold")
            ui.space()
        with ui.row().classes("m-auto h-16"):
            ui.label(text="The hour of the day that daily reset occurs (24 hour local time).").classes("w-4/6 m-auto")
            ui.space()
            ui.select(options=list(range(24)), label=None).bind_value(configs, "resetHour").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Enable if the script is being run on a Geforce Now client (HIGHLY RECOMMENDED)").classes("w-4/6 m-auto")
            ui.space()
            ui.switch().bind_value(configs, "GFN").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Enable if the script is being run on a low end native client (NOT RECOMMENDED)").classes("w-4/6 m-auto")
            ui.space()
            ui.switch().bind_value(configs, "performance").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Keybinds").classes("w-1/6 m-auto text-3xl font-bold")
            ui.space()
        with ui.row().classes("m-auto h-16"):
            ui.label(text="The mouse button used to move.").classes("w-4/6 m-auto")
            ui.space()
            ui.toggle(options={"left": "Left", "right": "Right"}).bind_value(configs, "move").classes("w-1/6 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Interact").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "interact").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Basic Attack").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "meleeAttack").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Specialty 1").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "specialty1").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Specialty 2").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "specialty2").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Health Potion").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "healthPot").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Content Menu").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "content").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Bifrost Menu").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "bifrost").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Pet Menu").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "pet").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Guild Menu").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "guild").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Unas Menu").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "unas").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Default Combat Preset").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "defaultCombatPreset").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Una Task Combat Preset").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "unaTaskCombatPreset").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Examine the Brilliant Spring Emote Slot").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "hesteraGardenEmoteSlot").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Preserve the Ancient Relic Pose Slot").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "southKurzanPoseSlot").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Befriend the Hiliaberry Thief Emote Slot").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "prehiliaEmoteSlot").classes("w-1/12 m-auto")
        with ui.row().classes("m-auto h-16"):
            ui.label(text="Writer's Life: Fan Meeting Emote Slot").classes("w-4/6 m-auto")
            ui.space()
            ui.input().bind_value(configs, "writersLifeEmoteSlot").classes("w-1/12 m-auto")


def configs_page():
    with ui.row():
        ui.button("Save configs", on_click=save_configs)
        ui.button("Reload configs", on_click=lambda: reload_configs())
    configs_layout()
