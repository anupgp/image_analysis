import oiffile
import numpy as np
from matplotlib import pyplot as plt
import copy
import math
import common_functions as comfun
import os

metadata_keys = [{"name":"Acquisition Parameters Common","keys":["Acquisition Device","ImageCaputreDate","LaserTransmissivity01","LaserWavelength01","ScanMode","ZoomValue"]},
                 {"name":"Axis Parameter Common","keys":["AxisCount","AxisOrder"]},
                 {"name":"Axis 0 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","ClipPosition","EndPosition","GUI MaxSize","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Axis 1 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","ClipPosition","EndPosition","GUI MaxSize","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Axis 2 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","EndPosition","GUI MaxSize","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Axis 3 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","AxisZControlUnit","PSU","CalibrateValueA","CalibrateValueB","EndPosition","GUI MaxSize","Interval","MaxSize","Piezo Z Slice","Piezo Z Start Position","Piezo Z Step","PixUnit","Start Absolute Position","StartPosition","Stop Absolute Position","UnitName"]},
                 {"name":"Axis 4 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","EndPosition","GUI MaxSize","Interval","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Bleach GUI Parameters Common","keys":[
                     "Comb 0 Activation Time Per Point",
                     "ImageHeight",
                     "ImageWidth"]},
                 {"name":"Bleach GUI Parameters Common","keys":[
                     "Number Of Point",
                     "Point 0 Number Of Pixel",
                     "Point 0 Position X",
                     "Point 0 Position Y",
                     "Point 1 Number Of Pixel",
                     "Point 1 Position X",
                     "Point 1 Position Y",
                     "Point 2 Number Of Pixel",
                     "Point 2 Position X",
                     "Point 2 Position Y",
                     "Point 3 Number Of Pixel",
                     "Point 3 Position X",
                     "Point 3 Position Y",
                     "Point 4 Number Of Pixel",
                     "Point 4 Position X",
                     "Point 4 Position Y",
                     "Point 5 Number Of Pixel",
                     "Point 5 Position X",
                     "Point 5 Position Y",
                 ]},
                 {"name":"Bleach Laser  6 parameters","keys":["LaserTransmissivity","LaserWavelength"]},
                 {"name":"GUI Channel 5 Parameters","keys":["AnalogPMTGain","AnalogPMTOffset","AnalogPMTVoltage","CH Name","EmissionWavelength","ExcitationWavelength"]},
                 {"name":"GUI Channel 6 Parameters","keys":["AnalogPMTGain","AnalogPMTOffset","AnalogPMTVoltage","CH Name","EmissionWavelength","ExcitationWavelength"]},
                 {"name":"Laser 5 Parameters","keys":["LaserTransmissivity","LaserWavelength"]},
                 {"name":"Reference Image Parameter","keys":["HeightConvertValue","HeightUnit","ImageDepth","ImageHeight","ImageWidth","PixConvertValue","PixUnit","ValidBitCounts","WidthConvertValue","WidthUnit"]},
                 {"name":"Version Info","keys":["FileVersion","SystemName","SystemVersion"]}]

class OlympusImageClass:
    def __init__(self,fname):
        self.fname = fname
        self.read_metadata_main(metadata_keys) # read main metadata from the file
        # show_metadata(self.metadata)
        self.read_data_main()                                 # read main data from the file
        # self.read_attachments()                               # read attachment data and metadata
        
    def read_metadata_main(self,metadata_keys):
        self.metadata={}
        with oiffile.OifFile(self.fname) as oib:
            # print(oib.mainfile)
            # print(dir(oib))
            if(not oib.is_oib):
                print("Program exit: Not an Olympus oib file!")
            for elm in metadata_keys:
                metaname = elm["name"]
                if (metaname in oib.mainfile.keys()):
                    # print(oib.mainfile[metaname].keys())
                    for key in elm["keys"]:
                        if key in oib.mainfile[metaname].keys():
                            value = comfun.string_convert(oib.mainfile[metaname][key])
                            # print('{:<70}{:<20}{:<15}'.format(metaname+" "+key,oib.mainfile[metaname][key],str(type(value))))
                            self.metadata[key] = value
                        
                else:
                    print("**** Warning ***** key: " +metaname + " not found!")

    def show_metadata(self):
        # print metadata keys and values
        metadata = self.metadata
        for key in metadata:
            print(key,metadata[key])
        
    def read_data_main(self):
        self.img = oiffile.imread(self.fname)
        print(self.img.shape)
        scanmode = self.metadata['ScanMode'] if 'ScanMode' in self.metadata.keys() else ""
        bitsize = int(self.metadata['ValidBitCounts']) if 'ValidBitCounts' in self.metadata.keys() else 0
        sizex = int(self.metadata['ImageWidth']) if 'ImageWidth' in self.metadata.keys() else 0
        sizey = int(self.metadata['ImageHeight']) if 'ImageHeight' in self.metadata.keys() else 0
        sizec = self.img.shape[0]
        if(scanmode == "XY"):
            # single frame scan
            self.img_type = "single framescan"
            print('Found a {}'.format(self.img_type))
            # reduce pixel data format to 8 bits
            # if (bitsize>8):
            #     self.img = np.uint8((self.img/(pow(2,bitsize)-1))*(pow(2,8)-1))
            # reorder dimensions: XYZC
            self.img = np.moveaxis(self.img,0,-1)
            # add missing channels for RGB image
            self.img = np.concatenate([self.img,np.zeros((int(sizex),int(sizey),int(3-sizec)),dtype=np.uint8)],axis=-1)
            print('img.shape = ',self.img.shape)
        if(scanmode == "XYZ"):
            print(self.img.shape)
            # zstack
            self.img_type = "zstack"
            print('Found a {}'.format(self.img_type))
        
            
    def display_image_with_markers(self,channels=[],title='',savepath=''):
    # display an olympus image
    # savepath  = path to save the file with name as 'title'.png
        nmarkers = int(self.metadata['Number Of Point']) if 'Number Of Point' in self.metadata.keys() else 0
        markers = [{'x':None,'y':None} for marker in range(nmarkers)]
        for i in range(nmarkers):
            xkey = "".join(("Point ",str(i),' Position X'))
            ykey = "".join(("Point ",str(i),' Position Y'))
            markers[i]["x"] =  int(self.metadata[xkey]) if xkey in self.metadata.keys() else 0
            markers[i]["y"] =  int(self.metadata[ykey]) if ykey in self.metadata.keys() else 0
        print(markers)
        fh = plt.figure()
        ah1 = plt.subplot(111)
        ah1.imshow(self.img[:,:,0],cmap="hot")
        # ah1.imshow(self.img)
        # display markers
        for marker in markers:
            print(marker)
            ah1.plot(marker['x'],marker['y'],'o',markersize=5,color='blue')
        fh.tight_layout()
        # ah1.imshow(img[:,:,channels],interpolation='nearest',origin='lower',aspect='equal')
        # adjust coordinates to reflect image orientation
        # ah1.set_xlim([0,len(img)])
        # ah1.set_ylim([0,len(img)])
        ah1.set_title(title)
        if (os.path.isdir(savepath) and len(title)>0):
            print('Path to save found!')
            print('Saving as:', savepath+'/'+title+'.png')
            plt.savefig(savepath+'/'+title+'.png')
        else:
            print('Path to save or title not found! Image not saved!')
        plt.show()
        return(fh,ah1)

    # def diplay_zprojection(self):
    #     # display the z-projected image of a zstack
        
class OlympusLineClass(OlympusImageClass):
    pass

class OlympusFrameClass(OlympusImageClass):
    pass
