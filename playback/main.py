from core.runner import *
from utils.jq_system import *
from vo.report import *
from utils.thread_utils import *


class PlaybackProcessor:

    def __init__(self, runner):
        self.runner = runner
        self.playback_cache = PlaybackTestCache()

    def launch(self):
        id = int(time.time())
        self.process(id)
        return id

    @start_new_thread
    def process(self, id=int(time.time())):
        login()
        clear_playback_test_ts()
        runner = self.runner
        start_time = "2020-01-01"
        end_time = "2020-12-31"
        start_datetime = datetime.datetime.strptime(start_time, '%Y-%m-%d')
        end_datetime = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        trade_day_list = get_all_trade_days()
        cur_datetime = start_datetime
        while cur_datetime <= end_datetime:
            if cur_datetime.date() not in trade_day_list:
                cur_datetime = cur_datetime + datetime.timedelta(1)
                continue
            # 正常交易时间为09:30~11:30 13:00~15:00
            # 换算为时间戳后，交易区间为[ts+34200, ts+41400], [ts+46800, ts+54000]
            logger.info("处理日期：{}, 当前总金额: {}, 当前持仓金额: {}, 收益率: {}%".format(cur_datetime, runner.total_cash,
                                                                          runner.position_cash, round(
                    (runner.total_cash - runner.init_cash) * 100 / runner.init_cash, 2)))
            trade_range_A = (int(cur_datetime.timestamp()) + 34200, int(cur_datetime.timestamp()) + 41400)
            trade_range_B = (int(cur_datetime.timestamp()) + 46800, int(cur_datetime.timestamp()) + 54000)
            cur_ts = trade_range_A[0]
            # 先执行盘前选股函数
            set_playback_test_ts(cur_ts)
            runner.before_market_open()
            # 每分钟执行一次
            while cur_ts <= trade_range_A[1]:
                set_playback_test_ts(cur_ts)
                runner.market_open()
                cur_ts = cur_ts + 60
            cur_ts = trade_range_B[0]
            while cur_ts <= trade_range_B[1]:
                set_playback_test_ts(cur_ts)
                runner.market_open()
                cur_ts = cur_ts + 60
            runner.after_market_close()
            date_str = cur_datetime.strftime("%Y-%m-%d")
            rate = round((runner.total_cash - runner.init_cash) * 100 / runner.init_cash, 2)
            result = ProcessResult(date_str, rate)
            self.playback_cache.add_result(id, date_str, result)
            cur_datetime = cur_datetime + datetime.timedelta(1)
            clear_playback_test_ts()

    def get_result(self, id):
        data = self.playback_cache.get_result(id)
        result = {}
        for k, v in data.items():
            result[k] = v.rate
        return result


if __name__ == "__main__":
    processor = PlaybackProcessor(Runner(DragonUpGoingStrategy(), 2))
    processor.process()
