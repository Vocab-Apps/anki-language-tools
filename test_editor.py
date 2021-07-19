import testing_utils
import editor_processing

def test_process_choosetranslation(qtbot):
    # pytest test_editor.py -rPP -k test_process_choosetranslation

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('batch_translation')

    mock_language_tools.cloud_language_tools.translate_all_result = {
        '老人家': {
            'serviceA': 'first translation A',
            'serviceB': 'second translation B'
        }
    }

    bridge_str = 'choosetranslation:1'

    # when the choose translation dialog comes up, we should pick serviceB
    mock_language_tools.anki_utils.display_dialog_behavior = 'choose_serviceB'

    editor = config_gen.get_mock_editor_with_note(config_gen.note_id_1)
    editor_manager = editor_processing.EditorManager(mock_language_tools)
    editor_manager.process_choosetranslation(editor,  bridge_str)

    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['field_index'] == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['text'] == 'second translation B'


def test_process_choosetranslation_cancel(qtbot):
    # pytest test_editor.py -rPP -k test_process_choosetranslation_cancel

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('batch_translation')

    mock_language_tools.cloud_language_tools.translate_all_result = {
        '老人家': {
            'serviceA': 'first translation A',
            'serviceB': 'second translation B'
        }
    }

    bridge_str = 'choosetranslation:1'

    # when the choose translation dialog comes up, we should pick serviceB
    mock_language_tools.anki_utils.display_dialog_behavior = 'cancel'

    editor = config_gen.get_mock_editor_with_note(config_gen.note_id_1)
    editor_manager = editor_processing.EditorManager(mock_language_tools)
    editor_manager.process_choosetranslation(editor,  bridge_str)    

    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 0
    

def test_editor_translation(qtbot):
    # pytest test_editor.py -rPP -k test_editor_translation

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('batch_translation')

    mock_language_tools.cloud_language_tools.translation_map = {
        '老人': 'old people (short)'
    }    

    editor = config_gen.get_mock_editor_with_note(config_gen.note_id_1)
    editor_manager = editor_processing.EditorManager(mock_language_tools)

    # regular example
    # ---------------

    field_index = 0
    note_id = config_gen.note_id_1
    field_value = '老人' # short version
    bridge_str = f'key:{field_index}:{note_id}:{field_value}'
    editor_manager.process_field_update(editor, bridge_str)

    # verify outputs
    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['field_index'] == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['text'] == 'old people (short)'

    # empty input
    # -----------
    field_value = '' # empty
    bridge_str = f'key:{field_index}:{note_id}:{field_value}'
    editor_manager.process_field_update(editor, bridge_str)

    # verify outputs
    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 2
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[1]['field_index'] == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[1]['text'] == ''


    # empty input (html tag)
    # ----------------------
    field_value = '<br/>' # empty
    bridge_str = f'key:{field_index}:{note_id}:{field_value}'
    editor_manager.process_field_update(editor, bridge_str)

    # verify outputs
    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 3
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[2]['field_index'] == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[2]['text'] == ''    

def test_editor_transliteration(qtbot):
    # pytest test_editor.py -rPP -k test_editor_transliteration

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('batch_transliteration')

    mock_language_tools.cloud_language_tools.transliteration_map = {
        '老人': 'laoren'
    }    

    editor = config_gen.get_mock_editor_with_note(config_gen.note_id_1)
    editor_manager = editor_processing.EditorManager(mock_language_tools)

    field_index = 0
    note_id = config_gen.note_id_1
    field_value = '老人' # short version
    bridge_str = f'key:{field_index}:{note_id}:{field_value}'
    editor_manager.process_field_update(editor, bridge_str)

    # verify outputs
    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['field_index'] == 3 # pinyin
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['text'] == 'laoren'

def test_editor_audio(qtbot):
    # pytest test_editor.py -rPP -k test_editor_audio

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('batch_audio')

    mock_language_tools.cloud_language_tools.transliteration_map = {
        '老人': 'laoren'
    }    

    editor = config_gen.get_mock_editor_with_note(config_gen.note_id_1)
    editor_manager = editor_processing.EditorManager(mock_language_tools)

    field_index = 0
    note_id = config_gen.note_id_1
    field_value = '老人' # short version
    bridge_str = f'key:{field_index}:{note_id}:{field_value}'
    editor_manager.process_field_update(editor, bridge_str)

    # verify outputs

    # sound should have been played
    assert mock_language_tools.anki_utils.played_sound['text'] == '老人'

    #
    return

    assert len(mock_language_tools.anki_utils.editor_set_field_value_calls) == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['field_index'] == 3 # pinyin
    assert mock_language_tools.anki_utils.editor_set_field_value_calls[0]['text'] == 'laoren'    