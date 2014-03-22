#-*-coding:utf-8-*-
import wx
from matplotlib.figure import Figure
import matplotlib.font_manager as font_manager
import numpy as np
from TestView import  *

from matplotlib.backends.backend_wxagg import \
  FigureCanvasWxAgg as FigureCanvas
# wxWidgets object ID for the timer
TIMER_ID = wx.NewId()
# number of data points
POINTS = 300

class PlotFigure(wx.Frame):
    """Matplotlib wxFrame with animation effect"""
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="CPU Usage Monitor", size=(600, 400))
        self.fig = Figure((6, 4), 100)
        self.canvas = FigureCanvas(self, wx.ID_ANY, self.fig)
        self.ax = self.fig.add_subplot(111)
        # limit the X and Y axes dimensions
        self.ax.set_ylim(2140, 2150)
        self.ax.set_xlim([0, POINTS])
        self.ax.set_autoscale_on(False)
        self.ax.set_xticks([])
        # we want a tick every 10 point on Y (101 is to have 10
        #self.ax.set_yticks(range(0, 101, 10))
        self.ax.grid(True)
        self.user = [None] * POINTS
        self.l_user,=self.ax.plot(range(POINTS),self.user,label=u'IF1406')

        self.md = MdThread("127.0.0.1",12345)
        self.md.start()
        self.md.RegTick(self.OnTick)
        # add the legend
        self.ax.legend(loc='upper center',
                           ncol=4,
                           prop=font_manager.FontProperties(size=10))
        self.canvas.draw()
        self.bg = self.canvas.copy_from_bbox(self.ax.bbox)
        #wx.EVT_TIMER(self, TIMER_ID, self.onTimer)

    def OnTick(self,tick):
        self.canvas.restore_region(self.bg)
                # update the data
        if tick.InstrumentID != 'IF1404':
            return
        print tick.LastPrice
        temp =np.random.randint(10,80)
        self.user = self.user[1:] + [tick.LastPrice]
        # update the plot
        self.l_user.set_ydata(self.user)
        # just draw the "animated" objects
        self.ax.draw_artist(self.l_user)# It is used to efficiently update Axes data (axis ticks, labels, etc are not updated)
        self.canvas.blit(self.ax.bbox)
if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = PlotFigure()
    t = wx.Timer(frame, TIMER_ID)
    t.Start(50)
    frame.Show()
    app.MainLoop()