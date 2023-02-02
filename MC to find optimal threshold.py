# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:50:30 2023

@author: HP
"""
import numpy as np
import pandas as pd
import math
#参数设定
minute = 200000#模拟多少分钟
feerate = 0.0001
#期权参数
pnow = 3400
k = 3400
rf = 0.03
remainingday = 93
yearvol = 0.1257
 
#获取期权gamma值
def getgamma(pnow,k,rf,remainingday,yearvol):
    d1 = ((math.log(pnow/k))+(rf+0.5*yearvol*yearvol)*(remainingday/255))/(yearvol*math.sqrt(remainingday/255))
    gamma = np.exp(-0.5*d1*d1)/(pnow*yearvol*np.sqrt(2*np.pi*remainingday/255))
    return gamma
gamma = getgamma(pnow,k,rf,remainingday,yearvol)
difdelta = pd.read_excel(pd.ExcelFile('delta差分序列.xlsx'),'Sheet1')
result = pd.DataFrame(columns=('阈值','gamma损失','交易次数','交易手续费损失','总期望损失'))
for gap in range(1,101):
    gap = gap/1000
    lose = 0#记录损失数
    hedge = 0#记录对冲次数
    nowplace = 0
    for i in range(0,minute):
        nowplace = nowplace + difdelta['difdelta'][np.random.randint(0,7468)]
        if np.abs(nowplace) > gap:
            changep = nowplace / gamma
            lose = lose + 0.5*gamma*changep*changep
            nowplace = 0
            hedge = hedge + 1
        if range == minute-1 and nowplace !=0:
            #最后一分钟结转所有损失
            lose = lose + 0.5*gamma*changep*changep
 
    result = result.append([{'阈值':gap,'gamma损失':lose,'交易次数':hedge,'交易手续费损失':hedge*pnow*feerate,'总期望损失':hedge*pnow*feerate+lose}])
result.to_excel('寻找最优阈值.xlsx')