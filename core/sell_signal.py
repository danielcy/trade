from abc import ABCMeta, abstractmethod
from utils.tech_data import *
from utils.date_utils import *
from data_key import *
from redis_dao import *
from stock_utils import *


class SellSignalPipeline:
    def __init__(self):
        self.signal_list = []

    def chain(self, signal):
        self.signal_list.append(signal)
        return self

    def judge(self, code):
        if len(self.signal_list) == 0:
            return False
        data = {}
        for signal in self.signal_list:
            data = signal.load_data(code, data)
            if signal.judge(code, data):
                return True
        return False


class SellSignal(metaclass=ABCMeta):
    @abstractmethod
    def load_data(self, code, data):
        pass

    @abstractmethod
    def judge(self, code, data):
        pass


# 30%利润后回撤10%止盈
class ThirtyTenPctSellSignal(SellSignal):
    def __init__(self):
        self.position_pool = PositionStockPool()

    def load_data(self, code, data):
        if LAST_PRICE not in data.keys():
            data[LAST_PRICE] = get_price_by_ts(code, get_current_ts())
        data[POSITION_STOCK_INFO] = self.position_pool.get_stock(code)
        return data

    def judge(self, code, data):
        position_stock = data[POSITION_STOCK_INFO]
        if position_stock is None:
            return False
        cur_price = data[LAST_PRICE]
        if position_stock.trigger_sale:
            # 利润回撤10%则卖出
            if cur_price < position_stock.max_price * 0.9:
                return True
        else:
            if cur_price > position_stock.open_price * 1.3:
                logger.info("{} 上涨超过阈值30%，触发止盈标记".format(get_stock_display_template(code)))
                position_stock.trigger_sale = True
                self.position_pool.update(position_stock)
        return False


# 高点回撤20%无脑止损
class TwentyPctLossSellSignal(SellSignal):
    def __init__(self):
        self.position_pool = PositionStockPool()

    def load_data(self, code, data):
        if LAST_PRICE not in data.keys():
            data[LAST_PRICE] = get_price_by_ts(code, get_current_ts())
        data[POSITION_STOCK_INFO] = self.position_pool.get_stock(code)
        return data

    def judge(self, code, data):
        position_stock = data[POSITION_STOCK_INFO]
        if position_stock is None:
            return False
        cur_price = data[LAST_PRICE]
        if cur_price < position_stock.max_price * 0.8:
            return True
        return False
