__author__ = 'Administrator'
# coding = utf-8
import copy
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import socket
import sys
import threading
import time

from ctypes import*
from datetime import datetime
from math import e

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from norlib_python.Thread import *
from Api.DATASPAN import *

class MdThread(threading.Thread):
    def __init__(self,ip,port):
        threading.Thread.__init__(self)
        self.__ip = ip
        self.__port = port
        self.dtData = {}
        self.__ontickcbs = []
    def run(self):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.bind((self.__ip,self.__port))
        print("Starting Receiving......")
        while True:
            try:
                (data,addr) = sock.recvfrom(1024)
                t = copy.deepcopy( cast( data, POINTER(ThostFtdcDepthMarketDataField)).contents)
                #self.dtData.__setitem__(t.InstrumentID, t)
                for cb in self.__ontickcbs:
                    try:cb(t)
                    finally:None
            except Exception,ex:
                print ex
                break
    def RegTick(self,callback):
        self.__ontickcbs.append(callback)
    def GetKLineDatas(self, id, dataspan, start, next):
        pass

class View:
    def __init__(self, md, id):
        self.__md = md
        self.__id = id
        self.__datas = []
        self.__times = []
        self.__ShowData()
    def Open(self):
        self.__md.RegTick(self.__OnTick)
    def __OnTick(self, tick):
        if tick.InstrumentID == 'IF1403':
            self.__datas.append(tick.LastPrice)
            strDate = tick.TradingDay
            strTime = tick.UpdateTime
            ms = tick.UpdateMillisec
            dtime = datetime.strptime(" ".join([strDate, strTime, str(ms)]), "%Y%m%d %H:%M:%S %f")
            self.__times.append(dtime)
            pass
    @SetInterval(2)
    def __ShowData(self):
        if not self.__datas:
            return
        if len(self.__datas)>0:
            try:
                #p1 = plt.subplot(110)
                plt.plot(self.__times, self.__datas)
                plt.draw()
                plt.show()
            except a,b:
                print(a)
                print(b)


        #print self.__datas[-1].LastPrice

#CTP Depth Market Data
class ThostFtdcDepthMarketDataField(Structure):
    _fields_ = [
                ("TradingDay",c_char*9),
                ("InstrumentID",c_char*31),
                ("ExchangeID",c_char*9),
                ("ExchangeInstID",c_char*31),
                ("LastPrice",c_double),
                ("PreSettlementPrice",c_double),
                ("PreClosePrice",c_double),
                ("PreOpenInterest",c_double),
                ("OpenPrice",c_double),
                ("HighestPrice",c_double),
                ("LowestPrice",c_double),
                ("Volume",c_int),
                ("Turnover",c_double),
                ("OpenInterest",c_double),
                ("ClosePrice",c_double),
                ("SettlementPrice",c_double),
                ("UpperLimitPrice",c_double),
                ("LowerLimitPrice",c_double),
                ("PreDelta",c_double),
                ("CurrDelta",c_double),
                ("UpdateTime",c_char*9),
                ("UpdateMillisec",c_int),
                ("BidPrice1",c_double),
                ("BidVolume1",c_int),
                ("AskPrice1",c_double),
                ("AskVolume1",c_int),
                ("BidPrice2",c_double),
                ("BidVolume2",c_int),
                ("AskPrice2",c_double),
                ("AskVolume2",c_int),
                ("BidPrice3",c_double),
                ("BidVolume3",c_int),
                ("AskPrice3",c_double),
                ("AskVolume3",c_int),
                ("BidPrice4",c_double),
                ("BidVolume4",c_int),
                ("AskPrice4",c_double),
                ("AskVolume4",c_int),
                ("BidPrice5",c_double),
                ("BidVolume5",c_int),
                ("AskPrice5",c_double),
                ("AskVolume5",c_int),
                ("AveragePrice",c_double),
                ("ActionDay",c_char*9),
                ]


if __name__ == "__main__":
    md = MdThread("127.0.0.1",12345)
    md.start()
    #s = datetime.datetime.now()
    #n = s.AddDays(1)
    #md.GetKLineDatas("IF1403" ,DataSpan.min1, s , n)
    view = View(md,"IF1403")
    #time.sleep(3)
    view.Open()
    print("opened")
    #plt.show()

