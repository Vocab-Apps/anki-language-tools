import sys
if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:
    from . import languagetools
    from . import gui
    from . import editor
    from . import anki_interface

    interface = anki_interface.AnkiInterface()
    languagetools = languagetools.LanguageTools(interface)
    gui.init(languagetools)
    editor.init(languagetools)
