import logging
import sys

if hasattr(sys, '_pytest_mode'):
    import errors
    import dialog_choosetranslation
    import deck_utils
else:
    from . import errors
    from . import dialog_choosetranslation
    from . import deck_utils

class EditorManager():
    def __init__(self, languagetools):
        self.languagetools = languagetools

    def process_choosetranslation(self, editor, str):
        try:
            logging.debug(f'choosetranslation command: [{str}]')
            components = str.split(':')
            field_index_str = components[1]
            field_index = int(field_index_str)

            note = editor.note
            current_translation_text = note.fields[field_index]

            deck_note_type = self.languagetools.deck_utils.build_deck_note_type_from_editor(editor)

            target_dntf = self.languagetools.deck_utils.get_dntf_from_fieldindex(deck_note_type, field_index)
            translation_from_field = self.languagetools.get_batch_translation_setting_field(target_dntf)
            from_field = translation_from_field['from_field']
            from_dntf = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, from_field)
            from_text = note[from_field]

            logging.debug(f'from field: {from_dntf} target field: {target_dntf}')

            # get to and from languages
            from_language = self.languagetools.get_language(from_dntf)
            to_language = self.languagetools.get_language(target_dntf)
            if from_language == None:
                raise errors.FieldLanguageMappingError(from_dntf)
            if to_language == None:
                raise errors.FieldLanguageMappingError(target_dntf)

            def load_translation_all():
                return self.languagetools.get_translation_all(from_text, from_language, to_language)

            def get_done_callback(from_text, from_language, to_language, editor, field_index):
                def load_translation_all_done(fut):
                    self.languagetools.anki_utils.stop_progress_bar()
                    data = fut.result()
                    # logging.debug(f'all translations: {data}')
                    dialog = dialog_choosetranslation.prepare_dialog(self.languagetools, from_text, from_language, to_language, data)
                    retval = self.languagetools.anki_utils.display_dialog(dialog)
                    if retval == True:
                        chosen_translation = dialog.selected_translation
                        #logging.debug(f'chosen translation: {chosen_translation}')
                        self.languagetools.anki_utils.editor_set_field_value(editor, field_index, chosen_translation)

                return load_translation_all_done

            self.languagetools.anki_utils.show_progress_bar("retrieving all translations")
            self.languagetools.anki_utils.run_in_background(load_translation_all, get_done_callback(from_text, from_language, to_language, editor, field_index))
        except Exception as e:
            self.languagetools.anki_utils.critical_message(str(e), None)

    def process_field_update(self, editor, str):
        components = str.split(':')
        if len(components) >= 4:
            field_index_str = components[1]
            note_id_str = components[2]
            field_value = ':'.join(components[3:])
            field_index = int(field_index_str)
            note_id = int(note_id_str)
            note = editor.note
            note_id = note.id

            from_deck_note_type_field = from_deck_note_type_field = self.languagetools.deck_utils.editor_get_dntf(editor, field_index)
            deck_note_type = from_deck_note_type_field.deck_note_type

            original_field_value = note[from_deck_note_type_field.field_name]

            # print(f'new field value: [{field_value}] original field value: [{original_field_value}]')

            if field_value != original_field_value:
                # only do something if the field has changed

                # do we have translation rules for this deck_note_type
                translation_settings = self.languagetools.get_batch_translation_settings(deck_note_type)
                relevant_settings = {to_field:value for (to_field,value) in translation_settings.items() if value['from_field'] == from_deck_note_type_field.field_name}
                for to_field, value in relevant_settings.items():
                    to_deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, to_field)
                    self.load_translation(editor, note_id, field_value, to_deck_note_type_field, value['translation_option'])

                # do we have transliteration rules for this deck_note_type
                transliteration_settings = self.languagetools.get_batch_transliteration_settings(deck_note_type)
                relevant_settings = {to_field:value for (to_field,value) in transliteration_settings.items() if value['from_field'] == from_deck_note_type_field.field_name}
                for to_field, value in relevant_settings.items():
                    to_deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, to_field)
                    self.load_transliteration(editor, note_id, field_value, to_deck_note_type_field, value['transliteration_option'])

                # do we have any audio rules for this deck_note_type
                audio_settings = self.languagetools.get_batch_audio_settings(deck_note_type)
                relevant_settings = {to_field:from_field for (to_field,from_field) in audio_settings.items() if from_field == from_deck_note_type_field.field_name}
                for to_field, from_field in relevant_settings.items():
                    to_deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, to_field)
                    # get the from language
                    from_language = self.languagetools.get_language(from_deck_note_type_field)
                    if from_language != None:
                        # get voice for this language
                        voice_settings = self.languagetools.get_voice_selection_settings()
                        if from_language in voice_settings:
                            voice = voice_settings[from_language]
                            self.load_audio(editor, note_id, field_value, to_deck_note_type_field, voice)        

    # generic function to load a transformation asynchronously (translation / transliteration / audio)
    def load_transformation(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, request_transformation_fn, interpret_response_fn):
        field_index = self.languagetools.deck_utils.get_field_id(to_deck_note_type_field)

        # is the source field empty ?
        if self.languagetools.text_utils.is_empty(field_value):
            self.languagetools.anki_utils.editor_set_field_value(editor, field_index, '')
            return

        def get_apply_transformation_lambda(languagetools, editor, field_index, original_note_id, original_field_value, interpret_response_fn):
            def apply_transformation(future_result):
                if editor.note == None:
                    # user has left the editor
                    return
                if original_note_id != 0:
                    if editor.note.id != original_note_id:
                        # user switched to a different note, ignore
                        return

                languagetools.anki_utils.hide_loading_indicator(editor, field_index, original_field_value)
                transformation_response = future_result.result()
                try:
                    result_text = interpret_response_fn(transformation_response)
                    self.languagetools.anki_utils.editor_set_field_value(editor, field_index, result_text)
                except errors.LanguageToolsRequestError as e:
                    self.languagetools.anki_utils.critical_message(str(e), None)
            return apply_transformation

        self.languagetools.anki_utils.show_loading_indicator(editor, field_index)

        self.languagetools.anki_utils.run_in_background(request_transformation_fn, 
                                        get_apply_transformation_lambda(self.languagetools, editor, field_index, original_note_id, field_value, interpret_response_fn))


    def load_translation(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, translation_option):
        def get_request_translation_lambda(languagetools, field_value, translation_option):
            def request_translation():
                return languagetools.get_translation_async(field_value, translation_option)
            return request_translation
        interpret_response_fn = self.languagetools.interpret_translation_response_async

        self.load_transformation(editor, 
                                 original_note_id, 
                                 field_value, 
                                 to_deck_note_type_field, 
                                 get_request_translation_lambda(self.languagetools, field_value, translation_option), interpret_response_fn)


    def load_transliteration(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, transliteration_option):
        def get_request_transliteration_lambda(languagetools, field_value, transliteration_option):
            def request_transliteration():
                return languagetools.get_transliteration_async(field_value, transliteration_option)
            return request_transliteration
        interpret_response_fn = self.languagetools.interpret_transliteration_response_async

        self.load_transformation(editor, 
                                 original_note_id, 
                                 field_value, 
                                 to_deck_note_type_field, 
                                 get_request_transliteration_lambda(self.languagetools, field_value, transliteration_option), interpret_response_fn)


    def load_audio(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, voice):
        def get_request_audio_lambda(languagetools, field_value, voice):
            def request_audio():
                try:
                    return languagetools.generate_audio_tag_collection(field_value, voice)
                except errors.LanguageToolsRequestError as err:
                    return {'error': str(err)}
            return request_audio

        def interpret_response_fn(response):
            if 'error' in response:
                # just re-raise
                raise errors.LanguageToolsRequestError('Could not generate audio: ' + response['error'])
            sound_tag = response['sound_tag']
            full_filename = response['full_filename']
            if sound_tag == None:
                return ''
            # sound is valid, play sound
            self.languagetools.anki_utils.play_sound(full_filename)
            return sound_tag

        self.load_transformation(editor, 
                                 original_note_id, 
                                 field_value, 
                                 to_deck_note_type_field, 
                                 get_request_audio_lambda(self.languagetools, field_value, voice), interpret_response_fn)
