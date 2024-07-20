from fake_useragent import UserAgent
import pywencai
import time
import datetime
from datetime import datetime

TopZhiShu = 15
ua = UserAgent()


# 获取同花顺概念指数 前N数据
def get_top_zhishu():
    start_time = time.time()
    ths_zhishu_df = pywencai.get(query='同花顺概念指数+涨跌幅排序', query_type='zhishu',
                                 page=1, perpage=TopZhiShu, loop=False,
                                 user_agent=ua.random)
    end_time = time.time()
    print('%s get_top10_ths_zhishu took %f second' % (datetime.now(), end_time - start_time))
    print(ths_zhishu_df)
    return ths_zhishu_df


# 获取昨日时间 格式：2024-07-20
def get_yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday.date()


# get_constituent_stock 获取成分股数据 构建 stock list
# 问财：半导体；涨幅排序：总市值，120均线，250均线；2024.7.19 9:50的分时收盘股价；2024.7.18收盘价；
def get_constituent_stock(zhishu_name):
    # 问财语句构建
    SQL_condition = [zhishu_name, '涨跌幅排序', '总市值', '120均线', '250均线']
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    cur_price_sql = cur_time + '分时收盘股价'
    SQL_condition.append(cur_price_sql)
    per_time = get_yesterday()
    per_time_sql = per_time+ '收盘价'
    SQL_condition.append(per_time_sql)
    print(SQL_condition)
    wencai_SQL = ';'.join(SQL_condition)
    # 查询问财获取数据

# 通过问财查询，板块今日可能会穿越年线的大于100亿市值的股票。
