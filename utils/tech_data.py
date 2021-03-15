from jqdatasdk import *
from utils.date_utils import *
from utils.list_utils import *
import numpy as np
import datetime


def ma(code, n, date, unit='1d', include_now=False):
    if isinstance(code, list):
        close_data = get_bars(security=code, count=n, unit=unit, fields=['close'], include_now=include_now, end_dt=date,
                              fq_ref_date=None)
        temp_data = {}
        for k, v in close_data['close'].to_dict().items():
            if k[0] not in temp_data.keys():
                temp_data[k[0]] = [v]
            else:
                temp_data[k[0]].append(v)
        result = {}
        for k, v in temp_data.items():
            result[k] = round(np.mean(v), 2)
        return result
    else:
        close_data = get_bars(security=code, count=n, unit=unit, fields=['close'], include_now=include_now, end_dt=date,
                              fq_ref_date=None)
        return round(close_data['close'][n*-1:].mean(), 2)


def max_price(code, count, end_dt):
    high_data = get_bars(security=code, count=count, unit='1d', fields=['high'], include_now=False, end_dt=end_dt,
             fq_ref_date=None)
    result = {}
    for k, v in high_data['high'].to_dict().items():
        if k[0] not in result.keys():
            result[k[0]] = v
        elif v > result[k[0]]:
            result[k[0]] = v
    return result


def min_price(code, count, end_dt):
    low_data = get_bars(security=code, count=count, unit='1d', fields=['low'], include_now=False, end_dt=end_dt,
                         fq_ref_date=None)
    result = {}
    for k, v in low_data['low'].to_dict().items():
        if k[0] not in result.keys():
            result[k[0]] = v
        elif v < result[k[0]]:
            result[k[0]] = v
    return result


def get_price_by_ts(code, ts):
    date = datetime.datetime.fromtimestamp(ts)
    if isinstance(code, list):
        data = get_price(security=code, count=1, frequency="1m", fields=['close'], end_date=date)
        result = {}
        for c, value in data.close.to_dict().items():
            result[c] = list(value.values())[0]
        return result
    else:
        data = get_price(security=code, count=1, frequency="1m", fields=['close'], end_date=date)
        return list(data.to_dict()['close'].values())[0]


def get_last_n_price_info(code, ts, n, frequency='daily'):
    date = datetime.datetime.fromtimestamp(ts)
    price_data = get_price(security=code, end_date=date, fields=['open', 'close', 'high', 'low'], count=n,
                           frequency=frequency).to_dict()
    temp_map = {}
    for k, v in price_data.items():
        temp_map[k] = list(v.values())
    result = []
    for i in range(n):
        info = {
            "open": temp_map["open"][i],
            "close": temp_map["close"][i],
            "high": temp_map["high"][i],
            "low": temp_map["low"][i]
        }
        result.append(info)
    return result


def get_last_low_price(code, unit='1d'):
    if isinstance(code, list):
        low_data = get_bars(security=code, count=1, unit=unit, fields=['low'], include_now=True, end_dt=now(),
                              fq_ref_date=None)
        result = {}
        for k, v in low_data['low'].to_dict().items():
            result[k[0]] = [v]
        return result
    else:
        low_data = get_bars(security=code, count=1, unit=unit, fields=['low'], include_now=True, end_dt=now(),
                              fq_ref_date=None)
        return low_data['low'].to_dict()[0]


# 判断是否为下分型
def judge_bottom_shape(price_info_list):
    # TODO: 处理包含关系, 目前由于不处理，前4根线只要满足最低点下跌即认为下跌
    if len(price_info_list) < 5:
        return False
    line1 = price_info_list[-1]
    line2 = price_info_list[-2]
    line3 = price_info_list[-3]
    line4 = price_info_list[-4]
    line5 = price_info_list[-5]
    if line5['low'] > line4['low'] > line3['low'] > line2['low'] and line1['low'] > line2['low']:
        if line1['high'] > line2['high'] and line2['high'] < line3['high']:
            return True

    return False


def rps(value=90):
    pre_stocks = get_index_stocks('000985.XSHG')
    # 获取A股昨日/半年前/1年前收盘价
    one_d_data = get_bars(security=pre_stocks, count=1, unit='1d', fields=['close'], end_dt=now())
    one_d_data.columns = ['first_close']
    half_y_data = get_bars(security=pre_stocks, count=1, unit='1d', fields=['close'], end_dt=get_date(now(), sub=183))
    half_y_data.columns = ['125_close']
    one_y_data = get_bars(security=pre_stocks, count=1, unit='1d', fields=['close'], end_dt=get_date(now(), sub=365))
    one_y_data.columns = ['250_close']
    rps_data = one_d_data.join(half_y_data).join(one_y_data)
    
    rps_data['rps250'] = (rps_data['first_close'] - rps_data['250_close']) / rps_data['250_close']
    rps_data['rps125'] = (rps_data['first_close'] - rps_data['125_close']) / rps_data['125_close']

    # 对RPS进行排名
    rps_data['rps250'] = 100 - (rps_data['rps250'].rank(ascending=False, method='max')) / len(rps_data) * 100
    rps_data['rps125'] = 100 - (rps_data['rps125'].rank(ascending=False, method='max')) / len(rps_data) * 100
    
    # 删除一年内上市的股票
    rps_data = rps_data.dropna(axis=0, how='any')[['rps250', 'rps125']]

    # 半年全年RPS同时满足大于90
    rps_data = rps_data[(rps_data['rps250'] > value) & (rps_data['rps125'] > value)]

    # 修正数据，使Key变为股票代码
    fixed_250_map = {}
    fixed_125_map = {}
    rps_map = rps_data.to_dict()
    rps_250 = rps_map['rps250']
    rps_125 = rps_map['rps125']
    for k, v in rps_250.items():
        fixed_250_map[k[0]] = v
    for k, v in rps_125.items():
        fixed_125_map[k[0]] = v
    rps_map['rps250'] = fixed_250_map
    rps_map['rps125'] = fixed_125_map
    return rps_map


# 获取仅沪深两市股票
def get_hs_stocks():
    sh_stocks = get_index_stocks('000001.XSHG')
    sz_stocks = get_index_stocks('399001.XSHE')
    cy_stocks = get_index_stocks('399006.XSHE')
    stocks = []
    stocks.extend(sh_stocks)
    stocks.extend(sz_stocks)
    codes = []
    for stock in stocks:
        if stock not in cy_stocks:
            codes.append(stock)
    return codes


# --------------------同花顺公式函数实现------------------------
def price(code, date=now()):
    if isinstance(code, list):
        price_data = get_bars(security=code, count=99999999999999, unit='1d', fields=['open', 'close', 'high', 'low'],
                              include_now=True,
                              end_dt=date,
                              fq_ref_date=None)
        result = {}
        for c in code:
            result[c] = {}
        for field in ('open', 'close', 'high', 'low'):
            temp_data = {}
            for k, v in price_data[field].to_dict().items():
                if k[0] not in temp_data.keys():
                    temp_data[k[0]] = [v]
                else:
                    temp_data[k[0]].append(v)
            for k, v in temp_data.items():
                result[k][field] = v
        return result
    else:
        price_data = get_bars(security=code, count=99999999999999, unit='1d', fields=['open', 'close', 'high', 'low'], include_now=True,
                              end_dt=date,
                              fq_ref_date=None)
        result = {
            "open": list(price_data.to_dict()['open'].values()),
            "close": list(price_data.to_dict()['close'].values()),
            "high": list(price_data.to_dict()['high'].values()),
            "low": list(price_data.to_dict()['low'].values())
        }
        return result


def close(code, date=now()):
    close_data = get_bars(security=code, count=99999999999999, unit='1d', fields=['close'], include_now=True, end_dt=date,
                          fq_ref_date=None)
    return list(close_data.to_dict()['close'].values())


def low(code, date=now()):
    close_data = get_bars(security=code, count=99999999999999, unit='1d', fields=['low'], include_now=True,
                          end_dt=date,
                          fq_ref_date=None)
    return list(close_data.to_dict()['low'].values())


def ref(func, code, n, date=now()):
    result = []
    for i in range(n):
        result.append(0)
    data = func(code, date)
    result.extend(data[0:-1*n])
    return result


def ema(x, n):
    # X为获取的股票数据 如收盘价系列数据
    # N为EMA的计算周期
    y = x.copy()  # 复制一个X对象
    for i in range(len(x)):   # 从X的第一个数据开始遍历到最后一个数据
        if i == 0:    # 如果是X中的第一项数据
            y[i] = x[i]      # Y的初始值=X的初始值
        if i > 0:   # 如果是X中的第2（包括2）以上项数据
            y[i] = (2 * x[i] + (n - 1) * y[i - 1]) / (n + 1)
    return y


def sma(x, n, m):               # 设置SMA的参数X,n,m
    y = x.copy()                     # 复制一个X对象
    for i in range(len(x)):      # 从第1个数据开始遍历X:i=1，i=2.......
        if i == 0:                     # X的第一个数据
            y[i] = x[i]                # 设置Y的初始值为X的初始值
        if i > 0:                         # X的第2个数据，开始遍历
            y[i] = (m * x[i] + (n - m) * y[i - 1]) / n     # 代入计算公式
    return y                           # 返回Y，即EMA数据序列


# 资金抄底计算公式
# 返回风险系数，20一下为机会区，80以上为风险区
def bottom_fishing_risk_score_ths(code, date=now()):
    if isinstance(code, list):
        result = {}
        price_list_map = price(code, date)
        for c in code:
            result[c] = bottom_fishing_process_data(price_list_map[c])
        return result
    else:
        price_list = price(code, date)
        return bottom_fishing_process_data(price_list)


def bottom_fishing_process_data(price_list):
    close_list = price_list['close']
    low_list = price_list['low']
    high_list = price_list['high']

    lc = ref_list(close_list, 1)
    minus_close_lc_list = minus_list(close_list, lc)
    rsi_minus_close_lc_list = clear_negative_number(minus_close_lc_list)
    abs_minus_close_lc_list = abs_list(minus_close_lc_list)
    sma_1_1 = sma(rsi_minus_close_lc_list, 3, 1)
    sma_1_2 = sma(abs_minus_close_lc_list, 3, 1)
    sma_2_1 = sma(rsi_minus_close_lc_list, 5, 1)
    sma_2_2 = sma(abs_minus_close_lc_list, 5, 1)
    sma_3_1 = sma(rsi_minus_close_lc_list, 8, 1)
    sma_3_2 = sma(abs_minus_close_lc_list, 8, 1)
    rsi_1 = multiply_num(divide_list(sma_1_1, sma_1_2), 100)
    rsi_2 = multiply_num(divide_list(sma_2_1, sma_2_2), 100)
    rsi_3 = multiply_num(divide_list(sma_3_1, sma_3_2), 100)
    # 计算出相对强弱
    relative_power = add_list(add_list(multiply_num(rsi_1, 0.5), multiply_num(rsi_2, 0.31)), multiply_num(rsi_3, 0.19))

    llv_low = llv(low_list, 8)
    hhv_high = hhv(high_list, 8)
    x = multiply_num(minus_list(close_list, llv_low), 100)
    y = minus_list(hhv_high, llv_low)
    de = divide_list(x, y)
    wave_1 = sma(de, 3, 1)
    wave_2 = sma(de, 5, 1)
    wave_3 = sma(de, 8, 1)
    # 计算出短线波段
    # wave = 0.5 * wave_1[-1] + 0.31 * wave_2[-1] + 0.19 * wave_3[-1]
    wave = add_list(add_list(multiply_num(wave_1, 0.5), multiply_num(wave_2, 0.31)), multiply_num(wave_3, 0.19))

    #return 0.5 * relative_power + 0.5 * wave
    return add_list(multiply_num(relative_power, 0.5), multiply_num(wave, 0.5))


# 机构筹码
def organization_chip(code, date=now()):
    price_list = price(code, date)


def process_organization_chip_date(price_list):
    close_list = price_list['close']
    low_list = price_list['low']
    high_list = price_list['high']

    xa_1 = ref_list(low_list, 1)
    # XA_2:=SMA(ABS(LOW-XA_1),3,1)/SMA(MAX(LOW-XA_1,0),3,1)*100;
    minus_low_lc_list = minus_list(low_list, xa_1)
    xa_2 = multiply_num(divide_list(sma(abs_list(minus_low_lc_list), 3, 1), sma(clear_negative_number(minus_low_lc_list), 3, 1)), 100)



