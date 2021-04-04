import sys
if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:
    from . import languagetools
    from . import gui
    from . import editor
    from . import anki_utils
    from . import deck_utils
    from . import cloudlanguagetools

    ankiutils = anki_utils.AnkiUtils()
    deckutils = deck_utils.DeckUtils(ankiutils)
    cloud_language_tools = cloudlanguagetools.CloudLanguageTools()
    languagetools = languagetools.LanguageTools(ankiutils, deckutils, cloud_language_tools)
    gui.init(languagetools)
    editor.init(languagetools)
