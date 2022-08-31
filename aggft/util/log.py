from datetime import datetime

from rich.console import Console
from rich.markup import escape

_console = Console()

def log(type, color, msg):
    now = datetime.now().strftime("[%H:%M:%S]")
    _console.print(f"[{color} bold]{now} {type}:[/] {escape(msg)}")

def info(msg):
    log("INFO", "blue", msg)

def error(msg):
    log("ERRR", "red", msg)

def warning(msg):
    log("WARN", "yellow", msg)

def success(msg):
    log("SUCC", "green", msg)
