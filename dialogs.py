from typing import List, Dict

import aqt.qt
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from .languagetools import DeckNoteType, Deck, DeckNoteTypeField, LanguageTools
from . import constants

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
    def __init__(self, languagetools: LanguageTools):
        self.languagetools: LanguageTools = languagetools
        
        # do some processing on languages
        data = languagetools.get_all_language_arrays()
        self.language_name_list = data['language_name_list']
        self.language_code_list = data['language_code_list']
        self.language_name_list.append('Not Set')

        self.language_mapping_changes = {}

        self.deckWidgetMap = {}
        self.deckNoteTypeWidgetMap = {}
        self.fieldWidgetMap = {}

        self.dntfComboxBoxMap = {}

        self.greenStylesheet = "background-color: #69F0AE"

    def setupUi(self, Dialog, deck_map: Dict[str, Deck]):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 800)

        self.Dialog = Dialog

        self.topLevel = QtWidgets.QVBoxLayout(Dialog)

        self.scrollArea = QtWidgets.QScrollArea()
        
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.layoutWidget = QtWidgets.QWidget()
        self.layoutWidget.setObjectName("layoutWidget")

        self.all_decks = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.all_decks.setContentsMargins(20, 20, 20, 20)
        self.all_decks.setObjectName("all_decks")

        # add header
        header = QtWidgets.QLabel()
        header.setText(f'Language Mapping')
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)  
        font.setPointSize(20)
        header.setFont(font)
        self.topLevel.addWidget(header)

        # add auto-detection widgets
        hlayout = QtWidgets.QHBoxLayout()
        self.autodetect_progressbar = QtWidgets.QProgressBar()
        hlayout.addWidget(self.autodetect_progressbar)

        font2 = QtGui.QFont()
        font2.setPointSize(14)
        autodetect_button = QtWidgets.QPushButton()
        autodetect_button.setText('Run Auto Detection')
        autodetect_button.setFont(font2)
        autodetect_button.setStyleSheet(self.greenStylesheet)
        autodetect_button.pressed.connect(self.runLanguageDetection)
        hlayout.addWidget(autodetect_button)

        self.topLevel.addLayout(hlayout)


        for deck_name, deck in deck_map.items():
            self.layoutDecks(deck_name, deck)


        self.scrollArea.setWidget(self.layoutWidget)
        self.topLevel.addWidget(self.scrollArea)

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.addButton("Apply", QtWidgets.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.topLevel.addWidget(self.buttonBox)

    def layoutDecks(self, deck_name, deck: Deck):
        deckWidgets = LanguageMappingDeckWidgets()
        self.deckWidgetMap[deck_name] = deckWidgets
        self.deckNoteTypeWidgetMap[deck_name] = {}
        self.fieldWidgetMap[deck_name] = {}

        deckWidgets.deck_info = QtWidgets.QHBoxLayout()
        deckWidgets.deck_info.setObjectName("deck_info")
        
        fontSize = 14

        deckWidgets.deck_label = QtWidgets.QLabel(self.layoutWidget)
        font1 = QtGui.QFont()
        font1.setBold(True)
        font1.setPointSize(fontSize)
        deckWidgets.deck_label.setFont(font1)
        deckWidgets.deck_label.setObjectName("deck_label")
        deckWidgets.deck_label.setText('Deck:')
        deckWidgets.deck_info.addWidget(deckWidgets.deck_label)

        font2 = QtGui.QFont()
        font2.setPointSize(fontSize)
        deckWidgets.deck_name = QtWidgets.QLabel(self.layoutWidget)
        deckWidgets.deck_name.setObjectName("deck_name")
        deckWidgets.deck_name.setText(deck_name)
        deckWidgets.deck_name.setFont(font2)
        deckWidgets.deck_info.addWidget(deckWidgets.deck_name)

        deckWidgets.deck_info.addStretch(1)

        self.all_decks.addLayout(deckWidgets.deck_info)
        
        # iterate over note types 
        for note_type_name, dntf_list in deck.note_type_map.items():
            self.layoutNoteTypes(deck_name, note_type_name, dntf_list)

        # add spacing at the end
        self.all_decks.addSpacing(30)
                        

    def layoutNoteTypes(self, deck_name, note_type_name, dntf_list: List[DeckNoteTypeField]):
        noteTypeWidgets = LanguageMappingNoteTypeWidgets()
        self.deckNoteTypeWidgetMap[deck_name][note_type_name] = noteTypeWidgets
        self.fieldWidgetMap[deck_name][note_type_name] = {}

        noteTypeWidgets.note_type_info = QtWidgets.QHBoxLayout()
        noteTypeWidgets.note_type_info.setObjectName("note_type_info")

        fontSize = 12

        font1 = QtGui.QFont()
        font1.setBold(True)
        font1.setPointSize(fontSize)

        noteTypeWidgets.note_type_label = QtWidgets.QLabel(self.layoutWidget)
        noteTypeWidgets.note_type_label.setObjectName("note_type_label")
        noteTypeWidgets.note_type_label.setText('Note Type:')
        noteTypeWidgets.note_type_label.setFont(font1)
        noteTypeWidgets.note_type_info.addWidget(noteTypeWidgets.note_type_label)

        font2 = QtGui.QFont()
        font2.setPointSize(fontSize)
        noteTypeWidgets.note_type_name = QtWidgets.QLabel(self.layoutWidget)
        noteTypeWidgets.note_type_name.setObjectName("note_type_name")
        noteTypeWidgets.note_type_name.setText(note_type_name)
        noteTypeWidgets.note_type_name.setFont(font2)
        noteTypeWidgets.note_type_info.addWidget(noteTypeWidgets.note_type_name)

        noteTypeWidgets.note_type_info.addStretch(1)

        self.all_decks.addLayout(noteTypeWidgets.note_type_info)

        noteTypeWidgets.field_info = QtWidgets.QGridLayout()
        noteTypeWidgets.field_info.setContentsMargins(20, 0, 0, 0)
        # set stretch factors
        noteTypeWidgets.field_info.setColumnStretch(0, 50)
        noteTypeWidgets.field_info.setColumnStretch(1, 50)
        noteTypeWidgets.field_info.setColumnStretch(2, 0)
        noteTypeWidgets.field_info.setObjectName("field_info")

        row = 0
        for deck_note_type_field in dntf_list:
            self.layoutField(row, deck_note_type_field, noteTypeWidgets.field_info)
            row += 1

        self.all_decks.addLayout(noteTypeWidgets.field_info)


    def layoutField(self, row:int, deck_note_type_field: DeckNoteTypeField, gridLayout: QtWidgets.QGridLayout):

        fieldWidgets = LanguageMappingFieldWidgets()
        self.fieldWidgetMap[deck_note_type_field.deck_note_type.deck_name][deck_note_type_field.deck_note_type.model_name][deck_note_type_field.field_name] = fieldWidgets

        language_set = self.languagetools.get_language(deck_note_type_field)

        fieldWidgets.field_label = QtWidgets.QLabel(self.layoutWidget)
        fieldWidgets.field_label.setObjectName("field_label")
        fieldWidgets.field_label.setText(deck_note_type_field.field_name)
        gridLayout.addWidget(fieldWidgets.field_label, row, 0, 1, 1)

        fieldWidgets.field_language = QtWidgets.QComboBox(self.layoutWidget)
        fieldWidgets.field_language.addItems(self.language_name_list)
        fieldWidgets.field_language.setMaxVisibleItems(15)
        fieldWidgets.field_language.setStyleSheet("combobox-popup: 0;")
        fieldWidgets.field_language.setObjectName("field_language")
        self.setFieldLanguageIndex(fieldWidgets.field_language, language_set)

        # listen to events
        def get_currentIndexChangedLambda(comboBox, deck_note_type_field: DeckNoteTypeField):
            def callback(currentIndex):
                self.fieldLanguageIndexChanged(comboBox, deck_note_type_field, currentIndex)
            return callback
        fieldWidgets.field_language.currentIndexChanged.connect(get_currentIndexChangedLambda(fieldWidgets.field_language, deck_note_type_field)) 

        self.dntfComboxBoxMap[deck_note_type_field] = fieldWidgets.field_language

        gridLayout.addWidget(fieldWidgets.field_language, row, 1, 1, 1)

        fieldWidgets.field_samples_button = QtWidgets.QPushButton(self.layoutWidget)
        fieldWidgets.field_samples_button.setObjectName("field_samples_button")
        fieldWidgets.field_samples_button.setText('Show Samples')

        def getShowFieldSamplesLambda(deck_note_type_field: DeckNoteTypeField):
            def callback():
                self.showFieldSamples(deck_note_type_field)
            return callback
        fieldWidgets.field_samples_button.pressed.connect(getShowFieldSamplesLambda(deck_note_type_field))

        gridLayout.addWidget(fieldWidgets.field_samples_button, row, 2, 1, 1)

    def setFieldLanguageIndex(self, comboBox, language):
        if language != None:
            # locate index of language
            current_index = self.language_code_list.index(language)
            comboBox.setCurrentIndex(current_index)
        else:
            # not set
            comboBox.setCurrentIndex(len(self.language_name_list) - 1)

    def fieldLanguageIndexChanged(self, comboBox, deck_note_type_field: DeckNoteTypeField, currentIndex):
        # print(f'fieldLanguageIndexChanged: {deck_note_type_field}')
        language_code = None
        if currentIndex < len(self.language_code_list):
            language_code = self.language_code_list[currentIndex]
        self.language_mapping_changes[deck_note_type_field] = language_code
        # change stylesheet of combobox
        comboBox.setStyleSheet(self.greenStylesheet)

    def showFieldSamples(self, deck_note_type_field: DeckNoteTypeField):
        field_samples = self.languagetools.get_field_samples(deck_note_type_field, 20)
        joined_text = ', '.join(field_samples)
        text = f'<b>Samples</b>: {joined_text}'
        aqt.utils.showInfo(text, title=f'{constants.MENU_PREFIX} Field Samples', textFormat='rich')

    def accept(self):
        self.saveLanguageMappingChanges()
        self.Dialog.close()

    def reject(self):
        self.Dialog.close()

    def saveLanguageMappingChanges(self):
        for key, value in self.language_mapping_changes.items():
            self.languagetools.store_language_detection_result(key, value)

    def runLanguageDetection(self):
        dtnf_list: List[DeckNoteTypeField] = self.languagetools.get_populated_dntf()
        progress_max = len(dtnf_list)
        self.autodetect_progressbar.setMaximum(progress_max)

        progress = 0
        for dntf in dtnf_list:
            language = self.languagetools.perform_language_detection_deck_note_type_field(dntf)
            #self.language_mapping_changes[deck_note_type_field] = language
            # need to set combo box correctly.
            comboBox = self.dntfComboxBoxMap[dntf]
            self.setFieldLanguageIndex(comboBox, language)

            # progress bar
            self.autodetect_progressbar.setValue(progress)
            progress += 1
        
        self.autodetect_progressbar.setValue(progress_max)




def language_mapping_dialogue(languagetools):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    mapping_dialog = aqt.qt.QDialog()
    mapping_dialog.ui = LanguageMappingDialog_UI(languagetools)
    mapping_dialog.ui.setupUi(mapping_dialog, deck_map)
    mapping_dialog.exec_()