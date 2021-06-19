import anki.utils

class TextUtils():
    def __init__(self):
        pass

    def is_empty(self, text):
        stripped_field_value = anki.utils.htmlToTextLine(text)
        return len(stripped_field_value) == 0

    def process(self, text):
        result = anki.utils.htmlToTextLine(text)
        return result