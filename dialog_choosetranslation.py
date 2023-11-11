import sys
import logging
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


class ChooseTranslationDialog(aqt.qt.QDialog):
    def __init__(self, languagetools: LanguageTools, original_text, from_language, to_language, all_translations):
        super(aqt.qt.QDialog, self).__init__()
        self.languagetools = languagetools

        self.original_text = original_text
        self.from_language = from_language
        self.to_language = to_language

        self.all_translations = all_translations

    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(500, 350)

        vlayout = aqt.qt.QVBoxLayout(self)
        vlayout.addWidget(gui_utils.get_header_label('Choose Translation'))

        # add the source text / languages
        translation_info_gridlayout = aqt.qt.QGridLayout()
        vlayout.addLayout(translation_info_gridlayout)

        translation_info_gridlayout.addWidget(gui_utils.get_medium_label('Source Text'), 0, 0, 1, 1)
        
        self.original_text_label = aqt.qt.QLabel(self.original_text)
        translation_info_gridlayout.addWidget(self.original_text_label, 1, 0, 1, 1)
        
        self.from_language_label = aqt.qt.QLabel(self.languagetools.get_language_name(self.from_language))
        translation_info_gridlayout.addWidget(gui_utils.get_medium_label('From'), 0, 1, 1, 1)
        translation_info_gridlayout.addWidget(self.from_language_label, 1, 1, 1, 1)
        
        self.to_language_label = aqt.qt.QLabel(self.languagetools.get_language_name(self.to_language))
        translation_info_gridlayout.addWidget(gui_utils.get_medium_label('To'), 0, 2, 1, 1)
        translation_info_gridlayout.addWidget(self.to_language_label, 1, 2, 1, 1)

        translation_info_gridlayout.setColumnStretch(0, 60)
        translation_info_gridlayout.setColumnStretch(1, 20)
        translation_info_gridlayout.setColumnStretch(2, 20)

        vlayout.addLayout(translation_info_gridlayout)


        # add grid with translations
        vlayout.addWidget(gui_utils.get_medium_label('Translations Available'))
        translation_gridlayout = aqt.qt.QGridLayout()

        i = 0
        for key, value in self.all_translations.items():
            service_radio_button = aqt.qt.QRadioButton()
            service_radio_button.setObjectName(f'radio_button_{i}')
            service_radio_button.service = key
            service_radio_button.toggled.connect(self.on_translation_selected)
            service_label = aqt.qt.QLabel()
            service_label.setText(f'<b>{key}</b>')
            service_label.setObjectName(f'service_label_{i}')
            translation_label = aqt.qt.QLabel()
            translation_label.setText(f'{value}')
            translation_label.setObjectName(f'translation_label_{i}')
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
        buttonBox = aqt.qt.QDialogButtonBox()
        self.apply_button = buttonBox.addButton("OK", aqt.qt.QDialogButtonBox.ButtonRole.AcceptRole)
        self.apply_button.setObjectName('apply')
        self.apply_button.setEnabled(False)
        self.cancel_button = buttonBox.addButton("Cancel", aqt.qt.QDialogButtonBox.ButtonRole.RejectRole)
        self.cancel_button.setObjectName('cancel')
        self.cancel_button.setStyleSheet(self.languagetools.anki_utils.get_red_stylesheet())
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        vlayout.addWidget(buttonBox)
    
    def on_translation_selected(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            self.apply_button.setEnabled(True)
            self.apply_button.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet())
            selected_service = radio_button.service
            logging.debug(f'selected service: {selected_service}')
            self.selected_translation = self.all_translations[selected_service]



def prepare_dialog(languagetools, original_text, from_language, to_language, all_translations):
    dialog = ChooseTranslationDialog(languagetools, original_text, from_language, to_language, all_translations)
    dialog.setupUi()
    return dialog