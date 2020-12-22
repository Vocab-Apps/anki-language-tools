# python imports
import os
import random
import requests
import json
from typing import List

# anki imports
import aqt
import aqt.progress
import anki.notes
import anki.cards

from . import constants
from . import version

# util functions
class DeckNoteType():
    def __init__(self, deck_id, deck_name, model_id, model_name):
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.model_id = model_id 
        self.model_name = model_name
    def __str__(self):
        return f'{self.model_name} / {self.deck_name}'

class DeckNoteTypeField():
    def __init__(self, deck_note_type, field_name):
        self.deck_note_type = deck_note_type
        self.field_name = field_name

    def get_model_name(self):
        return self.deck_note_type.model_name

    def get_deck_name(self):
        return self.deck_note_type.deck_name

    def __str__(self):
        return f'{self.get_model_name()} / {self.get_deck_name()} / {self.field_name}'

def build_deck_note_type_from_note_card(note: anki.notes.Note, card: anki.cards.Card) -> DeckNoteType:
    model_id = note.mid
    deck_id = card.did
    deck_note_type = build_deck_note_type(deck_id, model_id)
    return deck_note_type

def build_deck_note_type_from_note(note: anki.notes.Note) -> DeckNoteType:
    model_id = note.mid
    deck_id = note.model()["did"]

    deck_note_type = build_deck_note_type(deck_id, model_id)

    return deck_note_type

def build_deck_note_type(deck_id, model_id) -> DeckNoteType:
    model = aqt.mw.col.models.get(model_id)
    model_name = model['name']
    deck = aqt.mw.col.decks.get(deck_id)
    deck_name = deck['name']
    deck_note_type = DeckNoteType(deck_id, deck_name, model_id, model_name)
    return deck_note_type

def build_deck_note_type_field(deck_id, model_id, field_name) -> DeckNoteTypeField:
    deck_note_type = build_deck_note_type(deck_id, model_id)
    return DeckNoteTypeField(deck_note_type, field_name)


class LanguageTools():

    def __init__(self):
        self.base_url = 'https://cloud-language-tools-6e7b3.ondigitalocean.app'
        if constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL in os.environ:
            self.base_url = os.environ[constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL]
        self.config = aqt.mw.addonManager.getConfig(__name__)

    def initialize(self):
        # get language list
        response = requests.get(self.base_url + '/language_list')
        self.language_list = json.loads(response.content)

        response = requests.get(self.base_url + '/translation_language_list')
        self.translation_language_list = json.loads(response.content)

        response = requests.get(self.base_url + '/transliteration_language_list')
        self.transliteration_language_list = json.loads(response.content)

        if len(self.config[constants.CONFIG_DECK_LANGUAGES]) == 0:
            # suggest running language detection
            result = aqt.utils.askUser('Would you like to run language detection ? It takes a few minutes.', title='Language Tools')
            if result == True:
                self.perform_language_detection()

    def show_about(self):
        text = f'{constants.ADDON_NAME}: v{version.ANKI_LANGUAGE_TOOLS_VERSION}'
        aqt.utils.showInfo(text, title=constants.ADDON_NAME)

    def get_language_name(self, language):
        return self.language_list[language]

    def get_all_languages(self):
        return self.language_list

    def perform_language_detection(self):
        # print('perform_language_detection')
        aqt.mw.progress.start(max=100, min=0, label='language detection', immediate=True)
        aqt.mw.progress.update(label='Retrieving Decks', value=1)

        populated_deck_models = self.get_populated_deck_models()
        step_max = len(populated_deck_models)
        aqt.mw.progress.update(label='Processing Decks', value=2, max=step_max)

        i=0
        for deck_note_type in populated_deck_models:
            self.perform_language_detection_deck_note_type(deck_note_type, i, step_max)
            i += 1

        aqt.mw.progress.finish()

        # display a summary
        wanted_languages = self.config[constants.CONFIG_WANTED_LANGUAGES]

        languages_found = ''
        for key, value in wanted_languages.items():
            entry = f'<b>{self.get_language_name(key)}</b><br/>'
            languages_found += entry
        text = f'Found the following languages:<br/>{languages_found}'
        aqt.utils.showInfo(text, title=f'{constants.MENU_PREFIX} Detection', textFormat="rich")

                
    def get_populated_deck_models(self) -> List[DeckNoteType]:
        deck_list = aqt.mw.col.decks.all_names_and_ids()
        note_types = aqt.mw.col.models.all_names_and_ids()

        result: List[DeckNoteType] = []

        for deck_entry in deck_list:
            for note_type_entry in note_types:
                query = f'did:{deck_entry.id} mid:{note_type_entry.id}'
                notes = aqt.mw.col.find_notes(query)

                if len(notes) > 0:
                    result.append(DeckNoteType(deck_entry.id, deck_entry.name, note_type_entry.id, note_type_entry.name))

        return result

    def get_notes_for_deck_note_type(self, deck_note_type: DeckNoteType):
        query = f'did:{deck_note_type.deck_id} mid:{deck_note_type.model_id}'
        notes = aqt.mw.col.find_notes(query)
        return notes
        
    def perform_language_detection_deck_note_type(self, deck_note_type: DeckNoteType, step_num, step_max):
        label = f'Analyzing {deck_note_type.deck_name} / {deck_note_type.model_name}'
        aqt.mw.progress.update(label=label, value=step_num, max=step_max)

        # print(f'perform_language_detection_deck_note_type, {deck.name}, {note_type.name}')
        notes = self.get_notes_for_deck_note_type(deck_note_type)
        if len(notes) > 0:  
            model = aqt.mw.col.models.get(deck_note_type.model_id)
            fields = model['flds']
            for field in fields:
                field_name = field['name']
                deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
                result = self.perform_language_detection_deck_note_type_field(deck_note_type_field, notes)
                if result != None:
                    self.store_language_detection_result(deck_note_type_field, result)

    def perform_language_detection_deck_note_type_field(self, deck_note_type_field: DeckNoteTypeField, notes):
        # retain notes which have a non-empty field
        sample_size = 100

        all_field_values = [aqt.mw.col.getNote(x)[deck_note_type_field.field_name] for x in notes]
        non_empty_fields = [x for x in all_field_values if len(x) > 0]

        if len(non_empty_fields) == 0:
            # no data to perform detection on
            return None
        
        if len(non_empty_fields) < sample_size:
            field_sample = non_empty_fields
        else:
            field_sample = random.sample(non_empty_fields, sample_size)
        response = requests.post(self.base_url + '/detect', json={
                'text_list': field_sample
        })
        data = json.loads(response.content)
        detected_language = data['detected_language']

        return detected_language

    def guess_language(self, deck_note_type_field: DeckNoteTypeField):
        # retrieve notes
        notes = self.get_notes_for_deck_note_type(deck_note_type_field.deck_note_type)
        return self.perform_language_detection_deck_note_type_field(deck_note_type_field, notes)

    def store_language_detection_result(self, deck_note_type_field: DeckNoteTypeField, language, tooltip=False):
        # write per-deck detected languages

        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name

        if constants.CONFIG_DECK_LANGUAGES not in self.config:
            self.config[constants.CONFIG_DECK_LANGUAGES] = {}
        if model_name not in self.config[constants.CONFIG_DECK_LANGUAGES]:
            self.config[constants.CONFIG_DECK_LANGUAGES][model_name] = {}
        if deck_name not in self.config[constants.CONFIG_DECK_LANGUAGES][model_name]:
            self.config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name] = {}
        self.config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name][field_name] = language

        # store the languages we're interested in
        if constants.CONFIG_WANTED_LANGUAGES not in self.config:
            self.config[constants.CONFIG_WANTED_LANGUAGES] = {}
        self.config[constants.CONFIG_WANTED_LANGUAGES][language] = True

        aqt.mw.addonManager.writeConfig(__name__, self.config)

        if tooltip:
            aqt.utils.tooltip(f'Set {deck_note_type_field} to {self.get_language_name(language)}')

    def add_inline_translation(self, deck_note_type_field: DeckNoteTypeField, translation_option, target_language: str):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name

        if constants.CONFIG_INLINE_TRANSLATION not in self.config:
            self.config[constants.CONFIG_INLINE_TRANSLATION] = {}
        if model_name not in self.config[constants.CONFIG_INLINE_TRANSLATION]:
            self.config[constants.CONFIG_INLINE_TRANSLATION][model_name] = {}
        if deck_name not in self.config[constants.CONFIG_INLINE_TRANSLATION][model_name]:
            self.config[constants.CONFIG_INLINE_TRANSLATION][model_name][deck_name] = {}
        self.config[constants.CONFIG_INLINE_TRANSLATION][model_name][deck_name][field_name] = translation_option

        aqt.mw.addonManager.writeConfig(__name__, self.config)

        aqt.utils.tooltip(f'Add Inline Translation on {deck_note_type_field} to {self.get_language_name(target_language)}')

    def get_inline_translations(self, deck_note_type: DeckNoteType):
        model_name = deck_note_type.model_name
        deck_name = deck_note_type.deck_name

        return self.config.get(constants.CONFIG_INLINE_TRANSLATION, {}).get(model_name, {}).get(deck_name, {})

    def remove_inline_translations(self, deck_note_type_field: DeckNoteTypeField):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name

        if constants.CONFIG_INLINE_TRANSLATION not in self.config:
            return
        if model_name not in self.config[constants.CONFIG_INLINE_TRANSLATION]:
            return
        if deck_name not in self.config[constants.CONFIG_INLINE_TRANSLATION][model_name]:
            return
        del self.config[constants.CONFIG_INLINE_TRANSLATION][model_name][deck_name][field_name]

        aqt.mw.addonManager.writeConfig(__name__, self.config)

        aqt.utils.tooltip(f'Removed Inline Translation on {deck_note_type_field}')


    def get_language(self, deck_note_type_field: DeckNoteTypeField):
        """will return None if no language is associated with this field"""
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name
        return self.config.get(constants.CONFIG_DECK_LANGUAGES, {}).get(model_name, {}).get(deck_name, {}).get(field_name, None)

    def get_wanted_languages(self):
        return self.config[constants.CONFIG_WANTED_LANGUAGES].keys()

    def get_translation_async(self, source_text, translation_option):
        response = requests.post(self.base_url + '/translate', json={
            'text': source_text,
            'service': translation_option['service'],
            'from_language_key': translation_option['source_language_id'],
            'to_language_key': translation_option['target_language_id']
        })
        return response

    def interpret_translation_response_async(self, response):
        if response.status_code == 200:
            data = json.loads(response.content)
            return data['translated_text'] 
        if response.status_code == 400:
            data = json.loads(response.content)
            error_text = f"Could not load translation: {data['error']}"
            aqt.utils.showCritical(f"{constants.MENU_PREFIX} {error_text}")
            return error_text
        error_text = f"Could not load translation: {response.text}"
        aqt.utils.showCritical(f"{constants.MENU_PREFIX} {error_text}")
        return error_text


    def get_translation_all(self, source_text, from_language, to_language):
        response = requests.post(self.base_url + '/translate_all', json={
                'text': source_text,
                'from_language': from_language,
                'to_language': to_language
        })
        data = json.loads(response.content)        
        return data
    
    def get_transliteration(self, source_text, service, transliteration_key):
        response = requests.post(self.base_url + '/transliterate', json={
                'text': source_text,
                'service': service,
                'transliteration_key': transliteration_key
        })
        data = json.loads(response.content)
        return data['transliterated_text']

    def get_transliteration_options(self, language):
        candidates = [x for x in self.transliteration_language_list if x['language_code'] == language]
        return candidates

    def build_translation_option(self, service, source_language_id, target_language_id):
        return {
            'service': service,
            'source_language_id': source_language_id,
            'target_language_id': target_language_id
        }
        

    def get_translation_options(self, source_language: str, target_language: str):
        # get list of services which support source_language
        translation_options = []
        source_language_options = [x for x in self.translation_language_list if x['language_code'] == source_language]
        for source_language_option in source_language_options:
            service = source_language_option['service']
            # find out whether target language is supported
            target_language_options = [x for x in self.translation_language_list if x['language_code'] == target_language and x['service'] == service]
            if len(target_language_options) == 1:
                # found an option
                target_language_option = target_language_options[0]
                translation_option = self.build_translation_option(service, source_language_option['language_id'], target_language_option['language_id'])
                translation_options.append(translation_option)
        return translation_options


    def get_deck_note_type_field_from_fieldindex(self, deck_note_type: DeckNoteType, field_index) -> DeckNoteTypeField:
        model = aqt.mw.col.models.get(deck_note_type.model_id)
        fields = model['flds']
        field_name = fields[field_index]['name']
        return DeckNoteTypeField(deck_note_type, field_name)

