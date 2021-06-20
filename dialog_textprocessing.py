import sys
import PyQt5

if hasattr(sys, '_pytest_mode'):
    import constants
    import gui_utils
    import errors
    from languagetools import LanguageTools
else:
    from . import constants
    from . import gui_utils
    from . import errors
    from .languagetools import LanguageTools

class TextReplacementsTableModel(PyQt5.QtCore.QAbstractTableModel):
    def __init__(self):
        PyQt5.QtCore.QAbstractTableModel.__init__(self, None)

        self.replacements = []

        self.pattern_col_index = 0
        self.replacement_col_index = 1

        self.header_text = [
            'Pattern',
            'Replacement'
        ]
        self.col_index_to_transformation_type_map = {}
        col_index = 3
        for transformation_type in constants.TransformationType:
            self.header_text.append(transformation_type.name)
            self.col_index_to_transformation_type_map[col_index] = transformation_type
            col_index += 1

    def flags(self, index):
        # all columns are editable
        return PyQt5.QtCore.Qt.ItemIsEditable | PyQt5.QtCore.Qt.ItemIsSelectable | PyQt5.QtCore.Qt.ItemIsEnabled

    def rowCount(self, parent):
        return len(self.replacements)

    def columnCount(self, parent):
        return len(self.header_text)

    def data(self, index, role):
        if not index.isValid():
            return PyQt5.QtCore.QVariant()
        elif role != PyQt5.QtCore.Qt.DisplayRole and role != PyQt5.QtCore.Qt.EditRole: # only support display and edit
           return PyQt5.QtCore.QVariant()
        if index.column() == 0:
            # from field
            return PyQt5.QtCore.QVariant(self.from_field_data[index.row()])
        else:
            # result field
            return PyQt5.QtCore.QVariant(self.to_field_data[index.row()])

    def setData(self, index, value, role):
        if index.isValid() and role == PyQt5.QtCore.Qt.EditRole:
            
            # set the value into a TextReplacement object
            column = index.col()
            row = index.row()
            replacement = self.replacements[row]
            if column == self.pattern_col_index:
                replacement.pattern = value
            elif column == self.replacement_col_index:
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


def prepare_text_processing_dialog(languagetools):
    text_processing_dialog = TextProcessingDialog(languagetools)
    text_processing_dialog.setupUi()
    return text_processing_dialog

def text_processing_dialog(languagetools):
    dialog = prepare_text_processing_dialog(languagetools)
    dialog.exec_()