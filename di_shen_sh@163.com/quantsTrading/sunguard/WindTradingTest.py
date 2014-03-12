#encoding:utf-8
from WindPy import w
import time
w.start()

class Trading():      
    def __init__(self,TD,tradingOrder):
        self.TD=TD
        self.tradingOrder=tradingOrder
        TSNames=list(set([x[0] for x in tradingOrder]+[x[1] for x in tradingOrder]))
        self.tsData={}
        for i in range(len(TSNames)):
            self.tsData[TSNames[i]]=[]
     
    def OnTickSpread(self,Tick):
        if self.tsData.has_key(str(Tick.Codes[0])):       
            self.tsData[str(Tick.Codes[0])].append(Tick.Data[0][0])
            print tsData
            
        for i in range(len(self.tradingOrder)):
            if self.tsData[self.tradingOrder[i][0]]!=[] and self.tsData[self.tradingOrder[i][1]]!=[]:
                if self.tsData[self.tradingOrder[i][0]][-1]-self.tsData[self.tradingOrder[i][1]][-1]*self.tradingOrder[i][2]>self.tradingOrder[i][4] or self.tsData[self.tradingOrder[i][0]][-1]-self.tsData[self.tradingOrder[i][1]][-1]*self.tradingOrder[i][2]<self.tradingOrder[i][3]:    
                    #定义买单下单参数,并下单
                    print'it is trading spread order between %s and %s'%(self.tradingOrder[i][0],self.tradingOrder[i][1])
                    instrument_id=self.tradingOrder[i][0]
                    direction='buy'
                    limitPrice=w.wsq(instrument_id,'rt_last').Data[0]
                    volume=1
                    logonid=2
                    w.torder(instrument_id,direction,limitPrice,volume,logonid=logonid)
                    
                    #定义卖单下单参数,并下单
                  
                    instrument_id=self.tradingOrder[i][1]
                    direction='short'
                    limitPrice=w.wsq(instrument_id,'rt_last').Data[0]
                    volume=self.tradingOrder[i][2]
                    logonid=2
                    w.torder(instrument_id,direction,limitPrice,volume,logonid=logonid)        

     
#定义交易对象,此对象来自于计算机器结果
tradingOrder=[['RU1401.SHF', 'FG401.CZC', 36.011767364126612, -28373.745064529503, -33208.077687938567], ['ZN1401.SHF', 'TA401.CZC', 1.2126731163504074, 5500.6030064563192, 4893.9256643498748], ['RU1401.SHF', 'J1401.DCE', 17.642695764706176, -6310.4765649161745, -8590.0412593592864], ['RU1401.SHF', 'TA401.CZC', 7.6723619297322729, -38316.284059386315, -42628.309323957808], ['CU1401.SHF', 'RU1401.SHF', 1.0815425178390803, 31978.191774908541, 29644.633609589815], ['AG1312.SHF', 'AU1312.SHF', 30.191027322441442, -3600.9750756256853, -3970.7648976048631]]

TSNames=list(set([str(x[0]) for x in tradingOrder]+[str(x[1]) for x in tradingOrder]))
#登陆下单
TD=w.tlogon('0000',0,['W675324301','W675324302'],'000000',['sh','cfe'])
print TD
#启动OnTickSpread交易策略
#print w.wsq("000001.sz","rt_last")
data=w.wsq("000001.sz","rt_last",func=Trading(TD,tradingOrder).OnTickSpread)
print data
while True:
    time.sleep(1)