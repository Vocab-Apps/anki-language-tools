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
        vlayout.addWidget(self.api_text_input)

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
        self.typing_timer = PyQt5.QtCore.QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.api_key_changed)
        self.api_text_input.textChanged.connect(self.start_typing_timer)

    def start_typing_timer(self):
        """Wait until there are no changes for 1 second before making changes."""
        self.typing_timer.start(1000)

    def api_key_changed(self):
        print('api_key_changed')



def prepare_api_key_dialog(languagetools):
    dialog = ApiKeyDialog(languagetools)
    dialog.setupUi()
    return dialog