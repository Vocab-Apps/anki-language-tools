# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
import aqt.utils
# import all of the Qt GUI library
from aqt.qt import *
import requests
import json
import random

import anki.hooks


class LanguageTools():
    CONFIG_DECK_LANGUAGES = 'deck_languages'
    CONFIG_WANTED_LANGUAGES = 'wanted_languages'

    def __init__(self):
        self.base_url = 'http://0.0.0.0:5000'
        self.config = mw.addonManager.getConfig(__name__)

    def initialize(self):
        # get language list
        response = requests.get(self.base_url + '/language_list')
        self.language_list = json.loads(response.content)
        

    def get_language_name(self, language):
        return self.language_list[language]

    def perform_language_detection(self):
        deck_list = mw.col.decks.all_names_and_ids()
        note_types = mw.col.models.all_names_and_ids()

        for deck_entry in deck_list:
            for note_type_entry in note_types:
                deck_id = deck_entry.id
                note_type_id = note_type_entry.id
                self.perform_language_detection_deck_note_type(deck_entry, note_type_entry)
                
        
    def perform_language_detection_deck_note_type(self, deck, note_type):
        sample_size = 100
        # print(f'perform_language_detection_deck_note_type, {deck.name}, {note_type.name}')
        query = f'did:{deck.id} mid:{note_type.id}'
        notes = mw.col.find_notes(query)
        if len(notes) > 0:  
            # print(f'found {len(notes)} notes in {deck.name}, {note_type.name}')
            if len(notes) < sample_size:
                random_note_ids = notes
            else:
                random_note_ids = random.sample(notes, sample_size)
            model = mw.col.models.get(note_type.id)
            fields = model['flds']
            for field in fields:
                field_name = field['name']
                # print(f'  field: {field_name}, performing detection')
                field_sample = [mw.col.getNote(x)[field_name] for x in random_note_ids]
                response = requests.post(self.base_url + '/detect', json={
                        'text_list': field_sample
                })
                data = json.loads(response.content)
                detected_language = data['detected_language']

                self.store_language_detection_result(note_type.name, deck.name, field_name, detected_language)


    def store_language_detection_result(self, note_type_name, deck_name, field_name, language):
        # write per-deck detected languages
        CONFIG_DECK_LANGUAGES = LanguageTools.CONFIG_DECK_LANGUAGES
        CONFIG_WANTED_LANGUAGES = LanguageTools.CONFIG_WANTED_LANGUAGES
        if CONFIG_DECK_LANGUAGES not in self.config:
            self.config[CONFIG_DECK_LANGUAGES] = {}
        if note_type_name not in self.config[CONFIG_DECK_LANGUAGES]:
            self.config[CONFIG_DECK_LANGUAGES][note_type_name] = {}
        if deck_name not in self.config[CONFIG_DECK_LANGUAGES][note_type_name]:
            self.config[CONFIG_DECK_LANGUAGES][note_type_name][deck_name] = {}
        self.config[CONFIG_DECK_LANGUAGES][note_type_name][deck_name][field_name] = language

        # store the languages we're interested in
        if CONFIG_WANTED_LANGUAGES not in self.config:
            self.config[CONFIG_WANTED_LANGUAGES] = {}
        self.config[CONFIG_WANTED_LANGUAGES][language] = True

        mw.addonManager.writeConfig(__name__, self.config)

    def get_language(self, deck_id, model_id, field_name):
        model = mw.col.models.get(model_id)
        model_name = model['name']
        deck = mw.col.decks.get(deck_id)
        deck_name = deck['name']
        # print(f'model_name {model_name} deck_name {deck_name} field_name {field_name}')
        return self.config[LanguageTools.CONFIG_DECK_LANGUAGES][model_name][deck_name][field_name]

    def get_wanted_languages(self):
        return self.config[LanguageTools.CONFIG_WANTED_LANGUAGES].keys()

    def get_translation(self, source_text, from_language, to_language):
        response = requests.post(self.base_url + '/translate_all', json={
                'text': source_text,
                'from_language': from_language,
                'to_language': to_language
        })
        data = json.loads(response.content)        
        return data


languagetools = LanguageTools()
languagetools.initialize()


# add context menu handler

def show_translation(source_text, from_language, to_language):
    # print(f'translate {source_text} from {from_language} to {to_language}')
    result = languagetools.get_translation(source_text, from_language, to_language)

    translations = ''
    for key, value in result.items():
        entry = f'{key}: <b>{value}</b><br/>'
        translations += entry
    text = f"""Translation of <i>{source_text}</i> from {languagetools.get_language_name(from_language)} to {languagetools.get_language_name(to_language)}<br/>
        {translations}
    """
    aqt.utils.showInfo(text, title='Language Tools Translation', textFormat="rich")

def on_context_menu(web_view, menu):
    selected_text = web_view.selectedText()
    current_field_num = web_view.editor.currentField
    note = web_view.editor.note
    model_id = note.mid
    model = mw.col.models.get(model_id)
    field_name = model['flds'][current_field_num]['name']
    card = web_view.editor.card
    if card != None:
        deck_id = card.did

        language = languagetools.get_language(deck_id, model_id, field_name)

        source_text_max_length = 25
        source_text = selected_text
        if len(selected_text) > source_text_max_length:
            source_text = selected_text[0:source_text_max_length]

        menu_text = f'Language Tools: translate {source_text} from {languagetools.get_language_name(language)}'
        
        # source_text = 
        submenu = QMenu(menu_text, menu)

        # action1 = QAction()
        wanted_languages = languagetools.get_wanted_languages()
        for wanted_language in wanted_languages:
            if wanted_language != language:
                menu_text = f'To {languagetools.get_language_name(wanted_language)}'
                def get_translate_lambda(selected_text, language, wanted_language):
                    def translate():
                        show_translation(selected_text, language, wanted_language)
                    return translate
                submenu.addAction(menu_text, get_translate_lambda(selected_text, language, wanted_language))

        menu.addMenu(submenu)


anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)