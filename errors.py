import sys
import logging
if hasattr(sys, '_pytest_mode'):
    import constants
else:
    from . import constants

# all exceptions inherit from this one
class LanguageToolsError(Exception):
    pass

# when something we expected to find is not found, like a deck, model, or field
# can happen when language mapping is not updated to reflect note type changes
class AnkiItemNotFoundError(LanguageToolsError):
    pass

class AnkiNoteEditorError(LanguageToolsError):
    pass

class LanguageMappingError(LanguageToolsError):
    pass

class FieldNotFoundError(AnkiItemNotFoundError):
    def __init__(self, dntf):
        message = f'Field not found: <b>{dntf}</b>. {constants.DOCUMENTATION_EDIT_RULES}'
        super().__init__(message)    

class FieldLanguageMappingError(LanguageMappingError):
    def __init__(self, dntf):
        message = f'No language set for {dntf}. {constants.DOCUMENTATION_PERFORM_LANGUAGE_MAPPING}'
        super().__init__(message)


class LanguageToolsValidationFieldEmpty(LanguageToolsError):
    def __init__(self):
        message = f'Field is empty'
        super().__init__(message)    

class LanguageToolsRequestError(LanguageToolsError):
    pass

class AudioLanguageToolsRequestError(LanguageToolsRequestError):
    pass

class VoiceListRequestError(LanguageToolsRequestError):
    pass


# these ActionContext objects implement the "with " interface and help catch exceptions

class SingleActionContext():
    def __init__(self, error_manager, action):
        self.error_manager = error_manager
        self.action = action

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value != None:
            if isinstance(exception_value, LanguageToolsError):
                self.error_manager.report_single_exception(exception_value, self.action)
            else:
                self.error_manager.report_unknown_exception_interactive(exception_value, self.action)
            return True
        return False

class BatchActionContext():
    def __init__(self, batch_error_manager, action):
        self.batch_error_manager = batch_error_manager
        self.action = action

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value != None:
            if isinstance(exception_value, LanguageToolsError):
                self.batch_error_manager.report_batch_exception(exception_value, self.action)
            else:
                self.batch_error_manager.report_unknown_exception(exception_value, self.action)
            return True
        # no error, report success
        self.batch_error_manager.report_success(self.action)
        return False

class BatchErrorManager():
    def __init__(self, error_manager, batch_action):
        self.error_manager = error_manager
        self.batch_action = batch_action
        self.action_stats = {}

    def get_batch_action_context(self, action):
        return BatchActionContext(self, action)

    def init_action(self, action):
        if action not in self.action_stats:
            self.action_stats[action] = {
                'success': 0,
                'error': {}
            }

    def report_success(self, action):
        self.init_action(action)
        self.action_stats[action]['success'] = self.action_stats[action]['success'] + 1

    def track_error_stats(self, error_key, action):
        self.init_action(action)
        error_count = self.action_stats[action]['error'].get(error_key, 0)
        self.action_stats[action]['error'][error_key] = error_count + 1

    def report_batch_exception(self, exception, action):
        self.track_error_stats(str(exception), action)

    def report_unknown_exception(self, exception, action):
        error_key = f'Unknown Error: {str(exception)}'
        self.track_error_stats(error_key, action)
        self.error_manager.report_unknown_exception_batch(exception)


class ErrorManager():
    def __init__(self, anki_utils):
        self.anki_utils = anki_utils

    def report_single_exception(self, exception, action):
        self.anki_utils.report_known_exception_interactive(exception, action)

    def report_unknown_exception_interactive(self, exception, action):
        self.anki_utils.report_unknown_exception_interactive(exception, action)

    def report_unknown_exception_batch(self, exception):
        self.anki_utils.report_unknown_exception_background(exception)

    def get_single_action_context(self, action):
        return SingleActionContext(self, action)

    def get_batch_error_manager(self, batch_action):
        return BatchErrorManager(self, batch_action)
