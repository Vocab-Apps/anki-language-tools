import sys
import aqt
import anki.template
import anki.sound
import logging
import sentry_sdk
import aqt.qt
from . import constants    

    
class AnkiUtils():
    def __init__(self):
        pass

    def get_config(self):
        return aqt.mw.addonManager.getConfig(__name__)

    def write_config(self, config):
        aqt.mw.addonManager.writeConfig(__name__, config)

    def night_mode_enabled(self):
        night_mode = aqt.theme.theme_manager.night_mode
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

    def html_to_text_line(self, html):
        return anki.utils.html_to_text_line(html)

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

    def media_add_file(self, filename):
        full_filename = aqt.mw.col.media.addFile(filename)
        return full_filename

    def run_in_background(self, task_fn, task_done_fn):
        aqt.mw.taskman.run_in_background(task_fn, task_done_fn)

    def run_on_main(self, task_fn):
        aqt.mw.taskman.run_on_main(task_fn)

    def wire_typing_timer(self, text_input, text_input_changed):
        typing_timer = aqt.qt.QTimer()
        typing_timer.setSingleShot(True)
        typing_timer.timeout.connect(text_input_changed)
        text_input.textChanged.connect(lambda: typing_timer.start(1000))
        return typing_timer


    def call_on_timer_expire(self, timer, task):
        if timer.timer_obj != None:
            # stop it first
            timer.timer_obj.stop()
        timer.timer_obj = aqt.qt.QTimer()
        timer.timer_obj.setSingleShot(True)
        timer.timer_obj.timeout.connect(task)
        timer.timer_obj.start(timer.delay_ms)

    def info_message(self, message, parent):
        aqt.utils.showInfo(message, title=constants.ADDON_NAME, textFormat='rich', parent=parent)

    def critical_message(self, message, parent):
        aqt.utils.showCritical(message, title=constants.ADDON_NAME, parent=parent)

    def tooltip_message(self, message):
        aqt.utils.tooltip(message)

    def ask_user(self, message, parent):
        result = aqt.utils.askUser(message, parent=parent)
        return result

    def play_sound(self, filename):
        aqt.sound.av_player.insert_file(filename)

    def show_progress_bar(self, message):
        aqt.mw.progress.start(immediate=True, label=f'{constants.MENU_PREFIX} {message}')

    def stop_progress_bar(self):
        aqt.mw.progress.finish()

    def editor_note_set_field_value(self, editor, field_name, text):
        editor.note[field_name] = text
        editor.set_note(editor.note)

    def show_loading_indicator_field(self, editor, field_name):
        js_command= f"showLoadingIndicator('{field_name}')"
        if editor != None and editor.web != None:
            editor.web.eval(js_command)

    def hide_loading_indicator_field(self, editor, field_name):
        js_command= f"hideLoadingIndicator('{field_name}')"
        if editor != None and editor.web != None:
            editor.web.eval(js_command)

    def undo_start(self, action_name):
        return aqt.mw.col.add_custom_undo_entry(f'{constants.ADDON_NAME}: {action_name}')

    def undo_end(self, undo_id):
        def undo_end_fn():
            logging.debug(f'unfo_end_fn, undo_id: {undo_id}')
            try:
                aqt.mw.col.merge_undo_entries(undo_id)
                aqt.mw.update_undo_actions()
                aqt.mw.autosave()
            except Exception as e:
                # logging.error(f'exception in undo_end_fn: {str(e)}, undo_id: {undo_id}')
                # disable logging for now, needs the same logging setup as hypertts
                pass
        self.run_on_main(undo_end_fn)

    def update_note(self, note):
        aqt.mw.col.update_note(note)

    def display_dialog(self, dialog):
        return dialog.exec()

    def report_known_exception_interactive(self, exception, action):
        error_message = f'Encountered an error while {action}: {str(exception)}'
        logging.warning(error_message)
        self.critical_message(error_message, None)

    def report_unknown_exception_interactive(self, exception, action):
        error_message = f'Encountered an unknown error while {action}: {str(exception)}'
        sentry_sdk.capture_exception(exception)
        self.critical_message(error_message, None)

    def report_unknown_exception_background(self, exception):
        sentry_sdk.capture_exception(exception)
