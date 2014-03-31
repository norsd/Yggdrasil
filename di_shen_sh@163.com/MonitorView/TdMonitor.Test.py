import math
import numpy as np
import threading
import time
import wx
import wx.grid



class TdThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__ontdcbs = []

    def run(self):
        print("Starting Receiving......")
        while True:
            for cb in self.__ontdcbs:
                cash = np.random.randint(500000,600000)
                position = np.random.randint(1,3)
                try:cb(cash,position)
                finally:None
            time.sleep(2)

    def Open(self):
        self.start()

    def RegTradeCallback(self,callback):
        self.__ontdcbs.append(callback)


class TestFrame(wx.Frame):
    rowLabels = ["1", "2", "3", "4", "5"]
    colLabels = ["Name", "Cash", "Position", "D", "E"]
    def __init__(self,td):
        wx.Frame.__init__(self, None, title="Grid Headers",size=(500,200))
        grid = wx.grid.Grid(self)
        grid.CreateGrid(5,5)
        for row in range(5):
            grid.SetRowLabelValue(row, self.rowLabels[row])
            grid.SetColLabelValue(row, self.colLabels[row])
            for col in range(5):
                grid.SetCellValue(row, col, 
                        "(%s,%s)" % (self.rowLabels[row], self.colLabels[col]))
        grid.SetCellValue(0,0,"shendi")
        grid.SetCellValue(0,1,"12345.0")
        grid.SetCellValue(0,2,"1")
        self.__grid = grid
        self.__td = td
        self.__td.RegTradeCallback(self.__OnTd)

    def __OnTd(self,cash,position):
        self.__grid.SetCellValue(0,1, str(cash))
        self.__grid.SetCellValue(0,2,str(position))


app = wx.PySimpleApp()
td = TdThread()
frame = TestFrame(td)
td.Open()
frame.Show()
app.MainLoop()