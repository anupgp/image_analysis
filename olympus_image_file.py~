import oiffile
import numpy as np
from matplotlib import pyplot as plt
import copy
import math
import common_functions as comfun

metadata_keys = [{"name":"Acquisition Parameters Common","keys":["Acquisition Device","ImageCaputreDate","LaserTransmissivity01","LaserWavelength01","ScanMode","ZoomValue"]},
                 {"name":"Axis Parameter Common","keys":["AxisCount","AxisOrder"]},
                 {"name":"Axis 0 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","ClipPosition","EndPosition","GUI MaxSize","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Axis 1 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","ClipPosition","EndPosition","GUI MaxSize","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Axis 2 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","EndPosition","GUI MaxSize","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Axis 3 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","AxisZControlUnit","PSU","CalibrateValueA","CalibrateValueB","EndPosition","GUI MaxSize","Interval","MaxSize","Piezo Z Slice","Piezo Z Start Position","Piezo Z Step","PixUnit","Start Absolute Position","StartPosition","Stop Absolute Position","UnitName"]},
                 {"name":"Axis 4 Parameters Common","keys":["AbsolutePosition","AxisCode","AxisName","CalibrateValueA","CalibrateValueB","EndPosition","GUI MaxSize","Interval","MaxSize","PixUnit","StartPosition","UnitName"]},
                 {"name":"Bleach GUI Parameters Common","keys":["Comb 0 Activation Time Per Point","ImageHeight","ImageWidth","Number Of Point","Point 0 Number Of Pixel","Point 0 Position X","Point 0 Position Y"]},
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
        with oiffile.OifFile(self.fname) as oib:
            print(dir(oib))
            if(not oib.is_oib):
                print("Program exit: Not an Olympus oib file!")
            for elm in metadata_keys:
                metaname = elm["name"]
                if (metaname in oib.mainfile.keys()):
                    # print(oib.mainfile[metaname].keys())
                    for key in elm["keys"]:
                        if key in oib.mainfile[metaname].keys():
                            value = comfun.string_convert(oib.mainfile[metaname][key])
                            print('{:<70}{:<20}{:<15}'.format(metaname+" "+key,oib.mainfile[metaname][key],str(type(value))))
                        
                else:
                    print("**** Warning ***** key: " +metaname + " not found!")
        
    def read_data_main(self):
        self.data = oiffile.imread(self.fname)
        print(self.data.shape)
            
class OlympusLineClass(OlympusImageClass):
    pass

class OlympusFrameClass(OlympusImageClass):
    pass
