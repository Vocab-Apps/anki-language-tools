import sys
import aqt.qt
import logging
import html

if hasattr(sys, '_pytest_mode'):
    import constants
    import gui_utils
    import errors
    import text_utils
    from languagetools import LanguageTools
else:
    from . import constants
    from . import gui_utils
    from . import errors
    from . import text_utils
    from .languagetools import LanguageTools

COL_INDEX_TYPE = 0
COL_INDEX_PATTERN = 1
COL_INDEX_REPLACEMENT = 2

BLANK_TEXT = '<i>Enter sample text to verify text processing settings.</i>'

class TextReplacementsTableModel(aqt.qt.QAbstractTableModel):
    def __init__(self, recompute_sample_callback, replacements):
        aqt.qt.QAbstractTableModel.__init__(self, None)

        self.replacements = replacements
        self.recompute_sample_callback = recompute_sample_callback

        self.header_text = [
            'Type',
            'Pattern',
            'Replacement'
        ]
        self.col_index_to_transformation_type_map = {}
        col_index = COL_INDEX_REPLACEMENT + 1
        for transformation_type in constants.TransformationType:
            self.header_text.append(transformation_type.name)
            self.col_index_to_transformation_type_map[col_index] = transformation_type
            col_index += 1

    def flags(self, index):
        # all columns are editable
        col = index.column()
        if col == COL_INDEX_TYPE:
            # not editable
            return aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled
        if col == COL_INDEX_PATTERN or col == COL_INDEX_REPLACEMENT:
            return aqt.qt.Qt.ItemIsEditable | aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled
        # should be a transformation type
        return aqt.qt.Qt.ItemIsUserCheckable | aqt.qt.Qt.ItemFlag.ItemIsSelectable | aqt.qt.Qt.ItemFlag.ItemIsEnabled

    def rowCount(self, parent):
        return len(self.replacements)

    def columnCount(self, parent):
        return self.num_columns()

    def num_columns(self):
        return len(self.header_text)

    def add_replacement(self, replace_type):
        self.replacements.append(text_utils.TextReplacement({'replace_type': replace_type.name}))
        self.layoutChanged.emit()

    def delete_rows(self, row_index):
        row = row_index.row()
        del self.replacements[row]
        self.recompute_sample_callback()
        self.layoutChanged.emit()

    def data(self, index, role):
        if not index.isValid():
            return aqt.qt.QVariant()

        column = index.column()
        row = index.row()

        # check whether we've got data for this row
        if row >= len(self.replacements):
            return aqt.qt.QVariant()

        replacement = self.replacements[row]

        if role == aqt.qt.Qt.ItemDataRole.DisplayRole or role == aqt.qt.Qt.EditRole:

            if column == COL_INDEX_TYPE:
                return aqt.qt.QVariant(replacement.replace_type.name.title())
            if column == COL_INDEX_PATTERN:
                return self.data_display(replacement.pattern, role)
            if column == COL_INDEX_REPLACEMENT:
                return self.data_display(replacement.replace, role)

        if role == aqt.qt.Qt.CheckStateRole:
            if column == COL_INDEX_TYPE or column == COL_INDEX_PATTERN or column == COL_INDEX_REPLACEMENT:
                # don't support these columns in this role
                return aqt.qt.QVariant()

            # should be a transformation type
            transformation_type = self.col_index_to_transformation_type_map[column]
            is_enabled = replacement.transformation_type_map[transformation_type]
            if is_enabled:
                return aqt.qt.Qt.Checked
            return aqt.qt.Qt.Unchecked

        return aqt.qt.QVariant()

    def data_display(self, value, role):
        if role == aqt.qt.Qt.ItemDataRole.DisplayRole:
            text = '""'
            if value != None:
                text = '"' + value + '"'
            return aqt.qt.QVariant(text)
        elif role == aqt.qt.Qt.EditRole:
            return aqt.qt.QVariant(value)



    def setData(self, index, value, role):
        if not index.isValid():
            return False

        column = index.column()
        row = index.row()

        replacement = self.replacements[row]

        if role == aqt.qt.Qt.EditRole:
            
            # set the value into a TextReplacement object
            if column == COL_INDEX_TYPE:
                # editing no supported
                return False
            elif column == COL_INDEX_PATTERN:
                replacement.pattern = value
            elif column == COL_INDEX_REPLACEMENT:
                replacement.replace = value
            else:
                transformation_type = self.col_index_to_transformation_type_map[column]
                replacement.transformation_type_map[transformation_type] = value

            # emit change signal
            start_index = self.createIndex(row, column)
            end_index = self.createIndex(row, column)
            self.dataChanged.emit(start_index, end_index)
            self.recompute_sample_callback()
            return True
        elif role == aqt.qt.Qt.CheckStateRole:
            transformation_type = self.col_index_to_transformation_type_map[column]
            is_checked = value == aqt.qt.Qt.Checked
            replacement.transformation_type_map[transformation_type] = is_checked
            logging.info(f'setting {transformation_type} to {is_checked}')
            start_index = self.createIndex(row, column)
            end_index = self.createIndex(row, column)
            self.dataChanged.emit(start_index, end_index)       
            self.recompute_sample_callback()     
            return True
        else:
            return False

    def headerData(self, col, orientation, role):
        if orientation == aqt.qt.Qt.Orientation.Horizontal and role == aqt.qt.Qt.ItemDataRole.DisplayRole:
            return aqt.qt.QVariant(self.header_text[col])
        return aqt.qt.QVariant()

class TextProcessingDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools
        self.textReplacementTableModel = TextReplacementsTableModel(self.update_transformed_text, languagetools.text_utils.replacements)

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = aqt.qt.QVBoxLayout(self)

        vlayout.addWidget(gui_utils.get_header_label('Text Processing Settings'))

        # setup test input box
        # ====================

        vlayout.addWidget(gui_utils.get_medium_label('Preview Settings'))

        # first line
        hlayout = aqt.qt.QHBoxLayout()
        hlayout.addWidget(aqt.qt.QLabel('Transformation Type:'))
        self.sample_transformation_type_combo_box = aqt.qt.QComboBox()
        transformation_type_names = [x.name for x in constants.TransformationType]
        self.sample_transformation_type_combo_box.addItems(transformation_type_names)
        hlayout.addWidget(self.sample_transformation_type_combo_box)

        label = aqt.qt.QLabel('Enter sample text:')
        hlayout.addWidget(label)
        self.sample_text_input = aqt.qt.QLineEdit()
        hlayout.addWidget(self.sample_text_input)
        hlayout.addStretch()
        vlayout.addLayout(hlayout)

        # second line
        hlayout = aqt.qt.QHBoxLayout()
        hlayout.addWidget(aqt.qt.QLabel('Transformed Text:'))
        self.sample_text_transformed_label = aqt.qt.QLabel(BLANK_TEXT)
        hlayout.addWidget(self.sample_text_transformed_label)
        hlayout.addStretch()
        vlayout.addLayout(hlayout)

        vlayout.addWidget(gui_utils.get_medium_label('Text Replacement'))

        # setup preview table
        # ===================

        self.table_view = aqt.qt.QTableView()
        self.table_view.setModel(self.textReplacementTableModel)
        self.table_view.setSelectionMode(aqt.qt.QTableView.SelectionMode.SingleSelection)
        # self.table_view.setSelectionBehavior(aqt.qt.QTableView.SelectionBehavior.SelectRows)
        header = self.table_view.horizontalHeader()       
        header.setSectionResizeMode(0, aqt.qt.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, aqt.qt.QHeaderView.ResizeMode.Stretch)
        vlayout.addWidget(self.table_view)
        
        # setup buttons below table
        hlayout = aqt.qt.QHBoxLayout()
        self.add_replace_simple_button = aqt.qt.QPushButton('Add Simple Text Replacement Rule')
        hlayout.addWidget(self.add_replace_simple_button)
        self.add_replace_regex_button = aqt.qt.QPushButton('Add Regex Text Replacement Rule')
        hlayout.addWidget(self.add_replace_regex_button)
        self.remove_replace_button = aqt.qt.QPushButton('Remove Selected Rule')
        hlayout.addWidget(self.remove_replace_button)
        vlayout.addLayout(hlayout)

        # setup bottom buttons
        # ====================

        buttonBox = aqt.qt.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("OK", aqt.qt.QDialogButtonBox.ButtonRole.AcceptRole)
        self.applyButton.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet())
        self.cancelButton = buttonBox.addButton("Cancel", aqt.qt.QDialogButtonBox.ButtonRole.RejectRole)
        self.cancelButton.setStyleSheet(self.languagetools.anki_utils.get_red_stylesheet())
        
        vlayout.addWidget(buttonBox)

        # wire events
        # ===========
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.add_replace_simple_button.pressed.connect(lambda: self.textReplacementTableModel.add_replacement(constants.ReplaceType.simple))
        self.add_replace_regex_button.pressed.connect(lambda: self.textReplacementTableModel.add_replacement(constants.ReplaceType.regex))
        self.remove_replace_button.pressed.connect(self.delete_text_replacement)
        self.typing_timer = self.languagetools.anki_utils.wire_typing_timer(self.sample_text_input, self.sample_text_changed)
        self.sample_transformation_type_combo_box.currentIndexChanged.connect(self.sample_transformation_type_changed)

    def sample_transformation_type_changed(self):
        self.update_transformed_text()

    def sample_text_changed(self):
        self.update_transformed_text()

    def get_text_processing_settings(self):
        replacement_list = self.textReplacementTableModel.replacements
        replacement_dict_list = [x.to_dict() for x in replacement_list]
        return {'replacements': replacement_dict_list}

    def update_transformed_text(self):
        # get the sample text
        sample_text = self.sample_text_input.text()
        transformation_type = constants.TransformationType[self.sample_transformation_type_combo_box.currentText()]
        if len(sample_text) == 0:
            label_text = BLANK_TEXT
        else:
            # get the text replacements
            utils = text_utils.TextUtils(self.languagetools.anki_utils, self.get_text_processing_settings())
            sample_text_processed = utils.process(sample_text, transformation_type)
            label_text = f'<b>{html.escape(sample_text_processed)}</b>'

        # self.sample_text_transformed_label.setText(label_text)
        self.languagetools.anki_utils.run_on_main(lambda: self.sample_text_transformed_label.setText(label_text))


    def delete_text_replacement(self):
        rows_indices = self.table_view.selectionModel().selectedIndexes()
        if len(rows_indices) == 1:
            self.textReplacementTableModel.delete_rows(rows_indices[0])

    def accept(self):
        self.languagetools.store_text_processing_settings(self.get_text_processing_settings())
        self.close()

def prepare_text_processing_dialog(languagetools):
    text_processing_dialog = TextProcessingDialog(languagetools)
    text_processing_dialog.setupUi()
    return text_processing_dialog

def text_processing_dialog(languagetools):
    dialog = prepare_text_processing_dialog(languagetools)
    dialog.exec_()