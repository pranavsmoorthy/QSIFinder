from termcolor import colored
import traceback
import os
_debug_mode = True

if os.name == 'nt':
    _ = os.system('cls')
else:
    _ = os.system('clear')
    
def set_debug_mode(status: bool):
    global _debug_mode
    _debug_mode = status

def is_debug_mode():
    return _debug_mode

def log_debug(message: str):
    if is_debug_mode():
        print("\033[1m" + colored("DEBUG ", "yellow") + "\033[0m\x1B[3m" + message + "\x1B[0m")

def log_error():
    if is_debug_mode():
        print("\033[1m" + colored("---------------------- ERROR ----------------------", "red") + "\033[0m\n\x1B[3m" + traceback.format_exc() + "\x1B[0m")
