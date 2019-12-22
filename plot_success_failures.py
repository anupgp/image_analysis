import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib
matplotlib.use("TkAgg")


font_path = '/Users/macbookair/.matplotlib/Fonts/Arial.ttf'
fontprop = font_manager.FontProperties(fname=font_path,size=18)


datapath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis_old/' 
fname_tsuccess = 'iglusnfr_ca1_tsuccess.csv'
fname_ysuccess = 'iglusnfr_ca1_ysuccess.csv'
fname_tfailure = 'iglusnfr_ca1_tfailure.csv'
fname_yfailure = 'iglusnfr_ca1_yfailure.csv'

tsuccess = np.loadtxt(datapath+fname_tsuccess,delimiter=',')
ysuccess = np.loadtxt(datapath+fname_ysuccess,delimiter =',')
tfailure = np.loadtxt(datapath+fname_tfailure,delimiter=',')
yfailure = np.loadtxt(datapath+fname_yfailure,delimiter =',')

# convert t==0 to nan
tsuccess = np.where(tsuccess == 0,np.nan,tsuccess)
tsuccess[0] = 0
tfailure = np.where(tfailure == 0,np.nan,tfailure)
tfailure[0] = 0

ysuccess_avg = np.nanmean(ysuccess,axis=1)
yfailure_avg = np.nanmean(yfailure,axis=1)
# crop vector to the first 0 or nan
iysuccess_avg = np.where(ysuccess_avg != 0)[0]
print(iysuccess_avg)
ysuccess_avg = ysuccess_avg[iysuccess_avg]
tsuccess_avg = tsuccess[iysuccess_avg,0]

print(ysuccess_avg)
print(tsuccess_avg)

fh1 = plt.figure()
ah1 = fh1.add_subplot(111)

for i in np.arange(0,tsuccess.shape[1]):
    ah1.plot(tsuccess[:,i],ysuccess[:,i])

ah1.plot(tsuccess_avg,ysuccess_avg,color='k',linewidth=2)


fh2 = plt.figure()
ah2 = fh2.add_subplot(111)

for i in np.arange(0,tsuccess.shape[1]):
    ah2.plot(tfailure[:,i],yfailure[:,i])

ah2.plot(tfailure[:,1],yfailure_avg,color='k',linewidth=2)

nsuccess = ysuccess.shape[1]
nfailure = yfailure.shape[1]
ntrials = nsuccess + nfailure

# ---------------

ah1.spines["right"].set_visible(False)
ah1.spines["top"].set_visible(False)
ah1.spines["bottom"].set_linewidth(1)
ah1.spines["left"].set_linewidth(1)
ah1.set_xlabel('Time (s)',FontProperties=fontprop)
ah1.set_ylabel(r'$\Delta$F/F',fontproperties=fontprop)
ah1.tick_params(axis='both',length=6,direction='out',width=1,which='major')
ah1.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
ah1.tick_params(axis='both', which='major', labelsize=16)
ah1.tick_params(axis='both', which='minor', labelsize=12)
ah1.set_title('Success: '+str(nsuccess)+'/'+str(ntrials),fontproperties=fontprop)
ah1.set_ylim([-1,4])
ah1.set_xlim([0,0.1])
xticks = np.array([0,0.025,0.05,0.075,0.1])
ah1.set_xticks(xticks)
fh1.tight_layout()
# ------------
ah2.spines["right"].set_visible(False)
ah2.spines["top"].set_visible(False)
ah2.spines["bottom"].set_linewidth(1)
ah2.spines["left"].set_linewidth(1)
ah2.set_xlabel('Time (s)',FontProperties=fontprop)
ah2.set_ylabel(r'$\Delta$F/F',fontproperties=fontprop)
ah2.tick_params(axis='both',length=6,direction='out',width=1,which='major')
ah2.tick_params(axis='both',length=3,direction='out',width=1,which='minor')
ah2.tick_params(axis='both', which='major', labelsize=16)
ah2.tick_params(axis='both', which='minor', labelsize=12)
ah2.set_title('Failure: '+str(nfailure)+'/'+str(ntrials),fontproperties=fontprop)
ah2.set_ylim([-1,2])
ah2.set_xlim([0,0.1])
xticks = np.array([0,0.025,0.05,0.075,0.1])
ah2.set_xticks(xticks)
fh2.tight_layout()
# -----------------------
# save figures
success_figname = datapath + 'iglusnfr_ca1_success_trials' + '.png'
failure_figname = datapath + 'iglusnfr_ca1_failure_trials' + '.png'
# fh1.savefig(success_figname)
# fh2.savefig(failure_figname)
# plt.close(fh)
# plt.show()

# save the average success trace
avg_success = np.concatenate((tsuccess_avg[:,np.newaxis],ysuccess_avg[:,np.newaxis]),axis=1)
np.savetxt(datapath + 'iglusnfr_ca1_success_avg.csv',avg_success,delimiter=',')
