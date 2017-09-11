import os
import sys

import dask.bag
import dask.sizeof as ds
from dask import delayed
import distributed
import numpy as np
import pandas as pd

from util import human_size, timed_print

dask_client = distributed.Client(os.environ['DASK_SCHEDULER_URL'])

# Parse params from cli; fail fast if any are missing
exec('; '.join(sys.argv[1:]))
print('Using params: nparts=%s' % nparts)

# Synthesize a bag of random np.array's
approx_part_bytes = 12 * 1024**2
approx_bytes_per_list_element = 40
part_length = approx_part_bytes // approx_bytes_per_list_element
max_int = 1024**2
xs = dask.bag.from_delayed([
    delayed(lambda: list(np.random.randint(0, max_int, part_length)))()
    for _ in range(nparts)
])
ys = (
    xs.groupby(lambda x: x % xs.npartitions, method='tasks')
    .map_partitions(lambda kvs: [v for k, vs in kvs for v in vs])
)
print()
for zs in [xs, ys]:
    part_bytes = timed_print(lambda: pd.Series(zs.map_partitions(lambda part: ds.sizeof(part)).compute()))
    print('%-13s %s' % ('part_bytes', part_bytes.map(human_size).value_counts().to_dict()))
    print('%-13s %s' % ('bag_bytes', human_size(part_bytes.sum())))
    print()
