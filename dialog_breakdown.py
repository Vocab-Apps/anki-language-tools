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


def prepare_dialog(languagetools, text, from_language):
    dialog = BreakdownDialog(languagetools, text, from_language)
    dialog.setupUi()
    return dialog