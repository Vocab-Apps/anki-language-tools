import json
import os
import unittest
import pprint

# add external search path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'external'))

import cloudlanguagetools
import constants


# create unit test class for CLT API tests
class ValidateAPIKeyTests(unittest.TestCase):
    # setup
    def setUp(self):
        # setup test data
        self.clt = cloudlanguagetools.CloudLanguageTools()

    def test_validate_clt_api_key(self):
        self.assertEquals(self.clt.api_key_set(), False)
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_CLT_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        pprint.pprint(response)
        self.assertEquals(response['key_valid'], True)
        self.assertEquals(self.clt.use_vocabai_api, False)
        self.assertEquals(self.clt.api_key, api_key)
        self.assertEquals(self.clt.api_key_set(), True)

    def test_validate_vocab_api_key(self):
        self.assertEquals(self.clt.api_key_set(), False)
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_VOCAB_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        pprint.pprint(response)
        self.assertEquals(response['key_valid'], True)
        self.assertEquals(self.clt.use_vocabai_api, True)
        self.assertEquals(self.clt.api_key, api_key)
        self.assertEquals(self.clt.api_key_set(), True)

    def test_validate_bad_api_key(self):
        self.assertEquals(self.clt.api_key_set(), False)
        api_key = 'incorrect_key'
        response = self.clt.api_key_validate_query(api_key)
        self.assertEquals(response['key_valid'], False)
        self.assertEquals(self.clt.api_key, None)
        self.assertEquals(self.clt.api_key_set(), False)

# base class executes CLT tests, derived class executes VOCABAI tests
class CloudLanguageToolsCLTTests(unittest.TestCase):
    # setup
    def setUp(self):
        # setup test data
        self.clt = cloudlanguagetools.CloudLanguageTools()
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_CLT_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        self.assertEquals(response['key_valid'], True)

    def test_get_base_url(self):
        self.assertEquals(self.clt.get_base_url(), constants.CLT_API_BASE_URL)

    def test_get_language_data(self):
        response = self.clt.get_language_data()
        self.assertGreater(len(response['language_list']), 0)
        self.assertGreater(len(response['translation_options']), 0)
        self.assertGreater(len(response['transliteration_options']), 0)
        self.assertGreater(len(response['voice_list']), 0)
        self.assertGreater(len(response['tokenization_options']), 0)

    def test_account_info(self):
        response = self.clt.account_info()
        self.assertTrue('email' in response)
        self.assertTrue(len(response['email']) > 0)

    def test_detect(self):
        detected_language = self.clt.language_detection(['Bonjour', 'Au revoir'])
        self.assertEquals(detected_language, 'fr')

    def test_get_tts_audio_request(self):
        language_data = self.clt.get_language_data()
        voice_list = language_data['voice_list']
        service = 'Azure'
        french_voices = [x for x in voice_list if x['language_code'] == 'fr' and x['service'] == service]
        first_voice = french_voices[0]
        source_text = 'Bonjour'
        response = self.clt.get_tts_audio_request(source_text, first_voice['service'], first_voice['language_code'], first_voice['voice_key'], {})
        self.assertEquals(response.status_code, 200)

    # def test_translation(self):
    #     language_data = self.clt.get_language_data()
    #     translation_language_list = language_data['translation_options']
    #     chinese_azure = [x for x in translation_language_list if x['language_code'] == 'zh_cn' and x['service'] == 'Azure']
    #     translation_azure_chinese = chinese_azure[0]

    #     translation_option = {
    #         'text': '中国有很多外国人',
    #         'service': 'Azure',
    #         'from_language_key': translation_azure_chinese['language_id'],
    #         'to_language_key': 'en'
    #     }        

    #     pprint.pprint(translation_azure_chinese)
    #     response = self.clt.get_translation('中国有很多外国人', translation_azure_chinese)
    #     self.assertEquals(response.status_code, 200)



class CloudLanguageToolsVocabTests(unittest.TestCase):
    # setup
    def setUp(self):
        # setup test data
        self.clt = cloudlanguagetools.CloudLanguageTools()
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_VOCAB_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        self.assertEquals(response['key_valid'], True)

    # test get_base_url
    def test_get_base_url(self):
        self.assertEquals(self.clt.get_base_url(), constants.VOCABAI_API_BASE_URL)

if __name__ == '__main__':
    unittest.main()