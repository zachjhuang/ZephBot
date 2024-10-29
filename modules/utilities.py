import random
import time

import pyautogui
import pydirectinput


class RestartException(Exception):
    pass


class ResetException(Exception):
    pass


class TimeoutException(Exception):
    pass


def random_sleep(min, max) -> None:
    """Sleeps for a random amount of time (in ms) in the given range."""
    duration = random.randint(min, max) / 1000.0
    if duration < 0:
        return
    time.sleep(duration)


def left_click_at_position(position: tuple[int, int]) -> None:
    """
    Move mouse to position and left click.
    
    Args:
        position: (x, y) coordinate 
    """
    pydirectinput.moveTo(x=position[0], y=position[1])
    random_sleep(200, 250)
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
    region: None | tuple = None,
    grayscale: bool = False,
) -> None | tuple:
    """Return center of image as tuple if found on screen, otherwise return None."""
    try:
        return pyautogui.locateCenterOnScreen(
            image_path, confidence=confidence, region=region, grayscale=grayscale
        )
    except pyautogui.ImageNotFoundException:
        return None


def find_and_click_image(
    name: str, region: None | tuple = None, confidence: float = 0.8
) -> None:
    """If image found on screen, click on center of image."""
    image_position = find_image_center(
        f"./screenshots/{name}.png", region=region, confidence=confidence
    )
    if image_position is not None:
        left_click_at_position(image_position)
