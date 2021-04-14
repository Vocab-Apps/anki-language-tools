import logging

def process_choosetranslation(editor, languagetools, str):
    logging.debug(f'choosetranslation command: [{str}]')
    components = str.split(':')
    field_index_str = components[1]
    field_index = int(field_index_str)

    note = editor.note
    source_text = note.fields[field_index]
    logging.debug(f'source_text: {source_text}')

    deck_note_type = languagetools.deck_utils.build_deck_note_type_from_editor(editor)

    target_dntf = languagetools.deck_utils.get_dntf_from_fieldindex(deck_note_type, field_index)
    translation_from_field = languagetools.get_batch_translation_setting_field(target_dntf)
    from_field = translation_from_field['from_field']
    from_dntf = languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, from_field)

    logging.debug(f'from field: {from_dntf} target field: {target_dntf}')