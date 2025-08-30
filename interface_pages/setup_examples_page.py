from nicegui import ui

###













# DEPRECATED
















###

def setup_examples_page() -> None:
    with ui.scroll_area().classes("h-20 items-center"):
        with ui.tabs() as tabs:
            ui.tab("Bifrost Menu")
            ui.tab("Special Delivery (Lopang)")
            ui.tab("Bleak Night Fog")
            ui.tab("How to Succeed at Length")
            ui.tab("Examine the Brilliant Spring")
            ui.tab("Finding Valuable Resources")
            ui.tab("Preserve the ancient relic")
            ui.tab("Befriend the Hiliaberry Thief")
            ui.tab("Writer's Life: Fan Meeting")
            ui.tab("Birth of a Ghost Story")

    with ui.tab_panels(tabs, value="Bifrost Menu").classes("w-full"):
        with ui.tab_panel("Bifrost Menu"):
            bifrost_menu()
        with ui.tab_panel("Special Delivery (Lopang)"):
            lopang_tab()
        with ui.tab_panel("Bleak Night Fog"):
            ui.label("Set the 'bleakNightFog' bifrost in the interact circle.")
        with ui.tab_panel("How to Succeed at Length"):
            ui.label(
                "Align the bottom left of the screen as shown and set the 'mokomoko' bifrost:"
            )
            ui.image("./una_examples/mokomokoUna_ex.png").classes("w-96")
        with ui.tab_panel("Examine the Brilliant Spring"):
            ui.label(
                "Set the 'hesteraGarden' bifrost in the interact circle, and set emote keybind in CONFIG tab."
            )
        with ui.tab_panel("Finding Valuable Resources"):
            ui.label(
                "Set the 'sageTower' bifrost between the two interact points here."
            )
            ui.image("./una_examples/sageTowerUna_ex.png").classes("w-96")
        with ui.tab_panel("Preserve the ancient relic"):
            ui.label(
                "Set the 'southKurzan' bifrost at the top of the interact circle, and set pose keybind in CONFIG tab."
            )
        with ui.tab_panel("Befriend the Hiliaberry Thief"):
            ui.label(
                "Set the 'prehilia' bifrost in the interact circle close to the turn-in NPC, and set emote keybind in CONFIG tab."
            )
            ui.image("./una_examples/prehiliaUna_ex.png").classes("w-96")
        with ui.tab_panel("Writer's Life: Fan Meeting"):
            ui.label(
                "Set the 'writersLife' bifrost in center of the target image, and set emote keybind in CONFIG tab."
            )
            ui.image("./una_examples/writersLifeUna_ex.png").classes("w-96")
        with ui.tab_panel("Birth of a Ghost Story"):
            ui.label(
                "Set the 'ghostStory' bifrost inbetween the three interact points."
            )
            ui.image("./una_examples/ghostStoryUna_ex.png").classes("w-96")


def lopang_tab():
    ui.label("Set 'lopangIsland' bifrost here:")
    ui.image("./una_examples/lopang.png").classes("w-72")
    ui.label(
        "Set 'lopangShushire', 'lopangArthetine', and 'lopangVern' bifrost next to the respective turn-in NPC."
    )
    ui.label("Make sure that bifrosting is not obstructed.")


def bifrost_menu():
    ui.label("Make sure that the memos are exactly the same.")
    with ui.row():
        ui.image("./una_examples/bifrost_ex3.png").classes("w-96")
        ui.image("./una_examples/bifrost_ex2.png").classes("w-96")
        ui.image("./una_examples/bifrost_ex1.png").classes("w-96")
