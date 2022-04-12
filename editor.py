#python imports
import json
import typing
import urllib.parse
import logging
from typing import List, Dict

# anki imports
import aqt
import aqt.gui_hooks
import aqt.editor
import aqt.webview
import aqt.addcards
import anki.notes
import anki.models

# addon imports
# from .languagetools import LanguageTools, DeckNoteTypeField, build_deck_note_type, build_deck_note_type_from_note, build_deck_note_type_from_note_card, build_deck_note_type_from_addcard, LanguageToolsRequestError, AnkiNoteEditorError
from . import constants
from . import errors
from . import deck_utils
from .languagetools import LanguageTools
from . import editor_processing


def configure_editor_component_options(editor: aqt.editor.Editor, live_updates, typing_delay):
    live_updates_str = str(live_updates).lower()
    js_command = f"setLanguageToolsEditorSettings({live_updates_str}, {typing_delay})"
    # print(js_command)
    editor.web.eval(js_command)        


def init(languagetools):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")
    
    editor_manager = editor_processing.EditorManager(languagetools)

    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = [
            f"/_addons/{addon_package}/languagetools.js",
        ]
        css_path =  [
            f"/_addons/{addon_package}/languagetools.css",
        ]
        web_content.js.extend(javascript_path)
        web_content.css.extend(css_path)


    def loadNote(editor: aqt.editor.Editor):
        live_updates = languagetools.get_apply_updates_automatically()
        typing_delay = languagetools.get_live_update_delay()
        configure_editor_component_options(editor, live_updates, typing_delay)


    def on_editor_context_menu(web_view: aqt.editor.EditorWebView, menu: aqt.qt.QMenu):
        # gather some information about the context from the editor
        # =========================================================

        editor: aqt.editor.Editor = web_view.editor

        selected_text = web_view.selectedText()
        current_field_num = editor.currentField
        if current_field_num == None:
            # we don't have a field selected, don't do anything
            return
        note = web_view.editor.note
        if note == None:
            # can't do anything without a note
            return
        model_id = note.mid
        model = aqt.mw.col.models.get(model_id)
        field_name = model['flds'][current_field_num]['name']
        card = web_view.editor.card
        if card == None:
            # we can't get the deck without a a card
            return
        deck_id = card.did

        deck_note_type_field = languagetools.deck_utils.build_deck_note_type_field(deck_id, model_id, field_name)
        language = languagetools.get_language(deck_note_type_field)

        # check whether a language is set
        # ===============================

        if language != None:
            # all pre-requisites for translation/transliteration are met, proceed
            # ===================================================================

            show_play_audio = False
            show_choose_translation = False
            show_speak = True
            show_breakdown = True

            # is this a sound field ? 
            if language == constants.SpecialLanguage.sound.name:
                show_play_audio = True
            if language == constants.SpecialLanguage.sound.name or language == constants.SpecialLanguage.transliteration.name:
                show_speak = False
                show_breakdown = False

            # is it a translation field ? 
            if languagetools.get_batch_translation_setting_field(deck_note_type_field) != None:
                # translation field
                show_choose_translation = True

            if show_choose_translation:                
                menu_text = f'{constants.MENU_PREFIX} Choose Translation'
                menu.addAction(menu_text, editor_manager.get_choose_translation_lambda(editor, field_name))

            if show_play_audio:
                menu_text = f'{constants.MENU_PREFIX} Play Audio'
                menu.addAction(menu_text, editor_manager.get_play_tag_audio_lambda(editor, field_name))

            # add speak
            if show_speak:
                menu_text = f'{constants.MENU_PREFIX} Speak'
                menu.addAction(menu_text, editor_manager.get_speak_lambda(editor, field_name))

            # add breakdown
            if show_breakdown:
                menu_text = f'{constants.MENU_PREFIX} Breakdown'
                menu.addAction(menu_text, editor_manager.get_breakdown_lambda(editor, field_name))



    def onBridge(handled, str, editor):
        # logging.debug(f'bridge str: {str}')

        # return handled # don't do anything for now
        if not isinstance(editor, aqt.editor.Editor):
            return handled

        if str.startswith('playsoundcollection:'):
            logging.debug(f'playsoundcollection command: [{str}]')
            components = str.split(':')
            field_index_str = components[1]
            field_index = int(field_index_str)

            note = editor.note
            sound_tag = note.fields[field_index]
            logging.debug(f'sound tag: {sound_tag}')

            languagetools.anki_utils.play_anki_sound_tag(sound_tag)
            return handled

        if str.startswith('choosetranslation:'):
            editor_manager.process_choosetranslation(editor, str)
            return True, None

        if str.startswith('ttsspeak:'):
            logging.debug(f'ttsspeak command: [{str}]')
            components = str.split(':')
            field_index_str = components[1]
            field_index = int(field_index_str)

            note = editor.note
            source_text = note.fields[field_index]
            logging.debug(f'source_text: {source_text}')

            try:

                from_deck_note_type_field = languagetools.deck_utils.editor_get_dntf(editor, field_index)

                # do we have a voice set ?
                field_language = languagetools.get_language(from_deck_note_type_field)
                if field_language == None:
                    raise errors.AnkiNoteEditorError(f'No language set for field {from_deck_note_type_field}')
                voice_selection_settings = languagetools.get_voice_selection_settings()
                if field_language not in voice_selection_settings:
                    raise errors.AnkiNoteEditorError(f'No voice set for language {languagetools.get_language_name(field_language)}')
                voice = voice_selection_settings[field_language]

                def play_audio(languagetools, source_text, voice):
                    voice_key = voice['voice_key']
                    service = voice['service']
                    language_code = voice['language_code']

                    try:
                        filename = languagetools.get_tts_audio(source_text, service, language_code, voice_key, {})
                        if filename != None:
                            aqt.sound.av_player.play_file(filename)
                    except errors.LanguageToolsRequestError as err:
                        pass

                def play_audio_done(future_result):
                    pass

                aqt.mw.taskman.run_in_background(lambda: play_audio(languagetools, source_text, voice), lambda x: play_audio_done(x))

            except errors.AnkiNoteEditorError as e:
                # logging.error('Could not speak', exc_info=True)
                aqt.utils.showCritical(repr(e))

            return handled

        if str.startswith(constants.COMMAND_PREFIX_LANGUAGETOOLS):
            editor_manager.process_command(editor, str)
            return True, None

        if str.startswith("key:"):
            # user updated field, see if we need to do any transformations
            editor_manager.process_field_update(editor, str)


        return handled

        


    aqt.gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    aqt.gui_hooks.editor_did_load_note.append(loadNote)
    aqt.gui_hooks.webview_did_receive_js_message.append(onBridge)
    # right click menu
    aqt.gui_hooks.editor_will_show_context_menu.append(on_editor_context_menu)    
