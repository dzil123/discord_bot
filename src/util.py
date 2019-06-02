import random
import string

charset = string.ascii_uppercase + string.digits


def random_string(length: int):
    return "".join(random.choice(charset) for x in range(length))
