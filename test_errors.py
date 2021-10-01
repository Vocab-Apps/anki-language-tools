import unittest
import pytest
import pprint
import logging
import PyQt5

import errors

def test_exceptions(qtbot):
    try:
        raise errors.LanguageToolsValidationFieldEmpty()
    except Exception as e:
        error_message = str(e)
        assert error_message == 'Field is empty'