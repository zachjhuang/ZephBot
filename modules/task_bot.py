class TaskBot:
    def __init__(self, roster, config):
        self.curr: int = 0
        self.roster: list[dict] = roster
        self.config: dict = config
        self.remaining_tasks: list[int] = []

    def is_done(self) -> bool:
        """Return true if no remaining tasks, false otherwise."""
        return sum(self.remaining_tasks) == 0

    def set_current_char(self, index: int) -> None:
        """Updates current character of bot instance."""
        self.curr = index

    def set_char_remaining_tasks(self, index: int, n: int) -> None:
        """Updates current character of bot instance."""
        self.remaining_tasks[index] = n

    def do_tasks(self) -> None:
        pass

    def done_on_curr_char(self) -> bool:
        return self.remaining_tasks[self.curr] == 0
