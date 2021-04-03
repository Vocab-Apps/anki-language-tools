import sys
import re
import logging
import aqt
import anki.template
import anki.sound

if hasattr(sys, '_pytest_mode'):
    import constants
    import anki_interface
else:
    from . import constants
    from . import anki_interface

def get_green_stylesheet(interface):
    night_mode = interface.night_mode_enabled()
    if night_mode:
        return constants.GREEN_STYLESHEET_NIGHTMODE
    return constants.GREEN_STYLESHEET

def get_red_stylesheet(interface):
    night_mode = interface.night_mode_enabled()
    if night_mode:
        return constants.RED_STYLESHEET_NIGHTMODE
    return constants.RED_STYLESHEET

def play_anki_sound_tag(text):
    out = aqt.mw.col.backend.extract_av_tags(text=text, question_side=True)
    file_list = [
        x.filename
        for x in anki.template.av_tags_to_native(out.av_tags)
        if isinstance(x, anki.sound.SoundOrVideoTag)
    ]   
    if len(file_list) >= 1:
        filename = file_list[0]
        aqt.sound.av_player.play_file(filename)
