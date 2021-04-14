import sys
if hasattr(sys, '_pytest_mode'):
    import constants
else:
    from . import constants

# when something we expected to find is not found, like a deck, model, or field
# can happen when language mapping is not updated to reflect note type changes
class AnkiItemNotFoundError(Exception):
    pass

class AnkiNoteEditorError(Exception):
    pass

class LanguageMappingError(Exception):
    pass

class FieldLanguageMappingError(LanguageMappingError):
    def __init__(self, dntf):
        message = f'No language set for {dntf}. {constants.DOCUMENTATION_PERFORM_LANGUAGE_MAPPING}'
        super().__init__(message)

class LanguageToolsRequestError(Exception):
    pass

class AudioLanguageToolsRequestError(LanguageToolsRequestError):
    pass


