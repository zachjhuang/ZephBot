import math
import pyautogui

from .utilities import findImageCenter, checkImageOnScreen
from configs.config import config

from typing import Callable

SCREEN_CENTER_X = 960
SCREEN_CENTER_Y = 540

MINIMAP_REGION = (1655, 170, 240, 200)
MINIMAP_CENTER_X = 1772
MINIMAP_CENTER_Y = 272

MOB_RGB_RANGE_GFN = lambda r, g, b: 180 < r < 215 and 17 < g < 35 and 17 < b < 55
MOG_RGB_RANGE = lambda r, g, b: 180 < r < 215 and 17 < g < 35 and 17 < b < 55

ELITE_RGB_RANGE_GFN = lambda r, g, b: 184 < r < 215 and 124 < g < 147 and 59 < b < 78
ELITE_RGB_RANGE = lambda r, g, b: 189 < r < 215 and 124 < g < 150 and 29 < b < 70

BUFF_RGB_RANGE_GFN = lambda r, g, b: 210 < r < 255 and 170 < g < 190 and 30 < b < 60
BUFF_RGB_RANGE = lambda r, g, b: 189 < r < 215 and 124 < g < 150 and 29 < b < 70

PORTAL_RGB_RANGE_GFN = lambda r, g, b: (
    (75 < r < 105 and 140 < g < 170 and 240 < b < 256)
    or (120 < r < 130 and 210 < g < 240 and 240 < b < 256)
)
PORTAL_RGB_RANGE = lambda r, g, b: (
    (75 < r < 85 and 140 < g < 150 and 250 < b < 256)
    or (120 < r < 130 and 210 < g < 220 and 250 < b < 256)
)


class Minimap:
    def __init__(self):
        self.targetX = 0
        self.targetY = 0

    def findClosestMinimapPixel(
        self, name: str, inColorRange: Callable[[int, int, int], bool]
    ) -> bool:
        """
        Check minimap for closest pixel that satisfies the range lambda given.
        Return true if found and update minimap target coordinates.
        Return false otherwise.
        """
        minimap = pyautogui.screenshot(region=MINIMAP_REGION)
        width, height = minimap.size
        order = spiralSearch(
            width, height, math.floor(width / 2), math.floor(height / 2)
        )
        for entry in order:
            if entry[0] >= width or entry[1] >= height:
                continue
            r, g, b = minimap.getpixel((entry[0], entry[1]))
            if inColorRange(r, g, b):
                left, top, _w, _h = MINIMAP_REGION
                self.targetX = left + entry[0] - MINIMAP_CENTER_X
                self.targetY = top + entry[1] - MINIMAP_CENTER_Y
                # print(f"{name} pixel at x:{self.targetX} y:{self.targetY}")
                return True
        self.targetX = 0
        self.targetY = 0
        return False

    def getGameCoordsOfMinimapTarget(self) -> tuple[int, int, int]:
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


def spiralSearch(rows, cols, rStart, cStart) -> list[list]:
    ans = []
    end = rows * cols
    i = i1 = i2 = rStart
    j = j1 = j2 = cStart
    while True:
        j2 += 1
        while j < j2:
            if 0 <= j < cols and 0 <= i:
                ans.append([i, j])
            j += 1
            if 0 > i:
                j = j2
        i2 += 1
        while i < i2:
            if 0 <= i < rows and j < cols:
                ans.append([i, j])
            i += 1
            if j >= cols:
                i = i2
        j1 -= 1
        while j > j1:
            if 0 <= j < cols and i < rows:
                ans.append([i, j])
            j -= 1
            if i >= rows:
                j = j1
        i1 -= 1
        while i > i1:
            if 0 <= i < rows and 0 <= j:
                ans.append([i, j])
            i -= 1
            if 0 > j:
                i = i1
        if len(ans) == end:
            return ans
