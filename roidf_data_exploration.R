rm(list=ls());
source("/Users/macbookair/goofy/codes/image_analysis/loadlibraries.R");
## load the dataframe in csv format
datapath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis"
roidf = read.csv(paste(datapath,'iglusnfr_ca1_final_roidf_template_match_method.csv',sep='/'),sep=",",header=TRUE,stringsAsFactors=FALSE,row.names=NULL);
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
## plot histograms
noisepeaks = roidf[roidf$istim==0 & roidf$roitype == "spine","peak"]
noisemu = mean(noisepeaks,na.rm = TRUE)
noisesigma = sd(noisepeaks,na.rm = TRUE)
respeaks = roidf[roidf$istim>0 & roidf$roitype == "spine","peak"]
minpeak = min(min(noisepeaks,na.rm = TRUE),min(respeaks,na.rm = TRUE),na.rm = TRUE)
maxpeak = max(max(noisepeaks,na.rm = TRUE),max(respeaks,na.rm = TRUE),na.rm = TRUE)
nbreaks = 100
threshold = noisemu+(noisesigma*3)
breaks = seq(minpeak,maxpeak,(maxpeak-minpeak)/nbreaks)
hnoise = hist(noisepeaks,breaks,right=TRUE,plot = TRUE,freq=FALSE,col = rgb(0,0,1,1/4),main = "Histogram of noise and responses",xlab="Peak amplitude")
hres = hist(respeaks,breaks,right=TRUE,plot = TRUE,freq=FALSE,add = TRUE,col = rgb(1,0,0,1/4))
abline(v = threshold,col = "red")
successpeaks = respeaks[respeaks>threshold]
failurepeaks = respeaks[respeaks<=threshold]
dev.new()
hfailure = hist(failurepeaks,breaks,right=TRUE,plot = TRUE,freq=FALSE,col = rgb(0,0,1,1/4))
hsuccess = hist(successpeaks,breaks,right=TRUE,plot = TRUE,freq=FALSE,col = rgb(1,0,0,1/4),add = TRUE)

