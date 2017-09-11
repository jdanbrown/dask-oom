import time
import traceback

import humanize


def human_size(x):
    return humanize.naturalsize(x, binary=True)


def timed_print(f, **kwargs):
    elapsed, x = timed_format(f, **kwargs)
    print(elapsed)
    return x


def timed_format(f, **kwargs):
    elapsed_s, x = timed(f, **kwargs)
    elapsed = '[%s]' % format_duration(elapsed_s)
    return elapsed, x


def timed(f, if_error_return='exception'):
    start_s = time.time()
    try:
        x = f()
    except Exception as e:
        traceback.print_exc()
        x = e if if_error_return == 'exception' else if_error_return
    elapsed_s = time.time() - start_s
    return elapsed_s, x


def format_duration(secs):
    if secs < 0:
        return '-' + format_duration(-secs)
    else:
        s = int(secs) % 60
        m = int(secs) // 60 % 60
        h = int(secs) // 60 // 60
        res = ':'.join('%02.0f' % x for x in (
            [m, s] if h == 0 else [h, m, s]
        ))
        if isinstance(secs, float):
            ms = round(secs % 1, 3)
            res += ('%.3f' % ms)[1:]
        return res
