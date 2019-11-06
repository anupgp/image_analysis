import linescan_classes
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os.path

fnpathprefix = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/'
mastersheet = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/anup_iglusnfr_all_data.csv"
masterdf = pd.read_csv(mastersheet,sep=',',header=0, index_col=None,skip_blank_lines=True,usecols = [0,1,2,3,4])
for i in np.arange(0,len(masterdf)):
    fnlsts = fnpathprefix + masterdf.iloc[i]['filename-ts'] # Filename linescan timeseries 
    if(pd.isna(masterdf.iloc[i]['filename-ls'])):           # If no seperate lineselect file then treat fnlsts as the lsls file
        fnlsls = fnpathprefix + masterdf.iloc[i]['filename-ts']
    else:
        fnlsls = fnpathprefix + masterdf.iloc[i]['filename-ls'] # Filename linescan lineselect
    if ( not os.path.exists(fnlsts)):
        print('Linecan timeseries file: ', fnlsts, ' does not exist')
    if ( not os.path.exists(fnlsls)):
        print('Linecan timeseries file: ', fnlsls, ' does not exist')
    print('Filename Timeseries: ',fnlsts)
    print('Filename Lineselect: ',fnlsls)
        
        
        
