# Purpose
- Repro for https://github.com/dask/dask/issues/2456
- Investigate why a simple shuffle OOMs when total data exceeds total worker ram

# Experimental setup
- Use local docker containers to make a reproducible and portable distributed environment
- Worker setup (defined in docker-compose.yml):
  - 4 workers @ 1g mem + no swap (4g total worker ram)
  - Default `--memory-limit` (each worker reports 0.584g)
  - Limited to 1 concurrent task per worker, to minimize mem contention and oom risk
- For each of ddf, dask array, and dask bag:
  - Run a simple shuffle operation and test whether the operation succeeds or OOMs
  - Test against increasing data volumes, from much smaller than total worker ram to larger than total worker ram
  - Try to keep partition sizes below ~10-15m, to control for oom risk from large partitions

# Results

### oom_ddf.py
- https://github.com/jdanbrown/dask-oom/blob/master/oom_ddf.py

| params | ddf_bytes | part_bytes | runtime | success/OOM?
|---|---|---|---|---
| `cols=10 part_rows=157500 nparts=64`  | .75g | 12m | 00:08  | success
| `cols=10 part_rows=157500 nparts=128` | 1.5g | 12m | ~00:20 | usually&nbsp;OOM, sometimes&nbsp;success
| `cols=10 part_rows=157500 nparts=256` | 3g   | 12m | ~00:20 | OOM
| `cols=10 part_rows=157500 nparts=512` | 6g   | 12m | ~00:30 | OOM

### oom_array.py
- https://github.com/jdanbrown/dask-oom/blob/master/oom_array.py

| params | da_bytes | chunk_bytes | chunk_n | chunk_shape | runtime | success/OOM?
|---|---|---|---|---|---|---
| `sqrt_n=64`  | 128m | 2m   | 64  | (4096, 64)   | 00:01  | success
| `sqrt_n=96`  | 648m | 6.8m | 96  | (9216, 96)   | 00:03  | success
| `sqrt_n=112` | 1.2g | 11m  | 112 | (12544, 112) | 00:05  | success
| `sqrt_n=120` | 1.5g | 13m  | 120 | (14400, 120) | ~00:15 | usually&nbsp;OOM, rare&nbsp;success
| `sqrt_n=128` | 2g   | 16m  | 128 | (16384, 128) | ~00:10 | OOM

### oom_bag.py
- https://github.com/jdanbrown/dask-oom/blob/master/oom_bag.py
- Much slower than ddf and array, since bag operations are bottlenecked by more python execution

| params | bag_bytes | part_bytes | runtime | success/OOM?
|---|---|---|---|---
| `nparts=2`   | 25m  | 12m | 00:00:08 | success
| `nparts=4`   | 49m  | 12m | 00:00:14 | success
| `nparts=8`   | 98m  | 12m | 00:00:24 | success
| `nparts=32`  | 394m | 12m | 00:01:53 | success
| `nparts=64`  | 787m | 12m | 00:07:46 | success
| `nparts=128` | 1.5g | 12m | 00:17:40 | success
| `nparts=256` | 3.1g | 12m | 00:37:09 | success
| `nparts=512` | 6.2g | 12m | 01:16:30 | OOM (first OOM ~57:00, then ~4 more OOMs before client saw `KilledWorker`)

# Install + run

### Install
```sh
# Setup conda/pip env
conda create -y --name dask-oom --file conda-requirements.txt
source activate dask-oom
pip install -r requirements.txt

# Build docker image named dask-oom-local, for docker-compose.yml
# - Need to rebuild if you change *requirements.txt
# - Don't need to rebuilt if you only change *.py
docker build . -t dask-oom-local
```

### Run
```sh
# Launch 4 workers + 1 scheduler defined in docker-compose.yml
docker-compose up -t0 -d --scale={worker=4,scheduler=1}

# Run each repro
DASK_SCHEDULER_URL=localhost:8786 python oom_ddf.py cols=... part_rows=... nparts=...
DASK_SCHEDULER_URL=localhost:8786 python oom_array.py sqrt_n=...
DASK_SCHEDULER_URL=localhost:8786 python oom_bag.py nparts=...
```

### Misc. useful commands
```sh
# Restart workers, leave scheduler as is
docker-compose up -t0 -d --scale={worker=0,scheduler=1} && docker-compose up -t0 -d --scale={worker=4,scheduler=1}

# Restart workers + scheduler, in case scheduler state gets dirty
docker-compose up -t0 -d --scale={worker=0,scheduler=0} && docker-compose up -t0 -d --scale={worker=4,scheduler=1}

# Tail logs of containers launched from docker-compose.yml
docker-compose logs -f

# top for containers, to monitor resource usage
ctop

# List/kill running docker containers
docker ps
docker kill ...
```
