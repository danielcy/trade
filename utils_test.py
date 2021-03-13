import unittest
from utils.tech_data import *
from utils.jq_system import *
from utils.stock_utils import *


class UtilsTest(unittest.TestCase):
    def test_ma(self):
        login()
        # 以平安银行 2020-08-17为测试日期
        test_code = '000001.XSHE'
        # 由同花顺得知，当日ma5 = 14.47; ma10 = 14.17; ma20 = 13.93
        ma5 = ma(test_code, 5, '2020-08-18')
        self.assertEqual(ma5, 14.47)
        ma10 = ma(test_code, 10, '2020-08-18')
        self.assertEqual(ma10, 14.17)
        ma20 = ma(test_code, 20, '2020-08-18')
        self.assertEqual(ma20, 13.93)

    def test_ma2(self):
        login()
        test_code = ['000001.XSHE', '601899.XSHG']
        print(ma(test_code, 5, '2020-08-18'))

    def test_max(self):
        login()
        # 以平安银行 2020年为测试目标
        test_code = ['000001.XSHE']
        # 由同花顺得知，当年平安银行最高价为20.88
        maxp = max_price(test_code, 250, '2020-12-31')['000001.XSHE']
        self.assertEqual(maxp, 20.88)

    def test_min(self):
        login()
        # 以平安银行 2020年为测试目标
        test_code = ['000001.XSHE']
        # 由同花顺得知，当年平安银行最高价为11.91
        maxp = min_price(test_code, 250, '2020-12-31')['000001.XSHE']
        self.assertEqual(maxp, 11.91)

    def test_get_price_by_ts(self):
        login()
        # 以平安银行 2021年3月1日14:43:28秒时间戳测试
        test_code = '000001.XSHE'
        # 该时间点股价为21.41
        price = get_price_by_ts(test_code, 1614581008)
        self.assertEqual(price, 21.41)
        # 测试多个标的
        test_code = ['000001.XSHE', '601899.XSHG']
        print(get_price_by_ts(test_code, 1614581008))

    def test_print_last_price(self):
        login()
        test_code = '000001.XSHE'
        print(get_last_price(test_code)[test_code])
        print(get_price_by_ts(test_code, int(time.time())))

    def test_get_last_n_price_info(self):
        login()
        test_code = '000001.XSHE'
        print(get_last_n_price_info(test_code, 1614581008, 20))

    def test_rps(self):
        login()
        print(rps())

    def test_display_stocks(self):
        login()
        codes = ['600132.XSHG', '600161.XSHG', '600196.XSHG', '600305.XSHG', '600588.XSHG', '600600.XSHG', '600741.XSHG', '600763.XSHG', '600872.XSHG', '600882.XSHG', '603027.XSHG', '603127.XSHG', '603181.XSHG', '603288.XSHG', '603345.XSHG', '603392.XSHG', '603517.XSHG', '603713.XSHG', '603868.XSHG', '603896.XSHG', '603939.XSHG', '603991.XSHG', '688008.XSHG', '000869.XSHE', '002032.XSHE', '002410.XSHE', '002493.XSHE', '002607.XSHE']
        print(get_stock_display_template(codes))


class THSForumDataTest(unittest.TestCase):
    def test_close(self):
        login()
        test_code = '000001.XSHE'
        print(close(test_code))

    def test_ref(self):
        login()
        test_code = '000001.XSHE'
        print(ref(close, test_code, 1))

    def test_price(self):
        login()
        test_code = '000001.XSHE'
        print(price(test_code))
        test_code = ['000001.XSHE', '600031.XSHG']
        print(price(test_code))

    def test_bottom_fishing(self):
        login()
        test_code = ['600031.XSHG', '000001.XSHE']
        print(bottom_fishing_risk_score_ths(test_code)['600031.XSHG'][-1])


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(UtilsTest('test_ma'))
    suite.addTest(UtilsTest('test_rps'))

    runner = unittest.TextTestRunner()
    runner.run(suite)
