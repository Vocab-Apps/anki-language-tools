import sys
if hasattr(sys, '_pytest_mode'):
    pass
else:
    import aqt

    
class AnkiInterface():
    def __init__(self):
        pass

    def get_config(self):
        return aqt.mw.addonManager.getConfig(__name__)

    def night_mode_enabled(self):
        night_mode = aqt.mw.pm.night_mode()
        return night_mode