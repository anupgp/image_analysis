rm(list=ls());
source("/Users/macbookair/goofy/codes/image_analysis/loadlibraries.R");
## load the dataframe in csv format
datapath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis"
roidf = read.csv(paste(datapath,'iglusnfr_ca1_final_analysisV4.csv',sep='/'),sep=",",header=TRUE,stringsAsFactors=FALSE,row.names=NULL);
## remove rows with more than 8 istim
## roidf = roidf[roidf$istim<=8,]
## add a new column to hold expid
filenames = roidf$filename
expids = unlist(lapply(filenames,FUN=function(x){il=regexpr('[0-9]+_[^_]+_?',x,perl=TRUE)[];ir  = il + attr(regexpr('[0-9]+_[^_]+_?',x,perl=TRUE),'match.length')-1;return(substr(x,il,ir-1))}))
roidf = cbind(roidf,expid = expids)
## add new columm to hold roiid
roiids = paste(roidf[,"expid"],roidf[,"roitype"],roidf[,"iroi"],sep="_")
roidf = cbind(roidf,roiid = roiids)
## itrial begins from 1 for each filename, make a new itrial to count trials of each roiid
roidf = ddply(roidf,.(roiid,stimfreq,istim),function(x){
    trial = seq(1,dim(x)[1],1)
    dfout = cbind(x,trial = trial)
    return(as.data.frame(dfout))})
## test new roidf
## filenames = c("20190415_C3_Image8Block1","20190415_C3_Image10Block1")
## print(roidf[roidf$filename %in% filenames,c("filename","iroi","itrial","roiid","istim","trial")])
## compute probability of release
## for each expid+iroi+stimfreq+istim, calculate Pr and potency
peakmin = 0.03
rtmin = 0.001
rtmax = 0.03
dkmin = 0.02
dkmax = 1                               #
roidf=ddply(roidf,.(roiid,stimfreq,istim),function(x){
    ntrials = max(x$trial);
    ## set parameter values of responses whose peak < peakthres to NA
    ## adjust delay to reflect the actual delay from the stimulus
    ipeak = (x$peak >= peakmin);   #irows with peak >= peakthres
    irt = (x$risetime >= rtmin) & (x$risetime <= rtmax);   #irows with risetime >= rtmin & risetime <= rtmax
    idk = (x$decaytime >= dkmin) & (x$decaytime <= dkmax)
    isuccess = ipeak & irt & idk
    pr = sum(isuccess)/ntrials;          #Pr is number of success / ntrials
    potency = mean(x$peak[isuccess],na.rm = TRUE); #potency is mean of sucessfull peaks
    ## if(is.nan(potency)){
    ##     potency = 0;
    ## }
    print(c("ntrials: ",ntrials,"x$peak[isuccess] : ", x$peak[isuccess]));
    print(c("potency : ", toString(potency)));
    ## delay2 = x$delay - (0.1 + (1/x$stimfreq[1])*(x$istim[1]-1));
    ## delay2[!isuccess] = NA;
    ## --------
    ## peak2 =x$peak;
    ## peak2[!isuccess] = NA;
    ## -------x
    ## risetime2 = x$risetime;
    ## risetime2[!isuccess] = NA
    ## ---------
    ## decaytime2 = x$decaytime;
    ## decaytime2[!isuccess] = NA;
    ## dfout = cbind(x,isuccess = isuccess,peak2=peak2,risetime2 = risetime2,decaytime2 = decaytime2,delay2=delay2,ntrials = ntrials,pr = pr,potency = potency)
    dfout = cbind(x,ipeak = ipeak,irt = irt,idk = idk,isuccess = isuccess,ntrials = ntrials,pr = pr,potency = potency)
    return(as.data.frame((dfout)))})
## add new columns for potency and Pr normalized to first stimulus
roidf=ddply(roidf,.(roiid,stimfreq,trial),function(x){
    normpotency = x$potency/x$potency[1];
    normpr = x$pr/x$pr[1];
    dfout = cbind(x,normpr = normpr,normpotency = normpotency)
    return(as.data.frame(dfout))})
## make a histogram of peak amplitude to decide on the threshold
## hist(roidf$peak,breaks=100)
## ---------------
## freq = 8;
## stim = 1;
## trial = 1
## roitype = "spine"
## omit roi
roiidomit2hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1","20190418_S1E3_spine_1")
roiidomit8hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1")
roiidomit20hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1")
## add new columns to indicate omitrois for 2hz,8hz and 20hz
roidf=ddply(roidf,.(roiid,stimfreq),function(x){
    roiid = unique(as.character(x$roiid))
    nrows = dim(x)[1]
    iselect = rep(TRUE,nrows)
    ## stimfreq == 2
    if(all(x$stimfreq == 2) & roiid %in% roiidomit2hz){
        iselect = rep(FALSE,nrows)
    }
    ## stimfreq == 8
    if(all(x$stimfreq == 8) & roiid %in% roiidomit8hz){
        iselect = rep(FALSE,nrows)
    }
    ## stimfreq == 20
    if(all(x$stimfreq == 20) & roiid %in% roiidomit20hz){
        iselect = rep(FALSE,nrows)
    }
    dfout = cbind(x,iselect=iselect)
    return(as.data.frame(dfout))})
##
unique(as.character(roidf[roidf$stimfreq == 2 & roidf$roitype == "spine"  ,"roiid"]))
