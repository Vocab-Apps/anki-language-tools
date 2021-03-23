import unittest
import pytest

import dialogs
import languagetools

class MockLanguageTools():
    def __init__(self):
        pass

class MockDeckNoteType(languagetools.DeckNoteType):
    def __init__(self, deck_id, deck_name, model_id, model_name):
        languagetools.DeckNoteType.__init__(self, deck_id, deck_name, model_id, model_name)
    
    def get_field_names(self):
        return ['Chinese', 'English']


def test_add_audio_dialog(qtbot):
    print(qtbot)
    mock_language_tools = MockLanguageTools()
    deck_note_type = MockDeckNoteType(1, "deck 1", 2, "note-type") 
    note_id_list = [42, 43]
    add_audio_dialog = dialogs.AddAudioDialog(mock_language_tools, deck_note_type, note_id_list)
    add_audio_dialog.setupUi()
    add_audio_dialog.exec_()
    assert True