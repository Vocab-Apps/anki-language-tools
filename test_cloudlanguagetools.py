import json
import os
import unittest

# add external search path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'external'))

import cloudlanguagetools


# create unit test class for CLT API tests
class CltAPITests(unittest.TestCase):
    # setup
    def setUp(self):
        # setup test data
        self.clt = cloudlanguagetools.CloudLanguageTools()

    def test_validate_api_key(self):
        api_key = os.environ['ANKI_LANGUAGE_TOOLS_API_KEY']
        response = self.clt.api_key_validate_query(api_key)
        self.assertEquals(response['key_valid'], True)
        self.assertEquals(self.clt.use_vocabai_api, False)


if __name__ == '__main__':
    unittest.main()