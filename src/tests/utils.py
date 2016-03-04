
import hashlib
import random


def get_test_hash_id(name=''):

    rand_int = random.randrange(1000, 9999)

    return '%s-%s' % (name, str(
        hashlib.md5(str(rand_int)).hexdigest())[:5])
