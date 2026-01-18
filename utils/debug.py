import logging
import traceback
import os

logger = logging.getLogger(__name__)
debugMode = False

if os.name == 'nt':
    _ = os.system('cls')
else:
    _ = os.system('clear')

def setDebugMode(status: bool):
    global debugMode
    debugMode = status

def isDebugMode():
    return debugMode

def logDebug(message: str):
    if isDebugMode():
        print(f"[DEBUG] {message}")
    logger.info(message)

def logError():
    if isDebugMode():
        logger.error(traceback.format_exc())

