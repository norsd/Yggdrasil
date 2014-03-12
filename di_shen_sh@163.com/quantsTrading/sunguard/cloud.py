#-*- coding=utf-8 -*-
from KSTraderApi import KSTraderApi, KSTraderSpi
from KSMdApi import KSMdApi, KSMdSpi
import KSUserApiStruct
import KSUserApiType
from angelEyes import *
import time as time
import numpy as np
import pymongo
import Yggdrasil as Ygg
from pymongo import ASCENDING, DESCENDING
import xlrd as xl
import ConfigParser
import WindPy as wind
import datetime
import multiprocessing
import threading
import os
__author__ = 'Justin'

class tradingData():
    def __init__(self,spi,strategyName):
        self.spi=spi
        #先确认下单日期
        connection=pymongo.Connection('localhost',27017)
        db=connection.commodityTrading
        res=db.UserLogin.find({},{"TradingDay":1,"_id":0}).sort("TradingDay")
        self.tradingDay=[x for x in res][-1]["TradingDay"]
        #找到最新下参考号，并加1
        res=db.tradingRecord.find({"TradingDay":self.tradingDay},{"OrderRef":1,"_id":0})
        resList=[x for x in res]
        self.orderRef=str(sorted([int(x['OrderRef']) for x in resList])[-1]+1)
	self.strategyName=strategyName
    
    def inputOrderField(self,broker_id,investor_id,instrument_id,volume,limitPrice,orderPriceType,direction,combOffSetFlag,combHedgeFlag):
        data = KSUserApiStruct.CThostFtdcInputOrderField()
        #经纪公司代码
        data.BrokerID = broker_id
        #投资者代码
        data.InvestorID = investor_id
        #合约代码
        data.InstrumentID = instrument_id
        #instrument_id
        #报单引用
        data.OrderRef = self.orderRef
        #报单价格条件: 限价
        data.OrderPriceType = orderPriceType
        #买卖方向: 
        data.Direction = direction
        #组合开平标志: 开仓
        data.CombOffsetFlag = combOffSetFlag
        #组合投机套保标志
        data.CombHedgeFlag = combHedgeFlag
        #价格
        data.LimitPrice = limitPrice
        #数量: 1
        data.VolumeTotalOriginal = volume
        #有效期类型: 当日有效
        data.TimeCondition = KSUserApiType.THOST_FTDC_TC_GFD
        #成交量类型: 任何数量
        data.VolumeCondition = KSUserApiType.THOST_FTDC_VC_AV
        #最小成交量: 0
        data.MinVolume = 0
        #触发条件: 立即
        data.ContingentCondition = KSUserApiType.THOST_FTDC_CC_Immediately
        #强平原因: 非强平
        data.ForceCloseReason = KSUserApiType.THOST_FTDC_FCC_NotForceClose
        #自动挂起标志: 否
        data.IsAutoSuspend = 0
        #请求编号
        self.spi.requestid +=1
        data.RequestID = self.spi.requestid
        #用户强评标志: 否
        data.UserForceClose = 0 
        #用户强评标志: 否
        data.UserForceClose = 0
	
	#continue to insert to the table of tradingRecord 
	connection=pymongo.Connection('localhost',27017)
	db=connection.commodityTrading	
	res={"InvestorID":data.InvestorID,"BrokerID":data.BrokerID,"StrategyName":self.strategyName,"OrderRef":self.orderRef,"TradingDay":self.tradingDay,"Volume":data.VolumeTotalOriginal,"InstrumentID":data.InstrumentID,"Direction":data.Direction,"OrderPriceType":data.OrderPriceType,"CombOffsetFlag":data.CombOffsetFlag}
	db.tradingRecord.insert(res)	 
        return data

class TD():
    def __init__(self,broker_id,investor_id,front,passwd):
        self.broker_id=broker_id
        self.investor_id=investor_id
        self.passwd=passwd
        self.front=front
        self.logonID()
    
    def logonID(self):
	global spi
        user = KSTraderApi.CreateKSTraderApi("log_trader")
        spi = myTraderSpi(broker_id = self.broker_id,investor_id = self.investor_id,passwd = self.passwd)
        user.RegisterSpi(spi)
        user.SubscribePublicTopic(2)
        user.SubscribePrivateTopic(2)
        user.RegisterFront(self.front)
        t=threading.Thread(target=user.Init,args=())
        self.user=user
        self.spi=spi        
        t.start()
        t.join() 
        time.sleep(3)   
	
class MD():
    def __init__(self,instruments,broker_id,investor_id,front,passwd,fnOnTick):
        self.broker_id=broker_id
        self.investor_id=investor_id
        self.passwd=passwd
        self.front=front
	self.instruments=instruments 
	self.OnTick=fnOnTick
	self.logonID()
    
    def logonID(self):
        user = KSMdApi.CreateKSMdApi("log_md")
        spi = myMdSpi(instruments = self.instruments,broker_id = self.broker_id,investor_id = self.investor_id,passwd = self.passwd,fnOnTick=self.OnTick)
        user.RegisterSpi(spi)
        user.RegisterFront(self.front)
        t=threading.Thread(target=user.Init,args=())
        self.user=user
        self.spi=spi        
        t.start()
        t.join() 
        time.sleep(4) 
      
class strategy():   
    def strategySpread(self,startDate,endDate,assetCode,sigmaMultiplier,tableName):
        startDate=Ygg.dataOperation().strToDate(startDate)
        endDate=Ygg.dataOperation().strToDate(endDate)
        folderPath=os.getcwd()
        #提取期货数据 
        data=Ygg.dataOperation().retrieveData(assetCode,startDate,endDate)
         #进行价差分析运算
        [res0,startDate,endDate]=Ygg.strategy().spreadSpeculation(data,folderPath,sigmaMultiplier)
         #写入数据库
        Ygg.dataOperation().backtestDBInsert(res0,startDate,endDate,tableName)     
        
class strategyPreparation():
    def tradingFilter(self,BetaADF,correlation):
        #计算交易清单  
        connection=pymongo.Connection('localhost',27017)
        db=connection.backtestResult
        res=db.spread.find({"BetaADF":{"$lte":float(BetaADF)},"correlation":{"$gte":float(correlation)}},{"BetaADF":1,"name1":1,"name2":1,"beta":1,"sigma":1,"mean":1}).sort("correlation",1)
        group=[[x["beta"],x["name1"],x["name2"],x["mean"],x["sigma"]] for x in res]
        
        #导入交易准备数据库
        preDate=datetime.datetime.today()
        db=connection.tradingPreparation
        tempfinal=[[preDate]+[x[0],x[1],x[2],x[3]+1.5*x[4],x[3]-1.5*x[4]] for x in group]
        columnName=['preDate','Beta','name1','name2','upBound','downBound']
        finalDict=[dict(zip(columnName,x)) for x in tempfinal]
        #insert into the database
        db.spread.create_index([("preDate",DESCENDING)])
        db.spread.insert(finalDict)  
    
    #从数据库获取临时交易列表
    def tradingList(self,strategyName):
        connection=pymongo.Connection('localhost',27017)
        db=connection.tradingPreparation
        exec'res=db.%s.find()'%(strategyName)
        tradingList=[[x["upBound"],x["downBound"],x["Beta"],x["name1"],x["name2"]] for x in res]
        return tradingList
    
    #交易列表整理为交易篮子
    def tradingOrder(self,tradingTemp,path):
        tradingBasket=[]
        wb=xl.open_workbook(path)
    
        commodityContract=wb.sheet_by_index(0).col_values(0,1)
        
        for i in range(len(tradingTemp)):
            name1=tradingTemp[i][3]
            name2=tradingTemp[i][4]
            beta=tradingTemp[i][2]
            upBound=tradingTemp[i][0]
            downBound=tradingTemp[i][1]
            
            joinName1=name1[:name1.find(".")]
            joinName2=name2[:name2.find(".")]
        
            tradingName1=commodityContract[[x.startswith(joinName1) for x in commodityContract].index(True)][:-4]
            tradingName2=commodityContract[[x.startswith(joinName2) for x in commodityContract].index(True)][:-4]
            tradingBasket.append([tradingName1,tradingName2,beta,upBound,downBound])
        return  tradingBasket    

class Trading():
	
    def __init__(self,TD,tradingOrder):
	self.TD=TD
	self.tradingOrder=tradingOrder
	TSNames=list(set([x[0] for x in tradingOrder]+[x[1] for x in tradingOrder]))
	self.tsData={}
	self.askData={}
	self.bidData={}
	for i in range(len(TSNames)):
	    self.tsData[TSNames[i]]=[]
	    self.askData[TSNames[i]]=[]
	    self.bidData[TSNames[i]]=[]
	
    def OnTick(self,Tick):
	print repr(Tick)
	if self.tsData.has_key(Tick.InstrumentID):	
	    self.tsData[Tick.InstrumentID].append(Tick.LastPrice)
	    self.askData[Tick.InstrumentID].append(Tick.AskPrice1)  
	    self.bidData[Tick.InstrumentID].append(Tick.BidPrice1)  
	
	for i in range(len(self.tradingOrder)):
	    if self.tsData[self.tradingOrder[i][0]]!=[] and self.tsData[self.tradingOrder[i][1]]!=[]:
		if self.tsData[self.tradingOrder[i][0]][-1]-self.tsData[self.tradingOrder[i][1]][-1]*self.tradingOrder[i][2]>self.tradingOrder[i][4] or self.tsData[self.tradingOrder[i][0]][-1]-self.tsData[self.tradingOrder[i][1]][-1]*self.tradingOrder[i][2]<self.tradingOrder[i][3]:    
		    #定义买单下单参数
		    strategyName="spreadTrading"
		    instrument_id=self.tradingOrder[i][0]
		    limitPrice=self.askData[self.tradingOrder[i][0]][-1]
		    volume=Ygg.dataOperation().findMulti(self.tradingOrder[i][2])
		    orderPriceType='2'
		    direction='0'
		    combOffSetFlag='0'
		    combHedgeFlag='1'
		    #定义下单结构体
		    dataBuy=tradingData(self.TD.spi,strategyName).inputOrderField(self.TD.broker_id,self.TD.investor_id,instrument_id,volume,limitPrice,orderPriceType,direction,combOffSetFlag,combHedgeFlag)
		    
		    #定义卖单下单参数
		    instrument_id=self.tradingOrder[i][1]
		    limitPrice=self.bidData[self.tradingOrder[i][1]][-1]
		    volume=round(self.tradingOrder[i][2]*Ygg.dataOperation().findMulti(self.tradingOrder[i][2]))
		    orderPriceType='2'
		    direction='1'
		    combOffSetFlag='0'
		    combHedgeFlag='1'		
		    #定义下单结构体
		    dataSell=tradingData(self.TD.spi,strategyName).inputOrderField(self.TD.broker_id,self.TD.investor_id,instrument_id,volume,limitPrice,orderPriceType,direction,combOffSetFlag,combHedgeFlag)
		    #下单
		    self.TD.user.ReqOrderInsert(dataBuy,self.TD.spi.requestid)
		    self.TD.user.ReqOrderInsert(dataSell,self.TD.spi.requestid)