# Need to do:
# 1. Take off the normalization (delta F/F) from the ROI timeseries. Because, doing this normalization prior to the low pass filter substraction, to removes signal drifts, is a bad idea.
# 2. Include markers of stimulus arrival on the linescan timeseries displayed for selecting ROIs
# 3. Make the above figure a bit better aesthetically 

import zeissImageClasses as zeiss
from zeissImageClasses import compress_filename
from matplotlib import pyplot as plt
import h5py
import pandas as pd
import re
import os

# read masterfile in Microsoft_excel
# masterfile_path = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/'
image_path = '/Volumes/UOTT JF/czi file/'
# image_path = '/Users/macbookair/Downloads/jfdata/'
# masterfname = masterfile_path + 'anup_iglusnfr_all_good_data.xlsx'
fname = image_path + '2019-09-17-001-1.czi'
# masterdf = pd.read_excel(masterfname,header=0,use_cols=11)
# colnames = list(masterdf.columns)
# fcount=0

zfilelst = zeiss.Image(fname)
zfilelss = zeiss.Image(fname)
print(zfilelss.img)
input('key')
# X and Y are flipped to match the image orientation
x1 = zfilelss.attachimage_metadata['X1']
y1 = zfilelss.attachimage_metadata['Y1']
x2 = zfilelss.attachimage_metadata['X2']
y2 = zfilelss.attachimage_metadata['Y2']
fh1,ah1 = zeiss.display_lineselect_image(zfilelss.attachimage,1,x1,y1,x2,y2,title=fname,savepath="")
fh2,ah2 = zfilelst.select_roi_linescan()
plt.show()
input('enter key')
zfilelst.extract_roi()
print(zfilelst.roidf)
print(zfilelst.coords)
zfilelst.save_roi_to_csvfile(fname="test.csv",savepath=image_path)
# fh2,ah2 = zfilelst.select_roi_linescan()
    
# for row in range(0,masterdf.shape[0]):
#     lstfname = str(masterdf.loc[row,"linescan_timeseries_file"])
#     nspines = round(masterdf.loc[row,"nSpines"])
#     ndendrites = round(masterdf.loc[row,"nDendrites"])
#     ntrials = round(masterdf.loc[row,"ntrials"])
#     if(re.search(r'^.*nan.*$',lstfname) is not None):
#         continue
#     # add path to filename
#     lstfname = image_path+str(masterdf.loc[row,"linescan_timeseries_file"])
#     # check is linescan_timeseries file exists
#     if(not os.path.exists(lstfname)):
#         print('Linescan timeseries file does not exist!')
#         continue
#     fcount  = fcount + 1
#     print(str(fcount)+": "+lstfname)
#     # check is linescan_lineselect file exists
#     lssfname = str(masterdf.loc[row,"lineselect_file"])
#     if(re.search(r'^.*nan.*$',lssfname) is not None):
#         lssfname = lstfname
#     else:
#         lssfname = image_path + lssfname 
#     print(" "*len(str(fcount)+": ")+lssfname)
#     # check is linescan_select file exists
#     if(not os.path.exists(lssfname)):
#         print('Linescan select file does not exist!')
#         continue
#     # extract date
#     expdate = re.search('[0-9]{8,8}?',lstfname)[0]
#     print('Expdate:\t',expdate)
#     # extract spineid
#     spineid = re.search('\/[0-9]{8,8}?\/.*?\/',lstfname)[0][len(expdate)+2:-1]
#     print('Spineid:\t',spineid)
#     # filename
#     fname = re.search('[^/]+.\.*$',lstfname)[0][0:-4] # filename without extension
#     fname = re.sub(' ','_',fname)
#     print('Filename:\t',fname)
#     print('No. of spines:\t',nspines)
#     print('No. of dendrites:\t',ndendrites)
#     print('No. of trials:\t',ntrials)
#     # ------------
#     dirname = masterfile_path + expdate + '_' + spineid
#     # mkdir to place all the figures for that particular file
#     if(not os.path.isdir(dirname)):
#         os.mkdir(dirname)
#     # -----------
#     # open files
#     zfilelst = zeiss.Image(lstfname)
#     zfilelss = zeiss.Image(lssfname)
#     # show metadata
#     # zeiss.show_metadata(zfilelst.metadata)
#     # zeiss.show_metadata(zfilelss.metadata)
#     # print(zfilelss.attachimage_metadata)
#     # -------------
#     # print(zfilelst.attachment_names)
#     # print(zfilelss.attachment_names)
#     # X and Y are flipped to match the image orientation
#     x1 = zfilelss.attachimage_metadata['X1']
#     y1 = zfilelss.attachimage_metadata['Y1']
#     x2 = zfilelss.attachimage_metadata['X2']
#     y2 = zfilelss.attachimage_metadata['Y2']
#     fignamels = expdate+'_'+spineid+'_'+fname
#     figsavepath = dirname
#     fh1,ah1 = zeiss.display_lineselect_image(zfilelss.attachimage,1,x1,y1,x2,y2,title=fignamels,savepath=figsavepath)
#     fh2,ah2 = zfilelst.select_roi_linescan()
#     # -----------------
#     plt.show()
#     input('enter key')
#     zfilelst.extract_roi()
#     print(zfilelst.roidf)
#     print(zfilelst.coords)
#     zfilelst.save_roi_to_csvfile(fname=fignamels,savepath=dirname)
