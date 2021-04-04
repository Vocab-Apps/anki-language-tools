# when something we expected to find is not found, like a deck, model, or field
# can happen when language mapping is not updated to reflect note type changes
class AnkiItemNotFoundError(Exception):
    pass

class AnkiNoteEditorError(Exception):
    pass

class LanguageMappingError(Exception):
    pass

class LanguageToolsRequestError(Exception):
    pass

class AudioLanguageToolsRequestError(LanguageToolsRequestError):
    pass


