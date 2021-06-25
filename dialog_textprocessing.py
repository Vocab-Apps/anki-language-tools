import sys
import PyQt5
import logging

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

COL_INDEX_PATTERN = 0
COL_INDEX_REPLACEMENT = 1

class TextReplacementsTableModel(PyQt5.QtCore.QAbstractTableModel):
    def __init__(self, recompute_sample_callback):
        PyQt5.QtCore.QAbstractTableModel.__init__(self, None)

        self.replacements = []
        self.recompute_sample_callback = recompute_sample_callback

        self.header_text = [
            'Pattern',
            'Replacement'
        ]
        self.col_index_to_transformation_type_map = {}
        col_index = 2
        for transformation_type in constants.TransformationType:
            self.header_text.append(transformation_type.name)
            self.col_index_to_transformation_type_map[col_index] = transformation_type
            col_index += 1

    def flags(self, index):
        # all columns are editable
        col = index.column()
        if col == COL_INDEX_PATTERN or col == COL_INDEX_REPLACEMENT:
            return PyQt5.QtCore.Qt.ItemIsEditable | PyQt5.QtCore.Qt.ItemIsSelectable | PyQt5.QtCore.Qt.ItemIsEnabled
        # should be a transformation type
        return PyQt5.QtCore.Qt.ItemIsUserCheckable | PyQt5.QtCore.Qt.ItemIsSelectable | PyQt5.QtCore.Qt.ItemIsEnabled

    def rowCount(self, parent):
        return len(self.replacements)

    def columnCount(self, parent):
        return self.num_columns()

    def num_columns(self):
        return len(self.header_text)

    def add_replacement(self):
        self.replacements.append(text_utils.TextReplacement({}))
        self.layoutChanged.emit()

    def delete_rows(self, row_index):
        row = row_index.row()
        del self.replacements[row]
        self.recompute_sample_callback()
        self.layoutChanged.emit()

    def data(self, index, role):
        if not index.isValid():
            return PyQt5.QtCore.QVariant()

        column = index.column()
        row = index.row()

        # check whether we've got data for this row
        if row >= len(self.replacements):
            return PyQt5.QtCore.QVariant()

        replacement = self.replacements[row]

        if role == PyQt5.QtCore.Qt.DisplayRole or role == PyQt5.QtCore.Qt.EditRole:

            if column == COL_INDEX_PATTERN:
                return self.data_display(replacement.pattern, role)
            if column == COL_INDEX_REPLACEMENT:
                return self.data_display(replacement.replace, role)

        if role == PyQt5.QtCore.Qt.CheckStateRole:
            if column == COL_INDEX_PATTERN or column == COL_INDEX_REPLACEMENT:
                # don't support these columns in this role
                return PyQt5.QtCore.QVariant()

            # should be a transformation type
            transformation_type = self.col_index_to_transformation_type_map[column]
            is_enabled = replacement.transformation_type_map[transformation_type]
            if is_enabled:
                return PyQt5.QtCore.Qt.Checked
            return PyQt5.QtCore.Qt.Unchecked

        return PyQt5.QtCore.QVariant()

    def data_display(self, value, role):
        if role == PyQt5.QtCore.Qt.DisplayRole:
            text = '""'
            if value != None:
                text = '"' + value + '"'
            return PyQt5.QtCore.QVariant(text)
        elif role == PyQt5.QtCore.Qt.EditRole:
            return PyQt5.QtCore.QVariant(value)



    def setData(self, index, value, role):
        if not index.isValid():
            return False

        column = index.column()
        row = index.row()

        replacement = self.replacements[row]

        if role == PyQt5.QtCore.Qt.EditRole:
            
            # set the value into a TextReplacement object
            if column == COL_INDEX_PATTERN:
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
        elif role == PyQt5.QtCore.Qt.CheckStateRole:
            transformation_type = self.col_index_to_transformation_type_map[column]
            is_checked = value == PyQt5.QtCore.Qt.Checked
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
        if orientation == PyQt5.QtCore.Qt.Horizontal and role == PyQt5.QtCore.Qt.DisplayRole:
            return PyQt5.QtCore.QVariant(self.header_text[col])
        return PyQt5.QtCore.QVariant()

class TextProcessingDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self, languagetools: LanguageTools):
        super(PyQt5.QtWidgets.QDialog, self).__init__()
        self.languagetools = languagetools
        self.textReplacementTableModel = TextReplacementsTableModel(self.update_transformed_text)

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = PyQt5.QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(gui_utils.get_header_label('Text Processing Settings'))
        vlayout.addWidget(gui_utils.get_medium_label('Text Replacement'))

        # setup test input box
        # ====================
        hlayout = PyQt5.QtWidgets.QHBoxLayout()
        label = PyQt5.QtWidgets.QLabel('Enter sample text:')
        hlayout.addWidget(label)
        self.sample_text_input = PyQt5.QtWidgets.QLineEdit()
        hlayout.addWidget(self.sample_text_input)
        
        self.sample_text_transformed_label = PyQt5.QtWidgets.QLabel('<i>Enter sample text to test transformation</i>')
        hlayout.addWidget(self.sample_text_transformed_label)
        
        hlayout.addStretch()

        vlayout.addLayout(hlayout)        

        # setup preview table
        # ===================

        self.table_view = PyQt5.QtWidgets.QTableView()
        self.table_view.setModel(self.textReplacementTableModel)
        self.table_view.setSelectionMode(PyQt5.QtWidgets.QTableView.SingleSelection)
        # self.table_view.setSelectionBehavior(PyQt5.QtWidgets.QTableView.SelectRows)
        header = self.table_view.horizontalHeader()       
        header.setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, PyQt5.QtWidgets.QHeaderView.Stretch)
        vlayout.addWidget(self.table_view)
        
        # setup buttons below table
        hlayout = PyQt5.QtWidgets.QHBoxLayout()
        self.add_replace_button = PyQt5.QtWidgets.QPushButton('Add Text Replacement Rule')
        hlayout.addWidget(self.add_replace_button)
        self.remove_replace_button = PyQt5.QtWidgets.QPushButton('Remove Selected Text Replacement Rule')
        hlayout.addWidget(self.remove_replace_button)
        vlayout.addLayout(hlayout)

        # setup bottom buttons
        # ====================

        buttonBox = PyQt5.QtWidgets.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("OK", PyQt5.QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet())
        self.cancelButton = buttonBox.addButton("Cancel", PyQt5.QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setStyleSheet(self.languagetools.anki_utils.get_red_stylesheet())
        
        vlayout.addWidget(buttonBox)

        # wire events
        # ===========
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.add_replace_button.pressed.connect(self.textReplacementTableModel.add_replacement)
        self.remove_replace_button.pressed.connect(self.delete_text_replacement)
        self.typing_timer = self.languagetools.anki_utils.wire_typing_timer(self.sample_text_input, self.sample_text_changed)

    def sample_text_changed(self):
        self.update_transformed_text()

    def update_transformed_text(self):
        # get the sample text
        sample_text = self.sample_text_input.text()
        if len(sample_text) == 0:
            label_text = '<i>Enter sample text to test transformation</i>'
        else:
            # get the text replacements
            replacement_list = self.textReplacementTableModel.replacements
            replacement_dict_list = [x.to_dict() for x in replacement_list]
            utils = text_utils.TextUtils({'replacements': replacement_dict_list})
            sample_text_processed = utils.process(sample_text, constants.TransformationType.Audio)
            label_text = f'<i>result</i>: {sample_text_processed}'

        # self.sample_text_transformed_label.setText(label_text)
        self.languagetools.anki_utils.run_on_main(lambda: self.sample_text_transformed_label.setText(label_text))



    def delete_text_replacement(self):
        rows_indices = self.table_view.selectionModel().selectedIndexes()
        if len(rows_indices) == 1:
            self.textReplacementTableModel.delete_rows(rows_indices[0])

def prepare_text_processing_dialog(languagetools):
    text_processing_dialog = TextProcessingDialog(languagetools)
    text_processing_dialog.setupUi()
    return text_processing_dialog

def text_processing_dialog(languagetools):
    dialog = prepare_text_processing_dialog(languagetools)
    dialog.exec_()