import aqt
from . import constants

def get_green_stylesheet():
    night_mode = aqt.mw.pm.night_mode()
    if night_mode:
        return constants.GREEN_STYLESHEET_NIGHTMODE
    return constants.GREEN_STYLESHEET

def get_red_stylesheet():
    night_mode = aqt.mw.pm.night_mode()
    if night_mode:
        return constants.RED_STYLESHEET_NIGHTMODE
    return constants.RED_STYLESHEET