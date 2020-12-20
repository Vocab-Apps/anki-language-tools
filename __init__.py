# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
import aqt.utils
# import all of the Qt GUI library
from aqt.qt import *
import aqt.progress
import requests
import json
import random
import os

import aqt.gui_hooks
import anki.hooks

from . import version

ADDON_NAME = 'Language Tools'
MENU_PREFIX = ADDON_NAME + ':'

class LanguageTools():
    CONFIG_DECK_LANGUAGES = 'deck_languages'
    CONFIG_WANTED_LANGUAGES = 'wanted_languages'
    

    def __init__(self):
        self.base_url = 'https://cloud-language-tools-6e7b3.ondigitalocean.app'
        if 'ANKI_LANGUAGE_TOOLS_BASE_URL' in os.environ:
            self.base_url = os.environ['ANKI_LANGUAGE_TOOLS_BASE_URL']
        self.config = mw.addonManager.getConfig(__name__)

    def initialize(self):
        # get language list
        response = requests.get(self.base_url + '/language_list')
        self.language_list = json.loads(response.content)

        response = requests.get(self.base_url + '/transliteration_language_list')
        self.transliteration_language_list = json.loads(response.content)

        if len(self.config[LanguageTools.CONFIG_WANTED_LANGUAGES]) == 0:
            # suggest running language detection
            result = aqt.utils.askUser('Would you like to run language detection ? It takes a few minutes.', title='Language Tools')
            if result == True:
                self.perform_language_detection()

    def show_about(self):
        text = f'Language Tools v{version.ANKI_LANGUAGE_TOOLS_VERSION}'
        aqt.utils.showInfo(text, title='Language Tools')

    def get_language_name(self, language):
        return self.language_list[language]

    def perform_language_detection(self):
        # print('perform_language_detection')
        mw.progress.start(max=100, min=0, label='language detection', immediate=True)
        mw.progress.update(label='Retrieving Decks', value=1)

        populated_deck_models = self.get_populated_deck_models()
        step_max = len(populated_deck_models)
        mw.progress.update(label='Processing Decks', value=2, max=step_max)

        i=0
        for entry in populated_deck_models:
            deck_entry = entry['deck']
            note_type_entry = entry['model']
            self.perform_language_detection_deck_note_type(deck_entry, note_type_entry, i, step_max)
            i += 1

        mw.progress.finish()

        # display a summary
        wanted_languages = self.config[LanguageTools.CONFIG_WANTED_LANGUAGES]

        languages_found = ''
        for key, value in wanted_languages.items():
            entry = f'<b>{self.get_language_name(key)}</b><br/>'
            languages_found += entry
        text = f'Found the following languages:<br/>{languages_found}'
        aqt.utils.showInfo(text, title='Language Tools Detection', textFormat="rich")

                
    def get_populated_deck_models(self):
        deck_list = mw.col.decks.all_names_and_ids()
        note_types = mw.col.models.all_names_and_ids()

        result = []

        for deck_entry in deck_list:
            for note_type_entry in note_types:
                query = f'did:{deck_entry.id} mid:{note_type_entry.id}'
                notes = mw.col.find_notes(query)

                if len(notes) > 0:
                    result.append({'deck': deck_entry, 'model': note_type_entry})

        return result

        
    def perform_language_detection_deck_note_type(self, deck, note_type, step_num, step_max):
        label = f'Analyzing {deck.name} / {note_type.name}'
        mw.progress.update(label=label, value=step_num, max=step_max)

        # print(f'perform_language_detection_deck_note_type, {deck.name}, {note_type.name}')
        query = f'did:{deck.id} mid:{note_type.id}'
        notes = mw.col.find_notes(query)
        if len(notes) > 0:  
            model = mw.col.models.get(note_type.id)
            fields = model['flds']
            for field in fields:
                field_name = field['name']
                self.perform_language_detection_deck_note_type_field(deck, note_type, field_name, notes)



    def perform_language_detection_deck_note_type_field(self, deck, note_type, field_name, notes):
        # retain notes which have a non-empty field
        sample_size = 100

        all_field_values = [mw.col.getNote(x)[field_name] for x in notes]
        non_empty_fields = [x for x in all_field_values if len(x) > 0]

        if len(non_empty_fields) == 0:
            # no data to perform detection on
            return
        
        if len(non_empty_fields) < sample_size:
            field_sample = non_empty_fields
        else:
            field_sample = random.sample(non_empty_fields, sample_size)
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
        """will return None if no language is associated with this field"""
        model = mw.col.models.get(model_id)
        model_name = model['name']
        deck = mw.col.decks.get(deck_id)
        deck_name = deck['name']
        return self.config.get(LanguageTools.CONFIG_DECK_LANGUAGES, {}).get(model_name, {}).get(deck_name, {}).get(field_name, None)

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



languagetools = LanguageTools()

# add menu items

action = QAction("Language Tools: Run Language Detection", mw)
action.triggered.connect(languagetools.perform_language_detection)
mw.form.menuTools.addAction(action)

action = QAction("Language Tools: About", mw)
action.triggered.connect(languagetools.show_about)
mw.form.menuTools.addAction(action)


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

def show_transliteration(selected_text, service, transliteration_key):
    result = languagetools.get_transliteration(selected_text, service, transliteration_key)
    text = f"""Transliteration of <i>{selected_text}</i>: {result}"""
    aqt.utils.showInfo(text, title='Language Tools Transliteration', textFormat="rich")    

def on_context_menu(web_view, menu):
    # gather some information about the context from the editor
    # =========================================================

    selected_text = web_view.selectedText()
    current_field_num = web_view.editor.currentField
    if current_field_num == None:
        # we don't have a field selected, don't do anything
        return
    note = web_view.editor.note
    if note == None:
        # can't do anything without a note
        return
    model_id = note.mid
    model = mw.col.models.get(model_id)
    field_name = model['flds'][current_field_num]['name']
    card = web_view.editor.card
    if card == None:
        # we can't get the deck without a a card
        return
    deck_id = card.did

    language = languagetools.get_language(deck_id, model_id, field_name)



    # check whether a language is set
    # ===============================

    if language != None:
        # all pre-requisites for translation/transliteration are met, proceed
        # ===================================================================

        if len(selected_text) > 0:
            source_text_max_length = 25
            source_text = selected_text
            if len(selected_text) > source_text_max_length:
                source_text = selected_text[0:source_text_max_length]

            # add translation options
            # =======================
            menu_text = f'{MENU_PREFIX} translate from {languagetools.get_language_name(language)}'
            submenu = QMenu(menu_text, menu)
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

            # add transliteration options
            # ===========================

            menu_text = f'{MENU_PREFIX} transliterate {languagetools.get_language_name(language)}'
            submenu = QMenu(menu_text, menu)
            transliteration_options = languagetools.get_transliteration_options(language)
            for transliteration_option in transliteration_options:
                menu_text = transliteration_option['transliteration_name']
                def get_transliterate_lambda(selected_text, service, transliteration_key):
                    def transliterate():
                        show_transliteration(selected_text, service, transliteration_key)
                    return transliterate
                submenu.addAction(menu_text, get_transliterate_lambda(selected_text, transliteration_option['service'], transliteration_option['transliteration_key']))
            menu.addMenu(submenu)

    # show information about the field 
    # ================================

    if language == None:
        menu_text = f'{MENU_PREFIX} No language set'
    else:
        menu_text = f'{MENU_PREFIX} language: {languagetools.get_language_name(language)}'
    submenu = QMenu(menu_text, menu)
    # add change language option
    menu_text = f'Change Language'
    def get_change_language_lambda():
        def translate():
            show_translation(selected_text, language, wanted_language)
        return translate
    submenu.addAction(menu_text, get_change_language_lambda())
    menu.addMenu(submenu)        


anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)

# run some stuff after anki has initialized
aqt.gui_hooks.main_window_did_init.append(languagetools.initialize)