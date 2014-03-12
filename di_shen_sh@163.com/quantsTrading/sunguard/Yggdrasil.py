#-*- coding=utf-8 -*-
import ConfigParser
import xlwt
import os
import WindPy as wind
import numpy as np
import matplotlib.pyplot as plt
import math
import rpy2.robjects as robjects
import pymongo
from pymongo import ASCENDING, DESCENDING
import time
import datetime
import xlrd as xl


class dataOperation():
    def findMulti(self,x):
	a=[abs(y*x-round(y*x)) for y in range(1,50)]
	return a.index(np.min(a))+1	
    
    def r2p(self,a):
        row=robjects.r.dim(a)[0]
        col=robjects.r.dim(a)[1]
        return np.array([x for x in a]).reshape(col,row).transpose()
       
    def p2r(self,a):
        row=a.shape[0]
        col=a.shape[1]
        return robjects.r.matrix(list(a.transpose().reshape(1,row*col)[0]),ncol=col)
    
    def trans(self,x):
        x[0]=self.getdate(x[0])  
	
    def insertExcelData(self,path,database,collection):
    	wb=xl.open_workbook(path)
    	names=wb.sheet_by_index(0).row_values(0,1)
    	names=["_id"]+names[1:]
    	nrows=wb.sheet_by_index(0).nrows
    	data=[]
    	for i in range(nrows-2):
    	    data.append(wb.sheet_by_index(0).row_values(i+2,1))
    	    
    	[self.trans(x) for x in data]
    	
    	finalDict=[dict(zip(names,x)) for x in data]
    	connection=pymongo.Connection("localhost",27017)
    	exec("db=connection.%s"%(database))
    	exec("db.%s.drop()"%(collection))
    	exec("db.%s.insert(finalDict)"%(collection))
    	print "finish"
   
    def strToDate(self,str):
	return datetime.datetime(int(str[0:4]),int(str[5:7]),int(str[8:]))
	
    def getdate(self,date):
    	__s_date = datetime.date(1899, 12, 31).toordinal()-1
    	if isinstance(date, float):
    	    date = int(date)
    	    d = datetime.datetime.fromordinal(__s_date + date)
    	    #return d.strftime("%Y-%m-%d") 
	    return d
	  
	
    def retrieveData(self,assetCode,startDate,endDate):
    	[name,date,close]=[[],[],[]]
    	for i in range(len(assetCode)):
    	    connection=pymongo.Connection('localhost',27017)
    	    db=connection.commodityIndex
    	    res=db.daily.find({"date":{"$gte":startDate,"$lte":endDate},"code": "%s"%(assetCode[i])}).sort("date",1)
    	    group=[[x["code"],x["date"],x["CLOSE"]] for x in res]
    	    name.append([x[0] for x in group])
    	    date.append([x[1] for x in group])
    	    close.append([x[2] for x in group])
    	return[close,name,date]
	
    def getLowFreData(self,assetName,startDate,endDate,fields,commodityCode):
    	wind.w.start()
    	finalDict=[]
    	connection=pymongo.Connection('localhost',27017)
    	exec("db=connection.%s"%(assetName))
          
    	for i in range(len(commodityCode)):
    	    print i
    	    #print len(commodityCode)-i
    	    print commodityCode[i]
    	    res=wind.w.wsd(commodityCode[i],fields,startDate,endDate,"Fill=Previous")
    	    #print res
    	    name=res.Codes*len(res.Times)
    	    date=res.Times
    	    tempfinal=zip(name,date,res.Data[0],res.Data[1],res.Data[2],res.Data[3],res.Data[4],res.Data[5],res.Data[6],res.Data[7],res.Data[8],res.Data[9],res.Data[10],res.Data[11])
    	    columnName=['code','date']+res.Fields
    	    finalDict=[dict(zip(columnName,x)) for x in tempfinal]
    	    #insert into the database
    	    db.daily.create_index([("date",DESCENDING),("code",ASCENDING)])
    	    db.daily.insert(finalDict)  
	
	    
    def highFrequencyData(self,Data,name,Date):
    	#transform the data format
    	multiDate=[]
    	for i in range(len(Data)):
    	    multiDate.append(Date)
    	
    	#insert into the database
    	columnName=['_id','closePrice']
    	connection=pymongo.Connection('localhost',27017)
    	db=connection.highFrequencyData	
    	t1=time.time()
    	for i in range(len(Data)):	
    	    temp=zip(Date,Data[i])	
    	    finalDict=[dict(zip(columnName,x)) for x in temp]
    	    exec('db.%s.remove()'%(name[i])) 
    	    exec('db.%s.insert(finalDict)'%(name[i])) 
    	print 'highFrequency%s'%(time.time()-t1)    
    
    
    def priceToReturn(self,a):
        return [x*1.0/y for x,y in zip(-np.diff(a),a[1:])]

     
    def draw(self,spreadTemp,name,meanLine,plusSigma,minusSigma,tPlusSigma,tMinusSigma,folderPath):
        plt.clf()
        plt.plot(spreadTemp)
        plt.plot(meanLine)
        plt.plot(plusSigma)
        plt.plot(minusSigma)
        plt.plot(tPlusSigma)
        plt.plot(tMinusSigma)    
        plt.title('Historic Spread For %s' %(name))
        plt.ylabel('Spread')
        plt.xlabel('Date')
        plt.savefig('%s\SpreadTrading\%s.png'%(folderPath,name), format='png') 
	
    def backtestDBInsert(self,res0,startDate,endDate,tableName):
    	finalDict=[]
    	connection=pymongo.Connection('localhost',27017)
    	db=connection.backtestResult
    	tempfinal=[x+[startDate,endDate] for x in res0]
    	columnName=['name1','name2','standardized spread vol','correlation','mean','sigma','beta','BetaADF','startDate','endDate']
    	finalDict=[dict(zip(columnName,x)) for x in tempfinal]
    	#insert into the database
    	exec'db.%s.create_index([("date",DESCENDING),("name",ASCENDING)])'%(tableName)
    	exec'db.%s.insert(finalDict)'%(tableName)        
	     
        
class strategy(dataOperation):
    
    def spreadSpeculation(self,data,folderPath,sigmaMultiplier):
        x=np.array(data[0])
        y=data[1]
        z=data[2]         
        spreadStatisList=[]
        row=x.shape[0]
        rowList=range(row)
        robjects.r.library("tseries")
        adf=robjects.r('adf.test')  
        [lowMulti,highMulti]=[float(sigmalM) for sigmalM in sigmaMultiplier]
        
        for i in rowList:
            newRow=[k for k in rowList if k!=i]
            rowList=newRow
            for j in newRow:
                if j!=i:
                    robjects.globalEnv['y']=robjects.FloatVector(x[i])
                    robjects.globalEnv['x']=robjects.FloatVector(x[j])
                    lm_res=robjects.r.lm('y~x')
                    beta=lm_res[0][1]
                    betaSpread=list((x[i]-beta*x[j]))
                    #spreadTemp=list((x[i]-beta*x[j]))
                    spreadTempDate=z[0]               
                    r1=self.priceToReturn(x[i])
                    r2=self.priceToReturn(x[j])
                    correlation=np.corrcoef(r1,r2)[0][1]
                    mean=np.mean(betaSpread)
                    sigma=np.std(betaSpread)   
                    betaTemp=[betaCo for betaCo in betaSpread if math.isnan(betaCo)==False]
                    betaAdfResult=adf(betaTemp)[3][0]
                    #name="%s vs %s" %(y[i][0],y[j][0])
		    #i am trying it now
		    name1=y[i][0]
		    name2=y[j][0]
                    meanLine=[mean]*len(z[0])
                    plusSigma=[mean+lowMulti*sigma]*len(z[0])
                    minusSigma=[mean-lowMulti*sigma]*len(z[0])
                    tPlusSigma=[mean+highMulti*sigma]*len(z[0])
                    tMinusSigma=[mean-highMulti*sigma]*len(z[0])
                    #if math.isnan(mean)==False:
                        #self.draw(betaSpread,name,meanLine,plusSigma,minusSigma,tPlusSigma,tMinusSigma,folderPath)
                    #standalization of timeseries
		    #statistics=[name,sigma/abs(mean),correlation,mean,sigma,beta,betaAdfResult]
                    statistics=[name1,name2,sigma/abs(mean),correlation,mean,sigma,beta,betaAdfResult]
                    spreadStatisList.append(statistics) 
        
        spreadStatisList=[x for x in spreadStatisList if math.isnan(x[2])==False]
        
                
        return spreadStatisList,z[0][0],z[0][-1]
    
