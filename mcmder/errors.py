import signal


class McmderError(Exception):
    """Parent of Errors in this module."""
    pass


class McmdError(McmderError):
    """Raised when run() is called with check=True and the process.

    returns a non-zero exit status.
    Attributes:
      cmd, returncode, stderr, output
    """

    def __init__(self, returncode, cmd, output=None, stderr=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr

    def __str__(self):
        if self.returncode and self.returncode < 0:
            try:
                return "Command '%s' died with %r.\n %s" % (
                    self.cmd, signal.Signals(-self.returncode), self.stderr)
            except ValueError:
                return "Command '%s' died with unknown signal %d.\n %s" % (
                    self.cmd, -self.returncode, self.stderr)
        else:
            return "Command '%s' returned non-zero exit status %d.\n %s" % (
                self.cmd, self.returncode, self.stderr)
