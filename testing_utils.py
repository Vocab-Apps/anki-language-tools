import logging
import json

import constants
import deck_utils
import languagetools

class MockFuture():
    def __init__(self, result_data):
        self.result_data = result_data

    def result(self):
        return self.result_data


class MockAnkiUtils():
    def __init__(self, config):
        self.config = config
        self.written_config = None
        self.editor_set_field_value_called = None

    def get_config(self):
        return self.config

    def write_config(self, config):
        self.written_config = config

    def get_green_stylesheet(self):
        return constants.GREEN_STYLESHEET

    def get_red_stylesheet(self):
        return constants.RED_STYLESHEET

    def play_anki_sound_tag(self, text):
        self.last_played_sound_tag = text

    def get_deckid_modelid_pairs(self):
        return self.deckid_modelid_pairs

    def get_noteids_for_deck_note_type(self, deck_id, model_id, sample_size):

        note_id_list = self.notes[deck_id][model_id].keys()

        return note_id_list

    def get_note_by_id(self, note_id):
        return self.notes_by_id[note_id]


    def get_model(self, model_id):
        # should return a dict which has flds
        return self.models[model_id]

    def get_deck(self, deck_id):
        return self.decks[deck_id]

    def get_model_id(self, model_name):
        return self.model_by_name[model_name]

    def get_deck_id(self, deck_name):
        return self.deck_by_name[deck_name]

    def run_in_background(self, task_fn, task_done_fn):
        # just run the two tasks immediately
        result = task_fn()
        task_done_fn(MockFuture(result))

    def run_on_main(self, task_fn):
        # just run the task immediately
        task_fn()

    def wire_typing_timer(self, text_input, text_input_changed):
        # just fire the text_input_changed callback immediately, there won't be any typing
        text_input.textChanged.connect(text_input_changed)
        return None

    def info_message(self, message, parent):
        logging.info(f'info message: {message}')
        self.info_message_received = message

    def critical_message(self, message, parent):
        logging.info(f'critical error message: {message}')
        self.critical_message_received = message

    def play_sound(self, filename):
        # load the json inside the file
        with open(filename) as json_file:
            self.played_sound = json.load(json_file)

    def show_progress_bar(self, message):
        self.show_progress_bar_called = True

    def stop_progress_bar(self):
        self.stop_progress_bar_called = True

    def editor_set_field_value(self, editor, field_index, text):
        self.editor_set_field_value_called = {
            'field_index': field_index,
            'text': text
        }

    def display_dialog(self, dialog):
        # currently only used for the choose translation dialog

        if self.display_dialog_behavior == 'choose_serviceB':
            # choose second translation available
            dialog.selected_translation = dialog.all_translations['serviceB']
            return True
        
        if self.display_dialog_behavior == 'cancel':
            return False

class MockCloudLanguageTools():
    def __init__(self):
        self.verify_api_key_called = False
        self.verify_api_key_input = None
        self.verify_api_key_is_valid = True

        self.language_list = {
            'en': 'English',
            'zh_cn': 'Chinese',
            'mg': 'Malagasy'
        }
        self.translation_language_list = [
            {
                'service': "Azure",
                'language_code': "en",
                'language_name': "English",
                'language_id': "en"
            },
            {
                'service': "Azure",
                'language_code': "zh_cn",
                'language_name': "Chinese",
                'language_id': "zh-hans"
            },            
        ]
        self.transliteration_language_list = [] # todo fill this out

        self.voice_list = [
            {
                "audio_language_code": "en_US",
                "audio_language_name": "English (US)",
                "gender": "Male",
                "language_code": "en",
                "options": {
                    "pitch": {
                        "default": 0,
                        "max": 100,
                        "min": -100,
                        "type": "number"
                    },
                    "rate": {
                        "default": 1.0,
                        "max": 3.0,
                        "min": 0.5,
                        "type": "number"
                    }
                },
                "service": "Azure",
                "voice_description": "English (US), Male, Guy (Neural), Azure",
                "voice_key": {
                    "name": "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)"
                }
            },            
            {
                "audio_language_code": "en_US",
                "audio_language_name": "English (US)",
                "gender": "Female",
                "language_code": "en",
                "options": {
                    "pitch": {
                        "default": 0,
                        "max": 100,
                        "min": -100,
                        "type": "number"
                    },
                    "rate": {
                        "default": 1.0,
                        "max": 3.0,
                        "min": 0.5,
                        "type": "number"
                    }
                },
                "service": "Azure",
                "voice_description": "English (US), Female, Aria (Neural), Azure",
                "voice_key": {
                    "name": "Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)"
                }
            },
            {
                "audio_language_code": "zh_CN",
                "audio_language_name": "Chinese (Mandarin, Simplified)",
                "gender": "Female",
                "language_code": "zh_cn",
                "options": {
                    "pitch": {
                        "default": 0,
                        "max": 100,
                        "min": -100,
                        "type": "number"
                    },
                    "rate": {
                        "default": 1.0,
                        "max": 3.0,
                        "min": 0.5,
                        "type": "number"
                    }
                },
                "service": "Azure",
                "voice_description": "Chinese (Mandarin, Simplified), Female, Xiaoxiao 晓晓 (Neural), Azure",
                "voice_key": {
                    "name": "Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)"
                }
            },
            {
                "audio_language_code": "zh_CN",
                "audio_language_name": "Chinese (Mandarin, Simplified)",
                "gender": "Male",
                "language_code": "zh_cn",
                "options": {
                    "pitch": {
                        "default": 0,
                        "max": 100,
                        "min": -100,
                        "type": "number"
                    },
                    "rate": {
                        "default": 1.0,
                        "max": 3.0,
                        "min": 0.5,
                        "type": "number"
                    }
                },
                "service": "Azure",
                "voice_description": "Chinese (Mandarin, Simplified), Male, Yunyang 云扬 (Neural), Azure",
                "voice_key": {
                    "name": "Microsoft Server Speech Text to Speech Voice (zh-CN, YunyangNeural)"
                }
            }
        ]


    def get_language_list(self):
        return self.language_list

    def get_translation_language_list(self):
        return self.translation_language_list

    def get_transliteration_language_list(self):
        return self.transliteration_language_list

    def get_tts_voice_list(self, api_key):
        return self.voice_list

    def api_key_validate_query(self, api_key):

        self.verify_api_key_called = True
        self.verify_api_key_input = api_key

        return {
            'key_valid': self.verify_api_key_is_valid,
            'msg': f'api key: {self.verify_api_key_is_valid}'
        }     

    def language_detection(self, api_key, field_sample):
        return self.language_detection_result[field_sample[0]]

    def get_tts_audio(self, api_key, source_text, service, language_code, voice_key, options):
        self.requested_audio = {
            'text': source_text,
            'service': service,
            'language_code': language_code,
            'voice_key': voice_key,
            'options': options
        }
        encoded_dict = json.dumps(self.requested_audio, indent=2).encode('utf-8')
        return encoded_dict

    def get_translation_all(self, api_key, source_text, from_language, to_language):
        return self.translate_all_result[source_text]

class MockCard():
    def __init__(self, deck_id):
        self.did = deck_id

class MockNote():
    def __init__(self, model_id, field_dict, field_array):
        self.mid = model_id
        self.field_dict = field_dict
        self.fields = field_array
    
    def __getitem__(self, key):
        return self.field_dict[key]

class MockEditor():
    def __init__(self):
        self.addMode = False

class TestConfigGenerator():
    def __init__(self):
        self.deck_id = 42001
        self.model_id = 43001
        self.model_name = 'note-type'
        self.deck_name = 'deck 1'
        self.field_chinese = 'Chinese'
        self.field_english = 'English'
        self.field_sound = 'Sound'

        self.note_id_1 = 42005
        self.note_id_2 = 43005

        self.all_fields = [self.field_chinese, self.field_english, self.field_sound]

        self.chinese_voice_key = 'chinese voice'
        self.chinese_voice_description = 'this is a chinese voice'

    # different languagetools configs available
    # =========================================

    def get_default_config(self):
        languagetools_config = {
            'api_key': 'yoyo',
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
            },
            constants.CONFIG_WANTED_LANGUAGES: {
                'en': True,
                'zh_cn': True
            }

        }
        return languagetools_config

    def get_noapikey_config(self):
        languagetools_config = self.get_default_config()
        languagetools_config['api_key'] = ''
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

    def get_config_batch_translation(self):
        base_config = self.get_default_config()
        base_config[constants.CONFIG_BATCH_TRANSLATION] = {
            self.model_name: {
                self.deck_name: {
                   self.field_english: {
                       'from_field': self.field_chinese
                   }
                }
            }
        }
        return base_config        

    def get_config_language_no_voices(self):
        base_config = self.get_default_config()
        base_config[constants.CONFIG_WANTED_LANGUAGES]['mg'] = True
        base_config[constants.CONFIG_DECK_LANGUAGES][self.model_name][self.deck_name][self.field_english] = 'mg'
        return base_config    

    def get_languagetools_config(self, scenario):

        fn_map = {
            'default': self.get_default_config,
            'noapikey': self.get_noapikey_config,
            'no_language_mapping': self.get_config_no_language_mapping,
            'batch_audio': self.get_config_batch_audio,
            'batch_translation': self.get_config_batch_translation,
            'get_config_language_no_voices': self.get_config_language_no_voices
        }

        fn_instance = fn_map[scenario]
        return fn_instance()


    def get_model_map(self):
        return {
            self.model_id: {
                'name': self.model_name,
                'flds': [
                    {'name': self.field_chinese},
                    {'name': self.field_english},
                    {'name': self.field_sound}
                ]
            }
        }
    
    def get_language_detection_result(self):
        return {
            '老人家': 'zh_cn',
            'old people': 'en',
            '你好': 'zh_cn',
            'hello': 'en'
        }

    def get_deck_map(self):
        return {
            self.deck_id: {
                'name': self.deck_name
            }
        }

    def get_deck_by_name(self):
        return {
            self.deck_name: self.deck_id
        }

    def get_model_by_name(self):
        return {
            self.model_name: self.model_id
        }

    def get_deckid_modelid_pairs(self):
        return [
            [self.deck_id, self.model_id]
        ]        

    def get_note_id_list(self):
        notes_by_id, notes = self.get_notes()
        return list(notes_by_id.keys())

    def get_notes(self):
        notes_by_id = {
            self.note_id_1: {
                self.field_chinese: '老人家',
                self.field_english: 'old people',
                self.field_sound: ''
            },
            self.note_id_2: {
                self.field_chinese: '你好',
                self.field_english: 'hello',
                self.field_sound: ''
            }
        }
        notes = {
            self.deck_id: {
                self.model_id: notes_by_id
            }
        }
        return notes_by_id, notes

    def get_mock_editor_with_note(self, note_id):
        editor = MockEditor()
        editor.card = MockCard(self.deck_id)
        field_array = []
        notes_by_id, notes = self.get_notes()
        note_data = notes_by_id[note_id]        
        for field_entry in self.get_model_map()[self.model_id]['flds']:
            field_name = field_entry['name']
            field_array.append(note_data[field_name])
        editor.note = MockNote(self.model_id, note_data, field_array)
        return editor


    def build_languagetools_instance(self, scenario):
        languagetools_config = self.get_languagetools_config(scenario)
        mock_cloudlanguagetools = MockCloudLanguageTools()

        anki_utils = MockAnkiUtils(languagetools_config)
        deckutils = deck_utils.DeckUtils(anki_utils)
        mock_language_tools = languagetools.LanguageTools(anki_utils, deckutils, mock_cloudlanguagetools)
        mock_language_tools.initialize()
        mock_language_tools.clean_user_files_audio()

        anki_utils.models = self.get_model_map()
        anki_utils.decks = self.get_deck_map()
        anki_utils.model_by_name = self.get_model_by_name()
        anki_utils.deck_by_name = self.get_deck_by_name()
        anki_utils.deckid_modelid_pairs = self.get_deckid_modelid_pairs()
        anki_utils.notes_by_id, anki_utils.notes = self.get_notes()
        mock_cloudlanguagetools.language_detection_result = self.get_language_detection_result()

        return mock_language_tools