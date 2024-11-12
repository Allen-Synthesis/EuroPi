import sys


def is_test_env():
    """
    Are we in a test environment?

    If the implementation name is "micropython" it means we have access to real hardware
    """
    return sys.implementation.name != "micropython"
