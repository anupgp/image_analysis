import numpy as np
import pandas as pd
import math
import seaborn as sns
import re
import os
from scipy import stats as scipystats

# ----------------
import matplotlib
matplotlib.use("gtk3agg")
print(matplotlib.get_backend())
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
sns.set()
sns.set_style("white")
sns.set_style("ticks")
# ---------------


def format_plot(fh,ah,xlab="",ylab="",title=""):
    font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
    fontprop = font_manager.FontProperties(fname=font_path,size=18)
    ah.spines["right"].set_visible(False)
    ah.spines["top"].set_visible(False)
    ah.spines["bottom"].set_linewidth(1)
    ah.spines["left"].set_linewidth(1)
    ah.set_title(title,FontProperties=fontprop)
    ah.set_xlabel(xlab,FontProperties=fontprop)
    ah.set_ylabel(ylab,fontproperties=fontprop)
    ah.tick_params(axis='both',length=6,direction='out',width=1,which='major')
    ah.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
    ah.tick_params(axis='both', which='major', labelsize=16)
    ah.tick_params(axis='both', which='minor', labelsize=12)
    return(fh,ah)

# Set some pandas options
pd.set_option('display.notebook_repr_html', False)
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.max_rows', 10)


# open the csv file containing the main dataframe
datapath = "/home/anup/gdrive-beiquelab/CURRENT LAB MEMBERS/Anup Pillai/iglusnfr_carrydata"
fname="iglusnfr_ca1_carry_data_trains_v1.csv"
with open(os.path.join(datapath,fname),'r') as csvfile:
    df = pd.read_csv(csvfile)
# Generate extra columns from filename column
# df["spineid"] = df["filename"].str.extract("(?:[^_]+[_])([^_.*^_]+)(?:.*)")
# dfname = "".join(("iglusnfr_ca1_carry_data_","trains_","v1.csv"))
# dfname_withpath = os.path.join(datapath,dfname)
# df.to_csv(dfname_withpath,index=False)
print(df)
input()
print(df["spineid"].unique())

fh = plt.figure()
ah1 = fh.add_subplot(111)
hdf = df[(df["roitype"] == "spine") & (df["istim"] == 0)]
h,bins = np.histogram(hdf["peak"],bins=80,density=True)
ah1.plot(bins[1:],h)
ah1.plot([0,0],[0,10])
plt.show()


