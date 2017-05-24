from random import choice
from string import ascii_lowercase


def get_random_id(prefix="", length=10):
    """ Generates random identifier name with given prefix and length
    """
    return prefix + ''.join(choice(ascii_lowercase) for _ in range(length))
