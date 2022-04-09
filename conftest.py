import sys
import logging
import anki.lang

def pytest_configure(config):
    sys._pytest_mode = True
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', 
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging.DEBUG)    
    # required to access some anki functions such as anki.utils.html_to_text_line
    anki.lang.set_lang('en_US')                        

def pytest_unconfigure(config):
    del sys._pytest_mode