from typing import List, Dict
import sys

import aqt.qt
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from .languagetools import DeckNoteType, Deck, DeckNoteTypeField, LanguageTools, build_deck_note_type_from_note_card
from . import constants


def get_header_label(text):
        header = QtWidgets.QLabel()
        header.setText(text)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)  
        font.setPointSize(20)
        header.setFont(font)
        return header

class NoteTableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self, None)
        self.from_field_data = []
        self.to_field_data = []
        self.from_field = 'From'
        self.to_field = 'To'

    def setFromField(self, field_name):
        self.from_field = field_name
    
    def setToField(self, field_name):
        self.to_field = field_name

    def setFromFieldData(self, data):
        self.from_field_data = data
        self.to_field_data = [''] * len(self.from_field_data)

    def setToFieldData(self, row, to_field_result):
        self.to_field_data[row] = to_field_result

    def rowCount(self, parent):
        return len(self.from_field_data)

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if index.column() == 0:
            # from field
            return QtCore.QVariant(self.from_field_data[index.row()])
        else:
            # result field
            return QtCore.QVariant(self.to_field_data[index.row()])
            return QtCore.QVariant('')

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col == 0:
                return QtCore.QVariant(self.from_field)
            else:
                return QtCore.QVariant(self.to_field)
        return QtCore.QVariant()

class BatchConversionDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, deck_note_type: DeckNoteType, note_id_list):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        self.deck_note_type = deck_note_type
        self.note_id_list = note_id_list

        # get field list
        model = aqt.mw.col.models.get(deck_note_type.model_id)
        fields = model['flds']
        field_names = [x['name'] for x in fields]

        # these are the available fields
        self.field_name_list = []
        self.deck_note_type_field_list = []
        self.field_language = []

        self.from_field_data = []

        self.noteTableModel = NoteTableModel()

        # retain fields which have a language set
        for field_name in field_names:
            deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
            language = self.languagetools.get_language(deck_note_type_field)
            if language != None:
                self.field_name_list.append(field_name)
                self.deck_note_type_field_list.append(deck_note_type_field)
                self.field_language.append(language)


    def setupUi(self):
        self.resize(700, 500)

        vlayout = QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(get_header_label('Add Translation'))

        # setup to/from fields
        # ====================

        hlayout = QtWidgets.QHBoxLayout()
        from_label = aqt.qt.QLabel()
        from_label.setText('From Field:')
        hlayout.addWidget(from_label)

        self.from_combobox = QtWidgets.QComboBox()
        self.from_combobox.addItems(self.field_name_list)
        self.from_combobox.currentIndexChanged.connect(self.fromFieldIndexChanged)
        hlayout.addWidget(self.from_combobox)

        self.from_language_label = aqt.qt.QLabel()
        self.from_language = self.field_language[0]
        hlayout.addWidget(self.from_language_label)

        to_label = aqt.qt.QLabel()
        to_label.setText('To Field:')
        hlayout.addWidget(to_label)

        self.to_combobox = QtWidgets.QComboBox()
        self.to_combobox.addItems(self.field_name_list)
        self.to_combobox.currentIndexChanged.connect(self.toFieldIndexChanged)
        hlayout.addWidget(self.to_combobox)

        self.to_language_label = aqt.qt.QLabel()
        self.to_language = self.field_language[0]
        self.to_language_label.setText(self.languagetools.get_language_name(self.to_language))
        hlayout.addWidget(self.to_language_label)

        vlayout.addLayout(hlayout)

        # setup translation service
        # =========================

        hlayout = QtWidgets.QHBoxLayout()
        service_label = aqt.qt.QLabel()
        service_label.setText('Service:')
        hlayout.addWidget(service_label)

        self.service_combobox = QtWidgets.QComboBox()
        hlayout.addWidget(self.service_combobox)

        self.load_translations_button = QtWidgets.QPushButton()
        self.load_translations_button.setText('Load Translations')
        self.load_translations_button.pressed.connect(self.loadTranslations)
        hlayout.addWidget(self.load_translations_button)

        vlayout.addLayout(hlayout)

        # setup progress bar
        # ==================

        self.progress_bar = QtWidgets.QProgressBar()
        vlayout.addWidget(self.progress_bar)

        # setup preview table
        # ===================

        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.noteTableModel)
        vlayout.addWidget(self.table_view)

        self.pickDefaultFromToFields()
        self.updateTranslationOptions()

    def pickDefaultFromToFields(self):
        from_field_index = 0
        to_field_index = 1

        self.from_field = self.field_name_list[from_field_index]
        self.to_field = self.field_name_list[to_field_index]

        self.from_combobox.setCurrentIndex(from_field_index)
        self.to_combobox.setCurrentIndex(to_field_index)
        

    def fromFieldIndexChanged(self, currentIndex):
        self.from_field = self.field_name_list[currentIndex]
        language_code = self.field_language[currentIndex]
        self.from_language = language_code
        language_name = self.languagetools.get_language_name(language_code)
        self.from_language_label.setText(language_name)
        self.updateTranslationOptions()
        self.updateSampleData()


    def toFieldIndexChanged(self, currentIndex):
        self.to_field = self.field_name_list[currentIndex]
        language_code = self.field_language[currentIndex]
        self.to_language = language_code
        language_name = self.languagetools.get_language_name(language_code)
        self.to_language_label.setText(language_name)
        self.updateTranslationOptions()
        self.updateSampleData()

    def updateTranslationOptions(self):
        self.translation_options = self.languagetools.get_translation_options(self.from_language, self.to_language)
        self.translation_service_names = [x['service'] for x in self.translation_options]
        self.service_combobox.clear()
        self.service_combobox.addItems(self.translation_service_names)

    def updateSampleData(self):
        # self.from_field
        self.noteTableModel.setFromField(self.from_field)
        self.noteTableModel.setToField(self.to_field)
        from_field_data = []
        for note_id in self.note_id_list:
            note = aqt.mw.col.getNote(note_id)
            field_data = note[self.from_field]
            from_field_data.append(field_data)
        self.from_field_data = from_field_data
        self.noteTableModel.setFromFieldData(from_field_data)
        self.table_view.model().layoutChanged.emit()
        #self.loadTranslations()

    def loadTranslations(self):
        aqt.mw.taskman.run_in_background(self.loadTranslationsTask, self.loadTranslationDone)

    def loadTranslationsTask(self):
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setDisabled(True))
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setText('Loading...'))

        aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setValue(0))
        aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setMaximum(len(self.from_field_data)))

        # get service
        service = self.translation_service_names[self.service_combobox.currentIndex()]
        translation_options = self.languagetools.get_translation_options(self.from_language, self.to_language)
        translation_option_subset = [x for x in translation_options if x['service'] == service]
        assert(len(translation_option_subset) == 1)
        translation_option = translation_option_subset[0]

        i = 0
        for field_data in self.from_field_data:
            translation_result = self.languagetools.get_translation(field_data, translation_option)
            self.noteTableModel.setToFieldData(i, translation_result)
            self.table_view.model().layoutChanged.emit()
            i += 1
            aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setValue(i))

        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setDisabled(False))
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setText('Load Translations'))


    def loadTranslationDone(self, future_result):
        pass



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

        self.greenStylesheet = "background-color: #69F0AE;"

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
        self.topLevel.addWidget(get_header_label('Language Mapping'))

        # add auto-detection widgets
        hlayout = QtWidgets.QHBoxLayout()
        self.autodetect_progressbar = QtWidgets.QProgressBar()
        hlayout.addWidget(self.autodetect_progressbar)

        font2 = QtGui.QFont()
        font2.setPointSize(14)
        self.autodetect_button = QtWidgets.QPushButton()
        self.autodetect_button.setText('Run Auto Detection')
        self.autodetect_button.setFont(font2)
        self.autodetect_button.setStyleSheet(self.greenStylesheet)
        self.autodetect_button.pressed.connect(self.runLanguageDetection)
        hlayout.addWidget(self.autodetect_button)

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
        comboBox.setStyleSheet(self.greenStylesheet + "combobox-popup: 0;")

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
        if self.languagetools.check_api_key_valid() == False:
            return

        aqt.mw.taskman.run_in_background(self.runLanguageDetectionBackground, self.runLanguageDetectionDone)

    def runLanguageDetectionBackground(self):
        self.autodetect_button.setEnabled(False)

        dtnf_list: List[DeckNoteTypeField] = self.languagetools.get_populated_dntf()
        progress_max = len(dtnf_list)
        self.setProgressBarMax(progress_max)

        progress = 0
        for dntf in dtnf_list:
            language = self.languagetools.perform_language_detection_deck_note_type_field(dntf)
            #self.language_mapping_changes[deck_note_type_field] = language
            # need to set combo box correctly.
            comboBox = self.dntfComboxBoxMap[dntf]
            self.setFieldLanguageIndex(comboBox, language)

            # progress bar
            self.setProgressValue(progress)
            progress += 1
        
        self.setProgressValue(progress_max)

    def setProgressBarMax(self, progress_max):
        aqt.mw.taskman.run_on_main(lambda: self.autodetect_progressbar.setMaximum(progress_max))

    def setProgressValue(self, progress):
        aqt.mw.taskman.run_on_main(lambda: self.autodetect_progressbar.setValue(progress))

    def runLanguageDetectionDone(self, future_result):
        self.autodetect_button.setEnabled(True)


def language_mapping_dialogue(languagetools):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    mapping_dialog = aqt.qt.QDialog()
    mapping_dialog.ui = LanguageMappingDialog_UI(languagetools)
    mapping_dialog.ui.setupUi(mapping_dialog, deck_map)
    mapping_dialog.exec_()

def add_translation_dialog(languagetools, note_id_list):
    # print(f'* add_translation_dialog {note_id_list}')

    # ensure we only have one deck/notetype selected
    deck_note_type_map = {}

    for note_id in note_id_list:
        note = aqt.mw.col.getNote(note_id)
        cards = note.cards()
        for card in cards:
            deck_note_type = build_deck_note_type_from_note_card(note, card)
            if deck_note_type not in deck_note_type_map:
                deck_note_type_map[deck_note_type] = 0
            deck_note_type_map[deck_note_type] += 1

    if len(deck_note_type_map) > 1:
        # too many deck / model combinations
        summary_str = ', '.join([f'{numCards} note from {key}' for key, numCards in deck_note_type_map.items()])
        aqt.utils.showCritical(f'You must select notes from the same Deck / Note Type combination. You have selected {summary_str}', title=contants.ADDON_NAME)
        return
    
    deck_note_type = list(deck_note_type_map.keys())[0]

    dialog = BatchConversionDialog(languagetools, deck_note_type, note_id_list)
    dialog.setupUi()
    dialog.exec_()


