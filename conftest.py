import sys

def pytest_configure(config):
    sys._pytest_mode = True

def pytest_unconfigure(config):
    del sys._pytest_mode