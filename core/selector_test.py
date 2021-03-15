import unittest
from jq_system import *
from selector import *


class SelectorTest(unittest.TestCase):
    def test_rps_90_selector(self):
        login()
        pipe = SelectPipeline()
        pipe.chain(Rps90Selector())
        print(pipe.run())

    def test_up_going_selector(self):
        login()
        pipe = SelectPipeline()
        pipe.chain(UpGoingSelector())
        print(pipe.run())

    def test_dragon_head_selector(self):
        login()
        pipe = SelectPipeline()
        pipe.chain(DragonHeadSelector())
        print(pipe.run())

    def test_bottom_fishing_selector(self):
        login()
        pipe = SelectPipeline()
        pipe.chain(BottomFishingSelector())
        print(pipe.run())

    def test_month_golden_selector(self):
        login()
        pipe = SelectPipeline()
        pipe.chain(MonthGoldenSelector())
        print(pipe.run())


class SorterTest(unittest.TestCase):
    def test_rps_90_sorter(self):
        login()
        test_codes = ['000001.XSHE', '600438.XSHG', '601899.XSHG']
        sorter = RPS90Sorter()
        print(sorter.sort({}, test_codes))
