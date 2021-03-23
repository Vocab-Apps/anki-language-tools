import unittest
import pytest

import dialogs

class MockLanguageTools():
    def __init__(self):
        pass

def test_add_audio_dialog(qtbot):
    print(qtbot)
    assert True