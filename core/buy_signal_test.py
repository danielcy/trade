import unittest
from buy_signal import *
from date_utils import *
from jq_system import *


class BuySignalTest(unittest.TestCase):
    def test_stop_drop_buy_signal(self):
        login()
        test_code = "600031.XSHG"
        set_playback_test_ts(1605854608)
        signal = StopDropBuySignal()
        data = {}
        data = signal.load_data(test_code, data)
        self.assertEqual(signal.judge(test_code, data), True)
        clear_playback_test_ts()
