from jqdatasdk import *
from utils.tech_data import *
from utils.date_utils import *
from data_key import *
from abc import ABCMeta, abstractmethod


class BuySignalPipeline:
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
            if not signal.judge(code, data):
                return False
        return True


class BuySignal(metaclass=ABCMeta):
    @abstractmethod
    def load_data(self, code, data):
        pass

    @abstractmethod
    def judge(self, code, data):
        pass


# 前日为最低价，止跌后形成买入信号
# 试点买入点：当股价高于前日的最高价
class StopDropBuySignal(BuySignal):
    def load_data(self, code, data):
        if LAST_PRICE not in data.keys():
            data[LAST_PRICE] = get_price_by_ts(code, get_current_ts())
        if LAST_5_PRICE_DATA not in data.keys():
            data[LAST_5_PRICE_DATA] = get_last_n_price_info(code, get_current_ts(), 5)
        return data

    def judge(self, code, data):
        price_info_list = data[LAST_5_PRICE_DATA]
        last_price = data[LAST_PRICE]
        today_low = price_info_list[-1]['low']
        yesterday_low = price_info_list[-2]['low']
        if today_low < yesterday_low:
            return False
        for price_info in price_info_list:
            cur_low = price_info['low']
            if cur_low < yesterday_low:
                return False
        yesterday_high = price_info_list[-2]['high']
        if last_price >= yesterday_high:
            return True
        return False





# 日末跌K线买入信号
# TODO: 暂未验证，暂时不启用
class LastDropBuySignal(BuySignal):
    def load_data(self, code, data):
        if LAST_PRICE not in data.keys():
            data[LAST_PRICE] = get_price_by_ts(code, now())
        if LAST_20_PRICE_DATA not in data.keys():
            data[LAST_20_PRICE_DATA] = get_last_n_price_info(code, get_current_ts(), 20)
        return data

    def judge(self, code, data):
        # 判断是否为下分型
        if not judge_bottom_shape(data[LAST_20_PRICE_DATA]):
            return False
        # 判断当前价格是否高于前两日价格最高价
        if data[LAST_PRICE] < data[LAST_20_PRICE_DATA][-3]:
            return False
        return True
