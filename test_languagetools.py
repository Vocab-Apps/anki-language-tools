import json
import testing_utils

class EmptyFieldConfigGenerator(testing_utils.TestConfigGenerator):
    def __init__(self):
        testing_utils.TestConfigGenerator.__init__(self)
        self.notes_by_id = {
            self.note_id_1: testing_utils.MockNote(self.model_id,{
                self.field_chinese: '', # empty
                self.field_english: 'old people',
                self.field_sound: ''
            }, self.all_fields),
            self.note_id_2: testing_utils.MockNote(self.model_id, {
                self.field_chinese: '你好',
                self.field_english: 'hello',
                self.field_sound: ''
            }, self.all_fields)
        }                

class DummyHtmlEmptyFieldConfigGenerator(testing_utils.TestConfigGenerator):
    def __init__(self):
        testing_utils.TestConfigGenerator.__init__(self)
        self.notes_by_id = {
            self.note_id_1: testing_utils.MockNote(self.model_id,{
                self.field_chinese: '&nbsp;', # empty
                self.field_english: 'old people',
                self.field_sound: ''
            }, self.all_fields),
            self.note_id_2: testing_utils.MockNote(self.model_id, {
                self.field_chinese: '你好',
                self.field_english: 'hello',
                self.field_sound: ''
            }, self.all_fields)
        }                        

def test_generate_audio_for_field(qtbot):
    
    # regular case
    # ============

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('default')

    # common variables
    note_id = config_gen.note_id_1
    from_field = config_gen.field_chinese
    to_field = config_gen.field_sound

    voice_list = mock_language_tools.get_tts_voice_list()
    chinese_voices = [x for x in voice_list if x['language_code'] == 'zh_cn']
    voice = chinese_voices[0]

    result = mock_language_tools.generate_audio_for_field(note_id, from_field, to_field, voice)
    assert result == True

    # get the note
    note = config_gen.notes_by_id[config_gen.note_id_1]

    # make sure sound was added
    assert config_gen.field_sound in note.set_values
    assert 'sound:languagetools-' in note.set_values[config_gen.field_sound]
    assert note.flush_called == True

    assert mock_language_tools.anki_utils.added_media_file != None
    assert 'languagetools-' in mock_language_tools.anki_utils.added_media_file

    # empty field
    # ===========

    config_gen = EmptyFieldConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('default')

    result = mock_language_tools.generate_audio_for_field(note_id, from_field, to_field, voice)
    assert result == False    

    # get the note
    note = config_gen.notes_by_id[config_gen.note_id_1]

    # make sure no sound was added
    assert config_gen.field_sound not in note.set_values
    assert note.flush_called == False

    assert mock_language_tools.anki_utils.added_media_file == None

    # empty field but with html junk
    # ==============================

    config_gen = DummyHtmlEmptyFieldConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('default')

    result = mock_language_tools.generate_audio_for_field(note_id, from_field, to_field, voice)
    assert result == False    

    # get the note
    note = config_gen.notes_by_id[config_gen.note_id_1]

    # make sure no sound was added
    assert config_gen.field_sound not in note.set_values
    assert note.flush_called == False

    assert mock_language_tools.anki_utils.added_media_file == None    


def test_get_tts_audio(qtbot):
    # pytest test_languagetools.py -k test_get_tts_audio

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('text_replacement')

    filename = mock_language_tools.get_tts_audio('unter etw', 'Azure', 'de_de', {'name': 'voice1'}, {})
    file_contents = open(filename, 'r').read()
    data = json.loads(file_contents)

    assert data['text'] == 'unter etwas' # after text replacement

