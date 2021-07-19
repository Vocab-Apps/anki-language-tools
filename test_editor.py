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

    assert mock_language_tools.anki_utils.editor_set_field_value_called['field_index'] == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_called['text'] == 'second translation B'


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

    assert mock_language_tools.anki_utils.editor_set_field_value_called == None
    

def test_editor_translation(qtbot):
    # pytest test_editor.py -rPP -k test_editor_translation

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('batch_translation')

    mock_language_tools.cloud_language_tools.translation_map = {
        '老人': 'old people (short)'
    }    

    editor = config_gen.get_mock_editor_with_note(config_gen.note_id_1)
    editor_manager = editor_processing.EditorManager(mock_language_tools)

    field_index = 0
    note_id = config_gen.note_id_1
    field_value = '老人' # short version
    bridge_str = f'key:{field_index}:{note_id}:{field_value}'
    editor_manager.process_field_update(editor, bridge_str)

    # verify outputs
    assert mock_language_tools.anki_utils.editor_set_field_value_called['field_index'] == 1
    assert mock_language_tools.anki_utils.editor_set_field_value_called['text'] == 'old people (short)'

