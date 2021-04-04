#python imports
import json
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
from .languagetools import LanguageTools, DeckNoteTypeField, build_deck_note_type, build_deck_note_type_from_note, build_deck_note_type_from_note_card, build_deck_note_type_from_addcard, LanguageToolsRequestError, AnkiNoteEditorError
from . import constants


def get_field_id(deck_note_type_field: DeckNoteTypeField):
    model = aqt.mw.col.models.get(deck_note_type_field.deck_note_type.model_id)
    fields = model['flds']
    field_names = [x['name'] for x in fields]
    field_index = field_names.index(deck_note_type_field.field_name)
    return field_index    

def configure_editor_fields(editor: aqt.editor.Editor, field_options):
    # logging.debug(f'configure_editor_fields, field_options: {field_options}')
    js_command = f"configure_languagetools_fields({json.dumps(field_options)})"
    # print(js_command)
    editor.web.eval(js_command)

def show_loading_indicator(editor: aqt.editor.Editor, field_index):
    js_command = f"show_loading_indicator({field_index})"
    # print(js_command)
    editor.web.eval(js_command)

def hide_loading_indicator(editor: aqt.editor.Editor, field_index, original_field_value):
    js_command = f"""hide_loading_indicator({field_index}, "{original_field_value}")"""
    # print(js_command)
    editor.web.eval(js_command)


# generic function to load a transformation asynchronously (translation / transliteration / audio)
def load_transformation(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, request_transformation_fn, interpret_response_fn):
    field_index = get_field_id(to_deck_note_type_field)

    def apply_field_value(field_index, result_text):
        # set the field value on the note
        editor.note.fields[field_index] = result_text
        # update the webview
        js_command = f"""set_field_value({field_index}, "{result_text}")"""
        editor.web.eval(js_command)        

    # is the source field empty ?
    if languagetools.field_empty(field_value):
        apply_field_value(field_index, '')
        return

    def get_apply_transformation_lambda(languagetools, editor, field_index, original_note_id, original_field_value, interpret_response_fn):
        def apply_transformation(future_result):
            if editor.note == None:
                # user has left the editor
                return
            if original_note_id != 0:
                if editor.note.id != original_note_id:
                    # user switched to a different note, ignore
                    return

            hide_loading_indicator(editor, field_index, original_field_value)
            transformation_response = future_result.result()
            try:
                result_text = interpret_response_fn(transformation_response)
                apply_field_value(field_index, result_text)
            except LanguageToolsRequestError as e:
                aqt.utils.showCritical(str(e), title=constants.ADDON_NAME)
        return apply_transformation

    show_loading_indicator(editor, field_index)

    aqt.mw.taskman.run_in_background(request_transformation_fn, 
                                     get_apply_transformation_lambda(languagetools, editor, field_index, original_note_id, field_value, interpret_response_fn))



def load_translation(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, translation_option: Dict):
    def get_request_translation_lambda(languagetools, field_value, translation_option):
        def request_translation():
            return languagetools.get_translation_async(field_value, translation_option)
        return request_translation
    interpret_response_fn = languagetools.interpret_translation_response_async

    load_transformation(languagetools, editor, original_note_id, field_value, to_deck_note_type_field, get_request_translation_lambda(languagetools, field_value, translation_option), interpret_response_fn)


def load_transliteration(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, transliteration_option: Dict):
    def get_request_transliteration_lambda(languagetools, field_value, transliteration_option):
        def request_transliteration():
            return languagetools.get_transliteration_async(field_value, transliteration_option)
        return request_transliteration
    interpret_response_fn = languagetools.interpret_transliteration_response_async

    load_transformation(languagetools, editor, original_note_id, field_value, to_deck_note_type_field, get_request_transliteration_lambda(languagetools, field_value, transliteration_option), interpret_response_fn)


def load_audio(languagetools, editor: aqt.editor.Editor, original_note_id, field_value: str, to_deck_note_type_field: DeckNoteTypeField, voice: Dict):
    def get_request_audio_lambda(languagetools, field_value, voice):
        def request_audio():
            try:
                return languagetools.generate_audio_tag_collection(field_value, voice)
            except LanguageToolsRequestError as err:
                return {'error': str(err)}
        return request_audio

    def interpret_response_fn(response):
        if 'error' in response:
            # just re-raise
            raise LanguageToolsRequestError('Could not generate audio: ' + response['error'])
        sound_tag = response['sound_tag']
        full_filename = response['full_filename']
        if sound_tag == None:
            return ''
        # sound is valid, play sound
        aqt.sound.av_player.play_file(full_filename)            
        return sound_tag

    load_transformation(languagetools, editor, original_note_id, field_value, to_deck_note_type_field, get_request_audio_lambda(languagetools, field_value, voice), interpret_response_fn)


def editor_get_decknotetype(editor, languagetools):
    note = editor.note
    if note == None:
        raise languagetools.AnkiNoteEditorError(f'editor.note not found')

    if editor.addMode:
        deck_note_type = build_deck_note_type_from_addcard(note, editor.parentWindow)
    else:
        deck_note_type = build_deck_note_type_from_note_card(note, editor.card)

    return deck_note_type


def editor_get_dntf(editor, languagetools, field_index):
    deck_note_type = editor_get_decknotetype(editor, languagetools)
    deck_note_type_field = languagetools.get_deck_note_type_field_from_fieldindex(deck_note_type, field_index)
    return deck_note_type_field

def init(languagetools):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")

    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = f"/_addons/{addon_package}/editor_javascript.js"
        css_path = f"/_addons/{addon_package}/editor_style.css"
        web_content.js.append(javascript_path)
        web_content.css.append(css_path)

    def loadNote(editor: aqt.editor.Editor):
        note = editor.note
        deck_note_type = editor_get_decknotetype(editor, languagetools)

        model = note.model()
        fields = model['flds']
        field_options = []
        for index, field in enumerate(fields):
            field_name = field['name']

            field_type ='regular'
            # is this field a sound field ?
            dntf = DeckNoteTypeField(deck_note_type, field_name)
            field_language = languagetools.get_language(dntf)
            if field_language != None:
                if field_language == constants.SpecialLanguage.sound.name:
                    # add_play_sound_collection(editor, index, field_name)
                    field_type = 'sound'
                elif field_language in languagetools.get_voice_selection_settings(): # is there a voice associated with this language ?
                    # add_tts_speak(editor, index, field_name)
                    field_type = 'language'
            field_options.append(field_type)
        configure_editor_fields(editor, field_options)
        



    def onBridge(handled, str, editor):
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

            utils.play_anki_sound_tag(sound_tag)
            return handled

        if str.startswith('ttsspeak:'):
            logging.debug(f'ttsspeak command: [{str}]')
            components = str.split(':')
            field_index_str = components[1]
            field_index = int(field_index_str)

            note = editor.note
            source_text = note.fields[field_index]
            logging.debug(f'source_text: {source_text}')

            try:

                from_deck_note_type_field = editor_get_dntf(editor, languagetools, field_index)

                # do we have a voice set ?
                field_language = languagetools.get_language(from_deck_note_type_field)
                if field_language == None:
                    raise AnkiNoteEditorError(f'No language set for field {from_deck_note_type_field}')
                voice_selection_settings = languagetools.get_voice_selection_settings()
                if field_language not in voice_selection_settings:
                    raise AnkiNoteEditorError(f'No voice set for language {languagetools.get_language_name(field_language)}')
                voice = voice_selection_settings[field_language]

                def play_audio(languagetools, source_text, voice):
                    voice_key = voice['voice_key']
                    service = voice['service']

                    try:
                        filename = languagetools.get_tts_audio(source_text, service, voice_key, {})
                        if filename != None:
                            aqt.sound.av_player.play_file(filename)
                    except LanguageToolsRequestError as err:
                        pass

                def play_audio_done(future_result):
                    pass

                aqt.mw.taskman.run_in_background(lambda: play_audio(languagetools, source_text, voice), lambda x: play_audio_done(x))

            except AnkiNoteEditorError as e:
                # logging.error('Could not speak', exc_info=True)
                aqt.utils.showCritical(repr(e))

            return handled

        if languagetools.get_apply_updates_automatically() == False:
            # user doesn't want updates as they type
            return handled

        if str.startswith("key:"):
            # print(str)
            components = str.split(':')
            if len(components) >= 4:
                field_index_str = components[1]
                note_id_str = components[2]
                field_value = ':'.join(components[3:])
                field_index = int(field_index_str)
                note_id = int(note_id_str)
                note = editor.note
                note_id = note.id

                from_deck_note_type_field = from_deck_note_type_field = editor_get_dntf(editor, languagetools, field_index)
                deck_note_type = from_deck_note_type_field.deck_note_type

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
