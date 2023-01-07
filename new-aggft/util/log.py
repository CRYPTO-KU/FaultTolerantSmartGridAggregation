from datetime     import datetime

from rich.console import Console
from rich.markup  import escape

################################################################################
# Internal Helpers
################################################################################

_console = Console()

def _log(type, color, msg):
    now = datetime.now().strftime("[%H:%M:%S]")
    _console.print(f"[{color} bold]{now} {type}:[/] {escape(msg)}")

################################################################################
# Logging Helpers
################################################################################

def info(msg: str) -> None:
    color = "blue"
    _log("INFO", color, msg)

def error(msg: str) -> None:
    color = "red"
    _log("ERRR", color, msg)

def warning(msg: str) -> None:
    color = "yellow"
    _log("WARN", color, msg)

def success(msg: str) -> None:
    color = "green"
    _log("SUCC", color, msg)
