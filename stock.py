ALLTYPE = 'All'
SHANGHAI = '上海主板'
SHENZHEN = '深圳主板'
KECHUANG = '科创板'
CHUANGYE = '创业板'
BEIJING = '北交所'
UNKNOW = '未分类'


class Stock:
    def __init__(self):
        # 股票基本数据 Todo 题材板块
        self.Date = ""  # 时期
        self.Code = ""
        self.Name = ""
        self.Type = ''
        self.Percentage = 0.00
        self.MarketValue = 0.00  # 今日总市值（单位亿），这里图方便 不去计算Date的总市值
        self.YesterdayPrice = 0.00  # Date日前一天 股价
        self.Price = 0.00  # Date日 股价
        self.EMA250 = 0.00  # Date日 年线均价
        self.EMA120 = 0.00  # Date日 半年线均价
        # 股性 股票质量判断
        self.LimitUpGene = False  # 涨停基因，120天是否有过涨停
        self.LimitUpPremium = False  # 是否有涨停溢价

    # Todo 股票股性判断：1.近半年是否有过涨停。2.涨停第二天是否有溢价。最好是返回一个结构体。
    def get_stock_quality(self):
        # 查询120天涨幅数据，是否有涨停个股。并且判断第二天开盘涨幅是否大于0%
        self.LimitUpGene = False
        self.LimitUpPremium = False

    # 创业板（30XXXX）/科创板（688XXX）/主板（60XXXX/00XXXX）/北交所（8XXXXX/9XXXXX/4XXXXX)
    def get_stock_type(self):
        code = self.Code
        if code.startswith("30"):
            return CHUANGYE
        if code.startswith("688"):
            return KECHUANG
        if code.startswith("60"):
            return SHANGHAI
        if code.startswith("00"):
            return SHENZHEN
        if code.startswith("8") or code.startswith("9") or code.startswith("4"):
            return BEIJING
        return UNKNOW

    # 计算涨停股价
    def get_limit_up_price(self):
        if self.Type == SHANGHAI or self.Type == SHENZHEN:
            return self.YesterdayPrice * 1.1
        if self.Type == KECHUANG or self.Type == CHUANGYE:
            return self.YesterdayPrice * 1.2
        if self.Type == BEIJING:
            return self.YesterdayPrice * 1.3

    # 判断股价是否 可能会 cross EMA
    def if_may_cross_EMA(self, ema=250):
        if ema == 250 and self.YesterdayPrice < self.EMA250 <= self.get_limit_up_price():
            return True
        if ema == 120 and self.YesterdayPrice < self.EMA120 <= self.get_limit_up_price():
            return True
        return False

    # 判断股价是否已经大于年线，用来寻找高于年线的个股。
    def is_have_crossed_EMA(self, ema=250):
        if ema == 250 and self.Price >= self.EMA250:
            return True
        if ema == 120 and self.Price >= self.EMA120:
            return True
        return False
