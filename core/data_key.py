# 半年RPS大于90的股票Map
# 数据类型: dict
# 说明: key为股票代码，value为对应的rps值
RPS_90_MAP = "rps_90_map"

# 50日均线Map
# 数据类型: dict
MA_50_MAP = "ma_50_map"

# 150日均线Map
# 数据类型: dict
MA_150_MAP = "ma_150_map"

# 200日均线Map
# 数据类型: dict
MA_200_MAP = "ma_200_map"

# 15日前200日均线Map
# 数据类型: dict
MA_200_15D_MAP = "ma_200_15d_map"

# 1个月前200日均线Map
# 数据类型: dict
MA_200_1M_MAP = "ma_200_1m_map"

# 45日前200日均线Map
# 数据类型: dict
MA_200_45D_MAP = "ma_200_45d_map"

# 2个月前200日均线Map
# 数据类型: dict
MA_200_2M_MAP = "ma_200_2m_map"

# 最新价格Map
# 数据类型: dict
LAST_PRICE_MAP = "last_price_map"

# 一年内最高价Map
# 数据类型: dict
MAX_1Y_MAP = "max_1y_map"

# 一年内最低价Map
# 数据类型: dict
MIN_1Y_MAP = "min_1y_map"

# 龙头股票
# 数据类型: list
DRAGON_STOCK_LIST = "dragon_stock_list"

# 同花顺资金抄底风险数据
# 数据类型: dict
BOTTOM_FISHING_RISK_SCORE_MAP = "bottom_fishing_risk_score_map"

# 清仓过的股票
# 数据类型: dict
# 说明: key为股票代码，value为清仓时间戳
CLEARANCE_MAP = "clearance_map"

# ------------------------个股数据---------------------------- #

# 当前最新价
# 数据类型: float
LAST_PRICE = "last_price"

# 最近20日行情数据
# 数据类型: list
# 说明: 元素包含 open, close, high, low
LAST_20_PRICE_DATA = "last_20_price_data"

# 最近5日行情数据
# 数据类型: list
# 说明: 元素包含 open, close, high, low
LAST_5_PRICE_DATA = "last_5_price_data"

# 持仓数据
# 数据类型: vo.stock.PositionStock
POSITION_STOCK_INFO = "position_stock_info"


