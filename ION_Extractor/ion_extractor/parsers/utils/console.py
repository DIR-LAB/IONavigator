from rich import print, box, rule
from rich.console import Console, Group
from rich.padding import Padding
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
from rich.terminal_theme import TerminalTheme
from rich.terminal_theme import MONOKAI
from subprocess import call
from packaging import version
import shutil
import os
import sys



def get_console():
    return Console(record=True)


def formatted_print(console, text, style=None, justify=None):
    if style is not None:
        console.print(text, style=style, justify=justify)
    else:
        console.print(text, justify=justify)