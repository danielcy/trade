import unittest
import logger
from vo.stock import *
from redis_dao import *


class StockTracingPoolTest(unittest.TestCase):
    def test_add_and_get(self):
        pool = StockTracingPool()
        pool.clear()
        test_code = ['000001', '000002']
        pool.add(test_code)
        logger.info(pool.get())
        test_code2 = ['000003', '000004']
        pool.add(test_code2)
        logger.info(pool.get())
        pool.clear()


class PositionStockPoolTest(unittest.TestCase):
    def test_add_and_get(self):
        pool = PositionStockPool()
        pool.add(PositionStock("1", 1, 1, 1))
        pool.add(PositionStock("2", 2, 2, 2))
        pool.remove("1")
        pool.remove("3")
        print(pool.get())
        pool.clear()
