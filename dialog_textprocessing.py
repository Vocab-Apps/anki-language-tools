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
    def __init__(self):
        PyQt5.QtCore.QAbstractTableModel.__init__(self, None)

        self.replacements = []

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
        return PyQt5.QtCore.Qt.ItemIsEditable | PyQt5.QtCore.Qt.ItemIsUserCheckable | PyQt5.QtCore.Qt.ItemIsSelectable | PyQt5.QtCore.Qt.ItemIsEnabled

    def rowCount(self, parent):
        return len(self.replacements)

    def columnCount(self, parent):
        return self.num_columns()

    def num_columns(self):
        return len(self.header_text)

    def add_replacement(self):
        self.replacements.append(text_utils.TextReplacement({}))
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
        if index.isValid() and role == PyQt5.QtCore.Qt.EditRole:
            
            # set the value into a TextReplacement object
            column = index.column()
            row = index.row()
            replacement = self.replacements[row]
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
        self.textReplacementTableModel = TextReplacementsTableModel()

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(700, 500)

        vlayout = PyQt5.QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(gui_utils.get_header_label('Text Processing Settings'))
        vlayout.addWidget(gui_utils.get_medium_label('Text Replacement'))

        # setup preview table
        # ===================

        self.table_view = PyQt5.QtWidgets.QTableView()
        self.table_view.setModel(self.textReplacementTableModel)
        header = self.table_view.horizontalHeader()       
        header.setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, PyQt5.QtWidgets.QHeaderView.Stretch)
        vlayout.addWidget(self.table_view)
        
        # setup buttons below table
        hlayout = PyQt5.QtWidgets.QHBoxLayout()
        self.add_replace_button = PyQt5.QtWidgets.QPushButton('Add Text Replacement')
        hlayout.addWidget(self.add_replace_button)
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


def prepare_text_processing_dialog(languagetools):
    text_processing_dialog = TextProcessingDialog(languagetools)
    text_processing_dialog.setupUi()
    return text_processing_dialog

def text_processing_dialog(languagetools):
    dialog = prepare_text_processing_dialog(languagetools)
    dialog.exec_()