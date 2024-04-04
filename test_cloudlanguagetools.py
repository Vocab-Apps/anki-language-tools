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
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_CLT_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        pprint.pprint(response)
        self.assertEquals(response['key_valid'], True)
        self.assertEquals(self.clt.use_vocabai_api, False)
        self.assertEquals(self.clt.api_key, api_key)

    def test_validate_vocab_api_key(self):
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_VOCAB_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        pprint.pprint(response)
        self.assertEquals(response['key_valid'], True)
        self.assertEquals(self.clt.use_vocabai_api, True)
        self.assertEquals(self.clt.api_key, api_key)

    def test_validate_bad_api_key(self):
        api_key = 'incorrect_key'
        response = self.clt.api_key_validate_query(api_key)
        self.assertEquals(response['key_valid'], False)
        self.assertEquals(self.clt.api_key, None)

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