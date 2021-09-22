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

        self.breakdown_result = PyQt5.QtWidgets.QLabel()

        self.load_button = PyQt5.QtWidgets.QPushButton()
        self.load_button.setText('Load Breakdown')

        vlayout.addWidget(self.target_language_dropdown)
        vlayout.addWidget(self.tokenization_dropdown)
        vlayout.addWidget(self.translation_checkbox)
        vlayout.addWidget(self.translation_dropdown)
        vlayout.addWidget(self.transliteration_checkbox)
        vlayout.addWidget(self.transliteration_dropdown)
        vlayout.addWidget(self.breakdown_result)
        vlayout.addWidget(self.load_button)

        self.populate_target_languages()
        self.populate_controls()

        self.load_button.pressed.connect(self.load_breakdown)

    def load_breakdown(self):
        self.languagetools.anki_utils.run_in_background(self.query_breakdown, self.query_breakdown_done)

    def query_breakdown(self):
        # tokenization option
        tokenization_option = self.tokenization_options[self.tokenization_dropdown.currentIndex()]
        # transliteration option
        transliteration_option = self.transliteration_options[self.transliteration_dropdown.currentIndex()]
        # translation option
        translation_option = self.translation_options[self.translation_dropdown.currentIndex()]

        return self.languagetools.get_breakdown_async(self.text,
            tokenization_option,
            translation_option,
            transliteration_option)

    def query_breakdown_done(self, future_result):
        breakdown_result = self.languagetools.interpret_breakdown_response_async(future_result.result())
        lines = [self.languagetools.format_breakdown_entry(x) for x in breakdown_result]
        result_html = f"""
            {'<br/>'.join(lines)}
        """
        self.breakdown_result.setText(result_html)
        logging.info(breakdown_result)

    def populate_target_languages(self):
        self.wanted_language_arrays = self.languagetools.get_wanted_language_arrays()
        self.target_language_dropdown.addItems(self.wanted_language_arrays['language_name_list'])

        self.target_language_dropdown.currentIndexChanged.connect(self.target_language_index_changed)
        # run once
        self.target_language_index_changed(0)

    def target_language_index_changed(self, current_index):
        # populate translation options
        target_language = self.wanted_language_arrays['language_code_list'][current_index]
        self.translation_options = self.languagetools.get_translation_options(self.from_language, target_language)
        self.translation_dropdown.clear()
        self.translation_dropdown.addItems([x['service'] for x in self.translation_options])


    def populate_controls(self):
        # target language
        # ===============

        # tokenization
        # ============
        self.tokenization_options = self.languagetools.get_tokenization_options(self.from_language)
        tokenization_option_names = [x['tokenization_name'] for x in self.tokenization_options]
        self.tokenization_dropdown.addItems(tokenization_option_names)

        # translation
        # ===========
        # dropdown populated separately
        self.translation_checkbox.setChecked(True)

        # transliteration
        # ===============
        self.transliteration_checkbox.setChecked(True)
        self.transliteration_options = self.languagetools.get_transliteration_options(self.from_language)
        self.transliteration_dropdown.addItems([x['transliteration_name'] for x in self.transliteration_options])









def prepare_dialog(languagetools, text, from_language):
    dialog = BreakdownDialog(languagetools, text, from_language)
    dialog.setupUi()
    return dialog