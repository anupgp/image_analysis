import numpy as np
from matplotlib import pyplot as plt

class ROILineScan:
    def __init__(self,_fh,_ah):
        self.fig = _fh
        self.axis = _ah
        self.xyTdn = [None,None]
        self.xyBdn = [None,None]
        self.lineTdn, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyTdn[1],self.xyTdn[1]],color='blue',linewidth=2)
        self.lineBdn, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyBdn[1],self.xyBdn[1]],color='red',linewidth=2)
        self.xyTsp = [None,None]
        self.xyBsp = [None,None]
        self.lineTsp, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyTsp[1],self.xyTsp[1]],color='yellow',linewidth=2,linestyle='-')
        self.lineBsp, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyBsp[1],self.xyBsp[1]],color='green',linewidth=2,linestyle='-')
        self.region = 'None'
        self.boundary = "None"
        self.key = None
        self.x = None
        self.y = None
        self.action = self.region+': '+self.boundary
        self.actiondisplay = self.axis.text(0.5,0.95,self.action,fontsize=12,horizontalalignment='center',verticalalignment='center',transform=self.fig.transFigure)
        self.connect()
    
    def action_switcher(self,key):
        switcher = {
            'x':self.action_inactive,
            'd':self.region_dendrite,
            'p':self.region_spine,
            't':self.boundary_top,
            'b':self.boundary_bottom
        }
        func = switcher.get(key,lambda:"Invalid key")
        return(func())

    def get_coordinates(self):
        coord = {'dnTop':None,'dnBot':None,'spTop':None,'spBot':None}
        coord['dnTop'] = self.xyTdn[1]
        coord['dnBot'] = self.xyBdn[1]
        coord['spTop'] = self.xyTsp[1]
        coord['spBot'] = self.xyBsp[1]
        return(coord)
        
    def __call__(self,event):
        if(event.name == 'button_press_event'):
            print('button: ',event.button)
        if(event.inaxes is not None):
            if (self.region == "Dendrite" and self.boundary == 'Top'):
                self.xyTdn = [event.xdata,event.ydata]
                self.plot_lineTdn()
            if (self.region == "Dendrite" and self.boundary == 'Bottom'):
                self.xyBdn = [event.xdata,event.ydata]
                self.plot_lineBdn()
            if (self.region == "Spine" and self.boundary == 'Top'):
                self.xyTsp = [event.xdata,event.ydata]
                self.plot_lineTsp()
            if (self.region == "Spine" and self.boundary == 'Bottom'):
                self.xyBsp = [event.xdata,event.ydata]
                self.plot_lineBsp()
        if (event.name == 'key_press_event'):
            self.key = event.key
            self.action_switcher(event.key)                
            self.action = self.region+': '+self.boundary
            self.actiondisplay.set_text(self.action)
            self.actiondisplay.figure.canvas.draw()
            
        if (event.name == 'motion_notify_event'):
            self.x = event.x
            self.y = event.y
            
    def action_inactive(self):
        self.region = "None"
        self.boundary = "None"

    def region_dendrite(self):
        self.region  = "Dendrite"

    def region_spine(self):
        self.region = "Spine"

    def boundary_top(self):
        self.boundary = "Top"
        
    def boundary_bottom(self):
        self.boundary = "Bottom"
            
    def connect(self):
        'connect to all the events'
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self)
        self.cidkeypress = self.fig.canvas.mpl_connect('key_press_event',self)
        # self.cidfigenter = self.fig.canvas.mpl_connect('figure_enter_event', self.press)
        # self.cidfigleave = self.fig.canvas.mpl_connect('figure_leave_event', self.press)
    
    def plot_lineTdn(self):
        self.lineTdn.set_xdata(self.axis.get_xlim())
        self.lineTdn.set_ydata([self.xyTdn[1],self.xyTdn[1]])
        self.lineTdn.figure.canvas.draw()
        # self.hline.figure.canvas.flush_events()
    def plot_lineBdn(self):
        self.lineBdn.set_xdata(self.axis.get_xlim())
        self.lineBdn.set_ydata([self.xyBdn[1],self.xyBdn[1]])
        self.lineBdn.figure.canvas.draw()
    def plot_lineTsp(self):
        self.lineTsp.set_xdata(self.axis.get_xlim())
        self.lineTsp.set_ydata([self.xyTsp[1],self.xyTsp[1]])
        self.lineTsp.figure.canvas.draw()
        # self.hline.figure.canvas.flush_events()
    def plot_lineBsp(self):
        self.lineBsp.set_xdata(self.axis.get_xlim())
        self.lineBsp.set_ydata([self.xyBsp[1],self.xyBsp[1]])
        self.lineBsp.figure.canvas.draw()
        
    def disconnect(self):
        'disconnect all the stored connection ids'
        self.fig.canvas.mpl_disconnect(self.cidpress)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidkeypress)
        # self.fig.canvas.mpl_disconnect(self.cidfigenter)
        # self.fig.canvas.mpl_disconnect(self.cidfigleave)


# ------------------------------------------------------------
# lsts = np.random.randint(0,255,(128,3500,3))
# lsts[0,:,:] = 0                 # make first row black
# lsts[:,0,:] = 0                # make first col black

# fgh = plt.figure()
# axh = plt.subplot(111)
# # print('figure handle: ',fgh,axh)
# ph1 = axh.imshow(lsts,interpolation='none',cmap='jet',origin='upper',aspect='equal')
# roipick  = ROILineScan(fgh,axh)
# plt.show()
# plt.close('all')
# print(roipick.get_coordinates())
