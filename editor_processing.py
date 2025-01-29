import logging
import sys

if hasattr(sys, '_pytest_mode'):
    import constants
    import errors
    import dialog_choosetranslation
    import dialog_breakdown
    import deck_utils
else:
    from . import constants
    from . import errors
    from . import dialog_choosetranslation
    from . import dialog_breakdown
    from . import deck_utils

class FieldChangeTimer():
    def __init__(self, delay_ms):
        self.delay_ms = delay_ms
        self.timer_obj = None

class FieldChange():
    def __init__(self, editor, deck_note_type, from_deck_note_type_field, note_id, field_value):
        self.editor = editor
        self.deck_note_type = deck_note_type
        self.from_deck_note_type_field = from_deck_note_type_field
        self.note_id = note_id
        self.field_value = field_value

class EditorManager():
    def __init__(self, languagetools):
        self.languagetools = languagetools
        self.buffered_field_changes = {}
        self.apply_updates = languagetools.config.get(constants.CONFIG_APPLY_UPDATES_AUTOMATICALLY, True)
        self.update_field_change_timer(languagetools.get_live_update_delay())

    def update_field_change_timer(self, delay_ms):
        self.field_change_timer = FieldChangeTimer(delay_ms)

    def run_choose_translation(self, editor, field_name):
        with self.languagetools.error_manager.get_single_action_context(f'choosing translation'):
            note = editor.note
            current_translation_text = note[field_name]

            deck_note_type = self.languagetools.deck_utils.build_deck_note_type_from_editor(editor)

            target_dntf = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, field_name)
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

            def get_done_callback(from_text, from_language, to_language, editor, field_name):
                def load_translation_all_done(fut):
                    with self.languagetools.error_manager.get_single_action_context(f'retrieving all translations'):
                        self.languagetools.anki_utils.stop_progress_bar()
                        data = fut.result()
                        # logging.debug(f'all translations: {data}')
                        dialog = dialog_choosetranslation.prepare_dialog(self.languagetools, from_text, from_language, to_language, data)
                        retval = self.languagetools.anki_utils.display_dialog(dialog)
                        if retval == True:
                            chosen_translation = dialog.selected_translation
                            #logging.debug(f'chosen translation: {chosen_translation}')
                            self.languagetools.anki_utils.editor_note_set_field_value(editor, field_name, chosen_translation)

                return load_translation_all_done

            self.languagetools.anki_utils.show_progress_bar("retrieving all translations")
            self.languagetools.anki_utils.run_in_background(load_translation_all, get_done_callback(from_text, from_language, to_language, editor, field_name))

    def run_speak(self, editor, field_name):
        with self.languagetools.error_manager.get_single_action_context(f'speaking audio'):
            deck_note_type = self.languagetools.deck_utils.build_deck_note_type_from_editor(editor)
            dntf = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, field_name)
            source_text = editor.note[field_name]

            # do we have a voice set ?
            field_language = self.languagetools.get_language(dntf)
            if field_language == None:
                raise errors.AnkiNoteEditorError(f'No language set for field {dntf}')
            voice_selection_settings = self.languagetools.get_voice_selection_settings()
            if field_language not in voice_selection_settings:
                raise errors.AnkiNoteEditorError(f'No voice set for language {self.languagetools.get_language_name(field_language)}')
            voice = voice_selection_settings[field_language]

            def play_audio(languagetools, source_text, voice):
                voice_key = voice['voice_key']
                service = voice['service']
                language_code = voice['language_code']

                filename = languagetools.get_tts_audio(source_text, service, language_code, voice_key, {})
                self.languagetools.anki_utils.play_sound(filename)

            def play_audio_done(future_result):
                with self.languagetools.error_manager.get_single_action_context(f'loading audio'):
                    data = future_result.result()

            #aqt.mw.taskman.run_in_background(lambda: play_audio(languagetools, source_text, voice), lambda x: play_audio_done(x))            
            self.languagetools.anki_utils.run_in_background(lambda: play_audio(self.languagetools, source_text, voice), lambda x: play_audio_done(x))

    def run_breakdown(self, editor, field_name):
        with self.languagetools.error_manager.get_single_action_context(f'preparing breakdown dialog'):
            deck_note_type = self.languagetools.deck_utils.build_deck_note_type_from_editor(editor)
            deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, field_name)
            field_value = editor.note[field_name]
            logging.info(f'got breakdown on field {deck_note_type_field} value: {field_value}')
            field_language = self.languagetools.get_language_validate(deck_note_type_field)

            dialog = dialog_breakdown.prepare_dialog(self.languagetools, field_value, field_language, editor, deck_note_type_field.deck_note_type)
            dialog.exec()

    def process_all_field_changes(self):
        logging.info('processing all field changes')
        for dntf, field_change in self.buffered_field_changes.items():
            with self.languagetools.error_manager.get_single_action_context(f'processing live updates for {dntf}'):
                logging.info(f'processing field change on {dntf}')
                self.process_field_change(field_change)
        self.buffered_field_changes = {}

    def process_field_change(self, field_change):
        deck_note_type = field_change.deck_note_type
        editor = field_change.editor
        from_deck_note_type_field = field_change.from_deck_note_type_field
        note_id = field_change.note_id
        field_value = field_change.field_value

        # do we have translation rules for this deck_note_type
        translation_settings = self.languagetools.get_batch_translation_settings(deck_note_type)
        relevant_settings = {to_field:value for (to_field,value) in translation_settings.items() if value['from_field'] == from_deck_note_type_field.field_name}
        for to_field, value in relevant_settings.items():
            with self.languagetools.error_manager.get_single_action_context(f'adding translation to field {to_field}'):
                to_deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, to_field)
                self.load_translation(editor, note_id, field_value, to_deck_note_type_field, value['translation_option'])

        # do we have transliteration rules for this deck_note_type
        transliteration_settings = self.languagetools.get_batch_transliteration_settings(deck_note_type)
        relevant_settings = {to_field:value for (to_field,value) in transliteration_settings.items() if value['from_field'] == from_deck_note_type_field.field_name}
        for to_field, value in relevant_settings.items():
            with self.languagetools.error_manager.get_single_action_context(f'adding transliteration to field {to_field}'):
                to_deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, to_field)
                self.load_transliteration(editor, note_id, field_value, to_deck_note_type_field, value['transliteration_option'])


        # do we have any audio rules for this deck_note_type
        audio_settings = self.languagetools.get_batch_audio_settings(deck_note_type)
        relevant_settings = {to_field:from_field for (to_field,from_field) in audio_settings.items() if from_field == from_deck_note_type_field.field_name}
        for to_field, from_field in relevant_settings.items():
            with self.languagetools.error_manager.get_single_action_context(f'adding audio to field {to_field}'):
                to_deck_note_type_field = self.languagetools.deck_utils.build_dntf_from_dnt(deck_note_type, to_field)
                # get the from language
                from_language = self.languagetools.get_language(from_deck_note_type_field)
                if from_language != None:
                    # get voice for this language
                    voice_settings = self.languagetools.get_voice_selection_settings()
                    logging.debug(f'voice_settings: {voice_settings}')
                    logging.debug(f'from_language: {from_language}')
                    if from_language in voice_settings:
                        voice = voice_settings[from_language]
                        self.load_audio(editor, note_id, field_value, to_deck_note_type_field, voice)        

    def toggle_live_updates(self):
        new_value = not self.apply_updates
        self.set_live_updates(new_value)

    def set_live_updates(self, enabled):
        self.apply_updates = enabled
        logging.info(f'live updates enabled: {self.apply_updates}')
        self.languagetools.set_apply_updates_automatically(enabled)
        self.languagetools.anki_utils.tooltip_message(f'Live updates enabled: {enabled}')

    def set_typing_delay(self, delay_ms):
        self.update_field_change_timer(delay_ms)
        self.languagetools.set_live_update_delay(delay_ms)
        logging.info(f'set typing delay to {delay_ms}')

    def process_command(self, editor, str):
        components = str.split(':')
        if components[1] == 'liveupdates':
            enabled_str = components[2]
            if enabled_str == 'true':
                self.set_live_updates(True)
            else:
                self.set_live_updates(False)

        if components[1] == constants.COMMAND_FULLUPDATE:
            self.full_update(editor)

        if components[1] == 'typingdelay':
            typing_delay_ms = int(components[2])
            self.set_typing_delay(typing_delay_ms)

        if components[1] == 'breakdown':
            self.process_breakdown(editor, str)

    def full_update(self, editor):
        logging.info('full_update')
        # iterate over available field in the note
        # editor.note
        note_id = 0
        deck_note_type = self.languagetools.deck_utils.build_deck_note_type_from_editor(editor)
        field_list = list(editor.note.keys())
        for field_name in field_list:
            deck_note_type_field = deck_utils.DeckNoteTypeField(deck_note_type, field_name)
            field_change = FieldChange(editor, deck_note_type, deck_note_type_field, note_id, editor.note[field_name])
            self.buffered_field_changes[deck_note_type_field] = field_change
        # run immediately
        self.process_all_field_changes()            


    def process_forced_field_update(self, editor, str):
        # user is asking for fields to be regenerated

        components = str.split(':')
        field_index = int(components[2])
        field_value = ':'.join(components[3:])

        note_id = 0

        from_deck_note_type_field = from_deck_note_type_field = self.languagetools.deck_utils.editor_get_dntf(editor, field_index)
        deck_note_type = from_deck_note_type_field.deck_note_type

        field_change = FieldChange(editor, deck_note_type, from_deck_note_type_field, note_id, field_value)
        self.buffered_field_changes[from_deck_note_type_field] = field_change
        # run immediately
        self.process_all_field_changes()


    def process_field_update(self, editor, str):
        if not self.apply_updates:
            logging.info(f'live updates not enabled, skipping field update')
            return

        try:
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

                logging.debug(f'new field value: [{field_value}] original field value: [{original_field_value}]')

                if field_value != original_field_value:
                    # only do something if the field has changed

                    field_change = FieldChange(editor, deck_note_type, from_deck_note_type_field, note_id, field_value)
                    self.buffered_field_changes[from_deck_note_type_field] = field_change
                    self.languagetools.anki_utils.call_on_timer_expire(self.field_change_timer, self.process_all_field_changes)
        except:
            logging.exception(f'could not process field update [{str}]')


    # generic function to load a transformation asynchronously (translation / transliteration / audio)
    def load_transformation(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, 
        request_transformation_fn, interpret_response_fn, transformation_type):
        # field_index = self.languagetools.deck_utils.get_field_id(to_deck_note_type_field)

        # is the source field empty ?
        if self.languagetools.text_utils.is_empty(field_value):
            self.languagetools.anki_utils.editor_note_set_field_value(editor, to_deck_note_type_field.field_name, '')
            return

        def get_apply_transformation_lambda(languagetools, editor, original_note_id, original_field_value, 
            interpret_response_fn, transformation_type, to_deck_note_type_field):
            def apply_transformation(future_result):
                with self.languagetools.error_manager.get_single_action_context(f'loading {transformation_type.name.lower()} for field {to_deck_note_type_field}'):
                    if editor.note == None:
                        # user has left the editor
                        return
                    if original_note_id != 0:
                        if editor.note.id != original_note_id:
                            # user switched to a different note, ignore
                            return

                    # languagetools.anki_utils.hide_loading_indicator(editor, field_index, original_field_value)
                    languagetools.anki_utils.hide_loading_indicator_field(editor, to_deck_note_type_field.field_name)
                    transformation_response = future_result.result()
                    result_text = interpret_response_fn(transformation_response)
                    logging.debug(f'setting field [{to_deck_note_type_field.field_name}] value: [{result_text}]')
                    self.languagetools.anki_utils.editor_note_set_field_value(editor, to_deck_note_type_field.field_name, result_text)
            return apply_transformation

        # self.languagetools.anki_utils.show_loading_indicator(editor, field_index)
        self.languagetools.anki_utils.show_loading_indicator_field(editor, to_deck_note_type_field.field_name)
        
        self.languagetools.anki_utils.run_in_background(request_transformation_fn, 
            get_apply_transformation_lambda(self.languagetools, editor, original_note_id, field_value, interpret_response_fn, transformation_type, to_deck_note_type_field))


    def load_translation(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, translation_option):
        def get_request_translation_lambda(languagetools, field_value, translation_option):
            def request_translation():
                logging.info('request_translation')
                return languagetools.get_translation_async(field_value, translation_option)
            return request_translation
        interpret_response_fn = self.languagetools.interpret_translation_response_async

        self.load_transformation(editor, 
                                 original_note_id, 
                                 field_value, 
                                 to_deck_note_type_field, 
                                 get_request_translation_lambda(self.languagetools, field_value, translation_option), interpret_response_fn,
                                 constants.TransformationType.Translation)


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
                                 get_request_transliteration_lambda(self.languagetools, field_value, transliteration_option), interpret_response_fn,
                                 constants.TransformationType.Transliteration)


    def load_audio(self, editor, original_note_id, field_value: str, to_deck_note_type_field: deck_utils.DeckNoteTypeField, voice):
        logging.debug('load_audio')
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
            logging.debug(f'load_audio, got response: sound_tag: {sound_tag} full_filename: {full_filename}')
            if sound_tag == None:
                return ''
            # sound is valid, play sound
            self.languagetools.anki_utils.play_sound(full_filename)
            return sound_tag

        self.load_transformation(editor, 
                                 original_note_id, 
                                 field_value, 
                                 to_deck_note_type_field, 
                                 get_request_audio_lambda(self.languagetools, field_value, voice), interpret_response_fn,
                                 constants.TransformationType.Audio)

    def get_play_tag_audio_lambda(self, editor, field_name):
        def play_audio():
            sound_tag = editor.note[field_name]
            self.languagetools.anki_utils.play_anki_sound_tag(sound_tag)
        return play_audio        

    def get_choose_translation_lambda(self, editor, field_name):
        def choose_translation():
            self.run_choose_translation(editor, field_name)
        return choose_translation

    def get_speak_lambda(self, editor, field_name):
        def speak():
            self.run_speak(editor, field_name)
        return speak

    def get_breakdown_lambda(self, editor, field_name):
        def breakdown():
            self.run_breakdown(editor, field_name)
        return breakdown