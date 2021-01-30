#python imports
import json
import urllib.parse
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
from .languagetools import LanguageTools, DeckNoteTypeField, build_deck_note_type, build_deck_note_type_from_note, build_deck_note_type_from_note_card, build_deck_note_type_from_addcard, LanguageToolsRequestError
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


def load_translation(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, translation_option: Dict):
    field_index = get_field_id(to_deck_note_type_field)

    # print(f'load_translation, to_deck_note_type_field: {to_deck_note_type_field} field_index: {field_index} translation_option: {translation_option}')

    # now, we need to do the translation, asynchronously
    # prepare lambdas
    #     
    def get_request_translation_lambda(languagetools, field_value, translation_option):
        def request_translation():
            return languagetools.get_translation_async(field_value, translation_option)
        return request_translation

    def get_apply_translation_lambda(languagetools, editor, field_index, original_note_id):
        def apply_translation(future_result):
            if original_note_id != 0:
                if editor.note.id != original_note_id:
                    # user switched to a different note, ignore
                    return

            translation_response = future_result.result()
            try:
                translated_text = languagetools.interpret_translation_response_async(translation_response)
                # set the field value on the note
                editor.note.fields[field_index] = translated_text
                # update the webview
                js_command = f"""set_field_value({field_index}, "{translated_text}")"""
                editor.web.eval(js_command)
            except LanguageToolsRequestError as e:
                aqt.utils.showCritical(str(e), title=constants.ADDON_NAME)
        return apply_translation

    aqt.mw.taskman.run_in_background(get_request_translation_lambda(languagetools, field_value, translation_option), 
                                     get_apply_translation_lambda(languagetools, editor, field_index, original_note_id))

def load_transliteration(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, transliteration_option: Dict):
    field_index = get_field_id(to_deck_note_type_field)

    # print(f'load_transliteration, to_deck_note_type_field: {to_deck_note_type_field} field_index: {field_index} translation_option: {transliteration_option}')

    # now, we need to do the translation, asynchronously
    # prepare lambdas
    #     
    def get_request_transliteration_lambda(languagetools, field_value, transliteration_option):
        def request_transliteration():
            return languagetools.get_transliteration_async(field_value, transliteration_option)
        return request_transliteration

    def get_apply_transliteration_lambda(languagetools, editor, field_index, original_note_id):
        def apply_transliteration(future_result):
            if original_note_id != 0:
                if editor.note.id != original_note_id:
                    # user switched to a different note, ignore
                    return

            translation_response = future_result.result()
            try:
                translated_text = languagetools.interpret_transliteration_response_async(translation_response)
                # set the field value on the note
                editor.note.fields[field_index] = translated_text
                # update the webview
                js_command = f"""set_field_value({field_index}, "{translated_text}")"""
                editor.web.eval(js_command)
            except LanguageToolsRequestError as e:
                aqt.utils.showCritical(str(e), title=constants.ADDON_NAME)
                                
        return apply_transliteration

    aqt.mw.taskman.run_in_background(get_request_transliteration_lambda(languagetools, field_value, transliteration_option), 
                                     get_apply_transliteration_lambda(languagetools, editor, field_index, original_note_id))

def load_audio(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, voice: Dict):
    field_index = get_field_id(to_deck_note_type_field)

    # print(f'load_audio, to_deck_note_type_field: {to_deck_note_type_field} field_index: {field_index} voice: {voice}')

    # now, we need to do the translation, asynchronously
    # prepare lambdas
    #     
    def get_request_audio_lambda(languagetools, field_value, voice):
        def request_audio():
            return languagetools.generate_audio_tag_collection(field_value, voice)
        return request_audio

    def get_apply_audio_lambda(languagetools, editor, field_index, original_note_id):
        def apply_audio(future_result):
            if original_note_id != 0:
                if editor.note.id != original_note_id:
                    # user switched to a different note, ignore
                    return

            sound_tag, full_filename = future_result.result()
            if sound_tag == None:
                sound_tag = ''
                editor.note.fields[field_index] = sound_tag
                js_command = f"""set_field_value({field_index}, "")"""
                editor.web.eval(js_command)                
            else:
                # set sound tag, and play sound
                editor.note.fields[field_index] = sound_tag
                js_command = f"""set_field_value({field_index}, "{sound_tag}")"""
                editor.web.eval(js_command)
                # play sound
                aqt.sound.av_player.play_file(full_filename)

        return apply_audio

    aqt.mw.taskman.run_in_background(get_request_audio_lambda(languagetools, field_value, voice), 
                                     get_apply_audio_lambda(languagetools, editor, field_index, original_note_id))




def init(languagetools):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")

    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = f"/_addons/{addon_package}/editor_javascript.js"
        web_content.js.insert(0,  javascript_path)

    def loadNote(editor: aqt.editor.Editor):
        return # disable for now, and inline translations should be retired

        note = editor.note
        # can we get the card from the editor ?
        if editor.card != None:
            deck_note_type = build_deck_note_type_from_note_card(note, editor.card)
        else:
            deck_note_type = build_deck_note_type_from_note(note)
        # print(f'loadNote, deck_note_type: {deck_note_type}')

        inline_translations = languagetools.get_inline_translations(deck_note_type)
        # print(f'loadNote {deck_note_type} inline_translations: {inline_translations}')

        for field_name, target_language in inline_translations.items():
            deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
            apply_inline_translation_changes(languagetools, editor, deck_note_type_field, target_language)

    def onBridge(handled, str, editor):
        # return handled # don't do anything for now
        if not isinstance(editor, aqt.editor.Editor):
            return handled

        if languagetools.get_apply_updates_automatically() == False:
            # user doesn't want updates as they type
            return handled

        if str.startswith("key:"):
            components = str.split(':')
            if len(components) == 4:
                (key_str, field_index_str, note_id_str, field_value) = components
                field_index = int(field_index_str)
                note_id = int(note_id_str)
                note = editor.note
                note_id = note.id

                if editor.addMode:
                    deck_note_type = build_deck_note_type_from_addcard(note, editor.parentWindow)
                    #print(f'deck_note_type: {deck_note_type}')
                else:
                    deck_note_type = build_deck_note_type_from_note_card(note, editor.card)
                    # print(f'deck_note_type: {deck_note_type}')

                from_deck_note_type_field = languagetools.get_deck_note_type_field_from_fieldindex(deck_note_type, field_index)

                original_field_value = note[from_deck_note_type_field.field_name]

                # print(f'new field value: [{field_value}] original field value: [{original_field_value}]')

                if field_value != original_field_value:
                    # only do something if the field has changed

                    # do we have translation rules for this deck_note_type
                    translation_settings = languagetools.get_batch_translation_settings(deck_note_type)
                    relevant_settings = {to_field:value for (to_field,value) in translation_settings.items() if value['from_field'] == from_deck_note_type_field.field_name}
                    for to_field, value in relevant_settings.items():
                        to_deck_note_type_field = DeckNoteTypeField(deck_note_type, to_field)
                        load_translation(languagetools, editor, note_id, field_value, to_deck_note_type_field, value['translation_option'])

                    # do we have transliteration rules for this deck_note_type
                    transliteration_settings = languagetools.get_batch_transliteration_settings(deck_note_type)
                    relevant_settings = {to_field:value for (to_field,value) in transliteration_settings.items() if value['from_field'] == from_deck_note_type_field.field_name}
                    for to_field, value in relevant_settings.items():
                        to_deck_note_type_field = DeckNoteTypeField(deck_note_type, to_field)
                        load_transliteration(languagetools, editor, note_id, field_value, to_deck_note_type_field, value['transliteration_option'])

                    # do we have any audio rules for this deck_note_type
                    audio_settings = languagetools.get_batch_audio_settings(deck_note_type)
                    relevant_settings = {to_field:from_field for (to_field,from_field) in audio_settings.items() if from_field == from_deck_note_type_field.field_name}
                    for to_field, from_field in relevant_settings.items():
                        to_deck_note_type_field = DeckNoteTypeField(deck_note_type, to_field)
                        # get the from language
                        from_language = languagetools.get_language(from_deck_note_type_field)
                        if from_language != None:
                            # get voice for this language
                            voice_settings = languagetools.get_voice_selection_settings()
                            if from_language in voice_settings:
                                voice = voice_settings[from_language]
                                load_audio(languagetools, editor, note_id, field_value, to_deck_note_type_field, voice)



        return handled


    aqt.gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    aqt.gui_hooks.editor_did_load_note.append(loadNote)
    aqt.gui_hooks.webview_did_receive_js_message.append(onBridge)
