#-*- coding:utf-8 -*-
import cloud 
import ConfigParser
import Yggdrasil as Ygg
import xlrd as xl
import os


__author__ = 'Justin'
    

#公共参数准备    
config = ConfigParser.ConfigParser()
config.readfp(open('data.ini'))  
stockAccount=config.get("Trading","stockAccount")
futureAccount=config.get("Trading","futureAccount")
startDate=config.get("Date","startDate")
endDate=config.get("Date","endDate")
commodityCode=config.get("Data","commodityIndex").split(",")
securityMarginCode=config.get("Data","securityMargin").split(",")

#提取wind行情参数
quoteStartDate='1995-01-01'
quoteEndDate='2013-11-01'
fields=config.get("Data","fields")
commodityName="commodityIndex"
securityMarginName="securityMargin"

#提取wind行情并写入数据库
#Ygg.dataOperation().getLowFreData(commodityName,quoteStartDate,quoteEndDate,fields,commodityCode)
Ygg.dataOperation().getLowFreData(securityMarginName,quoteStartDate,quoteEndDate,fields,securityMarginCode)

'''
#主力合同位置
#C:\Users\Skywalker\Documents\Python\quantsTrading\configurationFile
path='%s/configurationFile/commodityContract.xlsx'%(os.getcwd()[0:-8])

#价差参数
sigmaMultiplier=config.get("Assumption","sigmaMultiplier").split(",")

#价差策略计算
strategyName='spread'
#strategy=cloud.strategy()
#strategy.strategySpread(startDate,endDate,commodityCode,sigmaMultiplier,strategyName)

#策略选择规则参数
BetaADF=0.1
correlation=0.7

#筛选并建立交易准备数据库
pre=cloud.strategyPreparation()
pre.tradingFilter(BetaADF, correlation)

#建立交易订单篮子
#tradingOrder=pre.tradingOrder(pre.tradingList(strategyName),path) 
tradingOrder=[["IF1312","al1312",0.44,-3874,-4164],["CF1401","a1401",0.71,17002,16116],["al1312","fu1312",0.88,10700,9902],["al1312","m1401",1.45,10370,9499],["ru1401","m1401",15.94,-27145,-34804],["cu1312","ru1401",1.08,31978,29644]]
tSNames=list(set([str(x[0]) for x in tradingOrder]+[str(x[1]) for x in tradingOrder]))

#开始交易

#配置交易参数
#南华的配置参数
#front = "tcp://124.160.44.166:17159"
#broker_id = "3748FD77"
#investor_id = "90024727"
#passwd="980526"
#银河
#front = "tcp://124.193.182.51:18998"

#金仕达配置参数
front = "tcp://210.5.154.195:13153"
broker_id="6A89B428"
investor_id="40000006"
passwd = "980526" 
instruments = tSNames
#注册交易用户
TD=cloud.TD(broker_id,investor_id,front,passwd)
MD=cloud.MD(instruments,broker_id,investor_id,front,passwd,cloud.Trading(TD,tradingOrder).OnTick)
#定义下单参数
instrument_id='IF1312'
limitPrice=2233
volume=1
orderPriceType='2'
direction='0'
combOffSetFlag='0'
combHedgeFlag='1'

#定义下单结构体
#限价单
strategyName="trendTrading"
data=cloud.tradingData(TD.spi,strategyName).inputOrderField(broker_id,investor_id,instrument_id,volume,limitPrice,orderPriceType,direction,combOffSetFlag,combHedgeFlag)
TD.user.ReqOrderInsert(data,TD.spi.requestid)
print 'finish'

'''