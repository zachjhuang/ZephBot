import modules.minimap as mm
import modules.chaos_bot as cb
import modules.kurzan_front_bot as kf
import matplotlib.pyplot as plt
import modules.bot_manager as bm
import time
import os
import keyboard
import pyautogui
from configs.roster import roster

from collections import deque
import math
# keyboard.add_hotkey("ctrl+page down", os._exit(1))
def testMinimap():
    m = mm.Minimap()
    m.update_valid_coords()
    xs = [i[0] for i in m.validCoords]
    ys = [i[1] for i in m.validCoords]
    plt.scatter(xs, ys)

    x, y = mm.average_coordinate(m.validCoords)
    plt.scatter(x, y)

    plt.xlim(-120, 120)
    plt.ylim(-100, 100)

    print(m.check_buff())
    print(m.targets)
    plt.scatter(m.targets[0][0], m.targets[0][1])

    close = m.getClosestValidCoords(m.targets[0], 5)
    close = m.getClosestValidCoords((25, 40), 5)
    xs = [i[0] for i in close]
    ys = [i[1] for i in close]
    plt.scatter(xs, ys)

    close = m.getClosestValidCoords((25, 40), 1)[0]
    plt.show()


# testMinimap()

def testChaos(n):
    c = cb.ChaosBot(roster)
    c.curr = n
    c.run_start_time = int(time.time())
    c.do_chaos_floor(3)
# testChaos(5)

def testKurzan(n):
    k = kf.KurzanFrontBot(roster)
    k.curr = n
    k.run_start_time = int(time.time())
    k.use_skills()

# testKurzan(3)

def testJumpDetection():
    im = pyautogui.screenshot()
    for x in range(im.width):
        for y in range(im.height):
            r, g, b = im.getpixel((x, y))
            if 205 < r < 230 and 165 < g < 182 and 132 < b < 145:
                print(x, y)

# testJumpDetection()

def testSwitch():
    b = bm.BotManager(False, True, True, True)
    while True:
        b.switch_to_char(0)
        b.switch_to_char(1)

testSwitch()


