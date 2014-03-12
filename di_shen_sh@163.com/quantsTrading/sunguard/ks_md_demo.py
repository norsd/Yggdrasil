#-*- coding=utf-8 -*-
"This is the main demo file"
from KSMdApi import KSMdApi, KSMdSpi
import KSUserApiStruct
import time
#import threading


class myMdSpi(KSMdSpi):
    requestid = 0
    def __init__(self, instruments, broker_id,
                 investor_id, passwd,**kwargs):
        self.instruments = instruments
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.passwd = passwd
        self.is_login = 0
        
        
    def OnFrontConnected(self):
        print "OnFrontConnected:"
        self.Req_UserLogin(self.broker_id, self.investor_id, self.passwd)
        
    def OnFrontDisConnected(self, reason):
        print "onFrontDisConnected:", repr(reason)        

    def Req_UserLogin(self, broker_id, investor_id, passwd):
        req = KSUserApiStruct.CThostFtdcReqUserLoginField(BrokerID = broker_id, UserID = investor_id, Password = passwd)
        self.requestid += 1
        r = self.api.ReqUserLogin(req, self.requestid)
        if r == 0: print u"发送用户登录请求: 成功\n"
        else: print u"发送用户登录请求: 失败\n"

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        print "OnRspUserLogin", bIsLast, repr(pRspInfo)
        if bIsLast and not self.isErrorRspInfo(pRspInfo):
            print "get today's trading day:", repr(self.api.GetTradingDay())
            self.is_login = 1
            self.requestid += 1
            self.api.SubscribeMarketData(inst)
	
    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        print "OnRspSubMarketData", repr(pRspInfo)
        print repr(pSpecificInstrument)
        if bIsLast and not self.isErrorRspInfo(pRspInfo):
            self.requestid+=1
            #self.api.UnSubscribeMarketData(inst)
			
    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        print "OnRspUnSubMarketData", repr(pRspInfo)
        print repr(pSpecificInstrument)
        if bIsLast and not self.isErrorRspInfo(pRspInfo):
            self.Req_UserLogout(self.broker_id, self.investor_id)

    def Req_UserLogout(self, broker_id, investor_id):
        req = KSUserApiStruct.CThostFtdcUserLogoutField(BrokerID = broker_id, UserID = investor_id)
        self.requestid+=1
        r = self.api.ReqUserLogout(req, self.requestid)
        if r == 0: print u"发送用户录出请求: 成功\n"
        else: print u"发送用户录出请求: 失败\n"
        
    def OnRtnDepthMarketData(self, depth_marketdata):
        print "OnRtnDepthMarketData"
        print repr(depth_marketdata)
        #print depth_marketdata.LastPrice
        
    def OnRspError(self, info, RequestId, IsLast):
        print " Error"
        self.isErrorRspInfo(info)

    def isErrorRspInfo(self, info):
        if info.ErrorID != 0:
            print "ErrorID = ", info.ErrorID, ", ErrorMsg = ", info.ErrorMsg
        return info.ErrorID

    def OnHeartBeatWarning(self, nTimeLapse):
        print "onHeartBeatWarning", nTimeLapse

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        print "OnRspUserLogout", repr(pRspInfo)
        print repr(pUserLogout)
	



def ks_spi_init(inst,front,broker_id,investor_id,passwd):
    user = KSMdApi.CreateKSMdApi("log_md")
    global spi
    spi = myMdSpi(instruments = inst,broker_id = broker_id,investor_id = investor_id,passwd = passwd)
    user.RegisterSpi(spi)
    user.RegisterFront(front)
    user.Init()

    
inst = [u'IF1312', u'cu1312']
#front = ["tcp://124.160.44.166:17159"]
front = "tcp://210.5.154.195:13153"
#broker_id = ["3748FD77"]
broker_id="6A89B428"
#investor_id = ["90024727"]
investor_id="40000006"
#passwd="123456"
passwd = "980526"


if __name__ == "__main__": 
    ks_spi_init(inst,front,broker_id,investor_id,passwd)
    while True:
        time.sleep(1)
    
    
    
