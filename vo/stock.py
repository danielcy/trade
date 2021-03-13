

# 持仓股票
class PositionStock:
    def __init__(self, code, open_price, amount, buy_ts):
        # 股票代码
        self.code = code
        # 开仓价
        self.open_price = open_price
        # 最高价
        self.max_price = open_price
        # 是否触发止盈
        self.trigger_sale = False
        # 持仓数
        self.amount = amount
        # 买入时间
        self.buy_ts = buy_ts
