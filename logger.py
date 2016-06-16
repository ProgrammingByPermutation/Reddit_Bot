import sys


def log(*args, **params):
    """
    Prints to the log.
    :param args: The arguments.
    :param params: The parameters.
    """
    print(*args, **params)
    sys.stdout.flush()
