
# pyqt
import aqt.qt

# anki imports
import aqt.qt
import aqt.editor
import aqt.gui_hooks
import aqt.sound
import anki.sound
import anki.hooks

# addon imports
from . import constants
from . import editor
from . import dialogs
from . import deck_utils
from . import dialog_voiceselection
from . import dialog_textprocessing


def init(languagetools):

    # add context menu handler

    def show_getting_started():
        url = aqt.qt.QUrl('https://languagetools.anki.study/tutorials/language-tools-getting-started?utm_campaign=langtools_menu&utm_source=languagetools&utm_medium=addon')
        aqt.qt.QDesktopServices.openUrl(url)

    def show_language_mapping():
        dialogs.language_mapping_dialogue(languagetools)

    def show_voice_selection():
        dialog_voiceselection.voice_selection_dialog(languagetools, aqt.mw)

    def show_text_processing():
        dialog_textprocessing.text_processing_dialog(languagetools)

    def show_yomichan_integration():
        dialogs.yomichan_dialog(languagetools)

    def show_api_key_dialog():
        dialogs.show_api_key_dialog(languagetools)

    # unused for now
    def show_change_language(deck_note_type_field: deck_utils.DeckNoteTypeField):
        current_language = languagetools.get_language(deck_note_type_field)

        if current_language == None:
            # perform detection
            current_language = languagetools.guess_language(deck_note_type_field)

        data = languagetools.get_all_language_arrays()
        language_list = data['language_name_list']
        language_code_list = data['language_code_list']

        # locate current language
        if current_language == None:
            current_row = 0
        else:
            current_row = language_code_list.index(current_language)
        chosen_index = aqt.utils.chooseList(f'{constants.MENU_PREFIX} Choose Language for {deck_note_type_field.field_name}', language_list, startrow=current_row)

        new_language = language_code_list[chosen_index]
        languagetools.store_language_detection_result(deck_note_type_field, new_language)


    # unused for now
    def show_translation(source_text, from_language, to_language):
        # print(f'translate {source_text} from {from_language} to {to_language}')
        result = languagetools.get_translation_all(source_text, from_language, to_language)

        translations = ''
        for key, value in result.items():
            entry = f'{key}: <b>{value}</b><br/>'
            translations += entry
        text = f"""Translation of <i>{source_text}</i> from {languagetools.get_language_name(from_language)} to {languagetools.get_language_name(to_language)}<br/>
            {translations}
        """
        aqt.utils.showInfo(text, title=f'{constants.MENU_PREFIX} Translation', textFormat="rich")

    # unused for now
    def show_transliteration(selected_text, transliteration_option):
        result = languagetools.get_transliteration(selected_text, transliteration_option)
        text = f"""Transliteration of <i>{selected_text}</i>: {result}"""
        aqt.utils.showInfo(text, title=f'{constants.MENU_PREFIX} Transliteration', textFormat="rich")


    # add menu items to anki deck picker / main screen
    # ================================================
    
    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Getting Started", aqt.mw)
    action.triggered.connect(show_getting_started)
    aqt.mw.form.menuTools.addAction(action)

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Language Mapping", aqt.mw)
    action.triggered.connect(show_language_mapping)
    aqt.mw.form.menuTools.addAction(action)

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Voice Selection", aqt.mw)
    action.triggered.connect(show_voice_selection)
    aqt.mw.form.menuTools.addAction(action)

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Text Processing", aqt.mw)
    action.triggered.connect(show_text_processing)
    aqt.mw.form.menuTools.addAction(action)

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Verify API Key && Account Info", aqt.mw)
    action.triggered.connect(show_api_key_dialog)
    aqt.mw.form.menuTools.addAction(action)    

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Yomichan Integration", aqt.mw)
    action.triggered.connect(show_yomichan_integration)
    aqt.mw.form.menuTools.addAction(action)        

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} About", aqt.mw)
    action.triggered.connect(languagetools.show_about)
    aqt.mw.form.menuTools.addAction(action)

    # right click menu
    # aqt.gui_hooks.editor_will_show_context_menu.append(on_context_menu)

    def collectionDidLoad(col: anki.collection.Collection):
        languagetools.setCollectionLoaded()

    def mainWindowInit():
        languagetools.setMainWindowInit()
    
    def deckBrowserDidRender(deck_browser: aqt.deckbrowser.DeckBrowser):
        languagetools.setDeckBrowserRendered()

    # run some stuff after anki has initialized
    aqt.gui_hooks.collection_did_load.append(collectionDidLoad)
    aqt.gui_hooks.main_window_did_init.append(mainWindowInit)
    aqt.gui_hooks.deck_browser_did_render.append(deckBrowserDidRender)

    def browerMenusInit(browser: aqt.browser.Browser):
        menu = aqt.qt.QMenu(constants.ADDON_NAME, browser.form.menubar)
        browser.form.menubar.addMenu(menu)

        action = aqt.qt.QAction(f'Add Translation To Selected Notes...', browser)
        action.triggered.connect(lambda: dialogs.add_translation_dialog(languagetools, browser, browser.selectedNotes()))
        menu.addAction(action)

        action = aqt.qt.QAction(f'Add Transliteration To Selected Notes...', browser)
        action.triggered.connect(lambda: dialogs.add_transliteration_dialog(languagetools, browser, browser.selectedNotes()))
        menu.addAction(action)

        action = aqt.qt.QAction(f'Add Audio To Selected Notes...', browser)
        action.triggered.connect(lambda: dialogs.add_audio_dialog(languagetools, browser, browser.selectedNotes()))
        menu.addAction(action)        

        action = aqt.qt.QAction(f'Run Rules for Selected Notes...', browser)
        action.triggered.connect(lambda: dialogs.run_rules_dialog(languagetools, browser, browser.selectedNotes()))
        menu.addAction(action)                

        action = aqt.qt.QAction(f'Show Rules for Selected Notes...', browser)
        action.triggered.connect(lambda: dialogs.show_settings_dialog(languagetools, browser, browser.selectedNotes()))
        menu.addAction(action)                

    # browser menus
    aqt.gui_hooks.browser_menus_did_init.append(browerMenusInit)