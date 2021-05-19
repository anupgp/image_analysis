import numpy as np
import pandas as pd
import re

datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/' 
batchfname = datapath + 'anup_iglusnfr_all_good_data.xcsv'
# open the csv file containing the list of roi timeseries data
with open(batchfname,'r') as csvfile:
    batchcsv = pd.read_csv(csvfile)
for i in range(0,len(batchcsv)):
# for i in range(0,20):
    expfname = batchcsv['filename'][i] # complete filename with path
    exppath = re.search('^.+/+',expfname)[0] # path to filename
    expfname2 = re.search('[^/]+.csv$',expfname)[0][0:-4] # filename without extension
    expdate = re.search('[0-9]{8,8}?',expfname2)[0]
    if (expdate is None):
        expdate = ''
        print('Warning expdate not found!')           
    print('opening roi timeseries file: ',expfname)
    # open one roi timeseries file 
    with open(expfname,'r') as csv_expfile:
        expfile = pd.read_csv(csv_expfile)
        print(expfile)
    expfileinfo = get_ntrialsrois(expfile)
    

    
