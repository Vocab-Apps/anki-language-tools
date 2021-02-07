# python imports
import os
import re
import random
import requests
import json
import tempfile
from typing import List, Dict
import hashlib
import anki.utils

# anki imports
import aqt
import aqt.progress
import aqt.addcards
import anki.notes
import anki.cards

from . import constants
from . import version

# util functions

class AnkiItemNotFoundError(Exception):
    pass

class LanguageToolsRequestError(Exception):
    pass

class DeckNoteType():
    def __init__(self, deck_id, deck_name, model_id, model_name):
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.model_id = model_id 
        self.model_name = model_name
    def __str__(self):
        return f'{self.model_name} / {self.deck_name}'

    def __eq__(self, other):
        if type(other) is type(self):
            return self.deck_id == other.deck_id and self.model_id == other.model_id
        else:
            return False    

    def __hash__(self):
        return hash((self.deck_id, self.model_id))

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

    def __eq__(self, other):
        if type(other) is type(self):
            return self.deck_note_type == other.deck_note_type and self.field_name == other.field_name
        else:
            return False    

    def __hash__(self):
        return hash((self.deck_note_type, self.field_name))

class Deck():
    def __init__(self):
        self.note_type_map = {}

    def add_deck_note_type_field(self, deck_note_type_field: DeckNoteTypeField):
        note_type = deck_note_type_field.get_model_name()
        if note_type not in self.note_type_map:
            self.note_type_map[note_type] = []
        self.note_type_map[note_type].append(deck_note_type_field)

def build_deck_note_type_from_note_card(note: anki.notes.Note, card: anki.cards.Card) -> DeckNoteType:
    model_id = note.mid
    deck_id = card.did
    deck_note_type = build_deck_note_type(deck_id, model_id)
    return deck_note_type

def build_deck_note_type_from_addcard(note: anki.notes.Note, add_cards: aqt.addcards.AddCards) -> DeckNoteType:
    model_id = note.mid
    deck_id = add_cards.deckChooser.selectedId()
    deck_note_type = build_deck_note_type(deck_id, model_id)
    return deck_note_type    

def build_deck_note_type_from_note(note: anki.notes.Note) -> DeckNoteType:
    model_id = note.mid
    deck_id = note.model()["did"]

    deck_note_type = build_deck_note_type(deck_id, model_id)

    return deck_note_type

def build_deck_note_type(deck_id, model_id) -> DeckNoteType:
    model = aqt.mw.col.models.get(model_id)
    if model == None:
        raise AnkiItemNotFoundError(f'Note Type id {model_id} not found')
    model_name = model['name']
    deck = aqt.mw.col.decks.get(deck_id)
    if deck == None:
        raise AnkiItemNotFoundError(f'Deck id {deck_id} not found')
    deck_name = deck['name']
    deck_note_type = DeckNoteType(deck_id, deck_name, model_id, model_name)
    return deck_note_type

def build_deck_note_type_field(deck_id, model_id, field_name) -> DeckNoteTypeField:
    deck_note_type = build_deck_note_type(deck_id, model_id)
    return DeckNoteTypeField(deck_note_type, field_name)

def build_deck_note_type_field_from_names(deck_name, model_name, field_name) -> DeckNoteTypeField:
    # get the deck_id from the deck_name
    # get the model_id from the model_name

    model_id = aqt.mw.col.models.id_for_name(model_name)
    deck_id = aqt.mw.col.decks.id_for_name(deck_name)

    if model_id == None:
        raise AnkiItemNotFoundError(f'Note Type {model_name} not found')
    if deck_id == None:
        raise AnkiItemNotFoundError(f'Deck {deck_name} not found')

    deck_note_type = build_deck_note_type(deck_id, model_id)
    return DeckNoteTypeField(deck_note_type, field_name)


class LanguageTools():

    def __init__(self):
        self.base_url = 'https://cloud-language-tools-prod.anki.study'
        if constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL in os.environ:
            self.base_url = os.environ[constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL]
        self.config = aqt.mw.addonManager.getConfig(__name__)

        self.collectionLoaded = False
        self.mainWindowInitialized = False
        self.deckBrowserRendered = False
        self.initDone = False

        self.api_key_checked = False

    def setCollectionLoaded(self):
        self.collectionLoaded = True
        self.checkInitialize()

    def setMainWindowInit(self):
        self.mainWindowInitialized = True
        self.checkInitialize()

    def setDeckBrowserRendered(self):
        self.deckBrowserRendered = True
        self.checkInitialize()

    def checkInitialize(self):
        if self.collectionLoaded and self.mainWindowInitialized and self.deckBrowserRendered and self.initDone == False:
            aqt.mw.taskman.run_in_background(self.initialize, self.initializeDone)

    def initialize(self):
        self.initDone = True

        # get language list
        response = requests.get(self.base_url + '/language_list')
        self.language_list = json.loads(response.content)

        response = requests.get(self.base_url + '/translation_language_list')
        self.translation_language_list = json.loads(response.content)

        response = requests.get(self.base_url + '/transliteration_language_list')
        self.transliteration_language_list = json.loads(response.content)

        # do we have an API key in the config ?
        if len(self.config['api_key']) > 0:
            validation_result = self.api_key_validate_query(self.config['api_key'])
            if validation_result['key_valid'] == True:
                self.api_key_checked = True

    def initializeDone(self, future):
        pass

    def get_api_key_checked(self):
        return self.api_key_checked

    def run_api_key_verification(self):
        (api_key, return_code) = aqt.utils.getText(f'{constants.MENU_PREFIX} Enter API Key', title=constants.MENU_PREFIX, default=self.config['api_key'])
        result = self.api_key_validate_query(api_key)
        if result['key_valid'] == True:
            self.config['api_key'] = api_key
            aqt.mw.addonManager.writeConfig(__name__, self.config)
            aqt.utils.showInfo(f"API Key is valid: {result['msg']}", title=constants.MENU_PREFIX)
            self.api_key_checked = True
            return True
        else:
            aqt.utils.showInfo(result['msg'], title=constants.MENU_PREFIX)
            return False


    def check_api_key_valid(self):
        # print(f'self.api_key_checked: {self.api_key_checked}')
        if self.api_key_checked:
            return True
        return self.run_api_key_verification()

    def api_key_validate_query(self, api_key):
        response = requests.post(self.base_url + '/verify_api_key', json={
            'api_key': api_key
        })
        data = json.loads(response.content)
        return data

    def language_detection_done(self):
        return len(self.config[constants.CONFIG_DECK_LANGUAGES]) > 0

    def show_about(self):
        text = f'{constants.ADDON_NAME}: v{version.ANKI_LANGUAGE_TOOLS_VERSION}'
        aqt.utils.showInfo(text, title=constants.ADDON_NAME)

    def get_language_name(self, language):
        if language == None:
            return 'Not set'
        if language == constants.SpecialLanguage.transliteration.name:
            return 'Transliteration'
        if language == constants.SpecialLanguage.sound.name:
            return 'Sound'
        return self.language_list[language]

    def language_available_for_translation(self, language):
        if language == None:
            return False
        if language == constants.SpecialLanguage.transliteration.name:
            return False
        if language == constants.SpecialLanguage.sound.name:
            return False
        return True

    def get_all_languages(self):
        return self.language_list

    def get_all_language_arrays(self):
        # return two arrays, one with the codes, one with the human descriptions
        language_dict = self.get_all_languages()
        language_list = []
        for key, name in language_dict.items():
            language_list.append({'key': key, 'name': name})
        # sort by language name
        language_list = sorted(language_list, key=lambda x: x['name'])
        language_code_list = [x['key'] for x in language_list]
        language_name_list = [x['name'] for x in language_list]

        # add the special languages
        language_name_list.append('Transliteration')
        language_code_list.append(constants.SpecialLanguage.transliteration.name)
        language_name_list.append('Sound')
        language_code_list.append(constants.SpecialLanguage.sound.name)

        return {'language_name_list': language_name_list,
                'language_code_list': language_code_list
        }

    def get_wanted_language_arrays(self):
        wanted_languages = self.get_wanted_languages()
        language_dict = self.get_all_languages()

        language_list = []
        for key in wanted_languages:
            language_list.append({'key': key, 'name': language_dict[key]})
        # sort by language name
        language_list = sorted(language_list, key=lambda x: x['name'])
        language_code_list = [x['key'] for x in language_list]
        language_name_list = [x['name'] for x in language_list]

        return {'language_name_list': language_name_list,
                'language_code_list': language_code_list
        }        

    def get_populated_dntf(self) -> List[DeckNoteTypeField]:
        populated_set = aqt.mw.col.db.all("select did, mid from notes inner join cards on notes.id = cards.nid group by mid, did")
        #print(populated_set)
        
        deck_list = aqt.mw.col.decks.all_names_and_ids()
        note_types = aqt.mw.col.models.all_names_and_ids()

        result: List[DeckNoteTypeField] = []

        for entry in populated_set:
            deck_id = entry[0]
            model_id = entry[1]
            deck_note_type = build_deck_note_type(deck_id, model_id)
            model = aqt.mw.col.models.get(model_id)
            fields = model['flds']
            for field in fields:
                field_name = field['name']
                deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
                result.append(deck_note_type_field)

        return result


    def get_populated_decks(self) -> Dict[str, Deck]:
        deck_note_type_field_list: List[DeckNoteTypeField] = self.get_populated_dntf()
        deck_map = {}
        for deck_note_type_field in deck_note_type_field_list:
            deck_name = deck_note_type_field.deck_note_type.deck_name
            if deck_name not in deck_map:
                deck_map[deck_name] = Deck()
            deck_map[deck_name].add_deck_note_type_field(deck_note_type_field)
        return deck_map
            
    def get_notes_for_deck_note_type(self, deck_note_type: DeckNoteType):
        query = f'deck:"{deck_note_type.deck_name}" note:"{deck_note_type.model_name}"'
        notes = aqt.mw.col.find_notes(query)
        return notes

    def field_empty(self, field_value: str) -> bool:
        stripped_field_value = anki.utils.htmlToTextLine(field_value)
        return len(stripped_field_value) == 0

    def get_field_samples(self, deck_note_type_field: DeckNoteTypeField, sample_size: int) -> List[str]:
        notes = self.get_notes_for_deck_note_type(deck_note_type_field.deck_note_type)

        stripImagesRe = re.compile("(?i)<img[^>]+src=[\"']?([^\"'>]+)[\"']?[^>]*>")
        
        def process_field_value(note_id, field_name):
            note = aqt.mw.col.getNote(note_id)
            if field_name not in note:
                # field was removed
                raise AnkiItemNotFoundError(f'field {field_name} not found')
            original_field_value = note[field_name]
            field_value = stripImagesRe.sub('', original_field_value)
            field_value = anki.utils.htmlToTextLine(field_value)
            max_len = 200 # restrict to 200 characters
            if len(original_field_value) > max_len:
                field_value = original_field_value[:max_len]
            return field_value

        all_field_values = [process_field_value(x, deck_note_type_field.field_name) for x in notes]
        non_empty_fields = [x for x in all_field_values if len(x) > 0]

        if len(non_empty_fields) < sample_size:
            field_sample = non_empty_fields
        else:
            field_sample = random.sample(non_empty_fields, sample_size)

        return field_sample

    def get_field_samples_for_language(self, language_code, sample_size):
        # self.config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name][field_name] = language

        dntf_list = []
        for model_name, model_data in self.config[constants.CONFIG_DECK_LANGUAGES].items():
            for deck_name, deck_data in model_data.items():
                for field_name, field_language_code in deck_data.items():
                    if field_language_code == language_code:
                        try:
                            # found the language we need
                            deck_note_type_field = build_deck_note_type_field_from_names(deck_name, model_name, field_name)
                            dntf_list.append(deck_note_type_field)
                        except AnkiItemNotFoundError as error:
                            # this deck probably got deleted
                            pass

        all_field_samples = []
        for dntf in dntf_list:
            try:
                field_samples = self.get_field_samples(dntf, sample_size)
                all_field_samples.extend(field_samples)
            except AnkiItemNotFoundError as error:
                # might be a field missing
                pass                
        
        # pick random sample
        if len(all_field_samples) < sample_size:
            result = all_field_samples
        else:
            result = random.sample(all_field_samples, sample_size)
        
        return result


    def perform_language_detection_deck_note_type_field(self, deck_note_type_field: DeckNoteTypeField):
        # get a random sample of data within this field

        sample_size = 100 # max supported by azure
        field_sample = self.get_field_samples(deck_note_type_field, sample_size)
        if len(field_sample) == 0:
            return None

        response = requests.post(self.base_url + '/detect', json={
                'text_list': field_sample
        }, headers={'api_key': self.config['api_key']})
        if response.status_code == 200:
            data = json.loads(response.content)
            detected_language = data['detected_language']

            return detected_language
        else:
            # error occured, return none
            return None

    def guess_language(self, deck_note_type_field: DeckNoteTypeField):
        # retrieve notes
        return self.perform_language_detection_deck_note_type_field(deck_note_type_field)

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
        if self.language_available_for_translation(language):
            if constants.CONFIG_WANTED_LANGUAGES not in self.config:
                self.config[constants.CONFIG_WANTED_LANGUAGES] = {}
            self.config[constants.CONFIG_WANTED_LANGUAGES][language] = True

        aqt.mw.addonManager.writeConfig(__name__, self.config)

        if tooltip:
            aqt.utils.tooltip(f'Set {deck_note_type_field} to {self.get_language_name(language)}')
 
    def store_batch_translation_setting(self, deck_note_type_field: DeckNoteTypeField, source_field: str, translation_option):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name

        if constants.CONFIG_BATCH_TRANSLATION not in self.config:
            self.config[constants.CONFIG_BATCH_TRANSLATION] = {}
        if model_name not in self.config[constants.CONFIG_BATCH_TRANSLATION]:
            self.config[constants.CONFIG_BATCH_TRANSLATION][model_name] = {}
        if deck_name not in self.config[constants.CONFIG_BATCH_TRANSLATION][model_name]:
            self.config[constants.CONFIG_BATCH_TRANSLATION][model_name][deck_name] = {}
        self.config[constants.CONFIG_BATCH_TRANSLATION][model_name][deck_name][field_name] = {
            'from_field': source_field,
            'translation_option': translation_option
        }
        aqt.mw.addonManager.writeConfig(__name__, self.config)

    def remove_translation_setting(self, deck_note_type_field: DeckNoteTypeField):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name        
        del self.config[constants.CONFIG_BATCH_TRANSLATION][model_name][deck_name][field_name]
        aqt.mw.addonManager.writeConfig(__name__, self.config)

    def store_batch_transliteration_setting(self, deck_note_type_field: DeckNoteTypeField, source_field: str, transliteration_option):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name

        if constants.CONFIG_BATCH_TRANSLITERATION not in self.config:
            self.config[constants.CONFIG_BATCH_TRANSLITERATION] = {}
        if model_name not in self.config[constants.CONFIG_BATCH_TRANSLITERATION]:
            self.config[constants.CONFIG_BATCH_TRANSLITERATION][model_name] = {}
        if deck_name not in self.config[constants.CONFIG_BATCH_TRANSLITERATION][model_name]:
            self.config[constants.CONFIG_BATCH_TRANSLITERATION][model_name][deck_name] = {}
        self.config[constants.CONFIG_BATCH_TRANSLITERATION][model_name][deck_name][field_name] = {
            'from_field': source_field,
            'transliteration_option': transliteration_option
        }
        aqt.mw.addonManager.writeConfig(__name__, self.config)

        # the language for the target field should be set to transliteration
        self.store_language_detection_result(deck_note_type_field, constants.SpecialLanguage.transliteration.name)

    def remove_transliteration_setting(self, deck_note_type_field: DeckNoteTypeField):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name        
        del self.config[constants.CONFIG_BATCH_TRANSLITERATION][model_name][deck_name][field_name]
        aqt.mw.addonManager.writeConfig(__name__, self.config)

    def get_batch_translation_settings(self, deck_note_type: DeckNoteType):
        model_name = deck_note_type.model_name
        deck_name = deck_note_type.deck_name

        return self.config.get(constants.CONFIG_BATCH_TRANSLATION, {}).get(model_name, {}).get(deck_name, {})

    def get_batch_transliteration_settings(self, deck_note_type: DeckNoteType):
        model_name = deck_note_type.model_name
        deck_name = deck_note_type.deck_name

        return self.config.get(constants.CONFIG_BATCH_TRANSLITERATION, {}).get(model_name, {}).get(deck_name, {})

    def store_batch_audio_setting(self, deck_note_type_field: DeckNoteTypeField, source_field: str):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name

        if constants.CONFIG_BATCH_AUDIO not in self.config:
            self.config[constants.CONFIG_BATCH_AUDIO] = {}
        if model_name not in self.config[constants.CONFIG_BATCH_AUDIO]:
            self.config[constants.CONFIG_BATCH_AUDIO][model_name] = {}
        if deck_name not in self.config[constants.CONFIG_BATCH_AUDIO][model_name]:
            self.config[constants.CONFIG_BATCH_AUDIO][model_name][deck_name] = {}
        self.config[constants.CONFIG_BATCH_AUDIO][model_name][deck_name][field_name] = source_field
        aqt.mw.addonManager.writeConfig(__name__, self.config)

        # the language for the target field should be set to sound
        self.store_language_detection_result(deck_note_type_field, constants.SpecialLanguage.sound.name)

    def remove_audio_setting(self, deck_note_type_field: DeckNoteTypeField):
        model_name = deck_note_type_field.get_model_name()
        deck_name = deck_note_type_field.get_deck_name()
        field_name = deck_note_type_field.field_name        
        del self.config[constants.CONFIG_BATCH_AUDIO][model_name][deck_name][field_name]
        aqt.mw.addonManager.writeConfig(__name__, self.config)

    def get_batch_audio_settings(self, deck_note_type: DeckNoteType):
        model_name = deck_note_type.model_name
        deck_name = deck_note_type.deck_name

        return self.config.get(constants.CONFIG_BATCH_AUDIO, {}).get(model_name, {}).get(deck_name, {})

    def store_voice_selection(self, language_code, voice_mapping):
        self.config[constants.CONFIG_VOICE_SELECTION][language_code] = voice_mapping
        aqt.mw.addonManager.writeConfig(__name__, self.config)

    def get_voice_selection_settings(self):
        return self.config.get(constants.CONFIG_VOICE_SELECTION, {})

    def get_apply_updates_automatically(self):
        return self.config.get(constants.CONFIG_APPLY_UPDATES_AUTOMATICALLY, True)

    def set_apply_updates_automatically(self, value):
        self.config[constants.CONFIG_APPLY_UPDATES_AUTOMATICALLY] = value
        aqt.mw.addonManager.writeConfig(__name__, self.config)

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
        }, headers={'api_key': self.config['api_key']})
        return response

    def interpret_translation_response_async(self, response):
        # print(response.status_code)
        if response.status_code == 200:
            data = json.loads(response.content)
            return data['translated_text'] 
        if response.status_code == 400:
            data = json.loads(response.content)
            error_text = f"Could not load translation: {data['error']}"
            raise LanguageToolsRequestError(error_text)
        if response.status_code == 401:
            data = json.loads(response.content)
            raise LanguageToolsRequestError(data['error'])
        error_text = f"Could not load translation: {response.text}"
        raise LanguageToolsRequestError(error_text)

    def get_translation(self, source_text, translation_option):
        return self.interpret_translation_response_async(self.get_translation_async(source_text, translation_option))

    def get_translation_all(self, source_text, from_language, to_language):
        if not self.check_api_key_valid():
            return

        response = requests.post(self.base_url + '/translate_all', json={
                'text': source_text,
                'from_language': from_language,
                'to_language': to_language
        }, headers={'api_key': self.config['api_key']})
        data = json.loads(response.content)        
        return data
    
    def get_transliteration_async(self, source_text, transliteration_option):
        response = requests.post(self.base_url + '/transliterate', json={
                'text': source_text,
                'service': transliteration_option['service'],
                'transliteration_key': transliteration_option['transliteration_key']
        }, headers={'api_key': self.config['api_key']})        
        return response

    def interpret_transliteration_response_async(self, response):
        if response.status_code == 200:
            data = json.loads(response.content)
            return data['transliterated_text'] 
        if response.status_code == 400:
            data = json.loads(response.content)
            error_text = f"Could not load transliteration: {data['error']}"
            raise LanguageToolsRequestError(error_text)
            return error_text
        if response.status_code == 401:
            data = json.loads(response.content)
            raise LanguageToolsRequestError(data['error'])
        error_text = f"Could not load transliteration: {response.text}"
        raise LanguageToolsRequestError(error_text)

    def get_transliteration(self, source_text, service, transliteration_key):
        if not self.check_api_key_valid():
            return

        response = requests.post(self.base_url + '/transliterate', json={
                'text': source_text,
                'service': service,
                'transliteration_key': transliteration_key
        }, headers={'api_key': self.config['api_key']})
        data = json.loads(response.content)
        return data['transliterated_text']

    def generate_audio_for_field(self, note_id, from_field, to_field, voice):
        note = aqt.mw.col.getNote(note_id)
        source_text = note[from_field]
        if len(source_text) == 0:
            return False
        
        response = self.generate_audio_tag_collection(source_text, voice)
        sound_tag = response['sound_tag']
        if sound_tag != None:
            # write to note
            note[to_field] = sound_tag
            note.flush()
            return True

        return False # failure

    def generate_audio_tag_collection(self, source_text, voice):
        result = {'sound_tag': None,
        'full_filename': None}
        generated_filename = self.get_tts_audio(source_text, voice['service'], voice['voice_key'], {})
        if generated_filename != None:
            full_filename = aqt.mw.col.media.addFile(generated_filename)
            collection_filename = os.path.basename(full_filename)
            sound_tag = f'[sound:{collection_filename}]'
            result['sound_tag'] = sound_tag
            result['full_filename'] = full_filename
        return result

    def get_hash_for_request(self, url_path, data):
        combined_data = {
            'url': url_path,
            'data': data
        }
        return hashlib.sha224(str(combined_data).encode('utf-8')).hexdigest()

    def get_audio_collection_filename(self, url_path, data):
        return f'languagetools-{self.get_hash_for_request(url_path, data)}'

    def get_tts_audio(self, source_text, service, voice_key, options):
        url_path = '/audio'
        data = {
            'text': source_text,
            'service': service,
            'voice_key': voice_key,
            'options': options
        }
        file_name = self.get_audio_collection_filename(url_path, data)
        response = requests.post(self.base_url + url_path, json=data, headers={'api_key': self.config['api_key']})

        if response.status_code == 200:
            output_temp_file = tempfile.NamedTemporaryFile(prefix=file_name, suffix='.mp3', delete=False)
            with open(output_temp_file.name, 'wb') as f:
                f.write(response.content)
            f.close()
            return output_temp_file.name
        else:
            return None

    def get_tts_voice_list(self):
        response = requests.get(self.base_url + '/voice_list')
        data = json.loads(response.content)
        return data

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

