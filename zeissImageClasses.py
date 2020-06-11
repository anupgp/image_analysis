import czifile
from io import BytesIO
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
import common_functions as comfun
import copy
import roilinescan_class
import xml.etree.ElementTree as ET
import math
import pandas as pd
from scipy import signal
from os import path
from scipy.signal import medfilt
import scipy.ndimage
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from scipy.signal import convolve

metadata_keys = [{"name":"./Metadata/Information/Image/","tags":["PixelType","ComponentBitCount","SizeX","SizeY","SizeZ","SizeC","SizeT"]},
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


def background_subtraction(t,f,tpre):
    # t: time, f: raw fluorescence, tpre: time from start for background substraction
    print(t,f,tpre)
    baseline = np.mean(f[0:np.where(t>tpre)[0][0]-1])
    return((f-baseline)/baseline)

def convolve_crazy(img,order=3,threshold=200):
    
    kernel1 = np.diag(np.ones(order))
    kernel2 = np.flip(np.diag(np.ones(order)),axis=-1)
    kernel3 = np.concatenate((np.ones((order,1)),np.zeros((order,1)),np.zeros((order,1))),axis=1)
    kernel4 = np.concatenate((np.zeros((order,1)),np.ones((order,1)),np.zeros((order,1))),axis=1)
    kernel5 = np.concatenate((np.zeros((order,1)),np.zeros((order,1)),np.ones((order,1))),axis=1)
    kernel6 = np.concatenate((np.ones((1,order)),np.zeros((1,order)),np.zeros((1,order))),axis=0)
    kernel7 = np.concatenate((np.zeros((1,order)),np.ones((1,order)),np.zeros((1,order))),axis=0)
    kernel8 = np.concatenate((np.zeros((1,order)),np.zeros((1,order)),np.ones((1,order))),axis=0)
    kernels = [kernel1,kernel2,kernel3,kernel4,kernel5,kernel6,kernel7,kernel8]
    img2 = np.zeros(img.shape)
    img[np.where(img<threshold)] = 0
    for kernel in kernels:
        print(kernel)
        if(len(img.shape)==3):
            kernel = kernel[:,:,None]
        imgc = scipy.signal.convolve(img,kernel,mode='same')
        imgc[np.where(imgc<threshold)] = 0
        img2 = img2 + imgc

    print(img2.shape)
    return(img2)

def convolve_supercrazy(img,order=3,threshold=200):
    
    kernel1 = np.diag(np.ones(order))
    kernel2 = np.flip(np.diag(np.ones(order)),axis=-1)
    kernel3 = np.concatenate((np.ones((order,1)),np.zeros((order,1)),np.zeros((order,1))),axis=1)
    kernel4 = np.concatenate((np.zeros((order,1)),np.ones((order,1)),np.zeros((order,1))),axis=1)
    kernel5 = np.concatenate((np.zeros((order,1)),np.zeros((order,1)),np.ones((order,1))),axis=1)
    kernel6 = np.concatenate((np.ones((1,order)),np.zeros((1,order)),np.zeros((1,order))),axis=0)
    kernel7 = np.concatenate((np.zeros((1,order)),np.ones((1,order)),np.zeros((1,order))),axis=0)
    kernel8 = np.concatenate((np.zeros((1,order)),np.zeros((1,order)),np.ones((1,order))),axis=0)
    kernels = [kernel1,kernel2,kernel3,kernel4,kernel5,kernel6,kernel7,kernel8]
    img2 = np.zeros(img.shape)
    img[np.where(img<threshold)] = 0
    for kernel in kernels:
        print(kernel)
        if(len(img.shape)==3):
            kernel = kernel[:,:,None]
        imgc = scipy.signal.convolve(img,kernel,mode='same')
        imgc[np.where(imgc<threshold)] = 0
        img2 = img2 + imgc

    print(img2.shape)
    return(img2)

def neuron_spine_plot(img1,sizeX,scaleX,img2,title=[],savepath=[]):
    # display the maximum projected framescan image
    if(len(img1.shape)>3):
        # kernel = np.array([[1,0,1,0,1],[0,1,1,1,0],[1,1,1,1,1],[0,1,1,1,0],[1,0,1,0,1]])
        # kernel = np.diag([1,1,1])
        # kernel =  np.flip(np.diag([1,1,1]),axis=-1)
        # kernel = np.ones((3,3),dtype=np.int)
        # kernel4d = kernel[:,:,None,None]
        # img1 = scipy.signal.convolve(img1,kernel4d,mode='same')

        img1 = np.concatenate((convolve_crazy(img1[:,:,:,0])[:,:,:,np.newaxis],convolve_crazy(img1[:,:,:,1])[:,:,:,np.newaxis]),axis=-1)
        print(img1.shape)
        img1c0 = np.max(img1[:,:,10:-10,0],axis=-1).astype('int')
        img1c1 = np.max(img1[:,:,10:-10:,1],axis=-1).astype('int')
    else:
        img1c0 = img1(img1[:,:,0])
        img1c1 = img1(img1[:,:,1])
        # ----------
    img1f = np.concatenate([img1c0[:,:,np.newaxis],img1c1[:,:,np.newaxis]],axis=-1)
    img1f = np.max(img1f,axis=-1)
    # img1f = np.max(img1f,axis=-1) - np.median(img1f,axis=-1) 
    # img1f[np.where(img1f<230)] = 0
    # img1f = medfilt(img1f,3)
    # img1f = image_hist_equalization(img1f).astype('int')
    # -------------
    if(img2 is None):
        img2 = np.random.randint(0,255,img1.shape[0:3])

    img2 = np.concatenate((convolve_crazy(img2[:,:,0],3,15)[:,:,np.newaxis],convolve_crazy(img2[:,:,1],3,15)[:,:,np.newaxis]),axis=-1)
    img2c0 = img2[:,:,0]
    img2c1 = img2[:,:,1]

    img2f = np.sum(np.concatenate([img2c0[:,:,np.newaxis],img2c1[:,:,np.newaxis]],axis=-1),axis=-1)
    img2f = np.round(pow(img2f,1.2))
    # img2f[img2f>255] = 255
    
    # img2f[np.where(img2f<20)] = 0
    # img2f = medfilt(img2f,3)
    # img2f = image_hist_equalization(img2f).astype('int')
    # img2f = medfilt(scipy.ndimage.zoom(img2f,3,order=0),3)
    # maxprojz = np.max(self.img[:,:,:,0],axis=-1) # maxmimum projection along Z
    # avgprojz = np.mean(self.img[:,:,:,0], axis=-1) # maxmimum projection along Z
    # medprojz = np.median(self.img[:,:,:,0], axis=-1) # maxmimum projection along Z
    
    # projz = image_hist_equalization(maxprojz)
    # projz = np.concatenate([np.ones(img0.shape)[:,:,np.newaxis],np.zeros(img0.shape)[:,:,np.newaxis],np.zeros(img0.shape)[:,:,np.newaxis]],axis=-1)
    # projz = np.concatenate([max0[:,:,np.newaxis],max1[:,:,np.newaxis],np.zeros(max0.shape)[:,:,np.newaxis]],axis=-1)
    # projz = np.concatenate([max0[:,:,np.newaxis],np.zeros(max0.shape)[:,:,np.newaxis],np.zeros(max0.shape)[:,:,np.newaxis]],axis=-1)
    # maxprojy = img.max(axis=1) # maxmimum projection along Z
    # maxprojy = np.flip(maxprojy,1)
    # maxprojx = img.max(axis=0) # maxmimum projection along Z
    # maxprojx = np.swapaxes(maxprojx,0,1)
    # maxprojx = np.flip(maxprojx,0)
    # add scale bar
    barX = np.round(20E-6/scaleX)
    offsetX = 30
    offsetY = 30
    scalebarX = np.arange(offsetX+10,offsetX+10+barX)
    fh = plt.figure(figsize=(8,5),constrained_layout=False) # width,height
    widths = [5,3]
    heights = [5]
    gsh = fh.add_gridspec(ncols=2,nrows=1,width_ratios=widths,height_ratios=heights)
    gsh.update(wspace=0.0,hspace=0.0)
    ah = fh.add_subplot(gsh[0,0])
    # ah = fh.add_subplot(111)
    ah.plot(scalebarX,np.ones(len(scalebarX))*(offsetY),color="white",linewidth=3)
    ah.text(offsetX,offsetY+35,r"$20\ \mu m$",color="white",fontsize=16)
    ah.axis('off')
    ah.imshow(img1f,cmap="hot")
    # draw rectangle
    img1rect = Rectangle((235,260),20,50,linewidth=1,edgecolor="w",facecolor='none')
    ah.add_patch(img1rect)
    ah = fh.add_subplot(gsh[0,1])
    ah.axis('off')
    xlims_img2 = [80,380]
    ah.imshow(img2f[:,xlims_img2[0]:xlims_img2[1]],cmap="hot")
    offsetX = 30
    offsetY = 30
    scalebarX = np.arange(0+offsetX,80+offsetX+barX)
    ah.plot(scalebarX,np.ones(len(scalebarX))*offsetY,color="w",linewidth=3)
    ah.text(offsetX,offsetY+35,r"$20\ \mu m$",color="white",fontsize=16)
    # ah = fh.add_subplot(gsh[1,0])
    # ah.imshow(maxprojx)
    # ah.plot(scalebarX,np.ones(len(scalebarX))*offsetY,color="black",linewidth=2)
    # ah.text(sizeX-offsetX-round(barX/1.5),offsetY+20,r"$100\ \mu m$",)
    # ah.axis('off')
    if (path.isdir(savepath) and len(title)>0):
        print('Path to save found!')
        print('Saving as:', savepath+'/'+title+'.png')
        plt.savefig(savepath+'/'+title+'.png',dpi=600)
    else:
        print('Path to save or title not found!')
    return(fh,ah)
    

def compress_filename(fname,depth=0):
    # depth indicates the number of subdirectories in the path to include in the title
    # depth = 0 and depth ~ inf will include all the subdirectories
    return('_'.join([''.join(part.split(' ')) for part in fname.split('.')[0].split('/')[-depth:]]))


def image_hist_equalization(img,nbins=256):
    hist,edges = np.histogram(img.flatten(),nbins,density=True)
    cdf = hist.cumsum()
    cdf = 255 * cdf/cdf[-1]
    imgeq = np.interp(img.flatten(),edges[:-1],cdf).reshape(img.shape)
    return(imgeq)
    
def findstimfreq(ts,evts):
    # computes stimulus rate from timeseries and a binary array of stimulus events: 1 when stimulus is present
    rate = np.mean(np.diff(ts[evts==1]))
    return(np.round(1/rate))

def display_lineselect_image(img,channelid,x1=0,y1=256,x2=512,y2=256,linescan=[],title='',savepath=''):
    # image a 2d numpy array, line a 1d numpy array, position [x1,y1], [x2,y2]
    # savepath  = path to save the file with name as 'title'.png
    fh = plt.figure()
    ah1 = plt.subplot(111)
    ah1.imshow(img,interpolation='nearest',origin='lower',aspect='equal')
    # adjust coordinates to reflect image orientation
    y1 = 512-y1
    y2 = 512-y2
    # flip the axis
    xx1,xx2 = [x1,x2]
    x1,x2 = [y1,y2]
    y1,y2 = [xx1,xx2]
    ah1.plot([x1,x2],[y1,y2],color='yellow')
    ah1.annotate("",xy=(x1,y1),xytext=(x2,y2),xycoords='data',arrowprops=dict(color='w',arrowstyle='<-'))
    ah1.set_xlim([0,len(img)])
    ah1.set_ylim([0,len(img)])
    ah1.set_title(title)
    # match the size of line to the frame
    if(len(linescan)<len(img) and len(linescan)>0):
        ah2 = plt.subplot(111)
        linescan = linescan[:,0,channelid]
        # fourier based interporaltion
        # linescan = signal.resample(linescan,len(img))
        # linescan[linescan<0]=0
        # numpy based linear interpolation
        linescan = np.interp(np.linspace(0,len(img)-1,len(img)),np.linspace(0,len(img)-1,len(linescan)),linescan)
        ah2.plot(linescan+len(img)/2,np.linspace(0,len(img)-1,len(img)),color='gray',linewidth=1)
        # Move left y-axis and bottim x-axis to centre, passing through (0,0)
        # ah2.spines['left'].set_position('center')
        # ah2.spines['bottom'].set_position('center')
        # Eliminate upper and right axes
        # ah2.spines['right'].set_color('none')
        # ah2.spines['top'].set_color('none')
        # Show ticks in the left and lower axes only
        # ah2.xaxis.set_ticks_position('bottom')
        # ah2.yaxis.set_ticks_position('left')
    if (path.isdir(savepath) and len(title)>0):
        print('Path to save found!')
        print('Saving as:', savepath+'/'+title+'.png')
        plt.savefig(savepath+'/'+title+'.png')
    else:
        print('Path to save or title not found! Image not saved!')
        # plt.show()
    return(fh,ah1)

def display_image(img,channels=[],title='',savepath=''):
    # display a zeiss image
    # savepath  = path to save the file with name as 'title'.png
    fh = plt.figure()
    ah1 = plt.subplot(111)
    ah1.imshow(img[:,:,0],cmap="gray")
    # ah1.imshow(img[:,:,channels],interpolation='nearest',origin='lower',aspect='equal')
    # adjust coordinates to reflect image orientation
    # ah1.set_xlim([0,len(img)])
    # ah1.set_ylim([0,len(img)])
    ah1.set_title(title)
    if (path.isdir(savepath) and len(title)>0):
        print('Path to save found!')
        print('Saving as:', savepath+'/'+title+'.png')
        plt.savefig(savepath+'/'+title+'.png')
    else:
        print('Path to save or title not found! Image not saved!')
        # plt.show()
    return(fh,ah1)


def eventtimes2events(ts,tevts):
    # function returns a vector of len(ts) with ones where events occured
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

def metadata_xmlstr_to_metadata_dict(metadata_xmlstr,metadata_elements):
    # extract metadata elements from metadata xml string
    root = ET.fromstring(metadata_xmlstr)
    metadata={}
    for element in metadata_elements:
        for item in root.findall(element["name"]):
            key = item.tag
            value = comfun.string_convert(item.text)
            # print(key,value)
            if (key in element["tags"]) or (not element["tags"]):
                if(key in metadata.keys()):
                    key = key+"2"
                metadata[key] = value
                # print("metadata:\t",key,value)
                    
    return(metadata)

def show_metadata(metadata):
    # print metadata keys and values
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
    
class Image:
    def __init__(self,_fname):       
        self.fname = _fname
        self.read_metadata_main(self.fname,metadata_keys) # read main metadata from the file
        # show_metadata(self.metadata)
        self.read_data_main()                                 # read main data from the file
        self.read_attachments()                               # read attachment data and metadata
        
    def read_metadata_main(self,fname,metadata_elements):
        with czifile.CziFile(fname) as czi:
            metadata_xmlstr = czi.metadata(raw=True)
            # print(metadata_xmlstr)
            self.metadata = metadata_xmlstr_to_metadata_dict(metadata_xmlstr,metadata_keys)

    def read_data_main(self):
        with czifile.CziFile(self.fname) as czi:
            print('Reading main data from file: {}'.format(self.fname))
            imgshape = np.array(czi.shape)
            imgaxes = list(czi.axes)
            print(imgshape,imgaxes)
            self.img_raw = czi.asarray()
            # get image info from metadata
            sizeX = int(self.metadata['SizeX']) if 'SizeX' in self.metadata.keys() else 0
            sizeY = int(self.metadata['SizeY']) if 'SizeY' in self.metadata.keys() else 0
            sizeZ = int(self.metadata['SizeZ']) if 'SizeZ' in self.metadata.keys() else 0
            sizeC = int(self.metadata['SizeC']) if 'SizeC' in self.metadata.keys() else 0
            sizeT = int(self.metadata['SizeT']) if 'SizeT' in self.metadata.keys() else 0
            # bitsize = self.metadata['ComponentBitCount'] if 'SizeT' in self.metadata.keys() else 0
            bitsize = self.metadata['ComponentBitCount']
            if(sizeX>0 and sizeY == 0 and sizeT == 0):
                # Found a single line scan
                self.img_type = "linescan" # BVCTZYX0' -> CX
                print(self.img.shape)
                input('key')
                self.img = self.img_raw[0,0,:,0,0,0,:,0]
                
                # reduce pixel data format to 8 bits
                if (bitsize>8):
                    self.img = np.uint8((self.img/(pow(2,bitsize)-1))*(pow(2,8)-1))
                    # reorder dimensions: XC
                self.img = self.img.swapaxes(0,-1)
                # Zeiss puts channel one as Green, then Red so, swap them again
                self.img = np.flip(self.img,-1)
                # add missing channels for RGB image
                self.img = np.concatenate([self.img[:,np.newaxis,:],np.zeros((sizeX,1,3-sizeC),dtype=np.uint8)],axis=-1) # original
                # self.img = np.concatenate([self.img[np.newaxis,:,:],np.zeros((sizeX,1,3-sizeC),dtype=np.uint8)],axis=-1)
                print(self.img)
                input('key')
            if(sizeX>0 and sizeY == 0 and sizeT >0):
                # Found linescan timeseries
                self.img_type = "linescan timeseries" # TX
                # print(self.img_raw.shape)
                # input('key')                
                self.img = self.img_raw[0,0,:,:,0,0,:,0] # BVCTZYX0' -> CX # put this back!
                # self.img = self.img_raw[0,:,:,0,0,:,0] # BVCTZYX0' -> CX
                # reduce pixel data format to 8 bits
                if (bitsize>8):
                    self.img = np.uint8((self.img/(pow(2,bitsize)-1))*(pow(2,8)-1))
                # reorder dimensions: XC
                self.img = self.img.swapaxes(0,-1)
                print(self.img.shape)
                # # Zeiss puts channel one as Green, then Red so, swap them again
                # self.img = np.flip(self.img,-1)
                # add missing channels for RGB image
                self.img = np.concatenate([self.img,np.zeros((sizeX,sizeT,3-sizeC),dtype=np.uint8)],axis=-1)
                print('img.shape = ',self.img.shape)
                
            if(sizeX>0 and sizeY > 0 and sizeT  == 0 and sizeZ == 0):
                # Found single frame scan
                self.img_type = "single framescan"
                print('Found a {}'.format(self.img_type))
                self.img = self.img_raw[0,0,:,0,0,:,:,0] # BVCTZYX0' -> CYX
                # reduce pixel data format to 8 bits
                if (bitsize>8):
                    self.img = np.uint8((self.img/(pow(2,bitsize)-1))*(pow(2,8)-1))
                    # reorder dimensions: XYZC
                self.img = np.transpose(self.img)
                # add missing channels for RGB image
                self.img = np.concatenate([self.img,np.zeros((int(sizeX),int(sizeY),int(3-sizeC)),dtype=np.uint8)],axis=-1)
                print('img.shape = ',self.img.shape)
                
            if(sizeX>0 and sizeY > 0 and sizeT >0):
                # Found framescan timeseries
                self.img_type = "framescan timeseries"
                print('Found a {}'.format(self.img_type))
            if(sizeX>0 and sizeY > 0 and sizeZ >0 and sizeT ==0):
                # Found framescan z-stack
                self.img_type = "framescan z-stack"
                print('Found a {}'.format(self.img_type))
                self.img = self.img_raw[0,0,:,0,:,:,:,0] # BVCTZYX0' -> CZYX
                # reduce pixel data format to 8 bits
                if (bitsize>8):
                    self.img = np.uint8((self.img/(pow(2,bitsize)-1))*(pow(2,8)-1))
                    # reorder dimensions: XYZC
                self.img = np.transpose(self.img)
                # Zeiss puts channel one as Green, then Red so, swap them again
                self.img = np.flip(self.img,-1)
                print(self.img.shape)
                # add missing channels for RGB image
                self.img = np.concatenate([self.img[:,:,:,:],np.zeros((sizeX,sizeY,sizeZ,3-sizeC),dtype=np.uint8)],axis=-1)
                print(self.img.shape)
                
    def read_attachments(self):
        with czifile.CziFile(self.fname) as czi:
            self.attachment_names = []
            for attachment in czi.attachments():
                print('Found attachment:\t',attachment.attachment_entry.name)
                if attachment.attachment_entry.name == 'Image':
                    self.attachment_names.append(attachment.attachment_entry.name)
                    imgshape = np.array(czi.shape)
                    imgaxes = list(czi.axes)
                    imageattachment = czifile.CziFile(BytesIO(attachment.data(raw=True)))
                    self.attachimage_raw = imageattachment.asarray()
                    self.attachimage_metadata = metadata_xmlstr_to_metadata_dict(imageattachment.metadata(),metadata_keys)
                    # check if image has 'X1','Y1','X2','Y2' metadata
                    keys = ['X1','Y1','X2','Y2']
                    values = [0,256,512,256]
                    for key,value in zip(keys,values):
                        if (not key in self.attachimage_metadata.keys()):
                            self.attachimage_metadata[key] = value
                            # modify image for display
                    sizeX = self.attachimage_metadata['SizeX']
                    sizeY = self.attachimage_metadata['SizeY']
                    sizeC = self.attachimage_metadata['SizeC']
                    bitsize = self.attachimage_metadata['ComponentBitCount']
                    # self.attachimageraw = czifile.CziFile(BytesIO(attachment.data(raw=True))) # NOT NEEDED
                    # reduce image dimension to CYX
                    # img = self.attachimage_raw[0,0,0:sizeC,0,0,0:sizeY,0:sizeX,0] # 'BVCTZYX0' -> CYX original
                    img = self.attachimage_raw[0,0:sizeC,0,0,0:sizeY,0:sizeX,0] # 'BVCTZYX0' -> CYX
                    # reduce pixel data format to 8 bits
                    if (bitsize>8):
                        img = np.uint8((img/(pow(2,bitsize)-1))*(pow(2,8)-1))
                        # swap axis for XYC order 
                    img = img.swapaxes(0,-1)
                    # flip image for top down orientation
                    img = np.flip(img,1)
                    # add channels for RGB display
                    img = np.concatenate((img[:,:,1][:,:,np.newaxis],img[:,:,0][:,:,np.newaxis],np.ones((sizeX,sizeY,1),dtype=np.uint8)*0),axis=-1) # orginal
                    # print(img.shape,bitsize)
                    # input('keky')
                    self.attachimage = img
                    
                if attachment.attachment_entry.name == 'TimeStamps':
                    self.attachment_names.append(attachment.attachment_entry.name)
                    self.timestamps = attachment.data()
                    if ("SizeT" in self.metadata):
                        print('SizeT: ',self.metadata['SizeT'])
                        self.timestamps = self.timestamps[0:int(self.metadata['SizeT'])]
                        
                if attachment.attachment_entry.name == 'EventList':
                    self.attachment_names.append(attachment.attachment_entry.name)
                    # self.event = {'time':0,'type':'','name':''}
                    self.events = []
                    for item in attachment.data():
                        # print(item.time)
                        # print(item.description)
                        # print(item.event_type)
                        # print(item.EV_TYPE)
                        self.events.append({'time':item.time,'type':item.event_type,'name':item.description})
                        self.eventtimes = [item['time'] for item in self.events]

    def set_data_attributes(self):
        # set main data type and attachments in the file: framescan, linescan
        pass
    
            
    def select_roi_linescan(self):
        # Class method to select roi on a linescan time series image from Zeiss LSM microscope
        if(not self.img_type == "linescan timeseries"):
            print("Object has no linescan timeseries");
            exit;
        if (not hasattr(self,'timestamps')):
            print('Exiting. No timestamps attribute in the object')
            exit  
        if (not hasattr(self,'eventtimes')):
            print('No eventtimes in the object')
            exit
            # seperate trials/blocks and compartments from a given linescan image by finding breaks
        ts = self.timestamps
        eventtimes = self.eventtimes

        
        tsdiff = np.diff(ts)
        self.itrials = np.where(tsdiff>1)[0] # breaks = number of timestamp sections seperated by > 1 sec
        self.itrials_begin = np.concatenate([[0],self.itrials])
        if (len(self.itrials)>1):
            triallen = np.mean(np.array([len(ts[self.itrials[i]:self.itrials[i+1]]) for i in range(0,len(self.itrials)-1)]),dtype=np.int)-1
        if(len(self.itrials)==1):
            triallen = len(ts[0:self.itrials[0]])
        if(len(self.itrials)==0):
            triallen = len(ts[0:-2])
            self.itrials_end = self.itrials_begin + triallen

        # split the eventtimes into eventtimes in each trial
        # convert event times to events
        self.tevents = []
        self.events = []
        for i in np.arange(0,len(self.itrials_begin)):

            tevents = np.array([evt for evt in eventtimes if (evt>=ts[self.itrials_begin[i]]) and (evt<=ts[self.itrials_end[i]])])
            self.tevents.append(tevents)
            events = eventtimes2events(ts[self.itrials_begin[i]:self.itrials_end[i]],tevents)
            self.events.append(events)



        # convert eventtimes to events
        
        
        # Call to Linescan timeseries ROI selection object
        fh = plt.figure()
        ah = plt.subplot(111)
        # Get linescan timeseries image
        # lsts = copy.deepcopy(self.img)
        # ah.imshow(self.img,origin="lower",aspect='equal',interpolation='nearest')
        # plt.show()
        
        roiselect = roilinescan_class.roiLineScanClass(fh,ah,self.img,self.itrials_begin,self.itrials_end,self.events)


            # itrial = coord["itrial"]-1
            # iroi = coord["iroi"]-1
            # postfix = "trial"+str(itrial+1)+"roi"+str(iroi+1)
            # ts = self.timestamps[itrials_begin[itrial]:itrials_end[itrial]]-self.timestamps[itrials_begin[itrial]] # ts start at 0 for each trial
            # print('self.timestamps[itrials_begin',self.timestamps[itrials_begin[itrial]],'self.timestamps[itrials_end[itrial]]',self.timestamps[itrials_end[itrial]])
            # print('self.tevents: ',self.tevents)
            # evts = eventtimes2events(ts,self.tevents[itrial]-self.timestamps[itrials_begin[itrial]])



        
        self.coords = roiselect.coords
        print('coords: ',self.coords)

        # ------- for testing purposes
        print('itrials_begin: ',self.itrials_begin)
        print('itrials_end: ',self.itrials_end)
        print('itrial_end-itrial_begin: ',self.itrials_end-self.itrials_begin)
        print('size: tevents',len(self.tevents))
        print('size: ts',np.shape(ts))
        # print('size: lsts',np.shape(lsts))
        # ----------------------------
        
        return(fh,ah)

    def extract_roi(self):
        itrials_begin = self.itrials_begin
        itrials_end = self.itrials_end
        coords = self.coords
        print('coords: ',coords)
        roidata={}
        self.nroi=np.zeros((len(itrials_begin))) # stores roi per trial
        self.stimfreq=np.zeros((len(itrials_begin))) # for stim frequency per trial

        for coord in coords:
            # print(coord)
            itrial = coord["itrial"]-1
            iroi = coord["iroi"]-1
            postfix = "trial"+str(itrial+1)+"roi"+str(iroi+1)
            ts = self.timestamps[itrials_begin[itrial]:itrials_end[itrial]]-self.timestamps[itrials_begin[itrial]] # ts start at 0 for each trial
            print('self.timestamps[itrials_begin',self.timestamps[itrials_begin[itrial]],'self.timestamps[itrials_end[itrial]]',self.timestamps[itrials_end[itrial]])
            print('self.tevents: ',self.tevents)
            evts = eventtimes2events(ts,self.tevents[itrial]-self.timestamps[itrials_begin[itrial]])
            print('extract _roi; ts: ',ts,' evts: ',evts)
            timename = "time_"+postfix
            stimname = "stim_"+postfix
            self.nroi[itrial] = iroi+1
            self.stimfreq[itrial]=findstimfreq(ts,evts)
            roidata[timename] = ts
            roidata[stimname] = evts
            if ((coord["dnTop"] != None) and (coord["dnBot"] != None)): # roi: dendrite
                denname = "dendrite_"+postfix
                dtop = np.uint(coord["dnTop"])
                dbot = np.uint(coord["dnBot"])
                den = np.mean(self.img[dbot:dtop,itrials_begin[itrial]:itrials_end[itrial],1],axis=0) # XTC Note channel order: RGB
                # with background substraction (delta F/F)
                # roidata[denname]= background_subtraction(ts,den,ts[np.where(evts>0)[0][0]])
                # no background substration
                roidata[denname] = den
                print("dendrite ROI: ",coord['iroi'],' Trial: ',coord['itrial'], ' itrial1: ',itrials_begin[itrial],' itrial2: ',itrials_end[itrial],' shape: ',den.shape)
            if ((coord["spTop"] != None) and (coord["spBot"] != None)): # roi: spine
                print("Found spine ROI")
                spinename = "spine_"+postfix
                stop = np.uint(coord["spTop"])
                sbot = np.uint(coord["spBot"])                
                spi = np.mean(self.img[sbot:stop,itrials_begin[itrial]:itrials_end[itrial],1],axis=0) # XTC Note channel order: RGB
                print("Spine ROI: ",coord['iroi'],' Trial: ',coord['itrial'], ' itrial1: ',itrials_begin[itrial],' itrial2: ',itrials_end[itrial],' stop: ',stop,' sbot: ',sbot)
                # background substraction (delta F/F)
                # roidata[spinename]= background_subtraction(ts,spi,ts[np.where(evts>0)[0][0]])
                # No background substration
                roidata[spinename] = spi
                # create pandas dataframe to store rois
        print(roidata)
        self.roidf = pd.DataFrame(roidata)

    def save_roi_to_csvfile(self,fname='',savepath=''):
        if (path.isdir(savepath) and len(fname)>0):
            fullpath = savepath+'/'+fname+'.csv'
            print('Saving as:', fullpath)
            with open(fullpath,'w') as csvfile:
                self.roidf.to_csv(csvfile,index=False)
        else:
            print('Path to save or title not found!')

