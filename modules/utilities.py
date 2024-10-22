import random
import time

import pyautogui
import pydirectinput


class Position:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def shift(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


class RestartException(Exception):
    pass


class ResetException(Exception):
    pass


class TimeoutException(Exception):
    pass


def random_sleep(min, max) -> None:
    """Sleeps for a random amount of time (in ms) in the given range."""
    sleepTime = random.randint(min, max) / 1000.0
    if sleepTime < 0:
        return
    time.sleep(sleepTime)


def mouse_move_to(**kwargs):
    x = kwargs["x"]
    y = kwargs["y"]
    pydirectinput.moveTo(x=x, y=y)
    pydirectinput.moveTo(x=x, y=y)


def mouse_move_to_position(position: Position) -> None:
    """Move mouse to position."""
    pydirectinput.moveTo(x=position.x, y=position.y)


def left_click_at_position(position: Position) -> None:
    """Move mouse to position and left click."""
    mouse_move_to_position(position=position)
    random_sleep(200, 250)
    pydirectinput.click(x=position.x, y=position.y, button="left")


def check_image_on_screen(
    image_path: str,
    confidence: float = 1.0,
    region: None | tuple = None,
    grayscale: bool = False,
) -> bool:
    """Return True if image found on screen, otherwise return False."""
    return find_image_center(image_path, confidence, region, grayscale) is not None


def find_image_center(
    image_path: str,
    confidence: float = 1.0,
    region: None | tuple = None,
    grayscale: bool = False,
) -> None | tuple:
    """Return center of image as tuple if found on screen, otherwise return None."""
    try:
        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence, region=region, grayscale=grayscale
        )
        return location
    except pyautogui.ImageNotFoundException:
        return None


def find_image_center_position(
    image_path: str,
    confidence: float = 1.0,
    region: None | tuple = None,
    grayscale: bool = False,
) -> None | Position:
    """Return center of image as Position class if found on screen, otherwise return None."""
    try:
        location = pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence, region=region, grayscale=grayscale
        )
        if location is not None:
            x, y = location
            return Position(x, y)
        return None
    except pyautogui.ImageNotFoundException:
        return None


def find_and_click_image(
    name: str, region: None | tuple = None, confidence: float = 0.8
) -> None:
    """If image found on screen, click on center of image."""
    imagePosition = find_image_center_position(
        f"./screenshots/{name}.png", region=region, confidence=confidence
    )
    if imagePosition is not None:
        left_click_at_position(imagePosition)
