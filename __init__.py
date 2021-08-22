import sys
import os
import traceback
if hasattr(sys, '_pytest_mode'):
    # called from within a test run
    pass
else:
    # setup sentry crash reporting
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    external_dir = os.path.join(addon_dir, 'external')
    sys.path.append(external_dir)
    import sentry_sdk
    sentry_sdk.init(
        "https://dbee54f0eff84f0db037e995ae46df11@o968582.ingest.sentry.io/5920286",
        traces_sample_rate=1.0
    )

    def excepthook(etype, val, tb) -> None:  # type: ignore
        # report exception
        sentry_sdk.capture_exception(val)
        # print exception to allow anki's logger to handle it
        sys.stderr.write(
            "Caught exception:\n%s\n"
            % ("".join(traceback.format_exception(etype, val, tb)))
        )
    sys.excepthook = excepthook

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
