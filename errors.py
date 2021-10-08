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
        message = f'Field not found: {dntf}'
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
    def __init__(self, error_manager):
        self.error_manager = error_manager

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value != None:
            if isinstance(exception_value, LanguageToolsError):
                self.error_manager.report_single_exception(exception_value)
            else:
                self.error_manager.report_unknown_exception_interactive(exception_value)
            return True
        return False

class BatchActionContext():
    def __init__(self, batch_error_manager):
        self.batch_error_manager = batch_error_manager

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value != None:
            if isinstance(exception_value, LanguageToolsError):
                self.batch_error_manager.report_batch_exception(exception_value)
            else:
                self.batch_error_manager.report_unknown_exception(exception_value)
            return True
        return False

class BatchErrorManager():
    def __init__(self, error_manager):
        self.error_manager = error_manager
        self.exception_count = {}

    def get_batch_action_context(self):
        return BatchActionContext(self)

    def report_batch_exception(self, exception):
        count = self.exception_count.get(str(exception), 0)
        self.exception_count[str(exception)] = count + 1

    def report_unknown_exception(self, exception):
        error_name = f'Unknown Error: {str(exception)}'
        count = self.exception_count.get(error_name, 0)
        self.exception_count[error_name] = count + 1
        self.error_manager.report_unknown_exception_batch(exception)

    def get_exception_count(self):
        return self.exception_count

class ErrorManager():
    def __init__(self, anki_utils):
        self.anki_utils = anki_utils
        self.batch_mode = False
        self.last_exception = None

    def report_single_exception(self, exception):
        self.anki_utils.critical_message(str(exception), None)

    def report_unknown_exception_interactive(self, exception):
        self.anki_utils.critical_message('An unknown error has occured: ' + str(exception), None)

    def report_unknown_exception_batch(self, exception):
        pass

    def get_single_action_context(self):
        return SingleActionContext(self)

    def get_batch_error_manager(self):
        return BatchErrorManager(self)
