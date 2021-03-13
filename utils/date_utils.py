import datetime
import time
from redis_dao import PlaybackTestCache


def get_date(dt, add=None, sub=None):
    if add is None and sub is None:
        return dt
    elif sub is None:
        return dt + datetime.timedelta(days=add)
    else:
        return dt - datetime.timedelta(days=sub)


def now():
    if get_playback_test_ts() is None:
        return datetime.datetime.now()
    return datetime.datetime.fromtimestamp(get_playback_test_ts())


def get_current_ts():
    if get_playback_test_ts() is None:
        return int(time.time())
    return get_playback_test_ts()


def set_playback_test_ts(ts):
    cache = PlaybackTestCache()
    cache.set_ts(ts)


def get_playback_test_ts():
    cache = PlaybackTestCache()
    return cache.get_ts()


def clear_playback_test_ts():
    cache = PlaybackTestCache()
    cache.clean_ts()
