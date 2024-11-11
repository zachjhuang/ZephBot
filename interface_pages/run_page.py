# credit to FabianGoessling for console output redirection to log element
# https://github.com/zauberzeug/nicegui/discussions/1663

import asyncio
import os
import sys
from io import StringIO
from logging import StreamHandler, getLogger

import keyboard
from nicegui import app, ui

import modules.start as start

logger = getLogger(__name__)
logger.setLevel("DEBUG")

options = {
    "do_chaos": False,
    "do_kurzan_front": False,
    "do_unas": False,
    "do_guild": False,
}

script_button = {"not running": True}

delay = {"duration": 0}


def toggle(x, v):
    x["not running"] = v


async def controller():
    script_task = asyncio.create_task(start.start_script(options=options))
    keyboard.add_hotkey("ctrl+page down", script_task.cancel)
    while True:
        try:
            await script_task
            break
        except asyncio.CancelledError:
            print("controller confirmed cancel")
            break


async def start_script():
    """Called after button click"""
    while True:
        if not script_button["not running"]:
            await asyncio.sleep(delay["duration"])
            await controller()
            script_button["not running"] = True
        await asyncio.sleep(1)


async def start_stream(log):
    """Start a 'stream' of console outputs."""
    # Create buffer
    console_output_buffer = StringIO()
    # Standard ouput like a print
    sys.stdout = console_output_buffer
    # Errors/Exceptions
    sys.stderr = console_output_buffer
    # Logmessages
    stream_handler = StreamHandler(console_output_buffer)
    stream_handler.setLevel("DEBUG")
    logger.addHandler(stream_handler)
    while 1:
        await asyncio.sleep(1)  # need to update ui
        # Push the log component and reset the buffer
        log.push(console_output_buffer.getvalue())
        console_output_buffer.truncate(0)
        console_output_buffer.seek(0)


def run_page():
    with ui.row(wrap=False).classes("w-full"):
        with ui.column().classes("w-1/6"):
            ui.switch("Chaos").bind_value(options, "do_chaos")
            ui.switch("Unas").bind_value(options, "do_unas")
            ui.switch("Kurzan Front (WIP)").bind_value(options, "do_kurzan_front")
            ui.switch("Guild").bind_value(options, "do_guild")
            ui.button(
                "Start script", on_click=lambda: toggle(script_button, False)
            ).bind_enabled(script_button, "not running")
            ui.label("Delay")
            ui.slider(min=0, max=18000, step=100, value=0).bind_value(
                delay, "duration"
            ).props("label-always")
        log = ui.log().classes("w-full").style("height: 500px")
    app.on_startup(start_stream(log))
    app.on_startup(start_script())
