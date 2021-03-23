import sys
if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:
    from . import languagetools
    from . import gui
    from . import editor

    languagetools = languagetools.LanguageTools()
    gui.init(languagetools)
    editor.init(languagetools)
