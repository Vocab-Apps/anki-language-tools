
# anki imports
import aqt.qt
import aqt.editor
import aqt.gui_hooks
import anki.hooks

# addon imports
from . import constants
from . import editor
from . import dialogs
from .languagetools import DeckNoteTypeField, build_deck_note_type_field


def init(languagetools):

    # add context menu handler

    def show_language_mapping():
        dialogs.language_mapping_dialogue(languagetools)

    def show_change_language(deck_note_type_field: DeckNoteTypeField):
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
        languagetools.store_language_detection_result(deck_note_type_field, new_language, tooltip=True)


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

    def show_transliteration(selected_text, service, transliteration_key):
        result = languagetools.get_transliteration(selected_text, service, transliteration_key)
        text = f"""Transliteration of <i>{selected_text}</i>: {result}"""
        aqt.utils.showInfo(text, title=f'{constants.MENU_PREFIX} Transliteration', textFormat="rich")

    def add_inline_translation(note_editor: aqt.editor.Editor, source_language, target_language, deck_note_type_field: DeckNoteTypeField):
        # choose translation service
        translation_options = languagetools.get_translation_options(source_language, target_language)

        # ask the user which one they want
        services = [x['service'] for x in translation_options]
        choice = aqt.utils.chooseList(f'{constants.MENU_PREFIX} Choose Translation Service', services)
        chosen_option = translation_options[choice]

        # determine the ranking of this field in the note type
        languagetools.add_inline_translation(deck_note_type_field, chosen_option, target_language)
        editor.apply_inline_translation_changes(languagetools, note_editor, deck_note_type_field, chosen_option)

    def disable_inline_translation(note_editor: aqt.editor.Editor, deck_note_type_field: DeckNoteTypeField):
        languagetools.remove_inline_translations(deck_note_type_field)
        editor.remove_inline_translation_changes(languagetools, note_editor, deck_note_type_field)

    def on_context_menu(web_view: aqt.editor.EditorWebView, menu: aqt.qt.QMenu):
        # gather some information about the context from the editor
        # =========================================================

        editor: aqt.editor.Editor = web_view.editor

        selected_text = web_view.selectedText()
        current_field_num = editor.currentField
        if current_field_num == None:
            # we don't have a field selected, don't do anything
            return
        note = web_view.editor.note
        if note == None:
            # can't do anything without a note
            return
        model_id = note.mid
        model = aqt.mw.col.models.get(model_id)
        field_name = model['flds'][current_field_num]['name']
        card = web_view.editor.card
        if card == None:
            # we can't get the deck without a a card
            return
        deck_id = card.did

        deck_note_type_field = build_deck_note_type_field(deck_id, model_id, field_name)
        language = languagetools.get_language(deck_note_type_field)

        # check whether a language is set
        # ===============================

        if language != None:
            # all pre-requisites for translation/transliteration are met, proceed
            # ===================================================================

            # these options require text to be selected

            if len(selected_text) > 0:
                source_text_max_length = 25
                source_text = selected_text
                if len(selected_text) > source_text_max_length:
                    source_text = selected_text[0:source_text_max_length]

                # add translation options
                # =======================
                menu_text = f'{constants.MENU_PREFIX} translate from {languagetools.get_language_name(language)}'
                submenu = aqt.qt.QMenu(menu_text, menu)
                wanted_languages = languagetools.get_wanted_languages()
                for wanted_language in wanted_languages:
                    if wanted_language != language:
                        menu_text = f'To {languagetools.get_language_name(wanted_language)}'
                        def get_translate_lambda(selected_text, language, wanted_language):
                            def translate():
                                show_translation(selected_text, language, wanted_language)
                            return translate
                        submenu.addAction(menu_text, get_translate_lambda(selected_text, language, wanted_language))
                menu.addMenu(submenu)

                # add transliteration options
                # ===========================

                transliteration_options = languagetools.get_transliteration_options(language)
                if len(transliteration_options) > 0:
                    menu_text = f'{constants.MENU_PREFIX} transliterate {languagetools.get_language_name(language)}'
                    submenu = aqt.qt.QMenu(menu_text, menu)
                    for transliteration_option in transliteration_options:
                        menu_text = transliteration_option['transliteration_name']
                        def get_transliterate_lambda(selected_text, service, transliteration_key):
                            def transliterate():
                                show_transliteration(selected_text, service, transliteration_key)
                            return transliterate
                        submenu.addAction(menu_text, get_transliterate_lambda(selected_text, transliteration_option['service'], transliteration_option['transliteration_key']))
                    menu.addMenu(submenu)

            # these options don't require text to be selected

            # add inline translation options
            # ==============================
            menu_text = f'{constants.MENU_PREFIX} Add Inline Translation'
            submenu = aqt.qt.QMenu(menu_text, menu)
            wanted_languages = languagetools.get_wanted_languages()
            for wanted_language in wanted_languages:
                if wanted_language != language:
                    menu_text = f'To {languagetools.get_language_name(wanted_language)}'
                    def get_add_inline_translation_lambda(editor, source_language, target_language, deck_note_type_field):
                        def add_inline_translation_fn():
                            add_inline_translation(editor, source_language, target_language, deck_note_type_field)
                        return add_inline_translation_fn
                    submenu.addAction(menu_text, get_add_inline_translation_lambda(editor, language, wanted_language, deck_note_type_field))
            # do we need to add a disable action ?
            if len(languagetools.get_inline_translations(deck_note_type_field.deck_note_type)) > 0:
                submenu.addSeparator()
                menu_text = 'Disable'
                def get_disable_inline_translation_lambda(editor, deck_note_type_field):
                    def disable_inline_translation_fn():
                        disable_inline_translation(editor, deck_note_type_field)
                    return disable_inline_translation_fn
                submenu.addAction(menu_text, get_disable_inline_translation_lambda(editor, deck_note_type_field))

            
            menu.addMenu(submenu)

        # was language detection run ?
        # ============================

        if languagetools.language_detection_done():

            # show information about the field 
            # ================================

            if language == None:
                menu_text = f'{constants.MENU_PREFIX} No language set'
            else:
                menu_text = f'{constants.MENU_PREFIX} language: {languagetools.get_language_name(language)}'
            submenu = aqt.qt.QMenu(menu_text, menu)

            # add change language option
            menu_text = f'Change Language'
            def get_change_language_lambda(deck_note_type_field):
                def change_language():
                    show_change_language(deck_note_type_field)
                return change_language
            submenu.addAction(menu_text, get_change_language_lambda(deck_note_type_field))

            menu.addMenu(submenu)

        else:
            # give user an option to run language detection
            menu_text = f'{constants.MENU_PREFIX} Run Language Detection'
            menu.addAction(menu_text, languagetools.run_language_detection)

    # add menu items to anki deck picker / main screen
    # ================================================

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Language Mapping", aqt.mw)
    action.triggered.connect(show_language_mapping)
    aqt.mw.form.menuTools.addAction(action)

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Verify API Key", aqt.mw)
    action.triggered.connect(languagetools.run_api_key_verification)
    aqt.mw.form.menuTools.addAction(action)    

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} About", aqt.mw)
    action.triggered.connect(languagetools.show_about)
    aqt.mw.form.menuTools.addAction(action)

    # right click menu
    aqt.gui_hooks.editor_will_show_context_menu.append(on_context_menu)

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