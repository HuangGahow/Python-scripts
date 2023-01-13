# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 16:08:26 2022

@author: HP
"""
def check(func): #定义装饰器check
    def newfunc(a,b): #定义函数模板，即如何处理func
        if type(a)==type(0) and type(b)==type(0):
            return func(a,b)
        else:
            print('Type must be number!')
            return None
    return newfunc #将处理后的func作为新函数newfunc输出

@check
def plus(a,b):
    return a+b

#主程序，计算1+2
plus(1,'kk')
 
