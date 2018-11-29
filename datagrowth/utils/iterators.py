import math
from itertools import islice


def ibatch(iterable, batch_size):  # TODO: test to unlock
    it = iter(iterable)
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            return
        yield batch


def batchize(elements, batch_size):  # TODO: test to unlock
    batches = int(math.floor(elements / batch_size))
    rest = elements % batch_size
    if rest:
        batches += 1
    return batches, rest
