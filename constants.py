import enum

ENV_VAR_ANKI_LANGUAGE_TOOLS_BASE_URL = 'ANKI_LANGUAGE_TOOLS_BASE_URL'
CONFIG_DECK_LANGUAGES = 'deck_languages'
CONFIG_WANTED_LANGUAGES = 'wanted_languages'
CONFIG_INLINE_TRANSLATION = 'inline_translations'
CONFIG_BATCH_TRANSLATION = 'batch_translations'
CONFIG_BATCH_TRANSLITERATION = 'batch_transliterations'
CONFIG_BATCH_AUDIO = 'batch_audio'
CONFIG_VOICE_SELECTION = 'voice_selection'
ADDON_NAME = 'Language Tools'
MENU_PREFIX = ADDON_NAME + ':'
DEFAULT_LANGUAGE = 'en' # always add this language, even if the user didn't add it themselves
EDITOR_WEB_FIELD_ID_TRANSLATION = 'translation'

GREEN_STYLESHEET = 'background-color: #69F0AE;'
RED_STYLESHEET = 'background-color: #FFCDD2;'

class TransformationType(enum.Enum):
    Translation = enum.auto()
    Transliteration = enum.auto()


# these are special languages that we store on a field level, which don't allow translating to/from
class SpecialLanguage(enum.Enum):
    transliteration = enum.auto()
    sound = enum.auto()