import asyncio
import time

import pydirectinput

from modules.bot_manager import BotManager
from modules.menu_nav import restart_game, wait_overworld_load
from modules.utilities import (
    ResetException,
    RestartException,
    left_click_at_position,
    rand_sleep,
)

SCREEN_CENTER_POS = (960, 540)

pydirectinput.PAUSE = 0.05


async def start_script(options: dict[str, bool]):

    print(f"script starting at {time.asctime(time.localtime())}")
    start_time = time.time()

    await left_click_at_position(SCREEN_CENTER_POS)

    bot_manager = BotManager(options=options)

    # stay invis in friends list
    # if config["invisible"] == True:
    #     goInvisible()

    while True:
        try:
            await bot_manager.run()
            print(f"script finished at {time.asctime(time.localtime())}")
            runtime = time.time() - start_time
            h, rem = divmod(runtime, 3600)
            m, s = divmod(rem, 60)
            print(f"time elapsed: {int(h)}h {int(m)}m {int(s)}s")
            break
        except asyncio.CancelledError:
            print("script aborted")
            raise
        except RestartException:
            await rand_sleep(10000, 12200)
            await restart_game()
            await wait_overworld_load()
        except ResetException:
            bot_manager = BotManager(options)
