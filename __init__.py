# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
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
            print(f'found {len(notes)} notes in {deck.name}, {note_type.name}')
            if len(notes) < sample_size:
                random_note_ids = notes
            else:
                random_note_ids = random.sample(notes, sample_size)
            model = mw.col.models.get(note_type.id)
            fields = model['flds']
            for field in fields:
                field_name = field['name']
                print(f'  field: {field_name}, performing detection')
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


languagetools = LanguageTools()



def retrieveLanguages():
    response = requests.get(base_url + '/language_list')
    result = json.loads(response.content)
    print(result)

def detectLanguage():
    print('detectLanguage')
    query = "mid:1354424015760 deck:Mandarin"
    note_ids = mw.col.find_notes(query)


    random_note_ids = random.sample(note_ids, 10)

    english_fields = [mw.col.getNote(x)['English'] for x in random_note_ids]
    chinese_fields = [mw.col.getNote(x)['Chinese'] for x in random_note_ids]
    # print(english_fields)

    response = requests.post(base_url + '/detect', json={
            'text_list': chinese_fields
    })

    data = json.loads(response.content)
    print(data)



def listCollection():

    # get all of the notetypes
    note_types = mw.col.models.all_names_and_ids()

    for note_type in note_types:
        query = f"mid:{note_type.id}"
        print(query)
        notes = mw.col.find_notes(query)
        print(f'found {len(notes)} notes with model {note_type.name}')
    print(note_types)

    deck_list = mw.col.decks.all_names_and_ids()
    first_deck = deck_list[0]
    first_deck_id = first_deck.id
    # print(deck_list)

    # obtain the deck
    deck = mw.col.decks.get(first_deck_id)

    print(type(deck))
    print(deck.keys())
    print(deck.values())

def testFunction():
    # print(f'testFunction')
    # get the number of cards in the current collection, which is stored in
    # the main window
    cardCount = mw.col.cardCount()
    # show a message box
    showInfo("Card count: %d" % cardCount)

# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)


action = QAction("retrieveLanguages", mw)
action.triggered.connect(retrieveLanguages)
mw.form.menuTools.addAction(action)

action = QAction("listCollection", mw)
action.triggered.connect(listCollection)
mw.form.menuTools.addAction(action)

action = QAction("detectLanguage", mw)
action.triggered.connect(languagetools.perform_language_detection)
mw.form.menuTools.addAction(action)


def translate_text_azure(source_text):
    url = base_url + '/translate'
    query_json = {
        'text': source_text,
        'service': 'Azure',
        'from_language_key': 'zh-Hans',
        'to_language_key': 'en'
    }
    print(query_json)
    response = requests.post(url, json=query_json)
    data = json.loads(response.content)
    print(data)
    print(f"translation: {data['translated_text']}")

def translate_text_google(source_text):
    url = base_url + '/translate'
    query_json = {
        'text': source_text,
        'service': 'Google',
        'from_language_key': 'zh-CN',
        'to_language_key': 'en'
    }
    print(query_json)
    response = requests.post(url, json=query_json)
    data = json.loads(response.content)
    print(data)
    print(f"translation: {data['translated_text']}")    

# add context menu handler

def on_context_menu(web_view, menu):
    submenu = QMenu("Language Tools", menu)

    selected_text = web_view.selectedText()

    # action1 = QAction()
    submenu.addAction(f'Test Language Tools: ', lambda: print('test1'))
    submenu.addAction(f'translate (azure): {selected_text}', lambda: translate_text_azure(selected_text))
    submenu.addAction(f'translate (google): {selected_text}', lambda: translate_text_google(selected_text))

    menu.addMenu(submenu)


anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)