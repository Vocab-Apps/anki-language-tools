import logging
import sys

if hasattr(sys, '_pytest_mode'):
    import errors
    import dialog_choosetranslation
else:
    from . import errors
    from . import dialog_choosetranslation

def process_choosetranslation(editor, languagetools, str):
    logging.debug(f'choosetranslation command: [{str}]')
    components = str.split(':')
    field_index_str = components[1]
    field_index = int(field_index_str)

    note = editor.note
    current_translation_text = note.fields[field_index]

    deck_note_type = languagetools.deck_utils.build_deck_note_type_from_editor(editor)

    target_dntf = languagetools.deck_utils.get_dntf_from_fieldindex(deck_note_type, field_index)
    translation_from_field = languagetools.get_batch_translation_setting_field(target_dntf)
    from_field = translation_from_field['from_field']
    from_dntf = languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, from_field)
    from_text = note[from_field]

    logging.debug(f'from field: {from_dntf} target field: {target_dntf}')

    # get to and from languages
    from_language = languagetools.get_language(from_dntf)
    to_language = languagetools.get_language(target_dntf)
    if from_language == None:
        raise errors.FieldLanguageMappingError(from_dntf)
    if to_language == None:
        raise errors.FieldLanguageMappingError(target_dntf)

    def load_translation_all():
        return languagetools.get_translation_all(from_text, from_language, to_language)

    def load_translation_all_done(fut):
        languagetools.anki_utils.stop_progress_bar()
        data = fut.result()
        # logging.debug(f'all translations: {data}')
        dialog = dialog_choosetranslation.prepare_dialog(languagetools, data)
        dialog.exec_()

    languagetools.anki_utils.show_progress_bar("retrieving all translations")
    languagetools.anki_utils.run_in_background(load_translation_all, load_translation_all_done)
