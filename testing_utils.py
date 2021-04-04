import constants

class MockAnkiUtils():
    def __init__(self, config):
        self.config = config

    def get_config(self):
        return self.config

    def get_green_stylesheet(self):
        return constants.GREEN_STYLESHEET

    def get_red_stylesheet(self):
        return constants.RED_STYLESHEET

    def play_anki_sound_tag(self, text):
        self.last_played_sound_tag = text

    def get_deckid_modelid_pairs(self):
        return self.deckid_modelid_pairs

    def get_model(self, model_id):
        # should return a dict which has flds
        return self.models[model_id]

class MockCloudLanguageTools():
    def __init__(self):
        self.language_list = {
            'en': 'English',
            'zh_cn': 'Chinese'
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


    def get_language_list(self):
        return self.language_list

    def get_translation_language_list(self):
        return self.translation_language_list

    def get_transliteration_language_list(self):
        return self.transliteration_language_list