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


class ChooseTranslationDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self, languagetools: LanguageTools, all_translations):
        super(PyQt5.QtWidgets.QDialog, self).__init__()
        self.languagetools = languagetools
        self.all_translations = all_translations

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(500, 350)

        vlayout = PyQt5.QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(gui_utils.get_header_label('Choose Translation'))

        # add grid with translations
        translation_gridlayout = PyQt5.QtWidgets.QGridLayout()

        i = 0
        for key, value in self.all_translations.items():
            service_radio_button = PyQt5.QtWidgets.QRadioButton()
            service_radio_button.service = key
            service_radio_button.toggled.connect(self.on_translation_selected)
            service_label = PyQt5.QtWidgets.QLabel()
            service_label.setText(f'<b>{key}</b>')
            translation_label = PyQt5.QtWidgets.QLabel()
            translation_label.setText(f'{value}')
            translation_gridlayout.addWidget(service_radio_button, i, 0, 1, 1)
            translation_gridlayout.addWidget(service_label, i, 1, 1, 1)
            translation_gridlayout.addWidget(translation_label, i, 2, 1, 1)
            i += 1
        translation_gridlayout.setColumnStretch(0, 5)
        translation_gridlayout.setColumnStretch(1, 15)
        translation_gridlayout.setColumnStretch(2, 80)
        vlayout.addLayout(translation_gridlayout)

        vlayout.addStretch()

        # buttom buttons
        buttonBox = PyQt5.QtWidgets.QDialogButtonBox()
        self.applyButton = buttonBox.addButton("OK", PyQt5.QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setObjectName('apply')
        self.applyButton.setEnabled(False)
        self.cancelButton = buttonBox.addButton("Cancel", PyQt5.QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setObjectName('cancel')
        self.cancelButton.setStyleSheet(self.languagetools.anki_utils.get_red_stylesheet())
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        vlayout.addWidget(buttonBox)
    
    def on_translation_selected(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            selected_service = radio_button.service
            logging.debug(f'selected service: {selected_service}')



def prepare_dialog(languagetools, all_translations):
    dialog = ChooseTranslationDialog(languagetools, all_translations)
    dialog.setupUi()
    return dialog