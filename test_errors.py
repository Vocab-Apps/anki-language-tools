import unittest
import pytest
import pprint
import logging
import PyQt5

import errors
import deck_utils

def test_exceptions(qtbot):
    try:
        raise errors.LanguageToolsValidationFieldEmpty()
    except Exception as e:
        error_message = str(e)
        assert error_message == 'Field is empty'

    # FieldNotFoundError

    try:
        dnt = deck_utils.DeckNoteType(1, 'Deck', 1, 'NoteType')
        dntf = deck_utils.DeckNoteTypeField(dnt, 'field1')
        raise errors.FieldNotFoundError(dntf)
    except Exception as e:
        error_message = str(e)
        assert error_message == 'Field not found: NoteType / Deck / field1'