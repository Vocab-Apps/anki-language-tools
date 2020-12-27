from typing import List, Dict

import aqt.qt
from PyQt5 import QtCore, QtGui, QtWidgets
from .languagetools import DeckNoteType, Deck, DeckNoteTypeField

class LanguageMappingDeckWidgets(object):
    def __init__(self):
        pass

class LanguageMappingNoteTypeWidgets(object):
    def __init__(self):
        pass

class LanguageMappingDialog_UI(object):
    def __init__(self):
        self.deckWidgetMap = {}
        self.deckNoteTypeWidgetMap = {}

    def setupUi(self, Dialog, deck_map: Dict[str, Deck]):
        Dialog.setObjectName("Dialog")
        Dialog.resize(608, 535)

        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(70, 20, 239, 358))
        self.layoutWidget.setObjectName("layoutWidget")

        self.all_decks = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.all_decks.setContentsMargins(0, 0, 0, 0)
        self.all_decks.setObjectName("all_decks")

        for deck_name, deck in deck_map.items():
            self.layoutDecks(deck_name, deck)

    def layoutDecks(self, deck_name, deck: Deck):
        deckWidgets = LanguageMappingDeckWidgets()
        self.deckWidgetMap[deck_name] = deckWidgets
        self.deckNoteTypeWidgetMap[deck_name] = {}

        deckWidgets.deck_info = QtWidgets.QHBoxLayout()
        deckWidgets.deck_info.setObjectName("deck_info")
        deckWidgets.deck_label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        deckWidgets.deck_label.setFont(font)
        deckWidgets.deck_label.setObjectName("deck_label")
        deckWidgets.deck_label.setText('Deck:')
        deckWidgets.deck_info.addWidget(deckWidgets.deck_label)
        deckWidgets.deck_name = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.deck_name.setObjectName("deck_name")
        deckWidgets.deck_name.setText(deck_name)
        deckWidgets.deck_info.addWidget(deckWidgets.deck_name)
        self.all_decks.addLayout(deckWidgets.deck_info)

        # iterate over note types 
        for note_type_name, dntf_list in deck.note_type_map.items():
            self.layoutNoteTypes(deck_name, note_type_name, dntf_list)
                        

    def layoutNoteTypes(self, deck_name, note_type_name, dntf_list: List[DeckNoteTypeField]):
        print(f'*** layoutNoteTypes {note_type_name}')

        noteTypeWidgets = LanguageMappingNoteTypeWidgets()
        self.deckNoteTypeWidgetMap[deck_name][note_type_name] = noteTypeWidgets

        noteTypeWidgets.note_type_info = QtWidgets.QHBoxLayout()
        noteTypeWidgets.note_type_info.setObjectName("note_type_info")
        noteTypeWidgets.note_type_label = QtWidgets.QLabel(self.layoutWidget)
        noteTypeWidgets.note_type_label.setObjectName("note_type_label")
        noteTypeWidgets.note_type_label.setText('Note Type:')
        noteTypeWidgets.note_type_info.addWidget(noteTypeWidgets.note_type_label)
        noteTypeWidgets.note_type_name = QtWidgets.QLabel(self.layoutWidget)
        noteTypeWidgets.note_type_name.setObjectName("note_type_name")
        noteTypeWidgets.note_type_name.setText(note_type_name)
        noteTypeWidgets.note_type_info.addWidget(noteTypeWidgets.note_type_name)
        self.all_decks.addLayout(noteTypeWidgets.note_type_info)

        # noteTypeWidgets.field_info = QtWidgets.QGridLayout()
        # noteTypeWidgets.field_info.setObjectName("field_info")
        # noteTypeWidgets.field_1_label = QtWidgets.QLabel(self.layoutWidget)
        # noteTypeWidgets.field_1_label.setObjectName("field_1_label")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_1_label, 0, 0, 1, 1)
        # noteTypeWidgets.field_1_language = QtWidgets.QComboBox(self.layoutWidget)
        # noteTypeWidgets.field_1_language.setObjectName("field_1_language")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_1_language, 0, 1, 1, 1)
        # noteTypeWidgets.field_1_samples = QtWidgets.QPushButton(self.layoutWidget)
        # noteTypeWidgets.field_1_samples.setObjectName("field_1_samples")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_1_samples, 0, 2, 1, 1)
        # noteTypeWidgets.field_2_label = QtWidgets.QLabel(self.layoutWidget)
        # noteTypeWidgets.field_2_label.setObjectName("field_2_label")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_2_label, 1, 0, 1, 1)
        # noteTypeWidgets.field_2_language = QtWidgets.QComboBox(self.layoutWidget)
        # noteTypeWidgets.field_2_language.setObjectName("field_2_language")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_2_language, 1, 1, 1, 1)
        # noteTypeWidgets.field_2_samples = QtWidgets.QPushButton(self.layoutWidget)
        # noteTypeWidgets.field_2_samples.setObjectName("field_2_samples")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_2_samples, 1, 2, 1, 1)
        # noteTypeWidgets.field_3_label = QtWidgets.QLabel(self.layoutWidget)
        # noteTypeWidgets.field_3_label.setObjectName("field_3_label")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_3_label, 2, 0, 1, 1)
        # noteTypeWidgets.field_3_language = QtWidgets.QComboBox(self.layoutWidget)
        # noteTypeWidgets.field_3_language.setObjectName("field_3_language")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_3_language, 2, 1, 1, 1)
        # noteTypeWidgets.field_3_samples = QtWidgets.QPushButton(self.layoutWidget)
        # noteTypeWidgets.field_3_samples.setObjectName("field_3_samples")
        # noteTypeWidgets.field_info.addWidget(noteTypeWidgets.field_3_samples, 2, 2, 1, 1)
        # self.all_decks.addLayout(noteTypeWidgets.field_info)        


def language_mapping_dialogue(languagetools):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    mapping_dialog = aqt.qt.QDialog()
    mapping_dialog.ui = LanguageMappingDialog_UI()
    mapping_dialog.ui.setupUi(mapping_dialog, deck_map)
    mapping_dialog.exec_()
    # mapping_dialog = LanguageMappingDialog()
    # mapping_dialog.layout()
    # mapping_dialog.exec_()