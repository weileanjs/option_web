
# 单个策略下合并所有交易，计算单个期权CODE信息
def combine_trade(items):
    option_code_list = list(set(i.OPTION_CODE for i in items))
    d = {}
    item_list = []
    for option_code in option_code_list:
        d[option_code] = {'PRICE':0,'NUM':0,'DELTA':0 ,'GAMMA':0,'THETA':0,'VIX':0,'VEGA':0,'deal_profit':0}
        for item in items:
            if option_code == item.OPTION_CODE:
                try:
                    # 持仓NUM为0，利润保留。  成本价重新计算
                    d[option_code]['PRICE'] = (d[option_code]['PRICE']*d[option_code]['NUM'] + float(item.PRICE)*float(item.NUM))/(d[option_code]['NUM']+item.NUM)
                except Exception as e:
                    d[option_code]['PRICE'] = (d[option_code]['PRICE']*d[option_code]['NUM'] + float(item.PRICE)*float(item.NUM))
                    # print('*********{}'.format(str(e)),d[option_code]['PRICE'])
                d[option_code]['NUM']= d[option_code]['NUM']+item.NUM

                d[option_code]['DELTA'] = float(item.DELTA)
                d[option_code]['GAMMA'] = float(item.GAMMA)
                d[option_code]['THETA'] = float(item.THETA)
                d[option_code]['VEGA'] =  float(item.THETA)
                d[option_code]['deal_profit'] = d[option_code]['deal_profit']+float(item.deal_profit)
                d[option_code]['DAYS'] = item.DAYS
                d[option_code]['VIX'] = item.VIX
                d[option_code]['PRICE_NOW'] = item.PRICE_NOW
                d[option_code]['UTIME'] = item.UTIME
    for k ,v in d.items():
        v['OPTION_CODE'] = k
        item_list.append(v)
    return item_list


def clac_strategy_money(items):
    combine_trade(items)
    TOTAL_DICT = {'OPTION_CODE':'合计'}
    TOTAL_DELTA = 0
    TOTAL_GAMMA = 0
    TOTAL_THETA =0
    TOTAL_VEGA = 0
    TOTAL_PROFIT = 0
    for item in items:
        item.PRICE = int(item.PRICE)
        TOTAL_DELTA = float(item.DELTA)*100 * int(item.NUM) + TOTAL_DELTA
        TOTAL_GAMMA = float(item.GAMMA) * int(item.NUM) + TOTAL_GAMMA
        TOTAL_THETA = float(item.THETA)*100 * int(item.NUM) + TOTAL_THETA
        TOTAL_VEGA = float(item.VEGA)*100 * int(item.NUM) + TOTAL_VEGA
        TOTAL_PROFIT = item.deal_profit + TOTAL_PROFIT
    TOTAL_DICT['TOTAL_DELTA'] = '%0.2f'%TOTAL_DELTA
    TOTAL_DICT['TOTAL_GAMMA'] = '%0.2f'%TOTAL_GAMMA
    TOTAL_DICT['TOTAL_THETA'] = '%0.2f'%TOTAL_THETA
    TOTAL_DICT['TOTAL_VEGA'] = '%0.2f'%TOTAL_VEGA
    TOTAL_DICT['TOTAL_PROFIT'] = '%0.2f'%TOTAL_PROFIT
    return TOTAL_DICT

# 计算单个头寸盈亏
def clac_deal_profit(PRICE,NUM,q_live_price):
    deal_profit = int(int(NUM)*(float(q_live_price)*10000-int(PRICE)))
    return  deal_profit
