import os
import re
import tifffile
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider  # import the Slider widget
from matplotlib.widgets import Cursor
import roilinescan_class
import numpy as np
import pandas as pd

metatags=["BitsPerPixel","DimensionOrder","SizeC","SizeT","SizeX","SizeY","SizeZ","HeightConvertValue","WidthConvertValue","Time Per Pixel","Time Per Line"]
    

def extract_metadata(metastr,metatags):
    metadata = {} 
    # extract values form the metadata string using the provided tags
    for metatag in metatags:
        pattern = "".join((".*",metatag,".*"))
        line = [item for item in metastr.split("\n") if re.search(pattern, item)][0]
        value = re.search("(?:^.*\=.)(.*)",line).group(1)
        try:
            conv_value = int(value)
        except:
            try:
                conv_value = float(value)
            except:
                conv_value = value.strip()
        metadata[metatag]=conv_value
    return(metadata)


class tiff_file:
    def __init__(self,_fname):
        self.fname = _fname
        # check file exists
        if (not (os.path.isfile(self.fname))):
            print("file provided does not exists")
            return
        self.openfile()

        
    def openfile(self):
        # extract metadata and imagedata
        with tifffile.TiffFile(self.fname) as tif:
            self.rawmetadata = tif.imagej_metadata
            metastr = self.rawmetadata["Info"]
            self.metadata = extract_metadata(metastr,metatags)
            self.imagedata = tif.asarray()
            # swap channels
            print("DimesionOrder:",self.metadata["DimensionOrder"])
            self.imagedata = np.swapaxes(self.imagedata,0,1)
            # --------------------------

    def roi_select(self,label,flip):
        # select the coordinates of  two rois (one each for dendrite and spine) from a tif image with a single trial
        leftlim = 326
        rightlim = 500
        # def on_press(event):
        #     print('you pressed', event.button, event.xdata, event.ydata)
        #     nonlocal cursor
                        
        def leftupdate(left):
            # caller function that executed when the slider is changed
            nonlocal leftlim
            nonlocal rightlim
            nonlocal ahavgx
            nonlocal ahavgy
            leftlim = left
            ah.set_xlim(leftlim,rightlim)
            ahpos = ah.get_position()
            ahavgx.set_position([ahpos.x0+ahpos.width,ahpos.y0,0.05,ahpos.height]) # [lbwh]
            avgyheight = 0.06
            ahavgy.set_position([ahpos.x0,ahpos.y0+ahpos.height,ahpos.width,avgyheight]) # [lbwh]
            ahavgy.set_xlim([leftlim,rightlim])
            fh.canvas.draw_idle()
        def rightupdate(right):
            # caller function that executed when the slider is changed
            nonlocal rightlim
            nonlocal leftlim
            nonlocal ahavgx
            nonlocal ahavgy
            rightlim = right
            ah.set_xlim(leftlim,rightlim)
            ahpos = ah.get_position()
            ahavgx.set_position([ahpos.x0+ahpos.width,ahpos.y0,0.05,ahpos.height]) # [lbwh]
            avgyheight = 0.06
            ahavgy.set_position([ahpos.x0,ahpos.y0+ahpos.height,ahpos.width,avgyheight]) # [lbwh]
            ahavgy.set_xlim([leftlim,rightlim])
            fh.canvas.draw_idle()
            # ------------
        def show_dendrite_spine_positions():
            labels = ["Dendrite","Spine"]
            if (flip):
                labels = labels[::-1]
            labelpos = [[0.5,0.1],[0.5,0.9]]
            for i in range(len(labels)):
                nh = ah.annotate(labels[i], xy=labelpos[i], xycoords="axes fraction",va="center", ha="center",bbox=dict(boxstyle="round", fc="w"))
            
        fh = plt.figure()
        ah = fh.add_subplot(111)
        ah.set_xlim(leftlim,rightlim)
        ahsl = fh.add_axes([0.1, 0.12, 0.8, 0.05]) # [lbwh]
        ahsr = fh.add_axes([0.1, 0.05, 0.8, 0.05])
        leftslider = Slider(ahsl,'left',0,self.metadata["SizeY"],valinit=leftlim)
        rightslider = Slider(ahsr,'right',0,self.metadata["SizeY"],valinit=rightlim)
        itrials_begin = [0]
        itrials_end = [self.imagedata.shape[1]]
        events = [np.zeros(itrials_end)]
        roiselect = roilinescan_class.roiLineScanClass(fh,ah,self.imagedata[:,:,np.newaxis],0,itrials_begin,itrials_end,events,label)
        show_dendrite_spine_positions()
        # cursor = Cursor(ah,vertOn=False,horizOn=True,color='yellow',linewidth=2)
        # cid = fh.canvas.mpl_connect('button_press_event',on_press)
        ahpos = ah.get_position()
        ahavgx = fh.add_axes([ahpos.x0+ahpos.width,ahpos.y0,0.05,ahpos.height]) # [lbwh]
        ahavgy = fh.add_axes([ahpos.x0,ahpos.y0+ahpos.height,ahpos.width,0.06]) # [lbwh]
        ahavgx.set_yticklabels([])
        ahavgx.set_xticklabels([])
        ahavgy.set_yticklabels([])
        ahavgy.set_xticklabels([])
        avgx = self.imagedata.mean(axis=1)
        ahavgx.plot(avgx,np.arange(0,len(avgx)))
        avgy = self.imagedata.mean(axis=0)
        ahavgy.plot(np.arange(0,len(avgy)),avgy)
        ahavgy.set_xlim([leftlim,rightlim])
        # ah.imshow(self.imagedata.T,cmap="hot",origin='lower')
        # ah.imshow(self.imagedata.T,interpolation='nearest',cmap='hot',origin='lower',aspect='equal')
        leftslider.on_changed(leftupdate)
        rightslider.on_changed(rightupdate)
        self.coords = roiselect.coords
        plt.show()
        return(fh,ah)
        
    def roi_extract(self):
        # extracts 1d data from the selected rois for dendrite and spine into a dataframe
        roidata={}        # open a dictionary to stores extracted data
        coords = self.coords
        # get time axis
        timeperline = self.metadata["Time Per Line"] * 1e-06 # convert time per line to seconds
        roitime = np.arange(0,self.imagedata.shape[1]) * timeperline # axis order: YX
        print(self.imagedata.shape)
        input("key")
        roidata["time"] = roitime
        for coord in coords:
            iroi = coord["iroi"]-1
            if ((coord["dnTop"] != None) and (coord["dnBot"] != None)): # found a dendrite ROI
                roitype = "dendrite"
                roitop = np.uint(coord["dnTop"])
                roibot = np.uint(coord["dnBot"])
                roiname = "".join((roitype,str(iroi)))
                roival = np.mean(self.imagedata[roibot:roitop,:],axis=0) # image is a 2d np array
                roidata[roiname] = roival
                # -----------------------------
            if ((coord["spTop"] != None) and (coord["spBot"] != None)): # found a spine ROI. axis order: YX
                roitype = "spine"
                roitop = np.uint(coord["spTop"])
                roibot = np.uint(coord["spBot"])
                roiname = "".join((roitype,str(iroi)))
                roival = np.mean(self.imagedata[roibot:roitop,:],axis=0) # image is a 2d np array. axis order: YX
                roidata[roiname] = roival
                # ----------------------------
            # create pandas dataframe to store rois
            self.roidf = pd.DataFrame(roidata)
            print(self.roidf)
            # fh = plt.figure()
            # ah = fh.add_subplot(111)
            # ah.plot(roidata["time"],roidata["spine0"],color="red")
            # ah.plot(roidata["time"],roidata["dendrite0"],color="black")
            # plt.show()
            # input('in roi extract: press a key')
            # ---------------------
        # ----------------------
        
    def roi_save(self,roisavepath='',roisavename=""):
        if (os.path.isdir(roisavepath) and len(roisavename)>0):
            # add extension (.csv) if the filename does not have it
            if(re.search("(?:.*)(.csv$)",roisavename)):
                roisavefname = os.path.join(roisavepath,roisavename)
            else:
                roisavefname = os.path.join(roisavepath,"".join((roisavename,".csv")))
            print('Saving as:', roisavefname)
            with open(roisavefname,'w') as csvfile:
                self.roidf.to_csv(csvfile,index=False,float_format='%.5f')
        else:
            print('!!!! Not saved: path to save or title not found !!!!')
            # ----------
        # -----------------
            
    def _def_(self):
        classname = self.__class__.__name
        print(classname.join(" destructed!"))
