from typing import List, Dict

import aqt.qt
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from .languagetools import DeckNoteType, Deck, DeckNoteTypeField

class LanguageMappingDeckWidgets(object):
    def __init__(self):
        pass

class LanguageMappingNoteTypeWidgets(object):
    def __init__(self):
        pass

class LanguageMappingFieldWidgets(object):
    def __init__(self):
        pass


class LanguageMappingDialog_UI(object):
    def __init__(self):
        self.deckWidgetMap = {}
        self.deckNoteTypeWidgetMap = {}
        self.fieldWidgetMap = {}

    def setupUi(self, Dialog, deck_map: Dict[str, Deck]):
        Dialog.setObjectName("Dialog")
        Dialog.resize(608, 900)

        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)

        self.scrollArea.setGeometry(QtCore.QRect(59, 29, 391, 501))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        # self.scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 389, 499))
        # self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.layoutWidget = QtWidgets.QWidget()
        # self.layoutWidget.setGeometry(QtCore.QRect(70, 20, 239, 358))
        self.layoutWidget.setObjectName("layoutWidget")

        self.all_decks = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.all_decks.setContentsMargins(0, 0, 0, 0)
        self.all_decks.setObjectName("all_decks")

        for deck_name, deck in deck_map.items():
            self.layoutDecks(deck_name, deck)

        self.scrollArea.setWidget(self.layoutWidget)

    def layoutDecks(self, deck_name, deck: Deck):
        deckWidgets = LanguageMappingDeckWidgets()
        self.deckWidgetMap[deck_name] = deckWidgets
        self.deckNoteTypeWidgetMap[deck_name] = {}
        self.fieldWidgetMap[deck_name] = {}

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
        self.fieldWidgetMap[deck_name][note_type_name] = {}

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

        noteTypeWidgets.field_info = QtWidgets.QGridLayout()
        noteTypeWidgets.field_info.setObjectName("field_info")        

        row = 0
        for deck_note_type_field in dntf_list:
            self.layoutField(row, deck_note_type_field, noteTypeWidgets.field_info)
            row += 1

        self.all_decks.addLayout(noteTypeWidgets.field_info)

        print(f'columnCount: {noteTypeWidgets.field_info.columnCount()} rowCount: {noteTypeWidgets.field_info.rowCount()}')

    def layoutField(self, row:int, deck_note_type_field: DeckNoteTypeField, gridLayout: QtWidgets.QGridLayout):
        print(f'layoutField: {deck_note_type_field} row {row}')

        fieldWidgets = LanguageMappingFieldWidgets()
        self.fieldWidgetMap[deck_note_type_field.deck_note_type.deck_name][deck_note_type_field.deck_note_type.model_name][deck_note_type_field.field_name] = fieldWidgets

        fieldWidgets.field_label = QtWidgets.QLabel(self.layoutWidget)
        fieldWidgets.field_label.setObjectName("field_label")
        fieldWidgets.field_label.setText(deck_note_type_field.field_name)
        gridLayout.addWidget(fieldWidgets.field_label, row, 0, 1, 1)

        fieldWidgets.field_language = QtWidgets.QComboBox(self.layoutWidget)
        fieldWidgets.field_language.setObjectName("field_language")
        gridLayout.addWidget(fieldWidgets.field_language, row, 1, 1, 1)

        fieldWidgets.field_samples_button = QtWidgets.QPushButton(self.layoutWidget)
        fieldWidgets.field_samples_button.setObjectName("field_samples_button")
        gridLayout.addWidget(fieldWidgets.field_samples_button, row, 2, 1, 1)


def language_mapping_dialogue(languagetools):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    mapping_dialog = aqt.qt.QDialog()
    mapping_dialog.ui = LanguageMappingDialog_UI()
    mapping_dialog.ui.setupUi(mapping_dialog, deck_map)
    mapping_dialog.exec_()
    # mapping_dialog = LanguageMappingDialog()
    # mapping_dialog.layout()
    # mapping_dialog.exec_()