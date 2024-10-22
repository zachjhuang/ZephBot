import math
from collections import deque
from typing import Callable

import pyautogui

from configs.config import config
from modules.utilities import check_image_on_screen, find_image_center

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

MINIMAP_REGION = (1653, 172, 240, 200)
MINIMAP_CENTER_X = 1773
MINIMAP_REGION = (1653, 172, 240, 200)
MINIMAP_CENTER_X = 1773
MINIMAP_CENTER_Y = 272


class Minimap:
    """
    Class for locating icons on the minimap and
    translating them to in game coordinates.

    Attributes:
        targets (list[tuple[int, int]]): (x, y) coordinates of determined targets, relative to center of minimap. Ordered from least to most recently acquired targets.

        valid_coords (list[tuple[int, int]]): All (x, y) coordinates that are valid, relative to center of minimap.
    """

    def __init__(self) -> None:
        """
        Initializes Minimap object with `targets` and `valid_coords` set to an empty list.
        """
        self.targets: list[tuple[int, int]] = []
        self.valid_coords: list[tuple[int, int]] = []

    def update_valid_coords(self) -> None:
        """
        Searches minimap for valid (i.e. accessible) areas.

        Updates `valid_coords` attribute.
        """
        minimap = pyautogui.screenshot(region=MINIMAP_REGION)
        width, height = minimap.size
        self.valid_coords = []
        for x in range(width):
            for y in range(height):
                r, g, b = minimap.getpixel((x, y))
                if VALID_AREA_RGB_RANGE(r, g, b):
                    self.valid_coords.append((x - width / 2, y - height / 2))

    def find_closest_pixel(
        self, name: str, inColorRange: Callable[[int, int, int], bool]
    ) -> bool:
        """
        Check minimap for closest pixel that satisfies the color range lambda given.

        Range lambda should take `r`, `g`, and `b` values and return True if each value is
        within a certain threshold.

        Updates `targets` attribute if found.

        This function is intended for internal use only.

        Returns:
            `True` if found, `False` otherwise.
        Check minimap for closest pixel that satisfies the color range lambda given.

        Range lambda should take `r`, `g`, and `b` values and return True if each value is
        within a certain threshold.

        Updates `targets` attribute if found.

        This function is intended for internal use only.

        Returns:
            `True` if found, `False` otherwise.
        """
        minimap = pyautogui.screenshot(region=MINIMAP_REGION)
        width, height = minimap.size

        closest_x = 0
        closest_y = 0
        closest_dist = 200
        for x in range(width):
            for y in range(height):
                r, g, b = minimap.getpixel((x, y))
                if inColorRange(r, g, b):
                    left, top, _w, _h = MINIMAP_REGION
                    dx = left + x - MINIMAP_CENTER_X
                    dy = top + y - MINIMAP_CENTER_Y
                    if math.sqrt(dx**2 + dy**2) < closest_dist:
                        closest_x = dx
                        closest_y = dy
                        closest_dist = math.sqrt(dx**2 + dy**2)
        if closest_dist < 200:
            print(f"{name} pixel at x:{closest_x} y:{closest_y}")
            self.targets.append((closest_x, closest_y))
            return True
        else:
            return False
        # for entry in order:
        #     if entry[0] >= width or entry[1] >= height:
        #         continue
        #     r, g, b = minimap.getpixel((entry[0], entry[1]))
        #     if inColorRange(r, g, b):
        #         left, top, _w, _h = MINIMAP_REGION
        #         self.targetX = left + entry[0] - MINIMAP_CENTER_X
        #         self.targetY = top + entry[1] - MINIMAP_CENTER_Y
        #         return True
        # self.targetX = 0
        # self.targetY = 0
        # return False

    def get_game_coords(self, target_found: bool = False, pathfind: bool = False) -> tuple[int, int, int]:
        """
        Translates coordinates of most recently acquired target from relative minimap coordinates into valid, ingame coordinates.

        Args:
            target_found: If `True`, calculate where to click based on the most recently acquired target's location. \\
                Otherwise, calculate based on an average of all previously acquired targets.

        Returns:
            The `x` and `y` values of where to click in the game, as well as the `duration` (magnitude).
        """
        if len(self.targets) == 0:
            return SCREEN_CENTER_X, SCREEN_CENTER_Y, 100

        if target_found:
            target = self.targets[-1]
        else:
            target = average_coordinate(self.targets)

        if not pathfind or distanceBetweenCoordinates(target, (0, 0)) < 15:
            coord = target
        else:
            self.update_valid_coords()
            coord = closest_connected_coordinate(
                self.valid_coords, self.get_closest_valid_coord(target)
            )
            print(f"closest valid coord at {coord}")
        magnitude = math.sqrt(coord[0] ** 2 + coord[1] ** 2)
        magnitude = max(magnitude, 1)

        unit_x = coord[0] / magnitude
        unit_y = coord[1] / magnitude

        x = int(unit_x * 320)
        y = int(unit_y * 240)  # y axis not orthogonal to camera axis unlike minimap

        return x + SCREEN_CENTER_X, y + SCREEN_CENTER_Y, int(magnitude * 50)

    def get_closest_valid_coord(self, target: tuple[int, int]) -> list[tuple]:
        """
        Given a target, return the valid coordinate closest to the target.
        """
        sorted_valid_coords = sorted(
            self.valid_coords,
            key=lambda validCoord: distanceBetweenCoordinates(validCoord, target),
        )
        if len(sorted_valid_coords) == 0:
            return 0, 0
        else:
            return sorted_valid_coords[0]

    def check_mob(self) -> bool:
        """
        Check minimap for closest orange pixel of elite icon.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        return self.find_closest_pixel("mob", MOG_RGB_RANGE)

    def check_elite(self) -> bool:
        """
        Check minimap for closest red pixel of mob icon.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        return self.find_closest_pixel("elite", ELITE_RGB_RANGE)

    def check_buff(self) -> bool:
        """
        Check minimap for closest yellow pixel of Kurzan Front elemental buff icon.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        return self.find_closest_pixel("buff", BUFF_RGB_RANGE)

    def check_portal(self) -> bool:
        """
        Check minimap for portal icon and closest blue portal pixels.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        if config["performance"] == False:
            for portal_part in ["portal", "portalTop", "portalBot"]:
                portal_coords = find_image_center(
                    f"./screenshots/chaos/{portal_part}.png",
                    region=MINIMAP_REGION,
                    confidence=0.7,
                )
                match portal_part:
                    case "portal":
                        offset = 0
                    case "portalTop":
                        offset = 7
                    case "portalBot":
                        offset = -7
                if portal_coords is not None:
                    x, y = portal_coords
                    x = x - MINIMAP_CENTER_X
                    y = y - MINIMAP_CENTER_Y + offset
                    self.targets.append((x, y))
                    print(f"{portal_part} image x: {x} y: {y}")
                    return True
        return self.find_closest_pixel("portal", PORTAL_RGB_RANGE)

    def check_boss(self) -> bool:
        """
        Check minimap for boss icon.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        boss_location = find_image_center(
            "./screenshots/chaos/boss.png", region=MINIMAP_REGION, confidence=0.65
        )
        if boss_location is not None:
            x, y = boss_location
            x = x - MINIMAP_CENTER_X
            y = y - MINIMAP_CENTER_Y
            self.targets.append((x, y))
            print(f"boss x: {x} y: {y}")
            return True
        bossbar = check_image_on_screen(
            "./screenshots/chaos/bossBar.png",
            region=(406, 159, 1000, 200),
            confidence=0.8,
        )
        if bossbar:
            return True
        return False

    def check_rift_core(self) -> bool:
        """
        Check minimap for rift core icon.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        for tower_part in ["tower", "towerTop", "towerBot"]:
            tower_coords = find_image_center(
                f"./screenshots/chaos/{tower_part}.png",
                region=MINIMAP_REGION,
                confidence=0.7,
            )
            if tower_coords is not None:
                x, y = tower_coords
                x = x - MINIMAP_CENTER_X
                y = y - MINIMAP_CENTER_Y
                self.targets.append((x, y))
                print(f"{tower_part} at x: {x} y: {y}")
                return True
        return False

    def checkJump(self) -> bool:
        """
        Check minimap for jump pad icon.

        Updates `targets` attribute with coordinates if found.

        Returns:
            `True` if found, `False` otherwise.
        """
        jumpIcon = find_image_center(
            "./screenshots/chaos/jumpIcon2.png",
            region=MINIMAP_REGION,
            confidence=0.90,
        )
        if jumpIcon is not None:
            x, y = jumpIcon
            x = x - MINIMAP_CENTER_X - 7
            y = y - MINIMAP_CENTER_Y + 7
            self.targets.append((x, y))
            print(f"jump icon at x: {x} y: {y}")
            return True
        return False


def distanceBetweenCoordinates(coord1: tuple[int, int], coord2: tuple[int, int]) -> int:
    """
    Calculates the distance between two coordinates.
    """
    target_dist = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
    return int(target_dist)


def average_coordinate(coords: list[tuple[int, int]]) -> tuple[int, int]:
    """
    Calculate the average coordinate from a list of coordinates.
    """
    xs = [coord[0] for coord in coords]
    ys = [coord[1] for coord in coords]
    meanX = int(sum(xs) / len(xs))
    meanY = int(sum(ys) / len(ys))
    return meanX, meanY


def get_adjacent_coordinates(coord: tuple[int, int]):
    """
    Return a list of adjacent coordinates (4-directional).
    """
    x, y = coord
    return [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]


def closest_connected_coordinate(
    valid_coords: list[tuple[int, int]], target: tuple[int, int]
) -> tuple[int, int]:
    """
    Find the coordinate closest to the origin that is connected to the target.
    """

    queue = deque([target])
    visited = []
    closest_coord = None
    min_distance = float("inf")

    while queue:
        current = queue.popleft()

        if current in visited:
            continue

        visited.append(current)

        if current in valid_coords:
            distance = distanceBetweenCoordinates(current, (0, 0))
            if distance < min_distance:
                min_distance = distance
                closest_coord = current

        for neighbor in get_adjacent_coordinates(current):
            if neighbor not in visited and neighbor in valid_coords:
                queue.append(neighbor)

    return closest_coord


def MOG_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 180 < r < 215 and 17 < g < 35 and 17 < b < 55
    else:
        return 180 < r < 215 and 17 < g < 35 and 17 < b < 55


def ELITE_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 184 < r < 215 and 124 < g < 147 and 59 < b < 78
    else:
        return 189 < r < 215 and 124 < g < 150 and 29 < b < 70

def BOSS_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 100 < r < 170 and g < 35 and b < 35
    else:
        return 100 < r < 170 and g < 35 and b < 35

def BUFF_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 210 < r < 245 and 170 < g < 190 and 30 < b < 50 and r - g > 40
    else:
        return 200 < r < 255 and 170 < g < 200 and 30 < b < 70


def VALID_AREA_RGB_RANGE(r: int, g: int, b: int) -> bool:
    return (130 < r < 165 and 140 < g < 160 and 125 < b < 150) or (
        140 < r < 150 and 130 < g < 140 and 115 < b < 125
    )


def PORTAL_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return (75 < r < 105 and 140 < g < 170 and 240 < b < 256) or (
            120 < r < 130 and 210 < g < 240 and 240 < b < 256
        )
    else:
        return (75 < r < 85 and 140 < g < 150 and 250 < b < 256) or (
            120 < r < 130 and 210 < g < 220 and 250 < b < 256
        )
        return False


def distanceBetweenCoordinates(coord1: tuple[int, int], coord2: tuple[int, int]) -> int:
    """
    Calculates the distance between two coordinates.
    """
    target_dist = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
    return int(target_dist)


def average_coordinate(coords: list[tuple[int, int]]) -> tuple[int, int]:
    """
    Calculate the average coordinate from a list of coordinates.
    """
    xs = [coord[0] for coord in coords]
    ys = [coord[1] for coord in coords]
    meanX = int(sum(xs) / len(xs))
    meanY = int(sum(ys) / len(ys))
    return meanX, meanY


def get_adjacent_coordinates(coord: tuple[int, int]):
    """
    Return a list of adjacent coordinates (4-directional).
    """
    x, y = coord
    return [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]


def closest_connected_coordinate(
    valid_coords: list[tuple[int, int]], target: tuple[int, int]
) -> tuple[int, int]:
    """
    Find the coordinate closest to the origin that is connected to the target.
    """

    queue = deque([target])
    visited = []
    closest_coord = None
    min_distance = float("inf")

    while queue:
        current = queue.popleft()

        if current in visited:
            continue

        visited.append(current)

        if current in valid_coords:
            distance = distanceBetweenCoordinates(current, (0, 0))
            if distance < min_distance:
                min_distance = distance
                closest_coord = current

        for neighbor in get_adjacent_coordinates(current):
            if neighbor not in visited and neighbor in valid_coords:
                queue.append(neighbor)

    return closest_coord


def MOG_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 180 < r < 215 and 17 < g < 35 and 17 < b < 55
    else:
        return 180 < r < 215 and 17 < g < 35 and 17 < b < 55


def ELITE_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 184 < r < 215 and 124 < g < 147 and 59 < b < 78
    else:
        return 189 < r < 215 and 124 < g < 150 and 29 < b < 70

def BOSS_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 100 < r < 170 and g < 35 and b < 35
    else:
        return 100 < r < 170 and g < 35 and b < 35

def BUFF_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return 210 < r < 245 and 170 < g < 190 and 30 < b < 50 and r - g > 40
    else:
        return 200 < r < 255 and 170 < g < 200 and 30 < b < 70


def VALID_AREA_RGB_RANGE(r: int, g: int, b: int) -> bool:
    return (130 < r < 165 and 140 < g < 160 and 125 < b < 150) or (
        140 < r < 150 and 130 < g < 140 and 115 < b < 125
    )


def PORTAL_RGB_RANGE(r: int, g: int, b: int) -> bool:
    if config["GFN"]:
        return (75 < r < 105 and 140 < g < 170 and 240 < b < 256) or (
            120 < r < 130 and 210 < g < 240 and 240 < b < 256
        )
    else:
        return (75 < r < 85 and 140 < g < 150 and 250 < b < 256) or (
            120 < r < 130 and 210 < g < 220 and 250 < b < 256
        )
