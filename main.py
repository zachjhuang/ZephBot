import argparse
import os
import time

import keyboard
import pydirectinput

from modules.bot_manager import BotManager
from modules.menu_nav import restart_game, wait_overworld_load
from modules.utilities import (
    ResetException,
    RestartException,
    left_click_at_position,
    random_sleep,
)

SCREEN_CENTER_POS = (960, 540)

pydirectinput.PAUSE = 0.05

def abort_script():
    os._exit(1)


def main():
    keyboard.add_hotkey("ctrl+page down", abort_script)

    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument(
        "--chaos", action="store_true", help="Enables 2x chaos on entire roster"
    )
    parser.add_argument(
        "--kurzanfront",
        action="store_true",
        help="Enables Kurzan Front on entire roster",
    )
    parser.add_argument(
        "--unas", action="store_true", help="Enables unas on entire roster"
    )
    parser.add_argument(
        "--guild",
        action="store_true",
        help="Enables guild donation/support on entire roster",
    )
    parser.add_argument("--delay", type=int, help="Delay start of program in seconds")
    args = parser.parse_args()

    if args.delay is not None:
        print(f"random_sleeping for {args.delay} seconds")
        random_sleep(args.delay * 1000, (args.delay + 1) * 1000)

    print(f"script starting at {time.asctime(time.localtime())}")
    start_time = time.time()

    left_click_at_position(SCREEN_CENTER_POS)

    bot_manager = BotManager(
        options={
            "do_chaos": args.chaos,
            "do_kurzan_front": args.kurzanfront,
            "do_unas": args.unas,
            "do_guild": args.guild
        }
    )

    # stay invis in friends list
    # if config["invisible"] == True:
    #     goInvisible()

    while True:
        try:
            bot_manager.run()
            print(f"script finished at {time.asctime(time.localtime())}")
            runtime = time.time() - start_time
            h, rem = divmod(runtime, 3600)
            m, s = divmod(rem, 60)
            print(f"time elapsed: {int(h)}h {int(m)}m {int(s)}s")
            break
        except RestartException:
            random_sleep(10000, 12200)
            restart_game()
            wait_overworld_load()
        except ResetException:
            bot_manager = BotManager(args.chaos, args.kurzanfront, args.unas, args.guild)


if __name__ == "__main__":
    main()
