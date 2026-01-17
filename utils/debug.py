import logging
import traceback
import os

logger = logging.getLogger(__name__)
_debug_mode = False

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
        print(f"[DEBUG] {message}")
    logger.info(message)

def log_error():
    if is_debug_mode():
        logger.error(traceback.format_exc())

