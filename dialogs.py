from typing import List, Dict
import sys
import traceback

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

def get_medium_label(text):
        label = QtWidgets.QLabel()
        label.setText(text)
        font = QtGui.QFont()
        label_font_size = 13
        font.setBold(True)
        font.setPointSize(label_font_size)
        label.setFont(font)
        return label

class NoteTableModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self, None)
        self.from_field_data = []
        self.to_field_data = []
        self.from_field = 'From'
        self.to_field = 'To'

    def setFromField(self, field_name):
        self.from_field = field_name
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, 1)
    
    def setToField(self, field_name):
        self.to_field = field_name
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, 1)

    def setFromFieldData(self, data):
        self.from_field_data = data
        self.to_field_data = [''] * len(self.from_field_data)
        # print(f'**** len(self.to_field_data): {len(self.to_field_data)}')
        start_index = self.createIndex(0, 0)
        end_index = self.createIndex(len(self.from_field_data)-1, 0)
        self.dataChanged.emit(start_index, end_index)

    def setToFieldData(self, row, to_field_result):
        # print(f'**** setToFieldData:, row: {row}')
        self.to_field_data[row] = to_field_result
        start_index = self.createIndex(row, 1)
        end_index = self.createIndex(row, 1)
        self.dataChanged.emit(start_index, end_index)

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

class NoFieldsAvailable(Exception):
    pass

class BatchConversionDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, deck_note_type: DeckNoteType, note_id_list, transformation_type):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        self.deck_note_type = deck_note_type
        self.note_id_list = note_id_list
        self.transformation_type = transformation_type

        # get field list
        model = aqt.mw.col.models.get(deck_note_type.model_id)
        fields = model['flds']
        field_names = [x['name'] for x in fields]

        # these are the available fields
        self.field_name_list = []
        self.deck_note_type_field_list = []
        self.field_language = []

        self.from_field_data = []
        self.to_field_data = []

        self.to_fields_empty = True

        self.noteTableModel = NoteTableModel()

        # retain fields which have a language set
        for field_name in field_names:
            deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
            language = self.languagetools.get_language(deck_note_type_field)
            if self.transformation_type == constants.TransformationType.Translation:
                if self.languagetools.language_available_for_translation(language):
                    self.field_name_list.append(field_name)
                    self.deck_note_type_field_list.append(deck_note_type_field)
                    self.field_language.append(language)
            elif self.transformation_type == constants.TransformationType.Transliteration:
                self.field_name_list.append(field_name)
                self.deck_note_type_field_list.append(deck_note_type_field)
                self.field_language.append(language)                

        if len(self.field_name_list) == 0:
            # no fields were found, could be that no fields have a language set
            raise NoFieldsAvailable(f'No fields available for {self.transformation_type.name} in  {self.deck_note_type}. {constants.DOCUMENTATION_ENSURE_LANGUAGE_MAPPING}')


    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = QtWidgets.QVBoxLayout(self)

        header_label_text_map = {
            constants.TransformationType.Translation: 'Add Translation',
            constants.TransformationType.Transliteration: 'Add Transliteration'
        }

        vlayout.addWidget(get_header_label(header_label_text_map[self.transformation_type]))

        # setup to/from fields
        # ====================

        gridlayout = QtWidgets.QGridLayout()

        # "from" side
        # -----------

        label_font_size = 13
        font1 = QtGui.QFont()
        font1.setBold(True)
        font1.setPointSize(label_font_size)

        from_label = aqt.qt.QLabel()
        from_label.setText('From Field:')
        from_label.setFont(font1)
        gridlayout.addWidget(from_label, 0, 0, 1, 1)

        self.from_combobox = QtWidgets.QComboBox()
        self.from_combobox.addItems(self.field_name_list)
        gridlayout.addWidget(self.from_combobox, 0, 1, 1, 1)

        gridlayout.addWidget(aqt.qt.QLabel('Language:'), 1, 0, 1, 1)

        self.from_language_label = aqt.qt.QLabel()
        gridlayout.addWidget(self.from_language_label, 1, 1, 1, 1)


        # "to" side
        # ---------

        to_label = aqt.qt.QLabel()
        to_label.setText('To Field:')
        to_label.setFont(font1)
        gridlayout.addWidget(to_label, 0, 3, 1, 1)

        self.to_combobox = QtWidgets.QComboBox()
        self.to_combobox.addItems(self.field_name_list)
        gridlayout.addWidget(self.to_combobox, 0, 4, 1, 1)

        gridlayout.addWidget(aqt.qt.QLabel('Language:'), 1, 3, 1, 1)
        self.to_language_label = aqt.qt.QLabel()
        gridlayout.addWidget(self.to_language_label, 1, 4, 1, 1)

        gridlayout.setColumnStretch(0, 50)
        gridlayout.setColumnStretch(1, 50)
        gridlayout.setColumnStretch(2, 30)
        gridlayout.setColumnStretch(3, 50)
        gridlayout.setColumnStretch(4, 50)

        gridlayout.setContentsMargins(20, 30, 20, 30)

        vlayout.addLayout(gridlayout)

        # setup translation service
        # =========================

        gridlayout = QtWidgets.QGridLayout()
        service_label = aqt.qt.QLabel()
        service_label.setFont(font1)
        service_label.setText('Service:')
        gridlayout.addWidget(service_label, 0, 0, 1, 1)

        self.service_combobox = QtWidgets.QComboBox()
        gridlayout.addWidget(self.service_combobox, 0, 1, 1, 1)


        self.load_translations_button = QtWidgets.QPushButton()
        self.load_button_text_map = {
            constants.TransformationType.Translation: 'Load Translations',
            constants.TransformationType.Transliteration: 'Load Transliterations'
        }        
        self.load_translations_button.setText(self.load_button_text_map[self.transformation_type])
        self.load_translations_button.setStyleSheet(constants.GREEN_STYLESHEET)
        gridlayout.addWidget(self.load_translations_button, 0, 3, 1, 2)

        if self.transformation_type == constants.TransformationType.Translation:
            gridlayout.setColumnStretch(0, 50)
            gridlayout.setColumnStretch(1, 50)
            gridlayout.setColumnStretch(2, 30)
            gridlayout.setColumnStretch(3, 50)
            gridlayout.setColumnStretch(4, 50)
        elif self.transformation_type == constants.TransformationType.Transliteration:
            # need to provide more space for the services combobox
            gridlayout.setColumnStretch(0, 20)
            gridlayout.setColumnStretch(1, 120)
            gridlayout.setColumnStretch(2, 0)
            gridlayout.setColumnStretch(3, 20)
            gridlayout.setColumnStretch(4, 20)            

        gridlayout.setContentsMargins(20, 0, 20, 10)

        vlayout.addLayout(gridlayout)

        # setup progress bar
        # ==================

        self.progress_bar = QtWidgets.QProgressBar()
        vlayout.addWidget(self.progress_bar)

        # setup preview table
        # ===================

        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.noteTableModel)
        header = self.table_view.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        vlayout.addWidget(self.table_view)

        # setup bottom buttons
        # ====================

        buttonBox = QtWidgets.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("Apply To Notes", QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setEnabled(False)
        self.cancelButton = buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setStyleSheet(constants.RED_STYLESHEET)

        
        vlayout.addWidget(buttonBox)

        self.pickDefaultFromToFields()
        self.updateTranslationOptions()

        # wire events
        # ===========
        self.from_combobox.currentIndexChanged.connect(self.fromFieldIndexChanged)
        self.to_combobox.currentIndexChanged.connect(self.toFieldIndexChanged)
        self.load_translations_button.pressed.connect(self.loadTranslations)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def pickDefaultFromToFields(self):
        # defaults in case nothing is set
        from_field_index = 0
        to_field_index = 1

        # do we have a batch translation setting set ?
        if self.transformation_type == constants.TransformationType.Translation:
            batch_translation_settings = self.languagetools.get_batch_translation_settings(self.deck_note_type)
            if len(batch_translation_settings) >= 1:
                # pick the first one
                setting_key = list(batch_translation_settings.keys())[0]
                setting = batch_translation_settings[setting_key]
                from_field = setting['from_field']
                to_field = setting_key
                # service = setting['translation_option']['service']
                if from_field in self.field_name_list:
                    from_field_index = self.field_name_list.index(from_field)
                if to_field in self.field_name_list:
                    to_field_index = self.field_name_list.index(to_field)
        if self.transformation_type == constants.TransformationType.Transliteration:
            batch_transliteration_settings = self.languagetools.get_batch_transliteration_settings(self.deck_note_type)
            if len(batch_transliteration_settings) >= 1:
                # pick the first one
                setting_key = list(batch_transliteration_settings.keys())[0]
                setting = batch_transliteration_settings[setting_key]
                from_field = setting['from_field']
                to_field = setting_key
                if from_field in self.field_name_list:
                    from_field_index = self.field_name_list.index(from_field)
                if to_field in self.field_name_list:
                    to_field_index = self.field_name_list.index(to_field)                

        # set some defaults
        self.from_field = self.field_name_list[from_field_index]
        self.to_field = self.field_name_list[to_field_index]

        # set languages
        self.from_language = self.field_language[from_field_index]
        self.to_language = self.field_language[to_field_index]

        self.from_combobox.setCurrentIndex(from_field_index)
        self.to_combobox.setCurrentIndex(to_field_index)
        
        self.fromFieldIndexChanged(from_field_index, initialization=True)
        self.toFieldIndexChanged(to_field_index, initialization=True)
        
    

    def fromFieldIndexChanged(self, currentIndex, initialization=False):
        self.from_field = self.field_name_list[currentIndex]
        language_code = self.field_language[currentIndex]
        self.from_language = language_code
        language_name = self.languagetools.get_language_name(language_code)
        self.from_language_label.setText(language_name)
        self.updateTranslationOptions()
        self.updateSampleData()


    def toFieldIndexChanged(self, currentIndex, initialization=False):
        self.to_field = self.field_name_list[currentIndex]
        language_code = self.field_language[currentIndex]
        self.to_language = language_code
        language_name = self.languagetools.get_language_name(language_code)
        self.to_language_label.setText(language_name)
        self.updateTranslationOptions()
        self.updateSampleData()

    def updateTranslationOptions(self):
        if self.transformation_type == constants.TransformationType.Translation:
            self.translation_options = self.languagetools.get_translation_options(self.from_language, self.to_language)
            self.translation_service_names = [x['service'] for x in self.translation_options]
            self.service_combobox.clear()
            self.service_combobox.addItems(self.translation_service_names)
            # do we have a user preference ?
            batch_translation_settings = self.languagetools.get_batch_translation_settings(self.deck_note_type)
            if len(batch_translation_settings) >= 1:
                # pick the first one
                setting_key = list(batch_translation_settings.keys())[0]
                setting = batch_translation_settings[setting_key]
                service = setting['translation_option']['service']
                if service in self.translation_service_names:
                    service_index = self.translation_service_names.index(service)
                    self.service_combobox.setCurrentIndex(service_index)
        if self.transformation_type == constants.TransformationType.Transliteration:
            self.transliteration_options = self.languagetools.get_transliteration_options(self.from_language)
            self.transliteration_service_names = [x['transliteration_name'] for x in self.transliteration_options]
            self.service_combobox.clear()
            self.service_combobox.addItems(self.transliteration_service_names)
            # do we have a user preference ?
            batch_transliteration_settings = self.languagetools.get_batch_transliteration_settings(self.deck_note_type)
            if len(batch_transliteration_settings) >= 1:
                # pick the first one
                setting_key = list(batch_transliteration_settings.keys())[0]
                setting = batch_transliteration_settings[setting_key]
                # find the index of the service we want
                transliteration_name = setting['transliteration_option']['transliteration_name']
                if transliteration_name in self.transliteration_service_names:
                    service_index = self.transliteration_service_names.index(transliteration_name)
                    self.service_combobox.setCurrentIndex(service_index)

    def updateSampleData(self):
        # self.from_field
        self.noteTableModel.setFromField(self.from_field)
        self.noteTableModel.setToField(self.to_field)
        from_field_data = []
        self.to_fields_empty = True
        for note_id in self.note_id_list:
            note = aqt.mw.col.getNote(note_id)
            field_data = note[self.from_field]
            from_field_data.append(field_data)
            # self.to_fields_empty = True
            if len(note[self.to_field]) > 0:
                self.to_fields_empty = False
        self.from_field_data = from_field_data
        self.noteTableModel.setFromFieldData(from_field_data)

    def loadTranslations(self):
        if self.languagetools.check_api_key_valid() == False:
            return
        aqt.mw.taskman.run_in_background(self.loadTranslationsTask, self.loadTranslationDone)

    def loadTranslationsTask(self):
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setDisabled(True))
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setStyleSheet(None))
        aqt.mw.taskman.run_on_main(lambda: self.applyButton.setDisabled(True))
        aqt.mw.taskman.run_on_main(lambda: self.applyButton.setStyleSheet(None))
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setText('Loading...'))

        aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setValue(0))
        aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setMaximum(len(self.from_field_data)))

        # get service
        if self.transformation_type == constants.TransformationType.Translation:
            service = self.translation_service_names[self.service_combobox.currentIndex()]
            translation_options = self.languagetools.get_translation_options(self.from_language, self.to_language)
            translation_option_subset = [x for x in translation_options if x['service'] == service]
            assert(len(translation_option_subset) == 1)
            self.translation_option = translation_option_subset[0]
        elif self.transformation_type == constants.TransformationType.Transliteration:
            self.transliteration_option = self.transliteration_options[self.service_combobox.currentIndex()]

        def get_set_to_field_lambda(i, translation_result):
            def set_to_field():
                self.noteTableModel.setToFieldData(i, translation_result)
            return set_to_field

        i = 0
        self.to_field_data = []
        for field_data in self.from_field_data:
            if self.transformation_type == constants.TransformationType.Translation:
                translation_result = self.languagetools.get_translation(field_data, self.translation_option)
            elif self.transformation_type == constants.TransformationType.Transliteration:
                translation_result = self.languagetools.get_transliteration(field_data, 
                                                                            self.transliteration_option['service'],
                                                                            self.transliteration_option['transliteration_key'])
            self.to_field_data.append(translation_result)
            aqt.mw.taskman.run_on_main(get_set_to_field_lambda(i, translation_result))
            i += 1
            aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setValue(i))

        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setDisabled(False))
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setStyleSheet(constants.GREEN_STYLESHEET))
        aqt.mw.taskman.run_on_main(lambda: self.applyButton.setDisabled(False))
        aqt.mw.taskman.run_on_main(lambda: self.applyButton.setStyleSheet(constants.GREEN_STYLESHEET))        
        aqt.mw.taskman.run_on_main(lambda: self.load_translations_button.setText(self.load_button_text_map[self.transformation_type]))


    def loadTranslationDone(self, future_result):
        pass

    def accept(self):
        if self.to_fields_empty == False:
            proceed = aqt.utils.askUser(f'Overwrite existing data in field {self.to_field} ?')
            if proceed == False:
                return
        # set field on notes
        action_str = f'Translate from {self.languagetools.get_language_name(self.from_language)} to {self.languagetools.get_language_name(self.to_language)}'
        aqt.mw.checkpoint(action_str)
        for (note_id, i) in zip(self.note_id_list, range(len(self.note_id_list))):
            #print(f'note_id: {note_id} i: {i}')
            note = aqt.mw.col.getNote(note_id)
            note[self.to_field] = self.to_field_data[i]
            # print(f'** setting field {self.to_field} to {self.to_field_data[i]}')
            note.flush()
        self.close()
        # memorize this setting
        deck_note_type_field = DeckNoteTypeField(self.deck_note_type, self.to_field)
        if self.transformation_type == constants.TransformationType.Translation:
            self.languagetools.store_batch_translation_setting(deck_note_type_field, self.from_field, self.translation_option)
        elif self.transformation_type == constants.TransformationType.Transliteration:
            self.languagetools.store_batch_transliteration_setting(deck_note_type_field, self.from_field, self.transliteration_option)
        aqt.utils.tooltip(f'Wrote data into field {self.to_field}')

class AddAudioDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, deck_note_type: DeckNoteType, note_id_list):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        self.deck_note_type = deck_note_type
        self.note_id_list = note_id_list

        # get field list
        model = aqt.mw.col.models.get(deck_note_type.model_id)
        fields = model['flds']
        field_names = [x['name'] for x in fields]

        self.voice_selection_settings = languagetools.get_voice_selection_settings()
        self.batch_audio_settings = languagetools.get_batch_audio_settings(self.deck_note_type)

        # these are the available fields
        # build separate lists for to and from
        self.from_field_name_list = []
        self.from_deck_note_type_field_list = []
        self.from_field_language = []

        self.to_field_name_list = []
        self.to_deck_note_type_field_list = []

        # retain fields which have a language set
        for field_name in field_names:
            deck_note_type_field = DeckNoteTypeField(deck_note_type, field_name)
            language = self.languagetools.get_language(deck_note_type_field)

            if self.languagetools.language_available_for_translation(language):
                self.from_field_name_list.append(field_name)
                self.from_deck_note_type_field_list.append(deck_note_type_field)
                self.from_field_language.append(language)

            self.to_field_name_list.append(field_name)
            self.to_deck_note_type_field_list.append(deck_note_type_field)

        
    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 200)

        vlayout = QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(get_header_label('Add Audio'))

        # from/ to field
        gridlayout = QtWidgets.QGridLayout()

        # from
        gridlayout.addWidget(get_medium_label('From Field:'), 0, 0, 1, 1)
        self.from_field_combobox = QtWidgets.QComboBox()
        self.from_field_combobox.addItems(self.from_field_name_list)
        gridlayout.addWidget(self.from_field_combobox, 0, 1, 1, 1)
        # to
        gridlayout.addWidget(get_medium_label('To Field:'), 0, 3, 1, 1)
        self.to_field_combobox = QtWidgets.QComboBox()
        self.to_field_combobox.addItems(self.to_field_name_list)
        gridlayout.addWidget(self.to_field_combobox, 0, 4, 1, 1)

        # voice
        gridlayout.addWidget(get_medium_label('Voice:'), 1, 0, 1, 2)
        self.voice_label = aqt.qt.QLabel()
        self.voice_label.setText('undefined')
        self.voice = QtWidgets.QComboBox()
        gridlayout.addWidget(self.voice_label, 1, 1, 1, 4)

        vlayout.addLayout(gridlayout)

        self.progress_bar = QtWidgets.QProgressBar()
        vlayout.addWidget(self.progress_bar)        

        vlayout.addStretch()

        buttonBox = QtWidgets.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("Apply To Notes", QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setEnabled(False)
        self.cancelButton = buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setStyleSheet(constants.RED_STYLESHEET)

        vlayout.addWidget(buttonBox)

        # wire events
        self.pick_default_fields()
        self.from_field_combobox.currentIndexChanged.connect(self.from_field_index_changed)
        self.to_field_combobox.currentIndexChanged.connect(self.to_field_index_changed)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def pick_default_fields(self):
        #self.batch_audio_settings
        self.from_field_index = 0
        self.to_field_index = 0

        if len(self.batch_audio_settings) > 0:
            to_field = list(self.batch_audio_settings.keys())[0]
            from_field = self.batch_audio_settings[to_field]
            try:
                from_field_index = self.from_field_name_list.index(from_field)
                to_field_index = self.to_field_name_list.index(to_field)

                if from_field_index < len(self.from_field_name_list):
                    self.from_field_index = from_field_index
                if to_field_index < len(self.to_field_name_list):
                    self.to_field_index = to_field_index
                
            except ValueError:
                pass

        self.from_field = self.from_field_name_list[self.from_field_index]
        self.to_field = self.to_field_name_list[self.to_field_index]

        self.from_field_index_changed(self.from_field_index)
        self.from_field_combobox.setCurrentIndex(self.from_field_index)

        self.to_field_combobox.setCurrentIndex(self.to_field_index)

    def from_field_index_changed(self, field_index):
        self.from_field_index = field_index
        self.from_field = self.from_field_name_list[self.from_field_index]
        from_language = self.from_field_language[field_index]
        # do we have a voice setup for this language ?

        if from_language in self.voice_selection_settings:
            self.voice = self.voice_selection_settings[from_language]
            voice_description = self.voice['voice_description']
            self.voice_label.setText('<b>' + voice_description + '</b>')
            self.applyButton.setEnabled(True)
            self.applyButton.setStyleSheet(constants.GREEN_STYLESHEET)
        else:
            language_name = self.languagetools.get_language_name(from_language)
            self.voice_label.setText(f'No Voice setup for <b>{language_name}</b>. Please go to Anki main window, ' +
            '<b>Tools -> Language Tools: Voice Selection </b>')
            self.applyButton.setEnabled(False)
            self.applyButton.setStyleSheet(None)

    def to_field_index_changed(self, field_index):
        self.to_field_index = field_index
        self.to_field = self.to_field_name_list[self.to_field_index]

    def accept(self):
        to_fields_empty = True
        for note_id in self.note_id_list:
            note = aqt.mw.col.getNote(note_id)
            if len(note[self.to_field]) > 0:
                to_fields_empty = False
        if to_fields_empty == False:
            proceed = aqt.utils.askUser(f'Overwrite existing data in field {self.to_field} ?')
            if proceed == False:
                # don't continue
                return

        self.applyButton.setText('Adding Audio...')
        self.applyButton.setEnabled(False)
        self.applyButton.setStyleSheet(None)

        self.progress_bar.setMaximum(len(self.note_id_list))

        deck_note_type_field = DeckNoteTypeField(self.deck_note_type, self.to_field)
        self.languagetools.store_batch_audio_setting(deck_note_type_field, self.from_field)

        self.success_count = 0

        action_str = f'Add Audio to {self.to_field}'
        aqt.mw.checkpoint(action_str)

        aqt.mw.taskman.run_in_background(self.add_audio_task, self.add_audio_task_done)

    def add_audio_task(self):
        i = 0
        for note_id in self.note_id_list:
            result = self.languagetools.generate_audio_for_field(note_id, self.from_field, self.to_field, self.voice)
            if result == True:
                self.success_count += 1
            i += 1
            aqt.mw.taskman.run_on_main(lambda: self.progress_bar.setValue(i))

    def add_audio_task_done(self, future_result):
        completion_message = f"Added Audio to field <b>{self.to_field}</b> using voice <b>{self.voice['voice_description']}</b>. Success: <b>{self.success_count}</b> out of <b>{len(self.note_id_list)}</b>."
        self.close()
        aqt.utils.showInfo(completion_message, title=constants.ADDON_NAME)

class NoteSettingsDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, deck_note_type: DeckNoteType):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        self.deck_note_type = deck_note_type

        self.remove_translation_map = {}
        self.remove_transliteration_map = {}
        self.remove_audio_map = {}

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(get_header_label(f'Settings for {self.deck_note_type}'))

        # do we have translation rules for this deck_note_type
        translation_settings = self.languagetools.get_batch_translation_settings(self.deck_note_type)
        if len(translation_settings) > 0:
            vlayout.addWidget(get_medium_label(f'Translation Settings'))
            gridlayout = QtWidgets.QGridLayout()
            i = 0
            for to_field, setting in translation_settings.items():
                from_field = setting['from_field']
                from_dntf = DeckNoteTypeField(self.deck_note_type, from_field)
                to_dntf = DeckNoteTypeField(self.deck_note_type, to_field)
                from_language_name = self.languagetools.get_language_name(self.languagetools.get_language(from_dntf))
                to_language_name = self.languagetools.get_language_name(self.languagetools.get_language(to_dntf))
                gridlayout.addWidget(QtWidgets.QLabel(f'From:'), i, 0, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'{from_field}'), i, 1, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'({from_language_name})'), i, 2, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'To:'), i, 3, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'{to_field}'), i, 4, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'({to_language_name})'), i, 5, 1, 1)
                
                delete_button = QtWidgets.QPushButton()
                delete_button.setText('Remove')
                gridlayout.addWidget(delete_button, i, 6, 1, 1)
                i += 1
            vlayout.addLayout(gridlayout)

        # do we have transliteration rules for this deck_note_type
        transliteration_settings = self.languagetools.get_batch_transliteration_settings(self.deck_note_type)
        if len(transliteration_settings) > 0:
            vlayout.addWidget(get_medium_label(f'Transliteration Settings'))
            gridlayout = QtWidgets.QGridLayout()
            i = 0
            for to_field, setting in transliteration_settings.items():
                from_field = setting['from_field']
                from_dntf = DeckNoteTypeField(self.deck_note_type, from_field)
                to_dntf = DeckNoteTypeField(self.deck_note_type, to_field)
                from_language_name = self.languagetools.get_language_name(self.languagetools.get_language(from_dntf))
                transliteration_name = setting['transliteration_option']['transliteration_name']
                gridlayout.addWidget(QtWidgets.QLabel(f'From:'), i, 0, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'{from_field}'), i, 1, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'({from_language_name})'), i, 2, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'To:'), i, 3, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'{to_field}'), i, 4, 1, 1)
                gridlayout.addWidget(QtWidgets.QLabel(f'({transliteration_name})'), i, 5, 1, 1)
                
                delete_button = QtWidgets.QPushButton()
                delete_button.setText('Remove')
                gridlayout.addWidget(delete_button, i, 6, 1, 1)
                i += 1
            vlayout.addLayout(gridlayout)            

        # do we have any audio rules for this deck_note_type
        audio_settings = self.languagetools.get_batch_audio_settings(self.deck_note_type)
        if len(audio_settings) > 0:
            vlayout.addWidget(get_medium_label(f'Audio Settings'))

        vlayout.addStretch()

        # buttom buttons
        buttonBox = QtWidgets.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("Save Settings", QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setEnabled(False)
        self.cancelButton = buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setStyleSheet(constants.RED_STYLESHEET)
        vlayout.addWidget(buttonBox)
  


class VoiceSelectionDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, voice_list):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        
        # get list of languages
        self.voice_list = voice_list
        wanted_language_arrays = languagetools.get_wanted_language_arrays()
        self.language_name_list = wanted_language_arrays['language_name_list']
        self.language_code_list = wanted_language_arrays['language_code_list']

        self.sample_size = 10

        self.voice_selection_settings = self.languagetools.get_voice_selection_settings()

        self.voice_mapping_changes = {} # indexed by language code

        self.voice_select_callback_enabled = True

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(get_header_label('Audio Voice Selection'))

        # setup grid
        # ==========

        gridlayout = QtWidgets.QGridLayout()

        label_font_size = 13
        font1 = QtGui.QFont()
        font1.setBold(True)
        font1.setPointSize(label_font_size)

        # language

        language_label = aqt.qt.QLabel()
        language_label.setText('Language:')
        language_label.setFont(font1)
        gridlayout.addWidget(language_label, 0, 0, 1, 1)

        language_combobox = QtWidgets.QComboBox()
        language_combobox.addItems(self.language_name_list)
        gridlayout.addWidget(language_combobox, 0, 1, 1, 1)

        # voices

        voice_label = aqt.qt.QLabel()
        voice_label.setText('Voice:')
        voice_label.setFont(font1)
        gridlayout.addWidget(voice_label, 1, 0, 1, 1)

        self.voice_combobox = QtWidgets.QComboBox()
        self.voice_combobox.setMaxVisibleItems(15)
        self.voice_combobox.setStyleSheet("combobox-popup: 0;")        
        gridlayout.addWidget(self.voice_combobox, 1, 1, 1, 1)

        # button to refresh samples
        samples_label = aqt.qt.QLabel()
        samples_label.setText('Random Samples:')
        samples_label.setFont(font1)
        gridlayout.addWidget(samples_label, 2, 0, 1, 1)

        samples_reload_button = QtWidgets.QPushButton()
        samples_reload_button.setText('Reload Random Samples')
        gridlayout.addWidget(samples_reload_button, 2, 1, 1, 1)

        gridlayout.setContentsMargins(10, 20, 10, 0)
        vlayout.addLayout(gridlayout)

        # samples, 
        self.samples_gridlayout = QtWidgets.QGridLayout()
        self.sample_labels = []
        self.sample_play_buttons = []
        for i in range(self.sample_size):
            sample_label = aqt.qt.QLabel()
            sample_label.setText('sample')
            self.sample_labels.append(sample_label)
            sample_button = QtWidgets.QPushButton()
            sample_button.setText('Play Audio')
            def get_play_lambda(i):
                def play():
                    self.play_sample(i)
                return play
            sample_button.pressed.connect(get_play_lambda(i))
            self.sample_play_buttons.append(sample_button)
            self.samples_gridlayout.addWidget(sample_label, i, 0, 1, 1)
            self.samples_gridlayout.addWidget(sample_button, i, 1, 1, 1)
        self.samples_gridlayout.setColumnStretch(0, 70)
        self.samples_gridlayout.setColumnStretch(1, 30)
        self.samples_gridlayout.setContentsMargins(20, 20, 20, 20)
        vlayout.addLayout(self.samples_gridlayout)

        vlayout.addStretch()

        # buttom buttons
        buttonBox = QtWidgets.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("Save Voice Selection", QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setEnabled(False)
        self.cancelButton = buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setStyleSheet(constants.RED_STYLESHEET)
        vlayout.addWidget(buttonBox)

        # wire events
        # ===========

        language_combobox.currentIndexChanged.connect(self.language_index_changed)
        # run once
        self.language_index_changed(0)
        self.voice_combobox.currentIndexChanged.connect(self.voice_index_changed)

        samples_reload_button.pressed.connect(self.load_field_samples)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def language_index_changed(self, current_index):
        self.voice_select_callback_enabled = False
        self.language_code = self.language_code_list[current_index]
        # filter voices that match this language
        available_voices = [x for x in self.voice_list if x['language_code'] == self.language_code]
        self.available_voices = sorted(available_voices, key=lambda x: x['voice_description'])
        available_voice_mappings = self.available_voices
        available_voice_names = [x['voice_description'] for x in self.available_voices]
        self.voice_combobox.clear()
        self.voice_combobox.addItems(available_voice_names)
        # do we have a required change for this language already ?
        voice_index = 0
        if self.language_code in self.voice_mapping_changes:
            try:
                voice_index = available_voice_mappings.index(self.voice_mapping_changes[self.language_code])
            except ValueError:
                pass
            # print(f'found language_code {self.language_code} in voice_mapping_changes: {voice_index}')
        elif self.language_code in self.voice_selection_settings:
            try:
                voice_index = available_voice_mappings.index(self.voice_selection_settings[self.language_code])
            except ValueError:
                pass                
            # print(f'found language_code {self.language_code} in voice_selection_settings: {voice_index}')
        self.voice_combobox.setCurrentIndex(voice_index)

        self.load_field_samples()

        self.voice_select_callback_enabled = True

    def voice_index_changed(self, current_index):
        if self.voice_select_callback_enabled:
            voice = self.available_voices[current_index]
            change_required = False
            if self.language_code not in self.voice_selection_settings:
                change_required = True
            elif self.voice_selection_settings[self.language_code] != voice:
                change_required = True

            if change_required:
                self.voice_mapping_changes[self.language_code] = voice
                # print(f'voice_mapping_changes: {self.voice_mapping_changes}')
                self.applyButton.setEnabled(True)
                self.applyButton.setStyleSheet(constants.GREEN_STYLESHEET)

    def load_field_samples(self):
        # get sample
        self.field_samples = self.languagetools.get_field_samples_for_language(self.language_code, self.sample_size)
        # print(self.field_samples)
        for i in range(self.sample_size):
            if i < len(self.field_samples):
                # populate label
                self.sample_labels[i].setText(self.field_samples[i])
            else:
                self.sample_labels[i].setText('empty')

    def play_sample(self, i):
        if i < len(self.field_samples):
            source_text = self.field_samples[i]
            # get index of voice
            voice_index = self.voice_combobox.currentIndex()
            voice = self.available_voices[voice_index]

            self.sample_play_buttons[i].setText('Loading...')
            self.sample_play_buttons[i].setDisabled(True)
            aqt.mw.taskman.run_in_background(lambda: self.play_audio(source_text, voice), lambda x: self.play_audio_done(x, i))


    def play_audio(self, source_text, voice):
        voice_key = voice['voice_key']
        service = voice['service']

        audio_temp_filename = self.languagetools.get_tts_audio(source_text, service, voice_key, {})
        if audio_temp_filename != None:
            aqt.sound.av_player.play_file(audio_temp_filename)

    def play_audio_done(self, future_result, i):
        self.sample_play_buttons[i].setText('Play Audio')
        self.sample_play_buttons[i].setDisabled(False)

    def accept(self):
        for language_code, voice_mapping in self.voice_mapping_changes.items():
            self.languagetools.store_voice_selection(language_code, voice_mapping)
        aqt.utils.tooltip(f'Saved Voice Selections')
        self.close()

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

        self.autodetect_in_progress = False

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
        self.autodetect_button.setStyleSheet(constants.GREEN_STYLESHEET)
        self.autodetect_button.pressed.connect(self.runLanguageDetection)
        hlayout.addWidget(self.autodetect_button)

        self.topLevel.addLayout(hlayout)


        for deck_name, deck in deck_map.items():
            self.layoutDecks(deck_name, deck)


        self.scrollArea.setWidget(self.layoutWidget)
        self.topLevel.addWidget(self.scrollArea)

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.applyButton = self.buttonBox.addButton("Apply", QtWidgets.QDialogButtonBox.AcceptRole)
        self.disableApplyButton()
        cancelButton = self.buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        cancelButton.setStyleSheet(constants.RED_STYLESHEET)
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
        comboBox.setStyleSheet(constants.GREEN_STYLESHEET + "combobox-popup: 0;")
        # enable apply button
        if not self.autodetect_in_progress:
            self.enableApplyButton()

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
        try:
            self.autodetect_in_progress = True
            self.autodetect_button.setEnabled(False)
            self.disableApplyButton()

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
        except:
            error_message = str(sys.exc_info())
            self.displayErrorMessage(error_message)


    def setProgressBarMax(self, progress_max):
        aqt.mw.taskman.run_on_main(lambda: self.autodetect_progressbar.setMaximum(progress_max))

    def setProgressValue(self, progress):
        aqt.mw.taskman.run_on_main(lambda: self.autodetect_progressbar.setValue(progress))

    def displayErrorMessage(self, message):
        aqt.mw.taskman.run_on_main(lambda: aqt.utils.showCritical(f"Could not run language detection: {message}", title=constants.ADDON_NAME))

    def runLanguageDetectionDone(self, future_result):
        self.autodetect_in_progress = False
        self.autodetect_button.setEnabled(True)
        self.enableApplyButton()


    def disableApplyButton(self):
        self.applyButton.setStyleSheet(None)
        self.applyButton.setDisabled(True)

    def enableApplyButton(self):
        self.applyButton.setStyleSheet(constants.GREEN_STYLESHEET)
        self.applyButton.setDisabled(False)


def language_mapping_dialogue(languagetools):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    mapping_dialog = aqt.qt.QDialog()
    mapping_dialog.ui = LanguageMappingDialog_UI(languagetools)
    mapping_dialog.ui.setupUi(mapping_dialog, deck_map)
    mapping_dialog.exec_()

def voice_selection_dialog(languagetools):
    # did the user perform language mapping ? 
    if not languagetools.language_detection_done():
        aqt.utils.showInfo(text='Please setup Language Mappings, from the Anki main screen: Tools -> Language Tools: Language Mapping', title=constants.ADDON_NAME)
        return

    voice_list = languagetools.get_tts_voice_list()

    voice_selection_dialog = dialog = VoiceSelectionDialog(languagetools, voice_list)
    voice_selection_dialog.setupUi()
    voice_selection_dialog.exec_()

def verify_deck_note_type_consistent(note_id_list):
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
        summary_str = ', '.join([f'{numCards} notes from {key}' for key, numCards in deck_note_type_map.items()])
        aqt.utils.showCritical(f'You must select notes from the same Deck / Note Type combination. You have selected {summary_str}', title=constants.ADDON_NAME)
        return None
    
    deck_note_type = list(deck_note_type_map.keys())[0]

    return deck_note_type

def add_transformation_dialog(languagetools, browser: aqt.browser.Browser, note_id_list, transformation_type):
    # print(f'* add_translation_dialog {note_id_list}')

    # did the user perform language mapping ? 
    if not languagetools.language_detection_done():
        aqt.utils.showInfo(text='Please setup Language Mappings, from the Anki main screen: Tools -> Language Tools: Language Mapping', title=constants.ADDON_NAME)
        return

    deck_note_type = verify_deck_note_type_consistent(note_id_list)
    if deck_note_type == None:
        return

    try:
        dialog = BatchConversionDialog(languagetools, deck_note_type, note_id_list, transformation_type)
        dialog.setupUi()
        dialog.exec_()

        # force browser to reload notes
        browser.model.reset()
    except NoFieldsAvailable as exception:
        aqt.utils.showCritical(str(exception), title=constants.ADDON_NAME)


def add_translation_dialog(languagetools, browser: aqt.browser.Browser, note_id_list):
    add_transformation_dialog(languagetools, browser, note_id_list, constants.TransformationType.Translation)

def add_transliteration_dialog(languagetools, browser: aqt.browser.Browser, note_id_list):
    add_transformation_dialog(languagetools, browser, note_id_list, constants.TransformationType.Transliteration)

def add_audio_dialog(languagetools, browser: aqt.browser.Browser, note_id_list):
    # did the user perform language mapping ? 
    if not languagetools.language_detection_done():
        aqt.utils.showInfo(text='Please setup Language Mappings, from the Anki main screen: Tools -> Language Tools: Language Mapping', title=constants.ADDON_NAME)
        return

    deck_note_type = verify_deck_note_type_consistent(note_id_list)
    if deck_note_type == None:
        return

    dialog = AddAudioDialog(languagetools, deck_note_type, note_id_list)
    dialog.setupUi()
    dialog.exec_()

    # force browser to reload notes
    browser.model.reset()    

def show_settings_dialog(languagetools, browser: aqt.browser.Browser, note_id_list):
    deck_note_type = verify_deck_note_type_consistent(note_id_list)
    if deck_note_type == None:
        return

    dialog = NoteSettingsDialog(languagetools, deck_note_type)
    dialog.setupUi()
    dialog.exec_()