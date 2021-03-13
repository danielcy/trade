from core.runner import *
from jq_system import *


if __name__=="__main__":
    login()
    clear_playback_test_ts()
    runner = Runner(DragonUpGoingStrategy(), 2)
    start_time = "2019-01-01"
    end_time = "2019-12-31"
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
                                                                      runner.position_cash, round((runner.total_cash - runner.init_cash) * 100 / runner.init_cash, 2)))
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
        runner.after_market_close()
        cur_datetime = cur_datetime + datetime.timedelta(1)
        clear_playback_test_ts()
