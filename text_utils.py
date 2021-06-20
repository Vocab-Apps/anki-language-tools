import sys
import anki.utils
import re

if hasattr(sys, '_pytest_mode'):
    import constants
else:
    from . import constants

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
            replace_transformation_type = replace.get(transformation_type.name, False)
            if replace_transformation_type == True:
                result = re.sub(replace['pattern'], replace['replace'], result)

        return result