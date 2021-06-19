import text_utils
import constants

def test_is_empty(qtbot):
    utils = text_utils.TextUtils({})

    assert utils.is_empty('yo') == False
    assert utils.is_empty('') == True
    assert utils.is_empty(' ') == True
    assert utils.is_empty('&nbsp;') == True
    assert utils.is_empty('&nbsp; ') == True
    assert utils.is_empty(' &nbsp; ') == True
    assert utils.is_empty('<br>') == True
    assert utils.is_empty('<div>\n</div>') == True

def test_process(qtbot):
    utils = text_utils.TextUtils({})

    assert utils.process('<b>hello</b> world', constants.TransformationType.Audio) == 'hello world'
    assert utils.process('<span style="color: var(--field-fg); background: var(--field-bg);">&nbsp;gerund</span>', constants.TransformationType.Audio) == 'gerund'

def test_replace(qtbot):
    utils = text_utils.TextUtils({'replacements': [
        {'pattern': ' / ', 
        'replace': ' ',
        'Audio': True,
        'Translation': False,
        'Transliteration': False},
        {'pattern': r'\(etw \+D\)', 
        'replace': 'etwas +Dativ',
        'Audio': True,
        'Translation': False,
        'Transliteration': False},        
    ]})

    assert utils.process('word1 / word2', constants.TransformationType.Audio) == 'word1 word2'
    assert utils.process('word1 / word2', constants.TransformationType.Translation) == 'word1 / word2'
    assert utils.process('word1 / word2', constants.TransformationType.Transliteration) == 'word1 / word2'
    assert utils.process('<b>word1</b> / word2', constants.TransformationType.Audio) == 'word1 word2'
    assert utils.process('unter (etw +D)', constants.TransformationType.Audio) == 'unter etwas +Dativ'
    assert utils.process('<b>unter</b> (etw +D)', constants.TransformationType.Audio) == 'unter etwas +Dativ'
    assert utils.process('<b>unter</b> (etw +D)', constants.TransformationType.Transliteration) == 'unter (etw +D)'
