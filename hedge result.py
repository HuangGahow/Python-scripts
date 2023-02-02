# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:49:30 2023

@author: HP
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

def bsm(S0,k,r,remainingday,yearvol):
    #输入：（现价,执行价，连续无风险利率3%，剩余天数100天，年波动率0.15）
    #输出：看涨期权价格[0]，看涨期权delta[1]
    d1 = ((np.log(S0/k))+(rf+0.5*yearvol*yearvol)*(remainingday/255))/(yearvol*np.sqrt(remainingday/255))
    d2 = ((np.log(S0/k))+(rf-0.5*yearvol*yearvol)*(remainingday/255))/(yearvol*np.sqrt(remainingday/255))
    nd1 = norm.cdf(d1)
    nd2 = norm.cdf(d2)
    exprt = np.exp(-rf*remainingday/255)
    prise = pnow*nd1-k*exprt*nd2
    return [prise,nd1]
 
# getbsm = bsm(3400,3400,0.03,100,0.15)

    
        
    
k=3400
rf=0.03#连续复利无风险利率
firstremaingday=93#第一天开始交易时剩余交易日，假设期权4月15日到期，距离12月1日还有93个交易日
yearvol=0.1257
 
#其他参数设定
marginrate=0.1#期货保证金率
rr=0.07#年化单利公司资金成本
gap=0.076#组合delta偏差容忍值
feerate=0.0001#期货交易手续费
 
#要记录的参数
#分钟期货交易损益
#分钟保证金利息
 
marketinfo = pd.read_excel(pd.ExcelFile('marketinfo.xlsx'),'Sheet1')
 
#记录净值表格
result = pd.DataFrame(columns=('时间','期权损益','期货损益','息前损益','利息','息后损益','净买入期货份额','剔除时间价值期权损益','剔除时间价值对冲净收益','累计期货手续费'))
#输出交易记录表格
trade = pd.DataFrame(columns=('时间','期货买入净额','调整前组合Delta','调整后组合Delta'))
 
totalfee = 0#统计手续费支出
futureposition = 0
lastprice = marketinfo.iloc[0]['price']
lastbsmprice = bsm(marketinfo.iloc[0]['price'],k,rf,firstremaingday,yearvol)[0]
lastbsmpriceCT = bsm(marketinfo.iloc[0]['price'],k,rf,firstremaingday,yearvol)[0]#剔除时间价值流逝期权价格
for day in range(0,22):
    #21个交易日遍历交易
    for minute in range(0,345):
        if day == 21 and minute == 225:
            #12月31日无夜盘
            break
        nowprice = marketinfo.iloc[day*345+minute]['price']
        nowtime = marketinfo.iloc[day*345+minute]['time']
        getbsm = bsm(nowprice,k,rf,firstremaingday-day-minute/345,yearvol)
        bsmpriceCT = bsm(nowprice,k,rf,firstremaingday,yearvol)[0]#剔除时间价值变化期权价
        optionbsmprice = getbsm[0]
        optionbsmdelta = -getbsm[1]
        profoliodelta = optionbsmdelta + futureposition
        #print("在",nowtime,"时刻的期权价值=",getbsm[0])
        
        #结算本分钟的期货头寸和期权头寸的盈亏
        futureprofit = futureposition*(nowprice-lastprice)
        optionprofit = -(optionbsmprice - lastbsmprice)
        netprofitbeforeinterest = futureprofit + optionprofit
 
        netbuy = 0
        #调整仓位
        if abs(profoliodelta) > gap:
            netbuy = -profoliodelta
            futureposition = futureposition + netbuy
            totalfee = totalfee + nowprice*feerate*abs(netbuy)
            #记录交易记录
            trade = trade.append([{'时间':nowtime,'期货买入净额':netbuy,'调整前组合Delta':profoliodelta,'调整后组合Delta':futureposition+optionbsmdelta}])
 
        #计算本分钟保证利息占用
        interest = futureposition*nowprice*marginrate*rr/255/345
        netprofitafterinterest = netprofitbeforeinterest - interest
 
        #记录本分钟交易数据 '时间','期权损益','期货损益','息前损益','利息','息后损益','净买入期货份额'
        result = result.append([{'时间':nowtime,'期权损益':optionprofit,'期货损益':futureprofit,'息前损益':netprofitbeforeinterest,'利息':interest,'息后损益':netprofitafterinterest,'净买入期货份额':netbuy,'剔除时间价值期权损益':-bsmpriceCT+lastbsmpriceCT,'剔除时间价值对冲净收益':-bsmpriceCT+lastbsmpriceCT+futureprofit-interest,'累计期货手续费':totalfee}], ignore_index=True)
 
        lastprice = nowprice
        lastbsmprice = optionbsmprice#记录本分钟bsm价格给下一分钟使用
        lastbsmpriceCT = bsm(nowprice,k,rf,firstremaingday,yearvol)[0]
        #print(marketinfo.iloc[day*345+minute]['time'])
 
#导出结果
result.to_excel('result.xlsx')
trade.to_excel('trade.xlsx')
