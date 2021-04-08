import os
import requests
import json
import logging

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

    def api_key_validate_query(self, api_key):
        response = requests.post(self.base_url + '/verify_api_key', json={
            'api_key': api_key
        })
        data = json.loads(response.content)
        return data

    def language_detection(self, api_key, field_sample):
        response = requests.post(self.base_url + '/detect', json={
                'text_list': field_sample
        }, headers={'api_key': api_key})
        if response.status_code == 200:
            data = json.loads(response.content)
            detected_language = data['detected_language']

            return detected_language
        else:
            # error occured, return none
            logging.error(f'could not perform language detection: (status code {response.status_code}) {response.content}')
            return None        

    def get_tts_voice_list(self, api_key):
        response = requests.get(self.base_url + '/voice_list')
        data = json.loads(response.content)
        return data