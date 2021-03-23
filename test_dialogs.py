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
        return ['Chinese', 'English']


def test_add_audio_regular(qtbot):
    model_name = 'note-type'
    deck_name = 'deck 1'
    field_chinese = 'Chinese'
    field_english = 'English'
    field_sound = 'Sound'
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
        }

    }
    mock_language_tools = MockLanguageTools(languagetools_config)
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type") 
    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()
    # add_audio_dialog.exec_()
    assert True

@pytest.mark.skip(reason="skip for now")
def test_add_audio_dialog_unmapped(qtbot):
    mock_language_tools = MockLanguageTools()
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type") 
    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()
    add_audio_dialog.exec_()
    assert True