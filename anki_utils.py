import sys
import aqt
import anki.template
import anki.sound
from . import constants    

    
class AnkiUtils():
    def __init__(self):
        pass

    def get_config(self):
        return aqt.mw.addonManager.getConfig(__name__)

    def write_config(self, config):
        aqt.mw.addonManager.writeConfig(__name__, config)

    def night_mode_enabled(self):
        night_mode = aqt.mw.pm.night_mode()
        return night_mode

    def get_green_stylesheet(self):
        night_mode = self.night_mode_enabled()
        if night_mode:
            return constants.GREEN_STYLESHEET_NIGHTMODE
        return constants.GREEN_STYLESHEET

    def get_red_stylesheet(self):
        night_mode = self.night_mode_enabled()
        if night_mode:
            return constants.RED_STYLESHEET_NIGHTMODE
        return constants.RED_STYLESHEET

    def play_anki_sound_tag(self, text):
        out = aqt.mw.col.backend.extract_av_tags(text=text, question_side=True)
        file_list = [
            x.filename
            for x in anki.template.av_tags_to_native(out.av_tags)
            if isinstance(x, anki.sound.SoundOrVideoTag)
        ]   
        if len(file_list) >= 1:
            filename = file_list[0]
            aqt.sound.av_player.play_file(filename)

    def get_deckid_modelid_pairs(self):
        return aqt.mw.col.db.all("select did, mid from notes inner join cards on notes.id = cards.nid group by mid, did")

    def get_noteids_for_deck_note_type(self, deck_id, model_id, sample_size):
        sql_query = f'SELECT notes.id FROM notes INNER JOIN cards ON notes.id = cards.nid WHERE notes.mid={model_id} AND cards.did={deck_id} ORDER BY RANDOM() LIMIT {sample_size}'

        note_id_result = aqt.mw.col.db.all(sql_query)
        note_ids = []
        query_strings = []
        for entry in note_id_result:
            note_id = entry[0]
            note_ids.append(note_id)

        return note_ids

    def get_note_by_id(self, note_id):
        note = aqt.mw.col.getNote(note_id)
        return note

    def get_model(self, model_id):
        return aqt.mw.col.models.get(model_id)

    def get_deck(self, deck_id):
        return aqt.mw.col.decks.get(deck_id)

    def get_model_id(self, model_name):
        return aqt.mw.col.models.id_for_name(model_name)

    def get_deck_id(self, deck_name):
        return aqt.mw.col.decks.id_for_name(deck_name)

    def run_in_background(self, task_fn, task_done_fn):
        aqt.mw.taskman.run_in_background(task_fn, task_done_fn)

    def run_on_main(self, task_fn):
        aqt.mw.taskman.run_on_main(task_fn)

    def info_message(self, message, parent):
        aqt.utils.showInfo(message, title=constants.ADDON_NAME, textFormat='rich', parent=parent)

    def critical_message(self, message, parent):
        aqt.utils.showCritical(message, title=constants.ADDON_NAME, parent=parent)