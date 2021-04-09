import unittest
import pytest
import pprint
import logging
import PyQt5

import dialogs
import dialog_languagemapping
import dialog_voiceselection
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

# https://pytest-qt.readthedocs.io/en/latest/tutorial.html


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

    # make sure our deck appears
    # --------------------------

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('no_language_mapping')

    mapping_dialog = dialog_languagemapping.prepare_language_mapping_dialogue(mock_language_tools)
    
    # assert deck name, note type, and 3 fields
    deck_frame = mapping_dialog.findChild(PyQt5.QtWidgets.QFrame, f'frame_{config_gen.deck_name}')
    assert deck_frame != None
    deck_name_label = mapping_dialog.findChild(PyQt5.QtWidgets.QLabel, f'deck_name_{config_gen.deck_name}')
    assert deck_name_label.text() == config_gen.deck_name
    note_type_label = mapping_dialog.findChild(PyQt5.QtWidgets.QLabel, f'note_type_name_{config_gen.deck_name}_{config_gen.model_name}')
    assert note_type_label.text() == config_gen.model_name

    # look for labels on all 3 fields
    for field_name in config_gen.all_fields:
        field_label_obj_name = f'field_label_{config_gen.model_name} / {config_gen.deck_name} / {field_name}'
        field_label = mapping_dialog.findChild(PyQt5.QtWidgets.QLabel, field_label_obj_name)
        assert field_label.text() == field_name

    # none of the languages should be set
    for field_name in config_gen.all_fields:
        field_language_obj_name = f'field_language_{config_gen.model_name} / {config_gen.deck_name} / {field_name}'
        field_language = mapping_dialog.findChild(PyQt5.QtWidgets.QComboBox, field_language_obj_name)
        assert field_language != None
        # ensure the "not set" option is selected
        assert field_language.currentText() == 'Not Set'

    # now, set languages manually
    # ---------------------------

    field_language_obj_name = f'field_language_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_chinese}'
    field_language_combobox = mapping_dialog.findChild(PyQt5.QtWidgets.QComboBox, field_language_obj_name)
    qtbot.keyClicks(field_language_combobox, 'Chinese')
    field_language_obj_name = f'field_language_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_english}'
    field_language_combobox = mapping_dialog.findChild(PyQt5.QtWidgets.QComboBox, field_language_obj_name)
    qtbot.keyClicks(field_language_combobox, 'English')

    apply_button = mapping_dialog.findChild(PyQt5.QtWidgets.QPushButton, 'apply')
    qtbot.mouseClick(apply_button, PyQt5.QtCore.Qt.LeftButton)

    # ensure configuration has been modified
    model_name = config_gen.model_name
    deck_name = config_gen.deck_name
    assert mock_language_tools.anki_utils.written_config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name][config_gen.field_chinese] == 'zh_cn'
    assert mock_language_tools.anki_utils.written_config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name][config_gen.field_english] == 'en'

    # run automatic detection
    # -----------------------
    
    mapping_dialog = dialog_languagemapping.prepare_language_mapping_dialogue(mock_language_tools)
    # apply button should be disabled
    apply_button = mapping_dialog.findChild(PyQt5.QtWidgets.QPushButton, 'apply')
    assert apply_button.isEnabled() == False

    autodetect_button = mapping_dialog.findChild(PyQt5.QtWidgets.QPushButton, 'run_autodetect')
    qtbot.mouseClick(autodetect_button, PyQt5.QtCore.Qt.LeftButton)
    
    # assert languages detected
    field_language_obj_name = f'field_language_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_chinese}'
    field_language = mapping_dialog.findChild(PyQt5.QtWidgets.QComboBox, field_language_obj_name)
    assert field_language.currentText() == 'Chinese'

    field_language_obj_name = f'field_language_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_english}'
    field_language = mapping_dialog.findChild(PyQt5.QtWidgets.QComboBox, field_language_obj_name)
    assert field_language.currentText() == 'English'

    # apply button should be enabled
    assert apply_button.isEnabled() == True

    # now , click the apply button
    qtbot.mouseClick(apply_button, PyQt5.QtCore.Qt.LeftButton)

    # ensure configuration has been modified
    model_name = config_gen.model_name
    deck_name = config_gen.deck_name
    assert mock_language_tools.anki_utils.written_config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name][config_gen.field_chinese] == 'zh_cn'
    assert mock_language_tools.anki_utils.written_config[constants.CONFIG_DECK_LANGUAGES][model_name][deck_name][config_gen.field_english] == 'en'    

    # mapping_dialog.exec_()

    # show field samples
    # ==================

    # reset this
    mock_language_tools.anki_utils.written_config = None
    mapping_dialog = dialog_languagemapping.prepare_language_mapping_dialogue(mock_language_tools)

    field_samples_button_obj_name = f'field_samples_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_english}'
    autodetect_button = mapping_dialog.findChild(PyQt5.QtWidgets.QPushButton, field_samples_button_obj_name)
    qtbot.mouseClick(autodetect_button, PyQt5.QtCore.Qt.LeftButton)

    assert 'old people' in mock_language_tools.anki_utils.info_message_received
    assert 'hello' in mock_language_tools.anki_utils.info_message_received

    field_samples_button_obj_name = f'field_samples_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_sound}'
    autodetect_button = mapping_dialog.findChild(PyQt5.QtWidgets.QPushButton, field_samples_button_obj_name)
    qtbot.mouseClick(autodetect_button, PyQt5.QtCore.Qt.LeftButton)    

    assert 'No usable field data found' in mock_language_tools.anki_utils.info_message_received

    # set one language manually
    field_language_obj_name = f'field_language_{config_gen.model_name} / {config_gen.deck_name} / {config_gen.field_chinese}'
    field_language_combobox = mapping_dialog.findChild(PyQt5.QtWidgets.QComboBox, field_language_obj_name)
    qtbot.keyClicks(field_language_combobox, 'Sound')

    # hit cancel
    cancel_button = mapping_dialog.findChild(PyQt5.QtWidgets.QPushButton, 'cancel')
    qtbot.mouseClick(cancel_button, PyQt5.QtCore.Qt.LeftButton)
    # there should not be any config change
    assert mock_language_tools.anki_utils.written_config == None

def test_voice_selection(qtbot):
    # pytest test_dialogs.py -rPP -k test_voice_selection

    # make sure the dialog comes up
    # -----------------------------

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('default')

    voice_list = mock_language_tools.cloud_language_tools.get_tts_voice_list('yoyo')
    voice_selection_dialog = dialog_voiceselection.prepare_voice_selection_dialog(mock_language_tools, voice_list)

    # there should be two languages. English And Chinese
    # for each language, there should be two voices
    # they should both have two samples each

    languages_combobox = voice_selection_dialog.findChild(PyQt5.QtWidgets.QComboBox, 'languages_combobox')
    assert languages_combobox.count() == 2
    assert languages_combobox.itemText(0) == 'Chinese'
    assert languages_combobox.itemText(1) == 'English'

    voices_combobox = voice_selection_dialog.findChild(PyQt5.QtWidgets.QComboBox, 'voices_combobox')
    assert voices_combobox.count() == 2
    assert 'Xiaoxiao' in voices_combobox.itemText(0)
    assert 'Yunyang' in voices_combobox.itemText(1)

    # check samples
    assert voice_selection_dialog.sample_labels[0].text() == '老人家'
    assert voice_selection_dialog.sample_labels[1].text() == '你好'

    # now, select English
    qtbot.keyClicks(languages_combobox, 'English')

    assert voices_combobox.count() == 2
    assert 'Aria' in voices_combobox.itemText(0)
    assert 'Guy' in voices_combobox.itemText(1)


    # voice_selection_dialog.exec_()