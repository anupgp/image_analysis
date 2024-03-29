import numpy as np
from matplotlib import pyplot as plt
import copy
# import cv2

class roiLineScanClass:
    def __init__(self,_fh,_ah,_lsts,_channel=None,_ifirst=None,_ilast=None,_events=[],_label=""): # A linescan timeseries matrix is iterated over trials for ROIs selection
        self.fig = _fh
        self.lsts = _lsts
        self.ifirst = _ifirst
        self.ilast = _ilast
        self.events = _events
        self.channel = _channel
        self.roicount = 0
        self.axis = _ah
        self.roi_initialize()
        self.key = None
        self.x = None
        self.y = None
        self.label = _label
        self.coord = {'itrial':None,'iroi':None,'dnTop':None,'dnBot':None,'spTop':None,'spBot':None}
        self.coords=[]          # a list of all the ROI coordinates
        self.labeldisplay = self.axis.text(0.5,0.95,self.label,fontsize=14,horizontalalignment='center',verticalalignment='center',transform=self.fig.transFigure,weight=None)
        self.titledisplay = self.axis.text(0.4,0.89,self.title,fontsize=14,horizontalalignment='center',verticalalignment='center',transform=self.fig.transFigure,weight=None)
        self.action = self.region+': '+self.boundary
        self.actiondisplay = self.axis.text(0.2,0.89,self.action,fontsize=12,horizontalalignment='center',verticalalignment='center',transform=self.fig.transFigure)
        self.roicount_text = 'Number of ROIs saved: '+ str(self.roicount)
        self.roicountdisplay = self.axis.text(0.7,0.89,self.roicount_text,fontsize=12,horizontalalignment='center',verticalalignment='center',transform=self.fig.transFigure)
        self.connect()

    def roi_initialize(self):
        self.region = 'None'
        self.boundary = "None"
        self.regioncolor = "black"
        self.boundarycolor = "black"
        self.xyTdn = [None,None]
        self.xyBdn = [None,None]
        self.xyTsp = [None,None]
        self.xyBsp = [None,None]
        self.itrial = 1         # index start at 0
        self.title = 'Trial: '+str(self.itrial)
        self.lsts0 = self.lsts[:,self.ifirst[self.itrial-1]:self.ilast[self.itrial-1]]
        self.events0 = self.events[self.itrial-1]
        # print("events: ",self.events)
        # print(self.lsts)
        # display linescan timeseries
        self.ih = self.axis.imshow(self.lsts0[:,:,self.channel],interpolation='nearest',cmap='jet',origin='lower',aspect='equal')
        # self.ih = self.axis.imshow(lsts0,interpolation='nearest',origin='lower',aspect='equal')
        # display events
        self.ph = self.axis.plot(np.arange(0,np.size(self.lsts0,1)),self.events0*np.size(self.lsts0,0),color="red",linewidth=1)
        self.lineTdn, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyTdn[1],self.xyTdn[1]],color='black',linewidth=2)
        self.lineBdn, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyBdn[1],self.xyBdn[1]],color='gray',linewidth=2)
        self.lineTsp, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyTsp[1],self.xyTsp[1]],color='red',linewidth=2,linestyle='-')
        self.lineBsp, = self.axis.plot(np.array(self.axis.get_xlim()),[self.xyBsp[1],self.xyBsp[1]],color='orange',linewidth=2,linestyle='-')
        # self.show_help()
        
    def clear_roi(self):
        self.xyTdn = [None,None]
        self.xyBdn = [None,None]
        self.xyTsp = [None,None]
        self.xyBsp = [None,None]
        self.coord['dnTop'] = self.xyTdn[1]
        self.coord['dnBot'] = self.xyBdn[1]
        self.coord['spTop'] = self.xyTsp[1]
        self.coord['spBot'] = self.xyBsp[1]
        self.plot_lineTdn()
        self.plot_lineBdn()
        self.plot_lineTsp()
        self.plot_lineBsp()
        self.titledisplay.figure.canvas.draw()
        self.roicountdisplay.set_text(self.roicount_text)
        self.roicountdisplay.figure.canvas.draw()

    def show_help(self):
        textstr = "\n".join((r'x: reset all',
                          r'd: ROI: dendrite',
                          r'p: ROI: spine',
                          r't: Boundary: top',
                          r'b: Boundary bottom',
                          r'n: Move to next ROI',
                          r'N: Move to next trial'))
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.axis.text(0.05,1.5,textstr,transform=self.axis.transAxes,fontsize=12,verticalalignment='center',bbox=props)
        
    def action_switcher(self,key):
        switcher = {
            'x':self.action_inactive, # deactivates the interactive functionalities
            'd':self.region_dendrite, # select region is dendrite
            'p':self.region_spine,    # select region is spine
            't':self.boundary_top,    # select ROI top
            'b':self.boundary_bottom,  # select ROI bottom
            'n':self.add_roi,     # save the current coordinates and start a new ROI (one trial has atleast #1ROI)
            'N':self.next_trial     # save ROIs of the current trial and start a new trial
        }
        func = switcher.get(key,lambda:"Invalid key")
        return(func())

    def save_roi(self):
        saved = False
        if(((self.xyTdn[1] != None) and (self.xyBdn[1] != None)) or
           ((self.xyTsp[1] != None) and (self.xyBsp[1] != None))):
            self.roicount = self.roicount+1
            self.coord['itrial'] = self.itrial
            self.coord['iroi'] =  self.roicount
            self.coord['dnTop'] = self.xyTdn[1]
            self.coord['dnBot'] = self.xyBdn[1]
            self.coord['spTop'] = self.xyTsp[1]
            self.coord['spBot'] = self.xyBsp[1]
            self.coords.append(copy.deepcopy(self.coord))
            print('ROI #{c} saved'.format(c=self.roicount))
            self.clear_roi()
            saved = True
            print('saved ROI:',self.coords)
        else:
            print('ROI #{n} empty'.format(n=self.roicount))
        return(saved)
    
    def __call__(self,event):
        # if(event.name == 'button_press_event'):
        #     print('button: ',event.button)
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
            self.titledisplay.figure.canvas.draw()
            self.actiondisplay.figure.canvas.draw()
            self.roicount_text = 'Number of ROIs saved: '+ str(self.roicount)
            self.roicountdisplay.set_text(self.roicount_text)
            self.roicountdisplay.figure.canvas.draw()
            
        if (event.name == 'motion_notify_event'):
            self.x = event.x
            self.y = event.y
            
    def action_inactive(self):
        self.region = "None"
        self.boundary = "None"
        self.clear_roi()

    def next_trial(self):
        if(self.itrial < len(self.ifirst) and self.roicount>0):
            saved = self.save_roi()
            self.roicount = 0
            self.itrial = self.itrial+1
            self.title = 'Trial: ' + str(self.itrial)
            self.titledisplay.set_text(self.title)
            self.titledisplay.figure.canvas.draw()
            self.lsts0 = self.lsts[:,self.ifirst[self.itrial-1]:self.ilast[self.itrial-1]] # itrial start at index 1
            self.ih.set_data(self.lsts0[:,:,1]) # pass only one channel
            self.events0 = self.events[self.itrial-1]
            self.ph.set_data(self.events0)
            self.fig.canvas.draw_idle()
    
    def add_roi(self):
        saved = self.save_roi()
        
    def region_dendrite(self):
        self.region  = "Dendrite"
        self.regioncolor = "black"

    def region_spine(self):
        self.region = "Spine"
        self.regioncolor = "red"

    def boundary_top(self):
        self.boundary = "Top"
        if (self.region == "Dendrite"):
            self.boundarycolor = "black"
        if (self.region == "Spine"):
            self.boundarycolor = "red"
        
    def boundary_bottom(self):
        self.boundary = "Bottom"
        if (self.region == "Dendrite"):
            self.boundarycolor = "gray"
        if (self.region == "Spine"):
            self.boundarycolor = "orange"
            
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

    def __del__(self):
        print('An object of class ROILinescan has been deleted!')
        
# ------------------------------------------------------------
# Below code for testing purpose only
# ------------------------------------------------------------
# lsts = np.random.randint(0,255,(128,3500,3))
# lsts[0,:,:] = 0                 # make first row black
# lsts[:,0,:] = 0                # make first col black

# fgh = plt.figure()
# axh = plt.subplot(111)
# # print('figure handle: ',fgh,axh)
# ph1 = axh.imshow(lsts,interpolation='none',cmap='jet',origin='upper',aspect='equal')
# roipick  = roiLineScanClass(fgh,axh)
# plt.show()
# plt.close('all')
# print(roipick.get_coordinates())
