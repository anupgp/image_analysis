import czifile
from io import BytesIO
import numpy as np
from matplotlib import pyplot as plt
import javabridge
import bioformats
from bioformats import log4j as bioformats_log4j
import common_functions as comfun
import zeiss_keymaps
import copy
import roilinescan
import xml.etree.ElementTree as ET

metadata_elements = [{"name":"./Metadata/Information/Image/","tags":["PixelType","ComponentBitCount","SizeX","SizeY","SizeZ","SizeC","SizeT"]},
                     {"name":"./Metadata/Information/Image/Dimensions/Channels/Channel/LaserScanInfo/","tags":[]},
                     {"name":"./Metadata/Information/Instrument/Objectives/Objective/","tags":["Immersion","LensNA","NominalMagnification"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/AcquisitionModeSetup/","tags":["BitsPerSample","OffsetX","OffsetY","OffsetZ","Reference","PixelPeriod","Rotation","AcqisitionMode","ScalingX","ScalingY","ScalingZ","TimeSeries","ZoomX","ZoomY"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/TimeSeriesSetup/StartMode/OnTrigger/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/TimeSeriesSetup/Switches/Switch/","tags":["DigitalIn"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/TimeSeriesSetup/Switches/Switch/SwitchAction/NoneAction/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/MultiTrackSetup/TrackSetup/Attenuators/Attenuator/","tags":[]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/MultiTrackSetup/TrackSetup/Detectors/Detector/","tags":["ImageChannelName","AmplifierGain","AmplifierOffset","DigitalGain","DigitalOffset"]},
                     {"name":"./Metadata/Experiment/ExperimentBlocks/AcquisitionBlock/Lasers/Laser/","tags":[]}]

def metadata_xmlstr_to_metadata_dict(metadata_xmlstr):
    print(metadata_xmlstr)
    root = ET.fromstring(metadata_xmlstr)
    metadata={}
    for element in metadata_elements:
        print(element)
        for item in root.findall(element["name"]):
            key = item.tag
            value = comfun.string_convert(item.text)
            if (key in element["tags"]) or (not element["tags"]):
                if(key in metadata.keys()):
                    key = key+"2"
                metadata[key] = value
                
    return(metadata)
    
class ZeissClass:
    def __init__(self,_fname):       
        self.fname = _fname
        self.metadata = {}      # main metadata
        self.read_metadata_main(self.fname,metadata_elements)
        print("Metadata:\t",self.metadata)
        self.read_data_main()
        self.read_attachments()
                        
    def read_metadata_main(self,fname,metadata_elements):
        with czifile.CziFile(fname) as czi:
            metadata_xmlstr = czi.metadata(raw=True)
            self.metadata = metadata_xmlstr_to_metadata_dict(metadata_xmlstr)

    def read_data_main(self):
        with czifile.CziFile(self.fname) as czi:
            print(czi.asarray().shape)
                                
    def read_attachments(self):
        with czifile.CziFile(self.fname) as czi:
            for attachment in czi.attachments():
                print(attachment.attachment_entry.name)
                print(attachment)
                if attachment.attachment_entry.name == 'Image':
                    attachment_image = czifile.CziFile(BytesIO(attachment.data(raw=True)))
                    attachment_image_metadata = metadata_xmlstr_to_metadata_dict(attachment_image.metadata())
                    print(attachment_image.shape)
                    print(attachment_image_metadata)        
        
        # self.read_single_framescan_with_czifile()
        
    def read_single_framescan_with_czifile(self):
        with czifile.CziFile(self.fname) as zfile:
            print(dir(zfile))
            print(zfile.shape)
            data = zfile.asarray()[0,0,1,0,0,0:512,0:512,0] # BVCTZYX0
            print(np.shape(data))
            data = np.concatenate((np.zeros((512,512,1),dtype=np.int),data[:,:,np.newaxis],np.zeros((512,512,1),dtype=np.int)),axis=2)
            print(data)
            figh = plt.figure()
            ax = plt.subplot(111)
            ax.imshow(data)
            plt.show()

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
            
class ZeissLinescan:
    def __init__(self,_fname):
        self.fname = _fname
        self.metadata = {}          # Metadata dictionary
        self.timestamps=[]
        self.eventlist = []
        self.read_metadata_with_bioformats()
        self.read_linescan_timeseries_with_czifile()

    def read_metadata_with_bioformats(self):
        # Using javabridge to parse and store all required metadata
        # -------------------------------------------------
        javabridge.start_vm(class_path=bioformats.JARS,run_headless=True,max_heap_size='2G')
        bioformats_log4j.basic_config()        # Configure logging for "WARN" level
        rdr = javabridge.JClassWrapper('loci.formats.in.ZeissCZIReader')()            
        # ZeissCZIReader is the file format reader for Zeiss .czi files.
        # rdr = javabridge.JClassWrapper('loci.formats.in.OMETiffReader')()
        # OMETiffReader is the file format reader for OME-TIFF files
        rdr.setOriginalMetadataPopulated(True)
        # Specifies whether to save proprietary metadata in the MetadataStore.
        clsOMEXMLService = javabridge.JClassWrapper('loci.formats.services.OMEXMLService')
        # Classes in loci.formats.services that implement OMEXMLService
        serviceFactory = javabridge.JClassWrapper('loci.common.services.ServiceFactory')()
        # Constructor loading runtime initiation of services from the defult location
        service = serviceFactory.getInstance(clsOMEXMLService.klass) # Retrieves an instance of a given service.
        omemetadata = service.createOMEXMLMetadata()
        # Creates OME-XML metadata object using reflection - avoids direct dependencies on loci.formats.ome package.
        rdr.setMetadataStore(omemetadata) # Sets the default metadata store for this reader.
        rdr.setId(self.fname)
        # Initializes a reader from the input file name.
        # Calls initFile(String id) to initializes the input file
        # Reads all of the metadata and sets the reader up for reading planes. This can take time here...
        # rdr.saveOriginalMetadata = True
        orgmetadata = service.getOriginalMetadata(omemetadata)
        globalmetadata = rdr.getGlobalMetadata()
        # Obtains the hashtable containing the metadata field/value pairs from the current file.
        keys = globalmetadata.keySet().toString().split(',')
        nkeys = globalmetadata.size()
        metadatavalues = globalmetadata.values().toString().split(',')
        metadatakeys = globalmetadata.keys()
        # Get additional atrributes
        self.dimOrder = copy.deepcopy(rdr.getDimensionOrder())
        self.isChannelInterleaved = copy.deepcopy(rdr.isInterleaved())
        self.isDimOrderCertain = copy.deepcopy(rdr.isOrderCertain())
        for i in np.arange(0,nkeys):
            key = metadatakeys.nextElement()
            value = globalmetadata.get(key)
            # print(key,value)
            if key in zeiss_keymaps.linescan:
                self.metadata[zeiss_keymaps.linescan[key]] = comfun.string_convert(value)
        # -----------------------------------
        javabridge.kill_vm() # kill javabridge
        print(self.metadata)
        print('Metadata reading successful')
        # -----------------------------------

    def select_roi_linescan(self,channels=[0,1,2]):
        nC = self.metadata['SizeC']
        nT = self.metadata['SizeT']
        nX = self.metadata['SizeX']
        print(self.data.shape)
        fgh = plt.figure()
        axh = plt.subplot(111)
        # red,green,blue = [np.random.randint(0,256,(10,10)) for _ in np.arange(0,3)]
        img=np.concatenate([self.data]+[(np.ones((nX,nT,1))*0) for _ in np.arange(0,len(channels)-nC)],axis=-1)
        print(self.data.shape)
        print(img.shape)
        roiselect = roilinescan.ROILineScan(fgh,axh)
        axh.imshow(self.data[:,:,0],interpolation=None,origin='upper',aspect='equal',cmap='jet')
        plt.show()
        
    def show_metadata(self):
        for key in self.metadata:
            print(key,self.metadata[key],type(self.metadata[key]))
        for entry in self.eventlist:
            print(entry['time'],entry['type'],entry['name'])
        print(self.timestamps)
        
    def read_linescan_timeseries_with_czifile(self):
        with czifile.CziFile(self.fname) as czi:
            attachDir = czi.attachment_directory
            subblkdir = czi.subblock_directory
            print(subblkdir)
            for attachment in czi.attachments():
                print(attachment.attachment_entry.name)
                print(attachment.attachment_entry.content_file_type)
                if(attachment.attachment_entry.name == 'TimeStamps'):
                    self.timestamps = attachment.data()
                    if 'SizeT' in self.metadata:
                        self.timestamps = self.timestamps[0:self.metadata['SizeT']-1]
                    self.t0 = self.timestamps[0]
                    print('Reading timestamps successful')
                if(attachment.attachment_entry.name == 'Image'):
                    # embedded_czifile = czifile.CziFile(
                    #     BytesIO(
                    #         next(
                    #             attachment for attachment in czi.attachments()
                    #             if attachment.attachment_entry.name == 'Image'
                    #         ).data(raw=True)
                    #     )
                    # )
                    # self.embedded_image = embedded_czifile.asarray()
                    # self.embedded_image
                    extract_attachments(self,czi)
                    print('Reading imageattachment successful')
                    
                if(attachment.attachment_entry.name == 'EventList'):
                    events = attachment.data()
                    eventtimes=[]
                    eventdict = {'time':0,'type':'','name':''}
                    for item in events:
                        # print(item.description)
                        self.eventlist.append({'time':item.time,'type':item.EV_TYPE[item.event_type],'name':item.description})
                        self.eventtimes = [item['time'] for item in self.eventlist]
                    print('Reading eventlist successful')

            if ((self.metadata['AcquisitionMode'] == 'Line') and (self.metadata['isTimeSeries']==True)):
                print("Detected: Zeiss linescan in timeseries")
                self.data = czi.asarray()
                imgShAll = np.array(czi.shape)
                imgAxAll = list(czi.axes)
                # find index of Channel axis
                axIdC = [idx for idx,item in enumerate(imgAxAll) if item == 'C'].pop()
                # find index of X axis
                axIdX = [idx for idx,item in enumerate(imgAxAll) if item == 'X'].pop()
                # find index of T axis
                axIdT = [idx for idx,item in enumerate(imgAxAll) if item == 'T'].pop()
                # self.data.resize(imgShAll[axIdC],imgShAll[axIdT],imgShAll[axIdX]) # CTX
                self.data.resize(imgShAll[axIdX],imgShAll[axIdT],imgShAll[axIdC]) # XTC
                
        
    def __call__(self):
        pass

    def display_lineselect(self,channels=[0,1,2]):
        if hasattr(self,'attachment_image'):
            print('Found lineselect image')
            fgh = plt.figure()
            axh = plt.subplot(111)
            print(self.attachment_image.shape)
            img = self.attachment_image[0,0,0,0,0,:,:,0]
            # img=np.concatenate(img+[(np.ones((nX,nT,1))*0) for _ in np.arange(0,len(channels)-nC)],axis=-1)
            axh.imshow(img,interpolation=None,origin='upper',aspect='equal',cmap='jet')
            plt.show()
            
    def detect_trials_linescan_ts(self):
        pass
        
def dict_recursive_display(mydict):
    if (isinstance(mydict,dict)):
        for key,value in mydict.items():
            if (isinstance(value,dict)):
                for item in value.items():
                    dict_recursive_display(item)
    else:
        print("Key: ",key," ","Value: ",value)                    
            

                    
            
    
        
# filepath = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 11 Block 1.czi'
linescanfile1 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190726/S1C1S1/2hz/Image 46.czi'
linescanfile2 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 11 Block 1.czi'
imagepath = '/Users/macbookair/goofy//data/beiquelab/linescan_testdata.czi'
# snfr = ZeissLinescan(filepath)
# print(snfr.lsts)
framefile = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190702/S1C1/Image 2.czi'
lineselect = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190829/s1c1s1/Image 30.czi'
# frame =ZeissFramescan(lineselect)
# frame.read_single_framescan_with_czifile()
linescan = ZeissClass(linescanfile1)
# linescan.display_lineselect()
# linescan.show_metadata()
# linescan.select_roi_linescan()
