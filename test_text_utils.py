import text_utils

def test_is_empty(qtbot):
    utils = text_utils.TextUtils()

    assert utils.is_empty('yo') == False
    assert utils.is_empty('') == True
    assert utils.is_empty(' ') == True
    assert utils.is_empty('&nbsp;') == True
    assert utils.is_empty('&nbsp; ') == True
    assert utils.is_empty(' &nbsp; ') == True
    assert utils.is_empty('<br>') == True
    assert utils.is_empty('<div>\n</div>') == True

def test_process(qtbot):
    utils = text_utils.TextUtils()

    assert utils.process('<b>hello</b> world') == 'hello world'
    assert utils.process('<span style="color: var(--field-fg); background: var(--field-bg);">&nbsp;gerund</span>') == 'gerund'