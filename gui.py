
# anki imports
import aqt.gui_hooks
import anki.hooks

# addon imports
from . import constants
from .languagetools import DeckNoteTypeField, build_deck_note_type_field

def init(languagetools):

    # add context menu handler

    def show_change_language(deck_note_type_field: DeckNoteTypeField):
        current_language = languagetools.get_language(deck_note_type_field)

        if current_language == None:
            # perform detection
            current_language = languagetools.guess_language(deck_note_type_field)

        language_dict = languagetools.get_all_languages()
        language_list = []
        for key, name in language_dict.items():
            language_list.append({'key': key, 'name': name})
        # sort by language name
        language_list = sorted(language_list, key=lambda x: x['name'])
        language_code_list = [x['key'] for x in language_list]
        # locate current language
        current_row = language_code_list.index(current_language)
        name_list = [x['name'] for x in language_list]
        chosen_index = aqt.utils.chooseList(f'{constants.MENU_PREFIX} Choose Language for {deck_note_type_field.field_name}', name_list, startrow=current_row)

        new_language = language_code_list[chosen_index]
        languagetools.store_language_detection_result(deck_note_type_field, new_language, tooltip=True)


    def show_translation(source_text, from_language, to_language):
        # print(f'translate {source_text} from {from_language} to {to_language}')
        result = languagetools.get_translation(source_text, from_language, to_language)

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

    def on_context_menu(web_view, menu):
        # gather some information about the context from the editor
        # =========================================================

        selected_text = web_view.selectedText()
        current_field_num = web_view.editor.currentField
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

                menu_text = f'{constants.MENU_PREFIX} transliterate {languagetools.get_language_name(language)}'
                submenu = aqt.qt.QMenu(menu_text, menu)
                transliteration_options = languagetools.get_transliteration_options(language)
                for transliteration_option in transliteration_options:
                    menu_text = transliteration_option['transliteration_name']
                    def get_transliterate_lambda(selected_text, service, transliteration_key):
                        def transliterate():
                            show_transliteration(selected_text, service, transliteration_key)
                        return transliterate
                    submenu.addAction(menu_text, get_transliterate_lambda(selected_text, transliteration_option['service'], transliteration_option['transliteration_key']))
                menu.addMenu(submenu)

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

    # add menu items
    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} Run Language Detection", aqt.mw)
    action.triggered.connect(languagetools.perform_language_detection)
    aqt.mw.form.menuTools.addAction(action)

    action = aqt.qt.QAction(f"{constants.MENU_PREFIX} About", aqt.mw)
    action.triggered.connect(languagetools.show_about)
    aqt.mw.form.menuTools.addAction(action)

    anki.hooks.addHook('EditorWebView.contextMenuEvent', on_context_menu)

    # run some stuff after anki has initialized
    aqt.gui_hooks.main_window_did_init.append(languagetools.initialize)