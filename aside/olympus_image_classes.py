import oiffile
import numpy as np
from matplotlib import pyplot as plt
import copy
import math

class OlympusImageClass:
    def __init__(self,fname):
        self.fname = fname
        self.read_metadata_main(metadata_keys) # read main metadata from the file
        # show_metadata(self.metadata)
        self.read_data_main()                                 # read main data from the file
        self.read_attachments()                               # read attachment data and metadata
        
    def read_metadata_main(self,metadata_keys):
        with oiffile.OifFile(infile) as oib:
            pass
        
    def read_data_main(self):
        self.data = oiffile.imread(self.fname)
        print(self.data.shape)
            
class OlympusLineClass(OlympusImageClass):
    pass

class OlympusFrameClass(OlympusImageClass):
    pass
