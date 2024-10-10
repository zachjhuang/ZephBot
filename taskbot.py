from characters import characters as roster


class TaskBot:
    def __init__(self):
        self.curr: int = 0
        self.roster: list[dict] = roster
        self.remainingTasks: list[int] = []

    def isCompleted(self) -> bool:
        """Return true if no remaining tasks, false otherwise."""
        return sum(self.remainingTasks) == 0

    def setCurrentCharacter(self, index: int) -> None:
        """Updates current character of bot instance."""
        self.curr = index

    def setCharacterRemainingTasks(self, index: int, n: int) -> None:
        """Updates current character of bot instance."""
        self.remainingTasks[index] = n

    def doTasks(self) -> None:
        pass

    def doneOnCurrentChar(self) -> bool:
        return self.remainingTasks[self.curr] == 0
