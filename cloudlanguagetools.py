import os
import sys
import requests
import json
import logging
import sentry_sdk

if hasattr(sys, '_pytest_mode'):
    import constants
    import errors
    import version
else:
    from . import constants
    from . import errors
    from . import version

class CloudLanguageTools():
    def __init__(self):
        self.clt_api_base_url = os.environ.get(constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL, constants.CLT_API_BASE_URL)
        self.vocab_api_base_url = os.environ.get(constants.ENV_VAR_ANKI_LANGUAGE_TOOLS_VOCABAI_BASE_URL, constants.VOCABAI_API_BASE_URL)
        self.initialization_done = False
        self.api_key = None

    def api_key_set(self):
        return self.api_key != None

    def get_base_url(self):
        if self.use_vocabai_api:
            return self.vocab_api_base_url
        else:
            return self.clt_api_base_url

    def get_headers_clt_api(self, api_key):
        headers={
            'api_key': api_key,
            'User-Agent': f'anki-language-tools/{version.ANKI_LANGUAGE_TOOLS_VERSION}',
            'client': constants.CLIENT_NAME, 
            'client_version': version.ANKI_LANGUAGE_TOOLS_VERSION
        }
        return headers

    def get_headers_vocabai_api(self, api_key):
        headers={
            'Authorization': f'Api-Key {api_key}',
            'User-Agent': f'anki-language-tools/{version.ANKI_LANGUAGE_TOOLS_VERSION}',
        }
        return headers

    def get_headers(self):
        if self.use_vocabai_api:
            return self.get_headers_vocabai_api(self.api_key)
        else:
            return self.get_headers_clt_api(self.api_key)

    def get_url(self, endpoint):
        clt_endpoint_overrides = {
            'language_data': 'language_data_v1',
            'audio': 'audio_v2',
            'breakdown': 'breakdown_v1'
        }
        if self.use_vocabai_api == False:
            if endpoint in clt_endpoint_overrides:
                endpoint = clt_endpoint_overrides[endpoint]
        return self.get_base_url() + '/' + endpoint

    def authenticated_get_request(self, endpoint):
        url = self.get_url(endpoint)
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json()

    def authenticated_post_request(self, endpoint, data):
        url = self.get_url(endpoint)
        response = requests.post(url, json=data, headers=self.get_headers())
        response.raise_for_status()
        return response.json()

    def authenticated_post_request_response(self, endpoint, data):
        # just return the response without any processing
        url = self.get_url(endpoint)
        response = requests.post(url, json=data, headers=self.get_headers())
        return response

    def get_language_data(self):
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='get_language_data'):
            return self.authenticated_get_request('language_data')

    def api_key_validate_query(self, api_key):
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='verify_api_key'):
            # first, try to validate api key using the account endpoint on vocabai

            # try to get account data on vocabai first
            response = requests.get(self.vocab_api_base_url + '/account', headers=self.get_headers_vocabai_api(api_key))
            if response.status_code == 200:
                # API key is valid on vocab API
                self.use_vocabai_api = True
                self.api_key = api_key
                return {
                    'key_valid': True,
                    'msg': f'api key: {api_key}'
                }

            # now try to get account data on CLT API
            url = self.clt_api_base_url + '/account'
            response = requests.get(url, headers=self.get_headers_clt_api(api_key))
            if response.status_code == 200:
                self.use_vocabai_api = False
                # API key is valid on CLT API
                # check if there are errors
                if 'error' in response.json():
                    return {
                        'key_valid': False,
                        'msg': f'api key: ' + response.json()['error']
                    }                    

                # otherwise, it's considered valid
                self.api_key = api_key
                return {
                    'key_valid': True,
                    'msg': f'api key: {api_key}'
                }

            # default case, API key is not valid
            return {
                'key_valid': False,
                'msg': f'API key not found'
            }

    def account_info(self):
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='account_info'):
            return self.authenticated_get_request('account')

    def language_detection(self, field_sample):
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='language_detection'):
            data = {
                    'text_list': field_sample
            }
            response_data = self.authenticated_post_request('detect', data)
            detected_language = response_data['detected_language']
            return detected_language

    def get_tts_audio_request(self, source_text, service, language_code, voice_key, options):
        url = self.get_url('audio')
        data = {
            'text': source_text,
            'service': service,
            'voice_key': voice_key,
            'request_mode': 'batch',
            'language_code': language_code,
            'deck_name': 'n/a',
            'options': options
        }
        headers = self.get_headers()
        return requests.post(url, json=data, headers=headers)

    def get_tts_audio(self, source_text, service, language_code, voice_key, options):
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name=f'Audio_{service}'):
            response = self.get_tts_audio_request(source_text, service, language_code, voice_key, options)

            if response.status_code == 200:
                return response.content
            else:
                response_data = json.loads(response.content)
                error_msg = response_data
                if 'error' in response_data:
                    error_msg = 'Error: ' + response_data['error']
                raise errors.AudioLanguageToolsRequestError(f'Status Code: {response.status_code} ({error_msg})')

    def get_translation(self, source_text, translation_option):
        # returns the response from requests directly
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='Translation_'+translation_option['service']):
            return self.authenticated_post_request_response('translate', {
                'text': source_text,
                'service': translation_option['service'],
                'from_language_key': translation_option['source_language_id'],
                'to_language_key': translation_option['target_language_id']
            })

    def get_transliteration(self, source_text, transliteration_option):
        # returns the response from requests directly
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='Transliteration_'+transliteration_option['service']):
            return self.authenticated_post_request_response('transliterate', {
                    'text': source_text,
                    'service': transliteration_option['service'],
                    'transliteration_key': transliteration_option['transliteration_key']
            })

    def get_breakdown(self, source_text, tokenization_option, translation_option, transliteration_option):
        # returns the response from requests directly
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='breakdown'):
            breakdown_request = {
                    'text': source_text,
                    'tokenization_option': tokenization_option
            }
            if translation_option != None:
                breakdown_request['translation_option'] = translation_option
            if transliteration_option != None:
                breakdown_request['transliteration_option'] = transliteration_option
            logging.debug(f'sending breakdown request: {breakdown_request}')
            return self.authenticated_post_request_response('breakdown', breakdown_request)

    def get_translation_all(self, source_text, from_language, to_language):
        with sentry_sdk.start_transaction(op=constants.SENTRY_OPERATION, name='translation_all'):
            return self.authenticated_post_request('translate_all', {
                    'text': source_text,
                    'from_language': from_language,
                    'to_language': to_language
            })
