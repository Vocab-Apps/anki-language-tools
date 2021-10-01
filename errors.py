import sys
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


