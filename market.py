from fake_useragent import UserAgent
import pywencai
import time
import datetime
from chinese_calendar import is_workday
import stock

# Pan_Zhong_Mode 盘中模式，YesterdayPrice表示上一个交易日股价。
# Pan_Hou_mode 盘后模式，YesterdayPrice表示今日收盘价格。
Pan_Zhong_Mode = 0
Pan_Hou_mode = 1
ua = UserAgent()


# 获取同花顺概念指数 前N数据
def get_top_zhishu():
    start_time = time.time()
    ths_zhishu_df = pywencai.get(query='同花顺概念指数+涨跌幅排序', query_type='zhishu',
                                 page=1, perpage=15, loop=False,
                                 user_agent=ua.random)
    end_time = time.time()
    print('%s get_top10_ths_zhishu took %f second' % (datetime.datetime.now(), end_time - start_time))
    print(ths_zhishu_df)
    return ths_zhishu_df


# 获取最近的工作日。不考虑节假日的话，周中返回当天，周末返回周五 格式：2024-07-20
def get_recent_work_day(day=datetime.date.today()):
    if is_workday(day):
        return day
    day = day - datetime.timedelta(days=1)
    return get_recent_work_day(day)


# 获取最近工作日的前一天工作日
def get_recent_work_yesterday():
    return get_recent_work_day(get_recent_work_day() - datetime.timedelta(days=1))


# get_constituent_stock 获取成分股数据 构建 stock list
# 问财：半导体；涨幅排序：总市值，120均线，250均线；2024.7.18收盘价；（现价不需要加入）
def get_constituent_stock(zhishu_name, time_mode=Pan_Zhong_Mode):
    # 问财语句构建
    SQL_condition = [zhishu_name, '涨跌幅从大到小排序', '总市值', '120均线', '250均线']
    # today 表示最近的工作日。 yesterday 表示最近工作日的上一个工作日
    today = get_recent_work_day().strftime('%Y%m%d')
    yesterday = get_recent_work_yesterday().strftime('%Y%m%d')
    yesterday_time_sql = yesterday + '收盘价'
    SQL_condition.append(yesterday_time_sql)
    wencai_SQL = ';'.join(SQL_condition)
    print(wencai_SQL)
    # 查询问财获取数据
    stock_df = pywencai.get(query=wencai_SQL, query_type='stock',
                            page=1, perpage=100, loop=True, user_agent=ua.random)
    # print(stock_df)
    '''
(['股票代码', '股票简称', '最新价', '总市值[20240722]', '120日均线[20240722]',
       '250日均线[20240722]', '收盘价:不复权[20240719]', '涨跌幅:前复权[20240722]', '行业简称',
       '涨跌幅:前复权行业排名[20240722]', 'a股市值(不含限售股)[20240722]', '买入信号inter[20240722]',
       '技术形态[20240722]', '开盘价:不复权[20240719]', '最高价:不复权[20240719]',
       '最低价:不复权[20240719]', '最新dde大单净额', '所属概念', '总股本[20240722]',
       '市盈率(pe)[20240722]', '开盘价:前复权[20240722]', '最高价:前复权[20240722]',
       '最低价:前复权[20240722]', '收盘价:前复权[20240722]', '振幅[20240722]',
       '成交量[20240722]', 'market_code', 'code'],
'''
    stocks = []
    for _, row in stock_df.iterrows():
        s = stock.Stock()
        s.Date = today
        s.Code = row["code"]
        s.Name = row["股票简称"]
        s.Type = s.get_stock_type()
        s.MarketValue = round(row[f'总市值[{today}]']/100000000, 2)
        s.Percentage = row[f'涨跌幅:前复权[{today}]']
        if time_mode == Pan_Zhong_Mode:
            s.Price = row["最新价"]
            s.YesterdayPrice = row[f'收盘价:不复权[{yesterday}]']
        elif time_mode == Pan_Hou_mode:
            s.Price = s.YesterdayPrice = row["最新价"]
        ema120 = row[f'120日均线[{today}]']
        ema250 = row[f'250日均线[{today}]']
        if ema120 == "":
            s.EMA120 = 0
        else:
            s.EMA120 = float(row[f'120日均线[{today}]'])
        if ema250 == "":
            s.EMA250 = 0
        else:
            s.EMA250 = float(row[f'250日均线[{today}]'])
        stocks.append(s)
        # print(vars(s))
        s.get_stock_quality()
    return stocks

