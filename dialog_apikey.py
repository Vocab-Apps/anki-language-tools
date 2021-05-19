import sys
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

class ApiKeyDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self, languagetools: LanguageTools):
        super(PyQt5.QtWidgets.QDialog, self).__init__()
        self.languagetools = languagetools
        
    def setupUi(self):
        self.setWindowTitle(constants.ADDON_NAME)
        self.resize(350, 280)

        vlayout = PyQt5.QtWidgets.QVBoxLayout(self)

        vlayout.addWidget(gui_utils.get_header_label('Enter API Key'))

        description_label = PyQt5.QtWidgets.QLabel("""<b>Why is Language Tools a paid addon and not free ?</b> """
        """ this addon makes use of cloud services such as Google Cloud and Microsoft Azure to generate premium text to speech, translations and transliterations. """
        """These service cost money and hence this addon cannot be provided for free. """
        """You can sign up for a free trial at the link below""")
        description_label.setWordWrap(True)
        vlayout.addWidget(description_label)

        urlLink="<a href=\"https://languagetools.anki.study/language-tools-signup\">Don't have an API Key? Sign up here</a>"
        signup_label=PyQt5.QtWidgets.QLabel()
        signup_label.setText(urlLink)
        signup_label.setOpenExternalLinks(True)
        vlayout.addWidget(signup_label)

        self.api_text_input = PyQt5.QtWidgets.QLineEdit()
        self.api_text_input.setText(self.languagetools.get_config_api_key())
        vlayout.addWidget(self.api_text_input)

        self.status_label = PyQt5.QtWidgets.QLabel('Enter API Key')
        vlayout.addWidget(self.status_label)

        self.buttonBox = PyQt5.QtWidgets.QDialogButtonBox()
        self.applyButton = self.buttonBox.addButton("OK", PyQt5.QtWidgets.QDialogButtonBox.AcceptRole)
        self.applyButton.setObjectName('apply')
        self.applyButton.setEnabled(False)
        self.cancelButton = self.buttonBox.addButton("Cancel", PyQt5.QtWidgets.QDialogButtonBox.RejectRole)
        self.cancelButton.setObjectName('cancel')
        self.cancelButton.setStyleSheet(self.languagetools.anki_utils.get_red_stylesheet())
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        vlayout.addStretch()
        vlayout.addWidget(self.buttonBox)

        # wire events
        self.typing_timer = self.languagetools.anki_utils.wire_typing_timer(self.api_text_input, self.api_key_changed)

        # run api_key_changed logic once
        self.api_key_changed()

    def start_typing_timer(self):
        """Wait until there are no changes for 1 second before making changes."""
        self.typing_timer.start(1000)

    def api_key_changed(self):
        api_key_text = self.api_text_input.text()
        if len(api_key_text) == 0:
            self.status_label.setText('Enter API Key')
            return
        self.status_label.setText('Verifying API Key...')
        self.languagetools.anki_utils.run_in_background(self.verify_api_key_background, self.verify_api_key_done)

    def verify_api_key_background(self):
        api_key_text = self.api_text_input.text()
        return self.languagetools.verify_api_key(api_key_text)

    def verify_api_key_done(self, future_result):
        is_valid, message = future_result.result()
        if is_valid:
            self.status_label.setText(message)
            self.applyButton.setEnabled(True)
            self.applyButton.setStyleSheet(self.languagetools.anki_utils.get_green_stylesheet())
        else:
            self.status_label.setText(message)
            self.applyButton.setEnabled(False)
            self.applyButton.setStyleSheet(None)

    def accept(self):
        # store api key into config
        api_key_text = self.api_text_input.text()
        self.languagetools.set_config_api_key(api_key_text)
        self.close()

def prepare_api_key_dialog(languagetools):
    dialog = ApiKeyDialog(languagetools)
    dialog.setupUi()
    return dialog