import os
import sys

import dask.dataframe as dd
import dask.sizeof as ds
from dask import delayed
import distributed
import numpy as np
import pandas as pd

from util import timed_print

dask_client = distributed.Client(os.environ['DASK_SCHEDULER_URL'])

# Parse params from cli; fail fast if any are missing
exec('; '.join(sys.argv[1:]))
print('Using params: cols=%s; part_rows=%s; nparts=%s' % (cols, part_rows, nparts))

# Synthesize a ddf of random ints
max_int = 1024**2
ddf = dd.from_delayed(meta={col: 'int64' for col in range(cols)}, dfs=[
    delayed(lambda: pd.DataFrame({
        col: np.random.randint(0, max_int, part_rows)
        for col in range(cols)
    }))()
    for _ in range(nparts)
])

# Compute a shuffle on a column of random ints
#   - Specify divisions so (a) we only compute once and (b) we ensure balanced tasks
divisions = {
    n: list(range(0, max_int, max_int // n)) + [max_int]
    for n in [2**i for i in range(13)]
}
ddf_indexed = ddf.set_index(0, divisions=divisions[nparts])
timed_print(lambda: print(ddf.map_partitions(lambda df: ds.sizeof(df)).compute().sum() / 1024**2))
timed_print(lambda: print(len(ddf_indexed)))
