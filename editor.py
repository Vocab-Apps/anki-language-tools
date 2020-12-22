#python imports
import json
import urllib.parse
from typing import List, Dict

# anki imports
import aqt
import aqt.gui_hooks
import aqt.editor
import aqt.webview
import anki.notes

# addon imports
from .languagetools import LanguageTools, DeckNoteTypeField, build_deck_note_type, build_deck_note_type_from_note
from . import constants


def get_field_id(deck_note_type_field: DeckNoteTypeField):
    model = aqt.mw.col.models.get(deck_note_type_field.deck_note_type.model_id)
    fields = model['flds']
    field_names = [x['name'] for x in fields]
    field_index = field_names.index(deck_note_type_field.field_name)
    return field_index    

def remove_inline_translation_changes(languagetools: LanguageTools, editor: aqt.editor.Editor, deck_note_type_field: DeckNoteTypeField):
    field_index = get_field_id(deck_note_type_field)
    js_command = f"remove_inline_field('{constants.EDITOR_WEB_FIELD_ID_TRANSLATION}', {field_index})"
    editor.web.eval(js_command)

def apply_inline_translation_changes(languagetools: LanguageTools, editor: aqt.editor.Editor, deck_note_type_field: DeckNoteTypeField, translation_option):
    # first, remove any inline translation which may be present already
    remove_inline_translation_changes(languagetools, editor, deck_note_type_field)

    field_index = get_field_id(deck_note_type_field)
    editor.web.eval(f"add_inline_field('{constants.EDITOR_WEB_FIELD_ID_TRANSLATION}', {field_index}, 'Translation')")

    note = editor.note
    field_value = note[deck_note_type_field.field_name]
    load_inline_translation(languagetools, editor, field_value, deck_note_type_field, translation_option)

def load_inline_translation(languagetools, editor: aqt.editor.Editor, field_value: str, deck_note_type_field: DeckNoteTypeField, translation_option: Dict):
    field_index = get_field_id(deck_note_type_field)

    # now, we need to do the translation, asynchronously
    # prepare lambdas
    #     
    def get_request_translation_lambda(languagetools, field_value, translation_option):
        def request_translation():
            return languagetools.get_translation_async(field_value, translation_option)
        return request_translation

    def get_apply_translation_lambda(languagetools, editor, field_index):
        def apply_translation(future_result):
            translation_response = future_result.result()
            translated_text = languagetools.interpret_translation_response_async(translation_response)
            js_command = f"""set_inline_field_value('{constants.EDITOR_WEB_FIELD_ID_TRANSLATION}', {field_index}, "{translated_text}")"""
            editor.web.eval(js_command)
        return apply_translation

    aqt.mw.taskman.run_in_background(get_request_translation_lambda(languagetools, field_value, translation_option), 
                                     get_apply_translation_lambda(languagetools, editor, field_index))

def init(languagetools):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")

    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = f"/_addons/{addon_package}/editor_javascript.js"
        web_content.js.insert(0,  javascript_path)

    def loadNote(editor: aqt.editor.Editor):
        note = editor.note
        deck_note_type = build_deck_note_type_from_note(note)

        inline_translations = languagetools.get_inline_translations(deck_note_type)

        for field_name, target_language in inline_translations.items():
            deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
            apply_inline_translation_changes(languagetools, editor, deck_note_type_field, target_language)

    def onBridge(handled, str, editor):
        # return handled # don't do anything for now
        if not isinstance(editor, aqt.editor.Editor):
            return handled
        if str.startswith("key:"):
            (key_str, field_index_str, note_id_str, field_value) = str.split(':')
            field_index = int(field_index_str)
            note_id = int(note_id_str)
            note = editor.note
            deck_note_type = build_deck_note_type_from_note(note)
            deck_note_type_field = languagetools.get_deck_note_type_field_from_fieldindex(deck_note_type, field_index)
            # check whether we have inline translations on this deck_note_type
            inline_translations = languagetools.get_inline_translations(deck_note_type)
            if deck_note_type_field.field_name in inline_translations:
                # found inline translation, we should update it
                load_inline_translation(languagetools, editor, field_value, deck_note_type_field, inline_translations[deck_note_type_field.field_name])
        return handled


    aqt.gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    aqt.gui_hooks.editor_did_load_note.append(loadNote)
    aqt.gui_hooks.webview_did_receive_js_message.append(onBridge)
