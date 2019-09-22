import czifile
from io import BytesIO
import numpy as np
from matplotlib import pyplot as plt
import common_functions as comfun
import copy
import roilinescan
import xml.etree.ElementTree as ET
import math
import pandas as pd

metadata_elements = [{"name":"./Metadata/Information/Image/","tags":["PixelType","ComponentBitCount","SizeX","SizeY","SizeZ","SizeC","SizeT"]},
                     {"name":"./Metadata/Information/Image/Dimensions/Channels/Channel/LaserScanInfo/","tags":[]},
                     {"name":"./Metadata/Information/Instrument/Objectives/Objective/","tags":["Immersion","LensNA","NominalMagnification"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/AcquisitionModeSetup/","tags":["BitsPerSample","OffsetX","OffsetY","OffsetZ","Reference","PixelPeriod","Rotation","AcqisitionMode","ScalingX","ScalingY","ScalingZ","TimeSeries","ZoomX","ZoomY"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/TimeSeriesSetup/StartMode/OnTrigger/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/TimeSeriesSetup/Switches/Switch/","tags":["DigitalIn"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/TimeSeriesSetup/Switches/Switch/SwitchAction/NoneAction/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/MultiTrackSetup/TrackSetup/Attenuators/Attenuator/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/MultiTrackSetup/TrackSetup/Detectors/Detector/","tags":["ImageChannelName","AmplifierGain","AmplifierOffset","DigitalGain","DigitalOffset"]},
                     {"name":"./Metadata/Layers/Layer/Elements/OpenArrow/Geometry/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/Lasers/Laser/","tags":[]}]

def findstimfreq(ts,evts):
    """ computes stimulus rate from timeseries and a binary array of stimulus events: 1 when stimulus is present"""
    rate = np.mean(np.diff(ts[evts==1]))
    return(np.round(1/rate))
        
def eventtimes2events(ts,tevts):
    """ function returns a vector of len(ts) with ones where events occured"""
    evts = np.zeros(len(ts),dtype=np.uint)
    ievts  = np.array([])
    for tevt in tevts:
        d = np.where(ts>tevt)[0]
        if(len(d)>0):
            ievts = np.append(ievts,d[0]-1)
    ievts = np.uint(ievts)
    if(len(ievts)>0):
        evts[ievts] = 1
    return(evts)

def metadata_xmlstr_to_metadata_dict(metadata_xmlstr):
    root = ET.fromstring(metadata_xmlstr)
    metadata={}
    for element in metadata_elements:
        for item in root.findall(element["name"]):
            key = item.tag
            value = comfun.string_convert(item.text)
            if (key in element["tags"]) or (not element["tags"]):
                if(key in metadata.keys()):
                    key = key+"2"
                metadata[key] = value
                
    return(metadata)

def show_metadata(metadata):
    for key in metadata:
        print(key,metadata[key])

def extract_attachments(cziobj,czi):
    embedded_czifile = czifile.CziFile(
        BytesIO(
            next(
                attachment for attachment in czi.attachments()
                if attachment.attachment_entry.name == 'Image'
            ).data(raw=True)
        )
    )
    cziobj.attachment_image = embedded_czifile.asarray()
    cziobj.attachment_metadata =embedded_czifile.metadata()
    
class ZeissClass:
    def __init__(self,_fname):       
        self.fname = _fname
        self.read_metadata_main(self.fname,metadata_elements) # read main metadata from the file
        # show_metadata(self.metadata)
        self.read_data_main()                                 # read main data from the file
        self.read_attachments()                               # read attachment data and metadata
                        
    def read_metadata_main(self,fname,metadata_elements):
        with czifile.CziFile(fname) as czi:
            metadata_xmlstr = czi.metadata(raw=True)
            self.metadata = metadata_xmlstr_to_metadata_dict(metadata_xmlstr)

    def read_data_main(self):
        with czifile.CziFile(self.fname) as czi:
            imgshape = np.array(czi.shape)
            imgaxes = list(czi.axes)
            # print(imgshape,imgaxes)
            self.data = czi.asarray()
            # print(czi.asarray().shape)
        

    def read_attachments(self):
        with czifile.CziFile(self.fname) as czi:
            for attachment in czi.attachments():
                print('Found attachment:\t',attachment.attachment_entry.name)
                if attachment.attachment_entry.name == 'Image':
                    imgshape = np.array(czi.shape)
                    imgaxes = list(czi.axes)
                    print(imgshape,imgaxes)
                    imageattachment = czifile.CziFile(BytesIO(attachment.data(raw=True)))
                    self.attachimage = imageattachment.asarray()
                    # print(imageattachment.metadata())
                    self.attachimage_metadata = metadata_xmlstr_to_metadata_dict(imageattachment.metadata())
                    print(self.attachimage.shape)
                    # show_metadata(self.attachimage_metadata)
                if attachment.attachment_entry.name == 'TimeStamps':
                    self.timestamps = attachment.data()
                    if ("SizeT" in self.metadata):
                        print('SizeT: ',self.metadata['SizeT'])
                        self.timestamps = self.timestamps[0:self.metadata['SizeT']-1]
                        print(self.timestamps.shape)
                if attachment.attachment_entry.name == 'EventList':
                    # self.event = {'time':0,'type':'','name':''}
                    self.events = []
                    for item in attachment.data():
                        self.events.append({'time':item.time,'type':item.EV_TYPE[item.event_type],'name':item.description})
                    self.eventtimes = [item['time'] for item in self.events]
                    print(self.eventtimes)
                    
    def get_lineselect_image(self,channels=[0,1,2]):
        fh = plt.figure()
        ah = plt.subplot(111)
        if hasattr(self,'attachimage'):
            print('Found lineselect image')
            sizeX = self.attachimage_metadata['SizeX']
            sizeY = self.attachimage_metadata['SizeY']
            sizeC = self.attachimage_metadata['SizeC']
            print(self.attachimage.shape)
            bitsize = self.attachimage_metadata['ComponentBitCount']
            img = self.attachimage[0,0,0:sizeC,0,0,0:sizeY,0:sizeX,0] # 'BVCTZYX0' -> CYX
            if (bitsize>8):
                img = np.uint8((img/(pow(2,bitsize)-1))*(pow(2,8)-1))
            img = img.swapaxes(0,-1)
            # img = img.swapaxes(0,1)
            img = np.flip(img,1)
            print(img.shape)
            img = np.concatenate((img[:,:,1][:,:,np.newaxis],img[:,:,0][:,:,np.newaxis],np.ones((sizeX,sizeY,1),dtype=np.uint16)*0),axis=-1)
            # lineselect
            sizex = self.attachimage_metadata['SizeX']
            sizey = self.attachimage_metadata['SizeY']
            x1 = self.attachimage_metadata['Y1'] # 256
            y1 = self.attachimage_metadata['X1'] # 0
            x2 = self.attachimage_metadata['Y2'] # 256
            y2 = self.attachimage_metadata['X2'] # 512

            # plot linescan select image
            # fh = plt.figure()
            # ah = plt.subplot(111)
            ah.imshow(img,interpolation='nearest',origin='lower',aspect='equal')
            # ah.plot([x1,x2],[y1,y2],color='blue')
            ah.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(color='w',arrowstyle='->'))
            ah.set_xlim([0,sizex])
            ah.set_ylim([0,sizey])
            # plt.show()
        return(fh,ah)
                    

    def select_roi_linescan(self):
        """ Class method to select roi on a linescan time series image from Zeiss LSM microscope """
        if (not hasattr(self,'timestamps')):
            print('Exiting. No timestamps attribute in the object')
            exit  
        if (not hasattr(self,'eventtimes')):
            print('No eventtimes in the object')
            exit
        # seperate trials/blocks and compartments from a given linescan image by finding breaks
        ts = self.timestamps

        tsdiff = np.diff(ts)
        itrials = np.where(tsdiff>1)[0] # breaks = number of timestamp sections seperated by > 1 sec
        if (len(itrials)>0):
            self.ifirst = np.concatenate((np.array([0]),itrials+1))
            self.ilast = np.concatenate((itrials,np.array([len(ts)-1])))
        else:
            self.ifirst = np.array([0])
            self.ilast = np.array([len(ts)-1])

        eventtimes = self.eventtimes
        self.tevents = []

        # split the eventtimes into eventtimes in each trial
        for i in np.arange(0,len(self.ifirst)):
            self.tevents.append(np.array([evt for evt in eventtimes if (evt>=ts[self.ifirst[i]]) and (evt<ts[self.ilast[i]])]))
        
        # Call to Linescan timeseries ROI selection object
        fh = plt.figure()
        ah = plt.subplot(111)
        # Get linescan timeseries image
        lsts = copy.deepcopy(np.transpose(self.data[0,0,0,:,0,0,:,0]))
        roiselect = roilinescan.ROILineScan(fh,ah,lsts,self.ifirst,self.ilast)
        self.coords = roiselect.coords

        # ------- for testing purposes
        print('ifirst: ',self.ifirst)
        print('ilast: ',self.ilast)
        print('tevents: ',self.tevents)
        print('ts: ',ts)
        print('size: tevents',len(self.tevents))
        print('size: ts',np.shape(ts))
        print('size: lsts',np.shape(lsts))
        # ----------------------------
        
        return(fh,ah)

    def extract_roi(self):
        ifirst = self.ifirst
        ilast = self.ilast
        coords = self.coords
        roidata={}
        self.nroi=np.zeros((len(self.ifirst)))
        self.stimfreq=np.zeros((len(self.ifirst)))

        for coord in coords:
            # print(coord)
            itrial = coord["itrial"]-1
            iroi = coord["iroi"]-1
            postfix = "trial"+str(itrial+1)+"roi"+str(iroi+1)
            ts = self.timestamps[ifirst[itrial]:ilast[itrial]]-self.timestamps[ifirst[itrial]] # ts start at 0 for each trial
            evts = eventtimes2events(ts,self.tevents[itrial]-self.timestamps[ifirst[itrial]])
            timename = "time_"+postfix
            stimname = "stim_"+postfix
            self.nroi[itrial] = iroi+1
            self.stimfreq[itrial]=findstimfreq(ts,evts)
            roidata[timename] = ts
            roidata[stimname] = evts 
            if ((coord["dnTop"] != None) and (coord["dnBot"] != None)): # roi: dendrite
                print("Found dendrite ROI")
                denname = "dend_"+postfix
                dntop = np.uint(coord["dnTop"])
                dnbot = np.uint(coord["dnBot"])
                den = np.transpose(self.data[0,0,0,ifirst[itrial]:ilast[itrial],0,0,:,0])
                den = np.mean(den[dnbot:dntop,:],axis=0)# [0:len(ts)]
                roidata[denname]= den
            if ((coord["spTop"] != None) and (coord["spBot"] != None)): # roi: spine
                print("Found spine ROI")
                spinename = "spine_"+postfix
                sptop = np.uint(coord["spTop"])
                spbot = np.uint(coord["spBot"])
                spi = np.transpose(self.data[0,0,0,ifirst[itrial]:ilast[itrial],0,0,:,0])
                spi = np.mean(spi[spbot:sptop,:],axis=0)# [0:len(ts)]
                roidata[spinename]= spi
        # create pandas dataframe to store rois
        self.roidf = pd.DataFrame(roidata)
        print(self.nroi)
        print(self.stimfreq)



            

        
