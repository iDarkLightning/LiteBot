from sys import stdout
import datetime
from datetime import datetime

GRAY = "\033[37m"
RED = "\033[31m"
YELLOW = "\033[33m"
END = "\033[0m"

format_time = lambda: datetime.now().strftime("%H:%M:%S")

def log(message):
    stdout.write("%s[%s]%s %s\n" % (
        GRAY,
        format_time(),
        END,
        message))

def warn(message):
    stdout.write("%s[%s]%s %s%s%s" % (
        GRAY,
        format_time(),
        END,
        YELLOW,
        message,
        END
    ))

def error(message):
    stdout.write("%s[%s]%s %s%s%s" % (
        GRAY,
        format_time(),
        END,
        RED,
        message,
        END
    ))