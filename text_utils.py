import anki.utils
import constants
import re

class TextUtils():
    def __init__(self, options):
        self.options = options
        self.replacements = self.options.get('replacements', [])

    def is_empty(self, text):
        stripped_field_value = anki.utils.htmlToTextLine(text)
        return len(stripped_field_value) == 0

    def process(self, text, transformation_type: constants.TransformationType):
        result = anki.utils.htmlToTextLine(text)

        # apply replacements
        for replace in self.replacements:
            if replace[transformation_type.name] == True:
                result = re.sub(replace['pattern'], replace['replace'], result)

        return result