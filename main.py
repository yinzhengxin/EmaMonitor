import json

import pandas as pd
import market
import gradio as gr

import stock

May_Cross = 'may_cross'
Have_Crossed = 'have_crossed'
Pan_Zhong_Mode = '盘中机会'
Pan_Hou_Mode = '盘后寻票'


# get_may_cross_ema_stock 查询今日可能穿越年线的股票：
# 1. 昨日收盘价低于年线 2.今日如果涨停股价会高于年线（区分有些涨停为20cm）
# 输入参数：1.均线（默认250） 2.市值要求 3.题材板块
# 输入参数：4.创业板（30XXXX）/科创板（688XXX）/主板（60XXXX/00XXXX）/北交所（8XXXXX/9XXXXX/4XXXXX)
# 默认参数： 250均线 总市值>100亿 全题材板块 主板+创业+科创
# 逻辑：1. 查询获取股票候选池 2.筛选符合条件的股票
# 查询规划：大于等于100亿，0-100亿 100-500亿 500-2000亿 大于2000亿
def get_cross_ema_stock(zhishu_name="半导体",
                        time_mode=market.Pan_Zhong_Mode, cross_mode=May_Cross,
                        ema=250, stock_type="",
                        min_val=100, max_val=100000):
    print(
        f'{zhishu_name} {ema}均线 时间模式：{time_mode} cross模式：{cross_mode} 股票类型:{stock_type}, {min_val}-{max_val}亿市值')
    cross_ema_stocks = []
    stocks = market.get_constituent_stock(zhishu_name, time_mode)
    for s in stocks:
        if stock_type != stock.ALLTYPE and stock_type != "" and stock_type != s.Type:
            continue
        if s.MarketValue < min_val or s.MarketValue > max_val:
            continue
        if cross_mode == May_Cross and s.if_may_cross_EMA(ema):
            cross_ema_stocks.append(s)
        if cross_mode == Have_Crossed and s.is_have_crossed_EMA(ema):
            cross_ema_stocks.append(s)
    return cross_ema_stocks


# gradio 指数选择涨幅排行榜
def zhishu_input():
    zhishu_df = market.get_top_zhishu()
    zhishu_list = zhishu_df['指数简称'].tolist()
    return gr.Dropdown(choices=zhishu_list, interactive=True)


stock_type_options = [stock.ALLTYPE, stock.SHANGHAI, stock.SHENZHEN, stock.KECHUANG, stock.CHUANGYE, stock.BEIJING]

# gradio 下拉框选择ema
ema_options = [120, 250]

# gradio 下拉框选择函数
market_value_options = ['All', '小于100亿', '大于100亿', '100-500亿', '大于500亿']


def convert_market_value_input(s):
    if s == 'All':
        return 0, 100000
    elif s == '小于100亿':
        return 0, 100
    elif s == '大于100亿':
        return 100, 100000
    elif s == '100-500亿':
        return 100, 500
    elif s == '大于500亿':
        return 500, 100000
    else:
        return 0, 0


time_mode_options = [Pan_Zhong_Mode, Pan_Hou_Mode]


def convert_time_mode_input(s):
    if s == Pan_Zhong_Mode:
        return market.Pan_Zhong_Mode
    if s == Pan_Hou_Mode:
        return market.Pan_Hou_mode


cross_mode_options = [May_Cross, Have_Crossed]


# 处理输入并生成输出的函数
def process_inputs(zhishu_dropdown, zhishu_text,
                   stock_type_dropdown, ema_dropdown, market_value_dropdown,
                   time_mode_dropdown, cross_mode_dropdown):
    # 如果有输出指数名称，用指数名称。没有用指数名称，用选择的数据。
    zhishu_name = ''
    if zhishu_text:
        zhishu_name = zhishu_text
    elif zhishu_dropdown:
        zhishu_name = zhishu_dropdown
    if zhishu_name == "":
        return
    # 转化输入，调用函数查询 cross EMA 股票
    min_val, max_val = convert_market_value_input(market_value_dropdown)
    cross_ema_stocks = get_cross_ema_stock(zhishu_name,
                                           convert_time_mode_input(time_mode_dropdown), cross_mode_dropdown,
                                           ema_dropdown, stock_type_dropdown,
                                           min_val, max_val)
    df = pd.DataFrame([vars(s) for s in cross_ema_stocks])

    # 设置dataframe 格式，然后改变style 为了展示
    df['Percentage'] = pd.to_numeric(df['Percentage'], errors='coerce')
    df['MarketValue'] = pd.to_numeric(df['MarketValue'], errors='coerce')
    df['YesterdayPrice'] = pd.to_numeric(df['YesterdayPrice'], errors='coerce')
    df['EMA250'] = pd.to_numeric(df['EMA250'], errors='coerce')
    df['EMA120'] = pd.to_numeric(df['EMA120'], errors='coerce')

    # dataframe 颜色设置
    def color_condition(value):
        if value > 0:
            return 'color: red'
        elif value < 0:
            return 'color: green'
        else:
            return ''

    styled_df = df.style.applymap(color_condition, subset=['Percentage'])
    styled_df.format("{:.2f}", subset=df.select_dtypes(include='float').columns)

    return styled_df


if __name__ == '__main__':
    zhishu_list = market.get_top_zhishu()['指数简称'].tolist()
    with gr.Blocks() as demo:
        # 输入设置为同一行
        with gr.Row():
            # 同花顺指数，初始化。同花顺指数，点击更新按钮，更新内容
            zhishu_dropdown = gr.Dropdown(label="同花顺指数", choices=zhishu_list)
            update_button = gr.Button("更新")
            update_button.click(zhishu_input, outputs=zhishu_dropdown)
            zhishu_text = gr.Textbox(label="输入指数名称")
            type_input = gr.Dropdown(stock_type_options, label="股票类型", value=stock.ALLTYPE)
            ema_input = gr.Dropdown(ema_options, label="均值", value=250)
            market_value_input = gr.Dropdown(market_value_options, label="市值", value='大于100亿')
            time_mode_input = gr.Dropdown(time_mode_options, label="time_mode", value=Pan_Zhong_Mode)
            cross_mode_input = gr.Dropdown(cross_mode_options, label="cross_mode", value=May_Cross)

        output = gr.DataFrame(label='输出结果')
        btn = gr.Button("提交")
        btn.click(process_inputs, inputs=[zhishu_dropdown, zhishu_text,
                                          type_input, ema_input, market_value_input,
                                          time_mode_input, cross_mode_input], outputs=output)

    demo.launch()
    # 同花顺股票的链接 https://stockpage.10jqka.com.cn/300550/
