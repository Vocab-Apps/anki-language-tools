import sys
import logging
import anki.utils
import re

if hasattr(sys, '_pytest_mode'):
    import constants
else:
    from . import constants

class TextReplacement():
    def __init__(self, options):
        self.pattern = options.get('pattern', None)
        self.replace = options.get('replace', None)
        self.transformation_type_map = {}
        for transformation_type in constants.TransformationType:
            self.transformation_type_map[transformation_type] = options.get(transformation_type.name, True)

    def to_dict(self):
        transformation_type_map = {key.name:value for (key, value) in self.transformation_type_map.items()}
        data = {
            'pattern': self.pattern,
            'replace': self.replace,
        }
        data.update(transformation_type_map)
        return data

    def process(self, text, transformation_type):
        result = text
        if self.transformation_type_map[transformation_type]:
            if self.pattern != None and self.replace != None:
                try:
                    result = re.sub(self.pattern, self.replace, text)
                except Exception as e:
                    logging.error(f'error while processing regular expression {self.pattern} / {self.replace}: {e}')
        return result

class TextUtils():
    def __init__(self, options):
        self.options = options
        replacements_array = self.options.get('replacements', [])
        self.replacements = [TextReplacement(replacement) for replacement in replacements_array]

    def is_empty(self, text):
        stripped_field_value = anki.utils.htmlToTextLine(text)
        return len(stripped_field_value) == 0

    def process(self, text, transformation_type: constants.TransformationType):
        result = anki.utils.htmlToTextLine(text)

        # apply replacements
        for replacement in self.replacements:
            result = replacement.process(result, transformation_type)

        return result