from strategy import *
from redis_dao import *
from vo.stock import *
from stock_utils import *
import logger


class Runner:
    def __init__(self, strategy, max_position_cnt=2, total_cash=300000):
        self.strategy = strategy
        self.tracing_pool = StockTracingPool()
        self.position_stock_pool = PositionStockPool()
        self.clearance_pool = ClearancePool()
        self.position_cnt = 0
        self.max_position_cnt = max_position_cnt
        self.total_cash = total_cash
        self.available_cash = total_cash
        self.init_cash = total_cash
        self.position_cash = 0
        self.success_cnt = 0
        self.fail_cnt = 0

        self.tracing_pool.clear()
        self.position_stock_pool.clear()
        self.clearance_pool.clear()

    def before_market_open(self):
        # 选出符合选股条件的股票
        codes = self.strategy.select_stocks()
        # 剔除所有已在仓内的股票
        position_stocks = self.position_stock_pool.get()
        final_codes = []
        for code in codes:
            if code not in position_stocks.keys():
                final_codes.append(code)
        # 将股票置入股票池进行追踪
        self.tracing_pool.set(final_codes)
        logger.info("选股策略【{}】选出股票：{}".format(self.strategy.get_name(), get_stock_display_template(final_codes)))

    def market_open(self):
        # 卖出逻辑
        position_stocks = self.position_stock_pool.get()
        for code, stock in position_stocks.items():
            if self.strategy.judge_sell(code):
                price = get_price_by_ts(code, get_current_ts())
                amount = stock.amount
                self.sell(code, price, amount)

        # 仅当有剩余仓位时考虑买入
        if self.position_cnt < self.max_position_cnt:
            # 取出追踪池内股票
            codes_map = self.tracing_pool.get()
            for code, _ in codes_map.items():
                if self.position_cnt >= self.max_position_cnt:
                    break
                if self.strategy.judge_buy(code):
                    price = get_price_by_ts(code, get_current_ts())
                    amount = self.get_amount(price)
                    self.order(code, price, amount)

        # 更新持仓股票状态
        position_stocks = self.position_stock_pool.get()
        for code, stock in position_stocks.items():
            cur_price = get_price_by_ts(code, get_current_ts())
            if cur_price > stock.max_price:
                stock.max_price = cur_price
            self.position_stock_pool.update(stock)

    def after_market_close(self):
        logger.info("【当日持仓情况】")
        position_stocks = self.position_stock_pool.get()
        self.position_cash = 0
        for code, stock in position_stocks.items():
            cur_price = get_price_by_ts(code, get_current_ts())
            last_price = get_price_by_ts(code, get_current_ts()-86400)
            rate = (cur_price - stock.open_price) / stock.open_price
            # 结算当天金钱
            total_price_diff = (cur_price - stock.open_price) * stock.amount
            last_price_diff = (cur_price - last_price) * stock.amount
            self.position_cash = self.position_cash + cur_price * stock.amount
            logger.info("{} 开仓价格: {} 当前价格: {} 涨幅: {} 持仓金额: {}, 当日盈亏: {} 总盈亏: {}".format(get_stock_display_template(code), stock.open_price,
                                                             cur_price, round(rate * 100, 2), round(cur_price * stock.amount, 2),
                                                            round(last_price_diff, 2), round(total_price_diff, 2)))
        self.total_cash = self.position_cash + self.available_cash

    def order(self, code, price, amount):
        if amount == 0:
            logger.warning("挂单买入{}失败，买入数量为0, 总金额: {}, 持仓金额".format(get_stock_display_template(code), round(self.total_cash, 2),
                                                                   round(self.position_cash, 2)))
            return
        logger.info("挂单买入{},买入价: {}, 买入{}股".format(get_stock_display_template(code), price, amount))
        stock = PositionStock(code, price, amount, int(time.time()))
        self.position_stock_pool.add(stock)
        self.tracing_pool.remove(code)
        self.position_cnt = self.position_cnt + 1
        self.position_cash = self.position_cash + price * amount
        self.available_cash = self.available_cash - price * amount

    def sell(self, code, price, amount):
        stock_map = self.position_stock_pool.get()
        if code not in stock_map.keys():
            logger.warning("卖出{}失败，当前持仓无该股票".format(get_stock_display_template(code)))
            return
        stock = stock_map.get(code)
        rate = (price - stock.open_price) / stock.open_price
        logger.info("挂单卖出{},卖出价: {}, 卖出{}股, 盈利: {}%".format(get_stock_display_template(code), price, amount, round(rate*100, 2)))
        if rate > 0:
            self.success_cnt = self.success_cnt + 1
        else:
            self.fail_cnt = self.fail_cnt + 1
        self.position_stock_pool.remove(code)
        self.position_cnt = self.position_cnt - 1
        self.position_cash = self.position_cash - price * amount
        self.clearance_pool.add([code])

    def get_amount(self, price):
        total_limit = self.total_cash / self.max_position_cnt
        available_cash = self.total_cash - self.position_cash
        amount = 0
        while True:
            if (amount + 100) * price > total_limit or (amount + 100) * price > available_cash:
                return amount
            amount = amount + 100

