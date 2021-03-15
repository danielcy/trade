import redis
import json
import pickle
from utils import logger
import time


TRACING_POOL_KEY = "tracing_pool"
POSITION_STOCK_POOL_KEY = "position_stock_pool"
PLAYBACK_TEST_TS = "playback_test_ts"
CLEARANCE_KEY = "clearance"
PLAYBACK_RESULT = "playback_result"
SELECTOR_RESULT = "selector_result"


class StockTracingPool:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def add(self, codes):

        ts = PlaybackTestCache().get_current_ts()
        data = self.client.get(TRACING_POOL_KEY)
        if data is None:
            self.client.set(TRACING_POOL_KEY, json.dumps(codes_ts_to_map(codes, ts)))
        else:
            data_map = json.loads(data)
            for code in codes:
                data_map[code] = ts
            # 将1个月前的股票从追踪池清除
            for k, v in data_map.items():
                if ts - v > 30 * 86400:
                    data_map.pop(k)
            self.client.set(TRACING_POOL_KEY, json.dumps(data_map))

    def set(self, codes):
        ts = PlaybackTestCache().get_current_ts()
        self.client.set(TRACING_POOL_KEY, json.dumps(codes_ts_to_map(codes, ts)))

    def get(self):
        data = self.client.get(TRACING_POOL_KEY)
        if data is None:
            return {}
        return json.loads(data)

    def remove(self, code):
        data = self.client.get(TRACING_POOL_KEY)
        if data is None:
            return
        try:
            data_map = json.loads(data)
            data_map.pop(code)
            self.client.set(TRACING_POOL_KEY, json.dumps(data_map))
        except KeyError:
            logger.warning("StockTracingPool: 删除不存在的code: {}".format(code))

    def clear(self):
        self.client.delete(TRACING_POOL_KEY)


class PositionStockPool:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def add(self, position_stock):
        data = self.client.get(POSITION_STOCK_POOL_KEY)
        if data is None:
            self.client.set(POSITION_STOCK_POOL_KEY, pickle.dumps({position_stock.code: position_stock}))
        else:
            stock_map = pickle.loads(data)
            stock_map[position_stock.code] = position_stock
            self.client.set(POSITION_STOCK_POOL_KEY, pickle.dumps(stock_map))

    def remove(self, code):
        data = self.client.get(POSITION_STOCK_POOL_KEY)
        if data is None:
            return
        try:
            stock_map = pickle.loads(data)
            stock_map.pop(code)
            self.client.set(POSITION_STOCK_POOL_KEY, pickle.dumps(stock_map))
        except KeyError:
            logger.warning("PositionStockPool: 删除不存在的code: {}".format(code))

    def update(self, position_stock):
        data = self.client.get(POSITION_STOCK_POOL_KEY)
        if data is None:
            return
        stock_map = pickle.loads(data)
        stock_map[position_stock.code] = position_stock
        self.client.set(POSITION_STOCK_POOL_KEY, pickle.dumps(stock_map))

    def get(self):
        data = self.client.get(POSITION_STOCK_POOL_KEY)
        if data is None:
            return {}
        else:
            return pickle.loads(data)

    def get_stock(self, code):
        stock_map = self.get()
        if code not in stock_map.keys():
            return None
        return stock_map[code]

    def clear(self):
        self.client.delete(POSITION_STOCK_POOL_KEY)


def codes_ts_to_map(codes, ts):
    result = {}
    for code in codes:
        result[code] = ts
    return result


class PlaybackTestCache:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def set_ts(self, ts):
        self.client.set(PLAYBACK_TEST_TS, ts)

    def get_ts(self):
        data = self.client.get(PLAYBACK_TEST_TS)
        if data is None:
            return None
        return int(data)

    def clean_ts(self):
        self.client.delete(PLAYBACK_TEST_TS)

    def get_current_ts(self):
        if self.get_ts() is None:
            return int(time.time())
        return self.get_ts()

    def add_result(self, id, date, result):
        id_map_data = self.client.hget(PLAYBACK_RESULT, id)
        id_map = {}
        if id_map_data is not None:
            id_map = pickle.loads(id_map_data)
        id_map[date] = result
        self.client.hset(PLAYBACK_RESULT, id, pickle.dumps(id_map))

    def get_result(self, id):
        data = self.client.hget(PLAYBACK_RESULT, id)
        if data is None:
            return {}
        return pickle.loads(data)


class ClearancePool:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def add(self, codes):
        ts = PlaybackTestCache().get_current_ts()
        data = self.client.get(CLEARANCE_KEY)
        if data is None:
            self.client.set(CLEARANCE_KEY, json.dumps(codes_ts_to_map(codes, ts)))
        else:
            data_map = json.loads(data)
            for code in codes:
                data_map[code] = ts
            self.client.set(CLEARANCE_KEY, json.dumps(data_map))

    def get(self):
        data = self.client.get(CLEARANCE_KEY)
        if data is None:
            return {}
        return json.loads(data)

    def clear(self):
        self.client.delete(CLEARANCE_KEY)


class SelectorResultCache:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def add(self, id, codes):
        data = json.dumps(codes)
        self.client.hset(SELECTOR_RESULT, id, data)

    def get(self, id):
        data_json = self.client.hget(SELECTOR_RESULT, id)
        if data_json is None:
            return []
        return json.loads(data_json)
