import testing_utils

def test_generate_audio_for_field(qtbot):
    
    # regular case
    # ============

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('default')

    # add some audio
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

