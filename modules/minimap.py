import math
from typing import Callable

import pyautogui

from configs.config import config
from modules.utilities import checkImageOnScreen, findImageCenter

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

MINIMAP_REGION = (1653, 172, 240, 200)
MINIMAP_CENTER_X = 1773
MINIMAP_CENTER_Y = 272


class Minimap:
    def __init__(self) -> None:
        self.targetX = 0
        self.targetY = 0

    def findClosestMinimapPixel(
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
        Translates relative minimap coordinates of target into game coordinates.

        Returns the x and y values of where to click, as well as the duration (magnitude).
        """
        magnitude = math.sqrt(self.targetX * self.targetX + self.targetY * self.targetY)
        magnitude = max(magnitude, 1)

        unit_x = self.targetX / magnitude
        unit_y = self.targetY / magnitude

        x = int(unit_x * 360)
        y = int(unit_y * 240)  # y axis not orthogonal to camera axis unlike minimap

        return x + SCREEN_CENTER_X, y + SCREEN_CENTER_Y, int(magnitude * 50)

    def checkMob(self) -> bool:
        """
        Check minimap for closest orange pixel of elite icon.
        Return true if found and update minimap target coordinates.
        Return false otherwise.
        """
        if config["GFN"]:
            return self.findClosestMinimapPixel("mob", MOB_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("mob", MOG_RGB_RANGE)

    def checkElite(self) -> bool:
        """
        Check minimap for closest red pixel of mob icon.
        Return true if found and update minimap target coordinates.
        Return false otherwise.
        """
        if config["GFN"]:
            return self.findClosestMinimapPixel("elite", ELITE_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("elite", ELITE_RGB_RANGE)

    def checkBuff(self) -> bool:
        """
        Check minimap for closest yello pixel of mob icon.
        Return true if found and update minimap target coordinates.
        Return false otherwise.
        """
        if config["GFN"]:
            return self.findClosestMinimapPixel("buff", BUFF_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("buff", BUFF_RGB_RANGE)

    def checkPortal(self) -> bool:
        """
        Check minimap for portal icon and blue portal pixels.

        Return true if found and update minimap target coordinates.

        Return false otherwise.
        """
        if config["performance"] == False:
            for portalPart in ["portal", "portalTop", "portalBot"]:
                portalCoords = findImageCenter(
                    f"./screenshots/chaos/{portalPart}.png",
                    region=MINIMAP_REGION,
                    confidence=0.7,
                )
                match portalPart:
                    case "portal":
                        offset = 0
                    case "portalTop":
                        offset = 7
                    case "portalBot":
                        offset = -7

                if portalCoords is not None:
                    x, y = portalCoords
                    self.targetX = x - MINIMAP_CENTER_X
                    self.targetY = y - MINIMAP_CENTER_Y + offset
                    print(f"{portalPart} image x: {self.targetX} y: {self.targetY}")
                    return True
        if config["GFN"]:
            return self.findClosestMinimapPixel("portal", PORTAL_RGB_RANGE_GFN)
        else:
            return self.findClosestMinimapPixel("portal", PORTAL_RGB_RANGE)

    def checkBoss(self) -> bool:
        """
        Check minimap for boss icon and screen for boss health bar

        Return true if found and update minimap target coordinates.

        Return false otherwise.
        """
        bossLocation = findImageCenter(
            "./screenshots/chaos/boss.png", confidence=0.65, region=MINIMAP_REGION
        )
        if bossLocation is not None:
            x, y = bossLocation
            self.targetX = x - MINIMAP_CENTER_X
            self.targetY = y - MINIMAP_CENTER_Y
            print(f"boss x: {self.targetX} y: {self.targetY}")
            return True
        bossbar = checkImageOnScreen(
            "./screenshots/chaos/bossBar.png",
            confidence=0.8,
            region=(406, 159, 1000, 200),
        )
        if bossbar:
            return True
        return False

    def checkRiftCore(self) -> bool:
        """
        Check minimap for rift core icon.

        Return true if found and update minimap target coordinates.

        Return false otherwise.
        """
        for towerPart in ["tower", "towerTop", "towerBot"]:
            towerCoords = findImageCenter(
                f"./screenshots/chaos/{towerPart}.png",
                region=MINIMAP_REGION,
                confidence=0.7,
            )
            if towerCoords is not None:
                x, y = towerCoords
                self.targetX = x - MINIMAP_CENTER_X
                self.targetY = y - MINIMAP_CENTER_Y
                print(f"{towerPart} at x: {self.targetX} y: {self.targetY}")
                return True
        return False

    def checkJump(self) -> bool:
        jumpIcon = findImageCenter(
            "./screenshots/chaos/jumpIcon.png",
            region=MINIMAP_REGION,
            confidence=0.75,
        )
        if jumpIcon is not None:
            x, y = jumpIcon
            self.targetX = x - MINIMAP_CENTER_X - 4
            self.targetY = y - MINIMAP_CENTER_Y + 4
            print(f"jump icon at x: {self.targetX} y: {self.targetY}")
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
