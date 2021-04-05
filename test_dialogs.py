import unittest
import pytest
import pprint
import logging

import dialogs
import languagetools
import constants
import testing_utils
import deck_utils
import errors

def assert_combobox_items_equal(combobox, expected_items):
    combobox_items = []
    for i in range(combobox.count()):
        combobox_items.append(combobox.itemText(i))
    
    combobox_items.sort()
    expected_items.sort()
    assert combobox_items == expected_items




def test_add_audio(qtbot):
    # pytest test_dialogs.py -rPP -k test_add_audio

    config_gen = testing_utils.TestConfigGenerator()

    # test 1 - everything setup but no prior setting
    # ----------------------------------------------
    mock_language_tools = config_gen.build_languagetools_instance('default')

    deck_note_type = mock_language_tools.deck_utils.build_deck_note_type(config_gen.deck_id, config_gen.model_id)

    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()

    # do some checks on the from field combo box
    assert_combobox_items_equal(add_audio_dialog.from_field_combobox, ['Chinese', 'English'])
    assert_combobox_items_equal(add_audio_dialog.to_field_combobox, config_gen.all_fields)
    assert add_audio_dialog.voice_label.text() == '<b>' + config_gen.chinese_voice_description + '</b>'

    # test 2 - some defaults already exist
    # ------------------------------------
    mock_language_tools = config_gen.build_languagetools_instance('batch_audio')

    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()
    assert_combobox_items_equal(add_audio_dialog.from_field_combobox, ['Chinese', 'English'])
    assert_combobox_items_equal(add_audio_dialog.to_field_combobox, config_gen.all_fields)

    # verify that selected fields match expectation
    assert add_audio_dialog.from_field_combobox.currentText() == config_gen.field_chinese
    assert add_audio_dialog.to_field_combobox.currentText() == config_gen.field_sound

    # test 3 - no language mapping done for any field
    # -----------------------------------------------
    mock_language_tools = config_gen.build_languagetools_instance('no_language_mapping')

    # add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    testcase_instance = unittest.TestCase()
    testcase_instance.assertRaises(errors.LanguageMappingError, dialogs.AddAudioDialog, mock_language_tools, deck_note_type, note_id_list)

    # only uncomment if you want to see the dialog come up
    # add_audio_dialog.exec_()

def test_add_translation_transliteration_no_language_mapping(qtbot):
    # pytest test_dialogs.py -rPP -k test_add_translation_transliteration_no_language_mapping

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('no_language_mapping')
    
    deck_note_type = mock_language_tools.deck_utils.build_deck_note_type(config_gen.deck_id, config_gen.model_id)

    note_id_list = [42, 43]

    testcase_instance = unittest.TestCase()
    
    # translation
    testcase_instance.assertRaises(errors.LanguageMappingError, dialogs.BatchConversionDialog, mock_language_tools, deck_note_type, note_id_list, constants.TransformationType.Translation)

    # transliteration
    testcase_instance.assertRaises(errors.LanguageMappingError, dialogs.BatchConversionDialog, mock_language_tools, deck_note_type, note_id_list, constants.TransformationType.Transliteration)



def test_language_mapping(qtbot):
    # pytest test_dialogs.py -rPP -k test_language_mapping

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('no_language_mapping')

    mapping_dialog = dialogs.prepare_language_mapping_dialogue(mock_language_tools)

    # mapping_dialog.exec_()


