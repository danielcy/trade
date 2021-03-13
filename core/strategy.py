from selector import *
from buy_signal import *
from sell_signal import *
from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):

    def __init__(self):
        self.selector_pipline = SelectPipeline()
        self.buy_signal_pipeline = BuySignalPipeline()
        self.sell_signal_pipeline = SellSignalPipeline()

    @abstractmethod
    def get_name(self):
        return "默认策略"

    def select_stocks(self):
        return self.selector_pipline.run()

    def judge_buy(self, code):
        return self.buy_signal_pipeline.judge(code)

    def judge_sell(self, code):
        return self.sell_signal_pipeline.judge(code)


class DragonUpGoingStrategy(Strategy):
    def get_name(self):
        return "龙头上行"

    def __init__(self):
        super().__init__()
        self.selector_pipline\
            .chain(DragonHeadSelector())\
            .chain(Rps90Selector())\
            .chain(UpGoingSelector())\
            .chain(RecentNoClearanceSelector())
        self.selector_pipline.set_sorter(RPS90Sorter())
        self.buy_signal_pipeline.chain(StopDropBuySignal())
        self.sell_signal_pipeline.chain(ThirtyTenPctSellSignal()).chain(TwentyPctLossSellSignal())

