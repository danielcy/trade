# import easytrader
#
# user = easytrader.use('gj_client')
# user.prepare('gj_prepare.json')
# print(user.balance)

from jqdatasdk import *

auth("13482892612", "5Kasile123")

df = get_price('000001.XSHE', start_date='2021-01-01', end_date='2021-02-27', frequency='daily')
print(df)