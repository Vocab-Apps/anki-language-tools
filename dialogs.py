from typing import List, Dict

import aqt.qt
from PyQt5 import QtCore, QtGui, QtWidgets
from .languagetools import DeckNoteType, Deck

class LanguageMappingDeckWidgets(object):
    def __init__(self):
        pass

class LanguageMappingDialog_UI(object):
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

        deckWidgets.deck_info = QtWidgets.QHBoxLayout()
        deckWidgets.deck_info.setObjectName("deck_info")
        deckWidgets.deck_label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        deckWidgets.deck_label.setFont(font)
        deckWidgets.deck_label.setObjectName("deck_label")
        deckWidgets.deck_label.setText(deck_name)
        deckWidgets.deck_info.addWidget(deckWidgets.deck_label)
        deckWidgets.deck_name = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.deck_name.setObjectName("deck_name")
        deckWidgets.deck_info.addWidget(deckWidgets.deck_name)
        self.all_decks.addLayout(deckWidgets.deck_info)
        deckWidgets.note_type_info = QtWidgets.QHBoxLayout()
        deckWidgets.note_type_info.setObjectName("note_type_info")
        deckWidgets.note_type_label = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.note_type_label.setObjectName("note_type_label")
        deckWidgets.note_type_info.addWidget(deckWidgets.note_type_label)
        deckWidgets.note_type_name = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.note_type_name.setObjectName("note_type_name")
        deckWidgets.note_type_info.addWidget(deckWidgets.note_type_name)
        self.all_decks.addLayout(deckWidgets.note_type_info)
        deckWidgets.field_info = QtWidgets.QGridLayout()
        deckWidgets.field_info.setObjectName("field_info")
        deckWidgets.field_1_label = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.field_1_label.setObjectName("field_1_label")
        deckWidgets.field_info.addWidget(deckWidgets.field_1_label, 0, 0, 1, 1)
        deckWidgets.field_1_language = QtWidgets.QComboBox(self.layoutWidget)
        deckWidgets.field_1_language.setObjectName("field_1_language")
        deckWidgets.field_info.addWidget(deckWidgets.field_1_language, 0, 1, 1, 1)
        deckWidgets.field_1_samples = QtWidgets.QPushButton(self.layoutWidget)
        deckWidgets.field_1_samples.setObjectName("field_1_samples")
        deckWidgets.field_info.addWidget(deckWidgets.field_1_samples, 0, 2, 1, 1)
        deckWidgets.field_2_label = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.field_2_label.setObjectName("field_2_label")
        deckWidgets.field_info.addWidget(deckWidgets.field_2_label, 1, 0, 1, 1)
        deckWidgets.field_2_language = QtWidgets.QComboBox(self.layoutWidget)
        deckWidgets.field_2_language.setObjectName("field_2_language")
        deckWidgets.field_info.addWidget(deckWidgets.field_2_language, 1, 1, 1, 1)
        deckWidgets.field_2_samples = QtWidgets.QPushButton(self.layoutWidget)
        deckWidgets.field_2_samples.setObjectName("field_2_samples")
        deckWidgets.field_info.addWidget(deckWidgets.field_2_samples, 1, 2, 1, 1)
        deckWidgets.field_3_label = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.field_3_label.setObjectName("field_3_label")
        deckWidgets.field_info.addWidget(deckWidgets.field_3_label, 2, 0, 1, 1)
        deckWidgets.field_3_language = QtWidgets.QComboBox(self.layoutWidget)
        deckWidgets.field_3_language.setObjectName("field_3_language")
        deckWidgets.field_info.addWidget(deckWidgets.field_3_language, 2, 1, 1, 1)
        deckWidgets.field_3_samples = QtWidgets.QPushButton(self.layoutWidget)
        deckWidgets.field_3_samples.setObjectName("field_3_samples")
        deckWidgets.field_info.addWidget(deckWidgets.field_3_samples, 2, 2, 1, 1)
        self.all_decks.addLayout(deckWidgets.field_info)        


def language_mapping_dialogue(languagetools):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    mapping_dialog = aqt.qt.QDialog()
    mapping_dialog.ui = LanguageMappingDialog_UI()
    mapping_dialog.ui.setupUi(mapping_dialog, deck_map)
    mapping_dialog.exec_()
    # mapping_dialog = LanguageMappingDialog()
    # mapping_dialog.layout()
    # mapping_dialog.exec_()