from . import languagetools
from . import gui
from . import editor

languagetools = languagetools.LanguageTools()
gui.init(languagetools)
editor.init(languagetools)
