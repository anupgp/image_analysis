import os
import re
import tifffile
from tiff_image_class import tiff_file
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

project=["trains"]
dpath = "/Volumes/GoogleDrive/Shared drives/Beique Lab/PAST LAB MEMBERS/Cary Soares/SNIFFER DATA SHARED AUG 2020/CaryData/tiff_archive"
roisavepath = "/Volumes/GoogleDrive/Shared drives/Beique Lab/CURRENT LAB MEMBERS/Anup Pillai/iglusnfr_carrydata"
roisavepath = os.path.join(roisavepath,project[0])

# read the exp_details.xlsx file
expdetails = pd.read_excel(os.path.join(dpath,project[0],"exp_details.xlsx"))
print(expdetails)
input()
# get all the directories (cells)
cells = [entry for entry in os.listdir(os.path.join(dpath,project[0])) if os.path.isdir(os.path.join(dpath,project[0],entry))]
print("cells: ",cells)
for i in range(len(cells)):
    print("opening cell: {}".format(cells[i]))
    # get experiments (train frequencies used for each cell
    exps = [entry for entry in os.listdir(os.path.join(dpath,project[0],cells[i])) if os.path.isdir(os.path.join(dpath,project[0],cells[i],entry))]
    for j in range(len(exps)):
        print("opening exp: {}".format(exps[j]))
        expdetails_id = "".join((cells[i],"-",re.search("([0-9]+)(?:.*)",exps[j]).group(1)))
        flip = int(expdetails.loc[expdetails["file_name"]==expdetails_id,"to_flip"])
        print("dendrite spine flip order for cell {} and exp {} is {}".format(cells[i],exps[j],flip))
        tifs = [entry for entry in os.listdir(os.path.join(dpath,project[0],cells[i],exps[j])) if re.search(".*.tif",entry)]
        tifgs = [entry for entry in tifs if re.search(".*_c0000_.*",entry)]
        tifrs = [entry for entry in tifs if re.search(".*_c0001_.*",entry)]
        for k in range(len(tifgs)):
        # for k in range(len([0])):
            itrial = k
            filename = os.path.join(dpath,project[0],cells[i],exps[j],tifgs[k]) 
            print("Opening file: ",filename)
            tif=tiff_file(filename)
            print("BitsPerPixel: ",tif.metadata["BitsPerPixel"])
            label = "".join((tifgs[k]))
            fh,ah = tif.roi_select(label,flip)
            plt.show()
            print("ROI coords: ",tif.coords)
            tif.roi_extract()
            roisavename = "".join((project[0],"_",cells[i],"_",exps[j],"_","trial",str(itrial)))
            print(roisavename)            
            tif.roi_save(roisavepath,roisavename)
            input("press a key to continue")




