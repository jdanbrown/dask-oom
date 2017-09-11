import itertools
import os
import sys

import dask.array as da
import distributed
import numpy as np

from util import human_size, timed_print


def da_chunk_shapes(x):
    return list(itertools.product(*x.chunks))


def da_chunk_bytes(x):
    shapes = list(itertools.product(*x.chunks))
    nbytes = [x.dtype.itemsize * np.prod(shape) for shape in shapes]
    return nbytes


dask_client = distributed.Client(os.environ['DASK_SCHEDULER_URL'])

# Parse params from cli; fail fast if any are missing
exec('; '.join(sys.argv[1:]))
print('Using params: sqrt_n=%s' % sqrt_n)

# rechunk (n, sqrt(n)) -> (sqrt(n), n)
n = sqrt_n ** 2
x = da.random.random((n, n), chunks=(n, int(np.sqrt(n))))
y = x.rechunk((int(np.sqrt(n)), n))
print()
for z in [x, y]:
    print('%-13s %s' % ('da_shape', z.shape))
    print('%-13s %s' % ('da_bytes', human_size(sum(da_chunk_bytes(z)))))
    print('%-13s %s * %s' % ('chunk_shape', set(da_chunk_shapes(z)), len(da_chunk_shapes(z))))
    print('%-13s %s * %s' % ('chunk_bytes', {human_size(x) for x in da_chunk_bytes(z)}, len(da_chunk_bytes(z))))
    print()
timed_print(lambda: print(y.sum().compute() / .5 * 8))
