class TaskBot:
    """Basic skeleton for bot class."""
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

    async def do_tasks(self) -> None:
        """Placeholder method to run tasks. MUST BE IMPLEMENTED BY CHILD CLASSES."""
        pass

    def done_on_curr_char(self) -> bool:
        """Check if bot has tasks to do on the current character"""
        return self.remaining_tasks[self.curr] == 0
