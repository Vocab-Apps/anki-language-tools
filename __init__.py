# python imports
from typing import List

# anki imports
import aqt
import aqt.qt
import aqt.utils

from . import languagetools
from . import gui

languagetools = languagetools.LanguageTools()
gui.init(languagetools)
