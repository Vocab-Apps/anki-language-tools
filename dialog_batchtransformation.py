import sys
import logging
from typing import List, Dict
import aqt.qt

if hasattr(sys, '_pytest_mode'):
    import constants
    import deck_utils
    import gui_utils
    import errors
    from languagetools import LanguageTools
else:
    from . import constants
    from . import deck_utils
    from . import gui_utils
    from . import errors
    from .languagetools import LanguageTools

class NoteTableModel(aqt.qt.QAbstractTableModel):
    def __init__(self):
        aqt.qt.QAbstractTableModel.__init__(self, None)
        self.from_field_data = []
        self.to_field_data = []
        self.from_field = 'From'
        self.to_field = 'To'

    def flags(self, index):
        if index.column() == 1: # second column is editable
            return aqt.qt.Qt.ItemIsEditable | aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled
        # return default
        return aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled

    def setFromField(self, field_name):
        self.from_field = field_name
        self.headerDataChanged.emit(aqt.qt.Qt.Orientation.Horizontal, 0, 1)
    
    def setToField(self, field_name):
        self.to_field = field_name
        self.headerDataChanged.emit(aqt.qt.Qt.Orientation.Horizontal, 0, 1)

    def setFromFieldData(self, data):
        self.from_field_data = data
        self.to_field_data = [None] * len(self.from_field_data)
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
            return aqt.qt.QVariant()
        elif role != aqt.qt.Qt.ItemDataRole.DisplayRole and role != aqt.qt.Qt.EditRole: # only support display and edit
           return aqt.qt.QVariant()
        if index.column() == 0:
            # from field
            return aqt.qt.QVariant(self.from_field_data[index.row()])
        else:
            # result field
            return aqt.qt.QVariant(self.to_field_data[index.row()])

    def setData(self, index, value, role):
        if index.column() != 1:
            return False
        if index.isValid() and role == aqt.qt.Qt.EditRole:
            # memorize the value
            row = index.row()
            self.to_field_data[row] = value
            # emit change signal
            start_index = self.createIndex(row, 1)
            end_index = self.createIndex(row, 1)
            self.dataChanged.emit(start_index, end_index)            
            return True
        else:
            return False

    def headerData(self, col, orientation, role):
        if orientation == aqt.qt.Qt.Orientation.Horizontal and role == aqt.qt.Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return aqt.qt.QVariant(self.from_field)
            else:
                return aqt.qt.QVariant(self.to_field)
        return aqt.qt.QVariant()

class BatchConversionDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, deck_note_type: deck_utils.DeckNoteType, note_id_list, transformation_type):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        self.deck_note_type = deck_note_type
        self.note_id_list = note_id_list
        self.transformation_type = transformation_type

        # get field list
        field_names = self.languagetools.deck_utils.get_field_names(deck_note_type)

        # these are the available fields
        self.field_name_list = []
        self.deck_note_type_field_list = []
        self.field_language = []

        self.from_field_data = []
        self.to_field_data = []

        self.to_fields_empty = True

        self.noteTableModel = NoteTableModel()

        at_least_one_field_language_set = False

        # retain fields which have a language set
        for field_name in field_names:
            deck_note_type_field = languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, field_name)
            language = self.languagetools.get_language(deck_note_type_field)

            if self.languagetools.language_available_for_translation(language):
                at_least_one_field_language_set = True

            if self.transformation_type == constants.TransformationType.Translation:
                if self.languagetools.language_available_for_translation(language):
                    self.field_name_list.append(field_name)
                    self.deck_note_type_field_list.append(deck_note_type_field)
                    self.field_language.append(language)
            elif self.transformation_type == constants.TransformationType.Transliteration:
                self.field_name_list.append(field_name)
                self.deck_note_type_field_list.append(deck_note_type_field)
                self.field_language.append(language)                

        if at_least_one_field_language_set == False:
            error_message = f'No fields available for {self.transformation_type.name} in {self.deck_note_type}'
            # no fields were found, could be that no fields have a language set
            raise errors.LanguageMappingError(error_message)


    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = aqt.qt.QVBoxLayout(self)

        header_label_text_map = {
            constants.TransformationType.Translation: 'Add Translation',
            constants.TransformationType.Transliteration: 'Add Transliteration'
        }

        vlayout.addWidget(gui_utils.get_header_label(header_label_text_map[self.transformation_type]))

        description_label = aqt.qt.QLabel(f'After adding {self.transformation_type.name.lower()} to notes, the setting will be memorized.')
        vlayout.addWidget(description_label)

        # setup to/from fields
        # ====================

        gridlayout = aqt.qt.QGridLayout()

        # "from" side
        # -----------

        label_font_size = 13
        font1 = aqt.qt.QFont()
        font1.setBold(True)
        font1.setPointSize(label_font_size)

        from_label = aqt.qt.QLabel()
        from_label.setText('From Field:')
        from_label.setFont(font1)
        gridlayout.addWidget(from_label, 0, 0, 1, 1)

        self.from_combobox = aqt.qt.QComboBox()
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

        self.to_combobox = aqt.qt.QComboBox()
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

        gridlayout = aqt.qt.QGridLayout()
        service_label = aqt.qt.QLabel()
        service_label.setFont(font1)
        service_label.setText('Service:')
        gridlayout.addWidget(service_label, 0, 0, 1, 1)

        self.service_combobox = aqt.qt.QComboBox()
        gridlayout.addWidget(self.service_combobox, 0, 1, 1, 1)


        self.load_translations_button = aqt.qt.QPushButton()
        self.load_button_text_map = {
            constants.TransformationType.Translation: 'Load Translations',
            constants.TransformationType.Transliteration: 'Load Transliterations'
        }        
        self.load_translations_button.setText(self.load_button_text_map[self.transformation_type])
        self.load_translations_button.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet())
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

        self.progress_bar = aqt.qt.QProgressBar()
        vlayout.addWidget(self.progress_bar)

        # setup preview table
        # ===================

        self.table_view = aqt.qt.QTableView()
        self.table_view.setModel(self.noteTableModel)
        header = self.table_view.horizontalHeader()       
        header.setSectionResizeMode(0, aqt.qt.QHeaderView.Stretch)
        header.setSectionResizeMode(1, aqt.qt.QHeaderView.Stretch)
        vlayout.addWidget(self.table_view)

        # setup bottom buttons
        # ====================

        buttonBox = aqt.qt.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("Apply To Notes", aqt.qt.QDialogButtonBox.AcceptRole)
        self.applyButton.setEnabled(False)
        self.cancelButton = buttonBox.addButton("Cancel", aqt.qt.QDialogButtonBox.RejectRole)
        self.cancelButton.setStyleSheet(self.languagetools.anki_utils.get_red_stylesheet())

        
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
        # don't crash
        from_field_index = min(from_field_index, len(self.field_name_list) - 1)
        to_field_index = min(to_field_index, len(self.field_name_list) - 1)
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
            note = self.languagetools.anki_utils.get_note_by_id(note_id)
            field_data = note[self.from_field]
            from_field_data.append(field_data)
            # self.to_fields_empty = True
            if len(note[self.to_field]) > 0:
                self.to_fields_empty = False
        self.from_field_data = from_field_data
        self.noteTableModel.setFromFieldData(from_field_data)

    def loadTranslations(self):
        if self.languagetools.ensure_api_key_checked() == False:
            return
        if self.transformation_type == constants.TransformationType.Translation:
            if len(self.translation_options) == 0:
                self.languagetools.anki_utils.critical_message(f'No service found for translation from language {self.languagetools.get_language_name(self.from_language)}', self)
                return
        elif self.transformation_type == constants.TransformationType.Transliteration:
            if len(self.transliteration_options) == 0:
                self.languagetools.anki_utils.critical_message(f'No service found for transliteration from language {self.languagetools.get_language_name(self.from_language)}', self)
                return
        self.languagetools.anki_utils.run_in_background(self.loadTranslationsTask, self.loadTranslationDone)

    def loadTranslationsTask(self):
        self.load_errors = []

        try:
            self.languagetools.anki_utils.run_on_main(lambda: self.load_translations_button.setDisabled(True))
            self.languagetools.anki_utils.run_on_main(lambda: self.load_translations_button.setStyleSheet(None))
            self.languagetools.anki_utils.run_on_main(lambda: self.applyButton.setDisabled(True))
            self.languagetools.anki_utils.run_on_main(lambda: self.applyButton.setStyleSheet(None))
            self.languagetools.anki_utils.run_on_main(lambda: self.load_translations_button.setText('Loading...'))

            self.languagetools.anki_utils.run_on_main(lambda: self.progress_bar.setValue(0))
            self.languagetools.anki_utils.run_on_main(lambda: self.progress_bar.setMaximum(len(self.from_field_data)))

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

        except Exception as e:
            self.load_errors.append(e)
            return


        i = 0
        for field_data in self.from_field_data:
            try:
                if self.transformation_type == constants.TransformationType.Translation:
                    translation_result = self.languagetools.get_translation(field_data, self.translation_option)
                elif self.transformation_type == constants.TransformationType.Transliteration:
                    translation_result = self.languagetools.get_transliteration(field_data, self.transliteration_option)
                self.languagetools.anki_utils.run_on_main(get_set_to_field_lambda(i, translation_result))
            except errors.LanguageToolsError as e:
                self.load_errors.append(e)
            except Exception as e:
                logging.exception(e)
                self.load_errors.append(e)
            i += 1
            self.languagetools.anki_utils.run_on_main(lambda: self.progress_bar.setValue(i))

        self.languagetools.anki_utils.run_on_main(lambda: self.applyButton.setDisabled(False))
        self.languagetools.anki_utils.run_on_main(lambda: self.applyButton.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet()))


        self.languagetools.anki_utils.run_on_main(lambda: self.load_translations_button.setDisabled(False))
        self.languagetools.anki_utils.run_on_main(lambda: self.load_translations_button.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet()))
        self.languagetools.anki_utils.run_on_main(lambda: self.load_translations_button.setText(self.load_button_text_map[self.transformation_type]))


    def loadTranslationDone(self, future_result):
        if len(self.load_errors) > 0:
            error_counts = {}
            for error_exception in self.load_errors:
                error = str(error_exception)
                current_count = error_counts.get(error, 0)
                error_counts[error] = current_count + 1
            error_message = '<p><b>Errors</b>: ' + ', '.join([f'{key} ({value} times)' for key, value in error_counts.items()]) + '</p>'
            complete_message = f'<p>Encountered errors while generating {self.transformation_type.name}. You can still click <b>Apply to Notes</b> to apply the values retrieved to your notes.</p>' + error_message
            self.languagetools.anki_utils.critical_message(complete_message, self)

    def accept(self):
        if self.to_fields_empty == False:
            proceed = self.languagetools.anki_utils.ask_user(f'Overwrite existing data in field {self.to_field} ?', self)
            if proceed == False:
                return
        # set field on notes
        action_str = self.transformation_type.name
        self.undo_id = self.languagetools.anki_utils.undo_start(action_str)
        for (note_id, i) in zip(self.note_id_list, range(len(self.note_id_list))):
            to_field_data = self.noteTableModel.to_field_data[i]
            if to_field_data != None:
                note = self.languagetools.anki_utils.get_note_by_id(note_id)
                note[self.to_field] = to_field_data
                self.languagetools.anki_utils.update_note(note)
        self.languagetools.anki_utils.undo_end(self.undo_id)
        self.close()
        # memorize this setting
        deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(self.deck_note_type, self.to_field)
        if self.transformation_type == constants.TransformationType.Translation:
            self.languagetools.store_batch_translation_setting(deck_note_type_field, self.from_field, self.translation_option)
        elif self.transformation_type == constants.TransformationType.Transliteration:
            self.languagetools.store_batch_transliteration_setting(deck_note_type_field, self.from_field, self.transliteration_option)


def prepare_batch_transformation_dialogue(languagetools, deck_note_type, note_id_list, transformation_type):
    deck_map: Dict[str, Deck] = languagetools.get_populated_decks()

    dialog = BatchConversionDialog(languagetools, deck_note_type, note_id_list, transformation_type)
    dialog.setupUi()
    return dialog

