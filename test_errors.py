import unittest
import pytest
import pprint
import logging
import PyQt5

import dialogs
import errors
import deck_utils
import testing_utils

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

def test_exception_operators(qtbot):
    dnt = deck_utils.DeckNoteType(1, 'Deck', 1, 'NoteType')
    dntf = deck_utils.DeckNoteTypeField(dnt, 'field1')

    exception1 = errors.FieldNotFoundError(dntf)
    exception2 = errors.FieldNotFoundError(dntf)

    assert str(exception1) == str(exception2)


def test_error_manager(qtbot):
    # pytest test_errors.py -s -rPP -k test_error_manager

    config_gen = testing_utils.TestConfigGenerator()
    mock_language_tools = config_gen.build_languagetools_instance('default')
    error_manager = errors.ErrorManager(mock_language_tools.anki_utils)

    dnt = deck_utils.DeckNoteType(1, 'Deck', 1, 'NoteType')
    dntf = deck_utils.DeckNoteTypeField(dnt, 'field1')


    # single actions
    # ==============

    with error_manager.get_single_action_context():
        logging.info('single action 1')
        raise errors.LanguageToolsValidationFieldEmpty()

    assert mock_language_tools.anki_utils.critical_message_received == 'Field is empty'
    mock_language_tools.anki_utils.critical_message_received = None

    with error_manager.get_single_action_context():
        logging.info('single action 2')
        logging.info('successful')

    assert mock_language_tools.anki_utils.critical_message_received == None
    mock_language_tools.anki_utils.critical_message_received = None

    def unhandled_exception():
        with error_manager.get_single_action_context():
            logging.info('single action 3')
            raise Exception('this is unhandled')
    
    testcase_instance = unittest.TestCase()
    testcase_instance.assertRaises(Exception, unhandled_exception)


    # batch actions
    # =============

    batch_error_manager = error_manager.get_batch_error_manager()

    with batch_error_manager.get_batch_action_context():
        logging.info('batch iteration 1')
        raise errors.LanguageToolsValidationFieldEmpty()

    with batch_error_manager.get_batch_action_context():
        logging.info('batch iteration 2')
        logging.info('ok')

    with batch_error_manager.get_batch_action_context():
        logging.info('batch iteration 3')
        raise errors.FieldLanguageMappingError(dntf)

    actual_exception_count = batch_error_manager.get_exception_count()
    expected_exception_count = {
        'Field is empty': 1,
        'No language set for NoteType / Deck / field1. Please setup Language Mappings, from the Anki main screen: <b>Tools -> Language Tools: Language Mapping</b>': 1
    }
    assert actual_exception_count == expected_exception_count

    # batch actions with unhandled exceptions
    # =======================================

    batch_error_manager = error_manager.get_batch_error_manager()

    def run_batch():
        with batch_error_manager.get_batch_action_context():
            logging.info('batch iteration 1')
            logging.info('ok')

        with batch_error_manager.get_batch_action_context():
            logging.info('batch iteration 2')
            raise Exception('this is unhandled')

    testcase_instance = unittest.TestCase()
    testcase_instance.assertRaises(Exception, run_batch)
