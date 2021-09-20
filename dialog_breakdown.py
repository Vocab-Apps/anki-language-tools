import sys
import logging
import PyQt5

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


class BreakdownDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self, languagetools: LanguageTools, text, from_language):
        super(PyQt5.QtWidgets.QDialog, self).__init__()
        self.languagetools = languagetools

        self.text = text
        self.from_language = from_language

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(500, 350)

        vlayout = PyQt5.QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(gui_utils.get_header_label('Breakdown'))
        vlayout.addWidget(gui_utils.get_medium_label(f'{self.text} ({self.languagetools.get_language_name(self.from_language)})'))

        # show tokenization options
        # show translation options, with checkbox
        # show transliteration options, with checkbox

        self.target_language_dropdown = PyQt5.QtWidgets.QComboBox()
        
        self.tokenization_dropdown = PyQt5.QtWidgets.QComboBox()
        self.translation_checkbox = PyQt5.QtWidgets.QCheckBox()
        self.translation_dropdown = PyQt5.QtWidgets.QComboBox()
        self.transliteration_checkbox = PyQt5.QtWidgets.QCheckBox()
        self.transliteration_dropdown = PyQt5.QtWidgets.QComboBox()

        vlayout.addWidget(self.target_language_dropdown)
        vlayout.addWidget(self.tokenization_dropdown)
        vlayout.addWidget(self.translation_checkbox)
        vlayout.addWidget(self.translation_dropdown)
        vlayout.addWidget(self.transliteration_checkbox)
        vlayout.addWidget(self.transliteration_dropdown)

        self.populate_controls()

    def populate_controls(self):
        # target language
        # ===============
        self.wanted_language_arrays = self.languagetools.get_wanted_language_arrays()
        self.target_language_dropdown.addItems(self.wanted_language_arrays['language_name_list'])

        # tokenization
        # ============
        self.tokenization_options = self.languagetools.get_tokenization_options(self.from_language)
        tokenization_option_names = [x['tokenization_name'] for x in self.tokenization_options]
        self.tokenization_dropdown.addItems(tokenization_option_names)

        self.translation_checkbox.setChecked(True)








def prepare_dialog(languagetools, text, from_language):
    dialog = BreakdownDialog(languagetools, text, from_language)
    dialog.setupUi()
    return dialog