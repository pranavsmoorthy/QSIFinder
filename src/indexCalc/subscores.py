from utils.debug import log_debug
import math

def getBandGapSubscore(bandGap):
    return math.e ** (-2 * ((bandGap - 1.5) ** 2))
    