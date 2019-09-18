import czifile
from io import BytesIO
import numpy as np
from matplotlib import pyplot as plt
import common_functions as comfun
import copy
import roilinescan
import xml.etree.ElementTree as ET
import math

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
        show_metadata(self.metadata)
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
            print(imgshape,imgaxes)
            self.data = czi.asarray()
            print(czi.asarray().shape)
        
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
                    show_metadata(self.attachimage_metadata)
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
            fh = plt.figure()
            ah = plt.subplot(111)
            ah.imshow(img,interpolation='nearest',origin='lower',aspect='equal')
            # ah.plot([x1,x2],[y1,y2],color='blue')
            ah.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(color='w',arrowstyle='->'))
            ah.set_xlim([0,sizex])
            ah.set_ylim([0,sizey])
            plt.show()
                    

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
        itbreaks = np.where(tsdiff>1)[0] # breaks = number of timestamp sections seperated by > 1 sec
        if (len(itbreaks)>0):
            it0trials = np.concatenate((np.array([0]),itbreaks+1))
            it9trials = np.concatenate((itbreaks,np.array([len(ts)-1])))
        else:
            it0trials = np.array([0])
            it9trials = np.array([len(ts)-1])

        eventtimes = self.eventtimes
        tevents = []

        # split the eventtimes into eventtimes in each trial
        for i in np.arange(0,len(it0trials)):
            tevents.append(np.array([evt for evt in eventtimes if (evt>=ts[it0trials[i]]) and (evt<ts[it9trials[i]])]))
        
        # Get linescan timeseries image
        lsts = np.transpose(self.data[0,0,0,0:1000,0,0,:,0])
        print(lsts.shape)
        fh = plt.figure()
        ah = plt.subplot(111)
        roiselect = roilinescan.ROILineScan(fh,ah)
        ah.imshow(lsts,interpolation='none',cmap='jet',origin='upper',aspect='equal')
        plt.show()
        print('Number of ROIs: ',roiselect.roicount)
        print(roiselect.coords)



        # print(ievts)
        # info: multiple trials mean that timestamps are seperated by the inter-trial iterval (> 1 sec)
        # print(itrials)
        # fh = plt.figure()
        # ah = plt.subplot(111)
        # ah.plot(self.timestamps)
        # for i in np.arange(0,4):
        #     ah.plot([it9trials[i],it9trials[i]],[36000,37000])
        # plt.show()
