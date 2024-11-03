# pylint: disable=missing-module-docstring
import yaml
from nicegui import ui

from modules.utilities import get_config

# pylint: disable=global-statement
config = get_config()


def save_configs():
    """
    Saves the application's config instance to file.
    """
    with open("configs/config.yaml", 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)
    ui.notify("configs saved successfully!")
    configs_layout.refresh()


def reload_configs():
    """
    Overwrites the application's config instance with the one saved on file.
    """
    global config
    config = get_config()
    configs_layout.refresh()


@ui.refreshable
def configs_layout():
    """
    Rows of config descriptions and editable fields.
    """
    with ui.element().classes('w-11/12 divide-y-2 m-auto'):
        system_settings_header()
        system_settings()
        
        keybinds_header()
        basic_control_keybinds()
        menu_keybinds()
        emote_slot_keybinds()

def system_settings_header():
    """
    Text header for system settings section.
    """
    with ui.row().classes("m-auto h-16"):
        ui.label(text="System").classes("w-1/6 m-auto text-3xl font-bold")
        ui.space()

def keybinds_header():
    """
    Text header for keybinds section.
    """
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Keybinds").classes("w-1/6 m-auto text-3xl font-bold")
        ui.space()

def system_settings() -> None:
    """
    Config elements for script and system functionality.
    """
    with ui.row().classes("m-auto h-16"):
        ui.label(text="The hour of the day that daily reset occurs (24 hour local time).").classes("w-4/6 m-auto")
        ui.space()
        ui.select(options=list(range(24)), label=None).bind_value(config, "resetHour").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Enable if the script is being run on a Geforce Now client (HIGHLY RECOMMENDED)").classes("w-4/6 m-auto")
        ui.space()
        ui.switch().bind_value(config, "GFN").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Enable if the script is being run on a low end native client (NOT RECOMMENDED)").classes("w-4/6 m-auto")
        ui.space()
        ui.switch().bind_value(config, "performance").classes("w-1/12 m-auto")

def basic_control_keybinds() -> None:
    """
    Config elements for basic control keybinds (move, interact, etc.)
    """
    with ui.row().classes("m-auto h-16"):
        ui.label(text="The mouse button used to move.").classes("w-4/6 m-auto")
        ui.space()
        ui.toggle(options={"left": "Left", "right": "Right"}).bind_value(config, "move").classes("m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Interact").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "interact").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Basic Attack").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "meleeAttack").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Specialty 1").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "specialty1").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Specialty 2").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "specialty2").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Health Potion").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "healthPot").classes("w-1/12 m-auto")

def menu_keybinds() -> None:
    """
    Config elements for menu keybinds.
    """
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Content Menu").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "content").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Bifrost Menu").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "bifrost").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Pet Menu").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "pet").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Guild Menu").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "guild").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Unas Menu").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "unas").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Default Combat Preset").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "defaultCombatPreset").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Una Task Combat Preset").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "unaTaskCombatPreset").classes("w-1/12 m-auto")

def emote_slot_keybinds() -> None:
    """
    Config elements for emote slots for daily una tasks.
    """
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Examine the Brilliant Spring Emote Slot").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "hesteraGardenEmoteSlot").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Preserve the Ancient Relic Pose Slot").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "southKurzanPoseSlot").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Befriend the Hiliaberry Thief Emote Slot").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "prehiliaEmoteSlot").classes("w-1/12 m-auto")
    with ui.row().classes("m-auto h-16"):
        ui.label(text="Writer's Life: Fan Meeting Emote Slot").classes("w-4/6 m-auto")
        ui.space()
        ui.input().bind_value(config, "writersLifeEmoteSlot").classes("w-1/12 m-auto")


def configs_page() -> None:
    """
    Full page for config tab.
    """
    with ui.row():
        ui.button("Save configs", on_click=save_configs)
        ui.button("Reload configs", on_click=reload_configs)
    configs_layout()
