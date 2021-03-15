import unittest
from strategy import *
from stock_utils import *
from jq_system import *
import logger
import time


class StrategyTest(unittest.TestCase):
    def test_dragon_up_going_strategy_select(self):
        login()
        clear_playback_test_ts()
        # set_playback_test_ts(1614581008)
        ClearancePool().clear()
        start = int(time.time())
        cnt = get_query_count()['spare']
        strategy = DragonUpGoingStrategy()
        codes = strategy.select_stocks()
        logger.info("策略【{}】选股: {}".format(strategy.get_name(), get_stock_display_template(codes)))
        end_select = int(time.time())
        logger.info("策略【{}】选股耗时: {}秒".format(strategy.get_name(), end_select - start))
        cnt_select = get_query_count()['spare']
        logger.info("策略【{}】选股请求数据: {}行".format(strategy.get_name(), cnt - cnt_select))
        fit_buy_codes = []
        for code in codes:
            if strategy.judge_buy(code):
                fit_buy_codes.append(code)
        logger.info("策略【{}】满足买入信号股票: {}".format(strategy.get_name(), get_stock_display_template(fit_buy_codes)))
        end_judge = int(time.time())
        logger.info("策略【{}】买入信号耗时: {}秒".format(strategy.get_name(), end_judge - end_select))
        cnt_judge = get_query_count()['spare']
        logger.info("策略【{}】买入信号请求数据: {}行".format(strategy.get_name(), cnt_select - cnt_judge))
        # clear_playback_test_ts()
