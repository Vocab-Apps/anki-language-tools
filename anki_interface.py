import sys
if hasattr(sys, '_pytest_mode'):
    pass
else:
    import aqt

def anki_night_mode_enabled():
    if not hasattr(sys, '_pytest_mode'):
        night_mode = aqt.mw.pm.night_mode()
        return night_mode
    return False