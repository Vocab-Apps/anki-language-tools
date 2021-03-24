import unittest
import pytest
import pprint
import logging

import dialogs
import languagetools
import constants

class MockLanguageTools(languagetools.LanguageTools):
    def __init__(self, config):
        self.config = config
        self.language_list = {
            'zh_cn': 'Chinese',
            'en': 'English'
        }
    
class MockDeckNoteType(languagetools.DeckNoteType):
    def __init__(self, deck_id, deck_name, model_id, model_name, all_fields):
        languagetools.DeckNoteType.__init__(self, deck_id, deck_name, model_id, model_name)
        self.all_fields = all_fields
    
    def get_field_names(self):
        return self.all_fields


def assert_combobox_items_equal(combobox, expected_items):
    combobox_items = []
    for i in range(combobox.count()):
        combobox_items.append(combobox.itemText(i))
    
    combobox_items.sort()
    expected_items.sort()
    assert combobox_items == expected_items

class TestConfigGenerator():
    def __init__(self):
        self.model_name = 'note-type'
        self.deck_name = 'deck 1'
        self.field_chinese = 'Chinese'
        self.field_english = 'English'
        self.field_sound = 'Sound'
        self.all_fields = [self.field_chinese, self.field_english, self.field_sound]

        self.chinese_voice_key = 'chinese voice'
        self.chinese_voice_description = 'this is a chinese voice'

    def get_default_config(self):
        languagetools_config = {
            constants.CONFIG_DECK_LANGUAGES: {
                self.model_name: {
                    self.deck_name: {
                        self.field_chinese: 'zh_cn',
                        self.field_english: 'en',
                        self.field_sound: 'sound'
                    }
                }
            },
            constants.CONFIG_VOICE_SELECTION: {
                'zh_cn': {
                    'voice_key': self.chinese_voice_key,
                    'voice_description': self.chinese_voice_description
                }
            }

        }
        return languagetools_config

    def get_config_no_language_mapping(self):
        base_config = self.get_default_config()
        base_config[constants.CONFIG_DECK_LANGUAGES] = {}
        return base_config

    def get_config_batch_audio(self):
        base_config = self.get_default_config()
        base_config[constants.CONFIG_BATCH_AUDIO] = {
            self.model_name: {
                self.deck_name: {
                   self.field_sound: self.field_chinese
                }
            }
        }
        return base_config

def test_add_audio(qtbot):
    # pytest test_dialogs.py -rPP -k test_add_audio_regular

    config_gen = TestConfigGenerator()
    languagetools_config = config_gen.get_default_config()

    # test 1 - everything setup but no prior setting
    # ----------------------------------------------

    mock_language_tools = MockLanguageTools(languagetools_config)
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type", config_gen.all_fields) 

    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()

    # do some checks on the from field combo box
    assert_combobox_items_equal(add_audio_dialog.from_field_combobox, ['Chinese', 'English'])
    assert_combobox_items_equal(add_audio_dialog.to_field_combobox, config_gen.all_fields)
    assert add_audio_dialog.voice_label.text() == '<b>' + config_gen.chinese_voice_description + '</b>'

    # test 2 - some defaults already exist
    # ------------------------------------
    languagetools_config = config_gen.get_config_batch_audio()
    mock_language_tools = MockLanguageTools(languagetools_config)

    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()
    assert_combobox_items_equal(add_audio_dialog.from_field_combobox, ['Chinese', 'English'])
    assert_combobox_items_equal(add_audio_dialog.to_field_combobox, config_gen.all_fields)

    # verify that selected fields match expectation
    assert add_audio_dialog.from_field_combobox.currentText() == config_gen.field_chinese
    assert add_audio_dialog.to_field_combobox.currentText() == config_gen.field_sound

    # test 3 - no language mapping done for any field
    # -----------------------------------------------
    languagetools_config = config_gen.get_config_no_language_mapping()
    mock_language_tools = MockLanguageTools(languagetools_config)

    # add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    testcase_instance = unittest.TestCase()
    testcase_instance.assertRaises(languagetools.LanguageMappingError, dialogs.AddAudioDialog, mock_language_tools, deck_note_type, note_id_list)

    # only uncomment if you want to see the dialog come up
    # add_audio_dialog.exec_()

def test_add_translation_transliteration_no_language_mapping(qtbot):
    config_gen = TestConfigGenerator()
    languagetools_config = config_gen.get_config_no_language_mapping()

    mock_language_tools = MockLanguageTools(languagetools_config)
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type", config_gen.all_fields) 

    note_id_list = [42, 43]

    testcase_instance = unittest.TestCase()
    
    # translation
    testcase_instance.assertRaises(languagetools.LanguageMappingError, dialogs.BatchConversionDialog, mock_language_tools, deck_note_type, note_id_list, constants.TransformationType.Translation)

    # transliteration
    testcase_instance.assertRaises(languagetools.LanguageMappingError, dialogs.BatchConversionDialog, mock_language_tools, deck_note_type, note_id_list, constants.TransformationType.Transliteration)

