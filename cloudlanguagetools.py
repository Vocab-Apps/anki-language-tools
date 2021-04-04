import os
import requests
import json

from . import constants

class CloudLanguageTools():
    def __init__(self):
        self.base_url = 'https://cloud-language-tools-prod.anki.study'
        if constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL in os.environ:
            self.base_url = os.environ[constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL]


    def get_language_list(self):
        response = requests.get(self.base_url + '/language_list')
        return json.loads(response.content)

    def get_translation_language_list(self):
        response = requests.get(self.base_url + '/translation_language_list')
        return json.loads(response.content)

    def get_transliteration_language_list(self):
        response = requests.get(self.base_url + '/transliteration_language_list')
        return json.loads(response.content)