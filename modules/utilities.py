"""
Provides various utilities for basic script functions, such as random sleeping, 
image recognition, screen navigation, and reading config files.
"""

import random
import time
import asyncio
from typing import Any

import yaml
import pyautogui
import pydirectinput


class RestartException(Exception):
    """Raised when normal gameplay is interrupted by disconnect, session limit, etc."""


class ResetException(Exception):
    """Raised when daily reset is detected."""


class TimeoutException(Exception):
    """Raised when time spent in a dungeon instance exceeds a limit"""


def random_sleep(min_duration, max_duration) -> None:
    """Sleeps for a random amount of time (in ms) in the given range."""
    duration = random.randint(min_duration, max_duration) / 1000.0
    if duration < 0:
        return
    time.sleep(duration)

async def rand_sleep(min_duration, max_duration) -> None:
    """Sleeps for a random amount of time (in ms) in the given range. Awaitable."""
    duration = random.randint(min_duration, max_duration) / 1000.0
    if duration < 0:
        return
    await asyncio.sleep(duration)


async def left_click_at_position(position: tuple[int, int]) -> None:
    """
    Move mouse to position and left click.

    Args:
        position: (x, y) coordinate
    """
    pydirectinput.moveTo(x=position[0], y=position[1])
    pydirectinput.moveTo(x=position[0], y=position[1])
    await rand_sleep(200, 250)
    pydirectinput.click(x=position[0], y=position[1], button="left")


def check_image_on_screen(
    image_path: str,
    confidence: float = 1.0,
    region: None | tuple = None,
    grayscale: bool = False,
) -> bool:
    """
    Checks if a specified image is located anywhere on screen.

    Returns true if image is found, False otherwise.
    """
    return find_image_center(image_path, confidence, region, grayscale) is not None


def find_image_center(
    image_path: str,
    confidence: float = 1.0,
    region: tuple[int, int, int, int] | None = None,
    grayscale: bool = False,
) -> None | tuple:
    """Return center of image as tuple if found on screen, otherwise return None."""
    try:
        return pyautogui.locateCenterOnScreen(
            image=image_path, confidence=confidence, region=region, grayscale=grayscale
        )
    except pyautogui.ImageNotFoundException:
        return None


async def find_and_click_image(
    name: str, region: None | tuple[int, int, int, int] = None, confidence: float = 0.8
) -> None:
    """If image found on screen, click on center of image."""
    image_position = find_image_center(
        f"./screenshots/{name}.png", region=region, confidence=confidence
    )
    if image_position is not None:
        await left_click_at_position(image_position)


def get_roster() -> list[dict]:
    """
    Gets the roster object by reading the corresponding .yaml file.

    Returns:
        list[dict]: The roster, represented by a list of characters (dictionaries).
    """
    with open("configs/roster.yaml", "r", encoding="utf-8") as file:
        roster = yaml.safe_load(file)
        if roster is None:
            return []
        return roster


def get_skills() -> dict[str, list[dict]]:
    """
    Get the skills object by reading the corresponding .yaml file.

    Returns:
        dict[str, list[dict]]: A skills object mapping class names to a list of skills.
    """
    with open("configs/skills.yaml", "r", encoding="utf-8") as file:
        skills = yaml.safe_load(file)
        if skills is None:
            return {}
        return skills


def get_config(key: str | None = None) -> dict[str, Any] | Any:
    """
    Get the configs object by reading the corresponding .yaml file.

    Args:
        key: Optional argument for the specific setting name to return. If no
            key is given then return the entire config object.
    Returns:
        A config object mapping setting names to values, or the value itself
            if the setting name is given as an argument.
    """
    with open("configs/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        if key is None:
            return config
        return config[key]
