__author__ = 'Administrator'
# coding = utf-8
import sys,socket,time,threading
from ctypes import*

class MdThread(threading.Thread):
    def __init__(self,ip,port):
        threading.Thread.__init__(self)
        self.__ip = ip
        self.__port = port
    def run(self):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.bind((self.__ip,self.__port))
        print("Starting Receiving......")
        print(type(ThostFtdcDepthMarketDataField))
        while True:
            try:
                (data,addr) = sock.recvfrom(1024)
                t = cast( data, POINTER(ThostFtdcDepthMarketDataField))
                print(t.contents.InstrumentID)
                #print(type(t))
                #print(data[0])
                #print(type(data))
            except Exception,ex:
                print ex
                break

class CThostFtdcDepthMarketDataField:
    def __init__(self, HighestPrice=0, BidPrice5=0, BidPrice4=0, BidPrice1=0, BidPrice3=0, BidPrice2=0, LowerLimitPrice=0, OpenPrice=0, AskPrice5=0, AskPrice4=0, AskPrice3=0, PreClosePrice=0, AskPrice1=0, PreSettlementPrice=0, AskVolume1=0, UpdateTime="", UpdateMillisec=0, AveragePrice=0, BidVolume5=0, BidVolume4=0, BidVolume3=0, BidVolume2=0, PreOpenInterest=0, AskPrice2=0, Volume=0, AskVolume3=0, AskVolume2=0, AskVolume5=0, AskVolume4=0, UpperLimitPrice=0, BidVolume1=0, InstrumentID="", ClosePrice=0, ExchangeID="", TradingDay="", PreDelta=0, OpenInterest=0, CurrDelta=0, Turnover=0, LastPrice=0, SettlementPrice=0, ExchangeInstID="", LowestPrice=0):
        self.HighestPrice=HighestPrice
        self.BidPrice5=BidPrice5
        self.BidPrice4=BidPrice4
        self.BidPrice1=BidPrice1
        self.BidPrice3=BidPrice3
        self.BidPrice2=BidPrice2
        self.LowerLimitPrice=LowerLimitPrice
        self.OpenPrice=OpenPrice
        self.AskPrice5=AskPrice5
        self.AskPrice4=AskPrice4
        self.AskPrice3=AskPrice3
        self.PreClosePrice=PreClosePrice
        self.AskPrice1=AskPrice1
        self.PreSettlementPrice=PreSettlementPrice
        self.AskVolume1=AskVolume1
        self.UpdateTime=UpdateTime
        self.UpdateMillisec=UpdateMillisec
        self.AveragePrice=AveragePrice
        self.BidVolume5=BidVolume5
        self.BidVolume4=BidVolume4
        self.BidVolume3=BidVolume3
        self.BidVolume2=BidVolume2
        self.PreOpenInterest=PreOpenInterest
        self.AskPrice2=AskPrice2
        self.Volume=Volume
        self.AskVolume3=AskVolume3
        self.AskVolume2=AskVolume2
        self.AskVolume5=AskVolume5
        self.AskVolume4=AskVolume4
        self.UpperLimitPrice=UpperLimitPrice
        self.BidVolume1=BidVolume1
        self.InstrumentID=InstrumentID
        self.ClosePrice=ClosePrice
        self.ExchangeID=ExchangeID
        self.TradingDay=TradingDay
        self.PreDelta=PreDelta
        self.OpenInterest=OpenInterest
        self.CurrDelta=CurrDelta
        self.Turnover=Turnover
        self.LastPrice=LastPrice
        self.SettlementPrice=SettlementPrice
        self.ExchangeInstID=ExchangeInstID
        self.LowestPrice=LowestPrice
        self.vcmap={}
    def __repr__(self): return "<%s>" % ",".join(["%s:%s" % (x, getattr(self, x)) for x in ['HighestPrice', 'BidPrice5', 'BidPrice4', 'BidPrice1', 'BidPrice3', 'BidPrice2', 'LowerLimitPrice', 'OpenPrice', 'AskPrice5', 'AskPrice4', 'AskPrice3', 'PreClosePrice', 'AskPrice1', 'PreSettlementPrice', 'AskVolume1', 'UpdateTime', 'UpdateMillisec', 'AveragePrice', 'BidVolume5', 'BidVolume4', 'BidVolume3', 'BidVolume2', 'PreOpenInterest', 'AskPrice2', 'Volume', 'AskVolume3', 'AskVolume2', 'AskVolume5', 'AskVolume4', 'UpperLimitPrice', 'BidVolume1', 'InstrumentID', 'ClosePrice', 'ExchangeID', 'TradingDay', 'PreDelta', 'OpenInterest', 'CurrDelta', 'Turnover', 'LastPrice', 'SettlementPrice', 'ExchangeInstID', 'LowestPrice']])
    def __str__(self): return u"abcdefg"
    def getval(self, n):
        if n in []:
            return self.vcmap[n]["'%s'" % getattr(self, n)].encode("utf-8")
        else: return getattr(self, n)

class TestStruct(Structure):
    _fields_=[
                ("ValueA",c_int),
                ("StringA",c_char*9)
            ]
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
    data = ThostFtdcDepthMarketDataField()
    POINTER(ThostFtdcDepthMarketDataField)
    print(sys.getsizeof(data))
    print(data.ExchangeInstID)
    md.start()

