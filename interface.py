from nicegui import ui
import nicegui.binding


from interface_pages.home_page import home_page
from interface_pages.roster_page import roster_page
from interface_pages.skills_page import skills_page
from interface_pages.configs_page import configs_page
from interface_pages.run_page import run_page
from interface_pages.setup_examples_page import setup_examples_page

nicegui.binding.MAX_PROPAGATION_TIME = 0.1

with ui.dialog() as dialog, ui.card():
    result = ui.markdown()

with ui.header().classes(replace="row items-center") as header:
    # ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
    #     "flat color=white"
    # )
    with ui.tabs() as tabs:
        ui.tab("Home")
        ui.tab("Roster")
        ui.tab("Skills")
        ui.tab("Config")
        ui.tab("Examples")
        ui.tab("Run")

# with ui.left_drawer(value=False).classes("bg-blue-100") as left_drawer:
#     ui.label("Side menu")

with ui.tab_panels(tabs, value="Home").classes("w-full"):
    with ui.tab_panel("Home"):
        home_page()
    with ui.tab_panel("Roster"):
        roster_page()
    with ui.tab_panel("Skills"):
        skills_page()
    with ui.tab_panel("Config"):
        configs_page()
    with ui.tab_panel("Examples"):
        setup_examples_page()
    with ui.tab_panel("Run"):
        run_page()

with ui.page_sticky(position="bottom-right", x_offset=20, y_offset=20):
    ui.button(on_click=ui.dark_mode().toggle, icon="dark_mode").props("fab")

ui.run(
    # native=True, # pywebview and pythonnet not supported in python 3.13
    title='ZephBot',
    favicon='favicon.ico',
    # window_size=(960, 540),
    fullscreen=False,
    dark=True,
    reload=False,
    uvicorn_reload_excludes="configs/*",
)
