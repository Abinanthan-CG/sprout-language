class SproutError(Exception):
    """A friendly error in Sprout."""
    def __init__(self, message, line=0):
        super().__init__(message)
        self.message = message
        self.line = line

    def __str__(self):
        if self.line:
            return f"{self.message}\n   (on line {self.line})"
        return self.message


class SproutReturn(Exception):
    """Used internally to unwind the call stack on 'bear'."""
    def __init__(self, value):
        self.value = value


class SproutBreak(Exception):
    """Used internally when a loop should stop."""
    pass

class SproutContinue(Exception):
    """Used internally when a loop iteration should be skipped."""
    pass

