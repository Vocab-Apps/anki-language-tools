import unittest
import pytest

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
    def __init__(self, deck_id, deck_name, model_id, model_name):
        languagetools.DeckNoteType.__init__(self, deck_id, deck_name, model_id, model_name)
    
    def get_field_names(self):
        return ['Chinese', 'English', 'Sound']


def assert_combobox_items_equal(combobox, expected_items):
    combobox_items = []
    for i in range(combobox.count()):
        combobox_items.append(combobox.itemText(i))
    
    combobox_items.sort()
    expected_items.sort()
    assert combobox_items == expected_items

def test_add_audio_regular(qtbot):
    # pytest test_dialogs.py -rPP -k test_add_audio_regular

    model_name = 'note-type'
    deck_name = 'deck 1'
    field_chinese = 'Chinese'
    field_english = 'English'
    field_sound = 'Sound'

    chinese_voice_key = 'chinese voice'
    chinese_voice_description = 'this is a chinese voice'
    languagetools_config = {
        constants.CONFIG_DECK_LANGUAGES: {
            model_name: {
                deck_name: {
                    field_chinese: 'zh_cn',
                    field_english: 'en',
                    field_sound: 'sound'
                }
            }
        },
        constants.CONFIG_VOICE_SELECTION: {
            'zh_cn': {
                'voice_key': chinese_voice_key,
                'voice_description': chinese_voice_description
            }
        }

    }
    mock_language_tools = MockLanguageTools(languagetools_config)
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type") 
    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()

    # do some checks on the from field combo box
    assert_combobox_items_equal(add_audio_dialog.from_field_combobox, ['Chinese', 'English'])
    assert_combobox_items_equal(add_audio_dialog.to_field_combobox, ['Chinese', 'English', 'Sound'])

    assert add_audio_dialog.voice_label.text() == '<b>' + chinese_voice_description + '</b>'

    # only uncomment if you want to see the dialog come up
    # add_audio_dialog.exec_()

@pytest.mark.skip(reason="skip for now")
def test_add_audio_dialog_unmapped(qtbot):
    mock_language_tools = MockLanguageTools()
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type") 
    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()
    add_audio_dialog.exec_()
    assert True