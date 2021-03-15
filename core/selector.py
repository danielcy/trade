from core.data_key import *
from repository.redis_dao import *
from utils.tech_data import *
from abc import ABCMeta, abstractmethod


class SelectPipeline:
    def __init__(self):
        self.selector_list = []
        self.sorter = Sorter()

    def chain(self, selector):
        self.selector_list.append(selector)
        return self

    def set_sorter(self, sorter):
        self.sorter = sorter

    def run(self):
        data = {}
        # 初始默认只取A股沪深两市股票，暂无创业板权限QAQ
        codes = get_hs_stocks()
        for selector in self.selector_list:
            data = selector.load_data(data, codes)
            codes = selector.select(data, codes)
        return self.sorter.sort(data, codes)


class Selector(metaclass=ABCMeta):
    @abstractmethod
    def load_data(self, data, codes):
        pass
    @abstractmethod
    def select(self, data, codes):
        pass


# 根据Rps选取股票
class Rps90Selector(Selector):
    def load_data(self, data, codes):
        if RPS_90_MAP not in data.keys():
            data[RPS_90_MAP] = rps(90)['rps125']
        return data

    def select(self, data, codes):
        result = []
        for code in codes:
            if code in data[RPS_90_MAP].keys():
                result.append(code)
        return result


# 判断上升趋势股票(From: 《股票魔法师-纵横天下股市的奥秘》 Mark Minervini)
class UpGoingSelector(Selector):
    def load_data(self, data, codes):
        if MA_50_MAP not in data.keys():
            data[MA_50_MAP] = ma(codes, 50, now())
        if MA_150_MAP not in data.keys():
            data[MA_150_MAP] = ma(codes, 150, now())
        if MA_200_MAP not in data.keys():
            data[MA_200_MAP] = ma(codes, 200, now())
        if MA_200_15D_MAP not in data.keys():
            data[MA_200_15D_MAP] = ma(codes, 200, get_date(now(), sub=15))
        if MA_200_1M_MAP not in data.keys():
            data[MA_200_1M_MAP] = ma(codes, 200, get_date(now(), sub=30))
        if MA_200_45D_MAP not in data.keys():
            data[MA_200_45D_MAP] = ma(codes, 200, get_date(now(), sub=45))
        if MA_200_2M_MAP not in data.keys():
            data[MA_200_2M_MAP] = ma(codes, 200, get_date(now(), sub=60))
        if LAST_PRICE_MAP not in data.keys():
            data[LAST_PRICE_MAP] = get_last_price(codes)
        if MAX_1Y_MAP not in data.keys():
            data[MAX_1Y_MAP] = max_price(codes, 250, now())
        if MIN_1Y_MAP not in data.keys():
            data[MIN_1Y_MAP] = min_price(codes, 250, now())
        return data

    def select(self, data, codes):
        result = []
        for code in codes:
            ma50 = data[MA_50_MAP][code]
            ma150 = data[MA_150_MAP][code]
            ma200 = data[MA_200_MAP][code]
            ma200_15d = data[MA_200_15D_MAP][code]
            ma200_1m = data[MA_200_1M_MAP][code]
            ma200_45d = data[MA_200_45D_MAP][code]
            ma200_2m = data[MA_200_2M_MAP][code]
            last_price = data[LAST_PRICE_MAP][code]
            max_1y = data[MAX_1Y_MAP][code]
            min_1y = data[MIN_1Y_MAP][code]
            # 1. 股价处于150日和200日均线上方
            if last_price > ma150 and last_price > ma200:
                # 2. 150日均线处于200日均线上方
                if ma150 > ma200:
                    # 3. 200日均线上涨2个月
                    if ma200 > ma200_15d and ma200_15d > ma200_1m and ma200_1m > ma200_45d and ma200_45d > ma200_2m:
                        # 4. 50日移动平均值大于150日与200日移动平均值
                        if ma50 > ma150 and ma50 > ma200:
                            # 5. 股价高于50日移动平均值
                            if last_price > ma50:
                                # 6. 股价比最近一年最低股价至少高30%
                                if last_price / min_1y > 1.3:
                                    # 7. 股价至少处于最近一年最高价的80%以上
                                    if last_price / max_1y > 0.75:
                                        result.append(code)

        return result


# 选择龙头板块股票
class DragonHeadSelector(Selector):
    def load_data(self, data, codes):
        dragon_stocks = get_index_stocks('000065.XSHG')
        sz_dragon_stocks = get_index_stocks('399653.XSHE')
        dragon_stocks.extend(sz_dragon_stocks)
        data[DRAGON_STOCK_LIST] = dragon_stocks
        return data

    def select(self, data, codes):
        result = []
        for code in codes:
            if code in data[DRAGON_STOCK_LIST]:
                result.append(code)
        return result


# 资金抄底选股(参考同花顺公式)
class BottomFishingSelector(Selector):
    def load_data(self, data, codes):
        if BOTTOM_FISHING_RISK_SCORE_MAP not in data.keys():
            data[BOTTOM_FISHING_RISK_SCORE_MAP] = bottom_fishing_risk_score_ths(codes)
        return data

    def select(self, data, codes):
        result = []
        for code in codes:
            score = data[BOTTOM_FISHING_RISK_SCORE_MAP][code][-1]
            if score < 20:
                result.append(code)
        return result


# 筛选近期未清仓过的股票
class RecentNoClearanceSelector(Selector):
    def load_data(self, data, codes):
        pool = ClearancePool()
        data[CLEARANCE_MAP] = pool.get()
        return data

    def select(self, data, codes):
        result = []
        clearance_map = data[CLEARANCE_MAP]
        for k, v in clearance_map.items():
            # 去除10个月前的股票
            if get_current_ts() - v > 10 * 30 * 86400:
                clearance_map.pop(k)
        for code in codes:
            if code not in clearance_map.keys():
                result.append(code)
        return result


# 月K线策略选股，5、10周期金叉，20在中间，股价站于5月线之上
class MonthGoldenSelector(Selector):
    def load_data(self, data, codes):
        if MONTH_MA_5_MAP not in data.keys():
            data[MONTH_MA_5_MAP] = ma(codes, 5, now(), '1M', include_now=True)
        if LAST_MONTH_MA_5_MAP not in data.keys():
            data[LAST_MONTH_MA_5_MAP] = ma(codes, 5, get_date(now(), sub=30), '1M', include_now=True)
        if MONTH_MA_10_MAP not in data.keys():
            data[MONTH_MA_10_MAP] = ma(codes, 10, now(), '1M', include_now=True)
        if LAST_MONTH_MA_10_MAP not in data.keys():
            data[LAST_MONTH_MA_10_MAP] = ma(codes, 10, get_date(now(), sub=30), '1M', include_now=True)
        if MONTH_MA_20_MAP not in data.keys():
            data[MONTH_MA_20_MAP] = ma(codes, 20, now(), '1M', include_now=True)
        if LAST_LOW_PRICE_MAP not in data.keys():
            data[LAST_LOW_PRICE_MAP] = get_last_low_price(codes, '1M')
        return data

    def select(self, data, codes):
        result = []
        for code in codes:
            ma5 = data[MONTH_MA_5_MAP][code]
            last_ma5 = data[LAST_MONTH_MA_5_MAP][code]
            ma10 = data[MONTH_MA_10_MAP][code]
            last_ma10 = data[LAST_MONTH_MA_10_MAP][code]
            ma20 = data[MONTH_MA_20_MAP][code]
            last_price = data[LAST_LOW_PRICE_MAP][code]

            # 当前月MA5 > MA20 > MA10
            if ma5 > ma20 > ma10:
                # 上上月MA5 < MA10(表示上月形成金叉)
                if last_ma5 < last_ma10:
                    # 当前价于MA5线之上
                    if last_price > ma5:
                        print("{} ma5: {}, ma10: {}, ma20: {}".format(code, ma5, ma10, ma20))
                        result.append(code)
        return result



##################################################################################


class Sorter:
    def sort(self, data, codes):
        return codes


# 根据RPS进行排序
class RPS90Sorter(Sorter):
    def sort(self, data, codes):
        if RPS_90_MAP not in data.keys():
            data[RPS_90_MAP] = rps(90)['rps125']
        wait_map = {}
        for code in codes:
            if code in data[RPS_90_MAP].keys():
                wait_map[code] = data[RPS_90_MAP][code]
        sort_list = sorted(wait_map.items(), key=lambda kv: (kv[1], kv[0]))
        top = []
        for tp in sort_list:
            top.append(tp[0])
        top = list(reversed(top))
        return top
