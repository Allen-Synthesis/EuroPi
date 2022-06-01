import functools


class PIO:
    OUT_LOW = 0


class StateMachine:
    pass


def asm_pio(**kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pass

        return wrapper

    return decorator
