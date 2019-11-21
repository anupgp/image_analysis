rm(list=ls());
source("/Users/macbookair/goofy/codes/image_analysis/loadlibraries.R");
## load the dataframe in csv format
datapath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis"
roidf = read.csv(paste(datapath,'iglusnfr_ca1_final_analysisV2.csv',sep='/'),sep=",",header=TRUE,stringsAsFactors=FALSE,row.names=NULL);
## remove rows with more than 8 istim
roidf = roidf[roidf$istim<=8,]
## add a new column to hold expid
filenames = roidf$filename
expids = unlist(lapply(filenames,FUN=function(x){il=regexpr('[0-9]+_[^_]+_?',x,perl=TRUE)[];ir  = il + attr(regexpr('[0-9]+_[^_]+_?',x,perl=TRUE),'match.length')-1;return(substr(x,il,ir-1))}))
roidf = cbind(roidf,expid = expids)
## add new columm to hold roiid
roiids = paste(roidf[,"expid"],roidf[,"roitype"],roidf[,"iroi"],sep="_")
roidf = cbind(roidf,roiid = roiids)
## itrial begins from 1 for each filename, make a new itrial to could trials of each roiid
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
    ipeaks = (x$peak >= peakmin);   #irows with peak >= peakthres
    irts = (x$risetime >= rtmin) & (x$risetime <= rtmax);   #irows with risetime >= rtmin & risetime <= rtmax
    idks = (x$decaytime >= dkmin) & (x$decaytime <= dkmax)
    isuccess = ipeaks & irts & idks
    pr = sum(isuccess)/ntrials;          #Pr is number of success / ntrials
    potency = mean(x$peak[isuccess],na.rm = TRUE); #potency is mean of sucessfull peaks
    if(is.nan(potency)){
        potency = 0;
    }
    print(c("ntrials: ",ntrials,"x$peak[isuccess] : ", x$peak[isuccess]));
    print(c("potency : ", toString(potency)));
    delay2 = x$delay - (0.1 + (1/x$stimfreq[1])*(x$istim[1]-1));
    delay2[!isuccess] = NA;
    ## --------
    peak2 =x$peak;
    peak2[!isuccess] = NA;
    ## -------x
    risetime2 = x$risetime;
    risetime2[!isuccess] = NA
    ## ---------
    decaytime2 = x$decaytime;
    decaytime2[!isuccess] = NA;
    dfout = cbind(x,peak2=peak2,risetime2 = risetime2,decaytime2 = decaytime2,delay2=delay2,ntrials = ntrials,pr = pr,potency = potency)
    return(as.data.frame((dfout)))})
## add new columns for potency and Pr normalized to first stimulus
roidf=ddply(roidf,.(roiid,stimfreq,trial),function(x){
    npotency = x$potency/x$potency[1];
    npr = x$pr/x$pr[1];
    dfout = cbind(x,npr = npr,npotency = npotency)
    return(as.data.frame(dfout))})
## make a histogram of peak amplitude to decide on the threshold
## hist(roidf$peak,breaks=100)
## ---------------
## freq = 8;
## stim = 1;
## trial = 1
## roitype = "spine"
## aggrdata = roidf[roidf$stimfreq == freq & roidf$roitype == roitype,] 
## freqstim=NULL
## freqstim = aggregate(cbind(pr) ~ (roiid+istim), FUN=function(x){return(mean(x, na.rm = TRUE))},data=aggrdata); # peak
## ## freqstim = freqstim[order(freqstim$date),]
## print(freqstim)
## ## ---------------
## ## dev.new(width=8, height=5)
## plotsavepath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/plots/spines_2hz_potency_vs_stim.png"
## png(plotsavepath,width=20,height=10,units="cm",bg="white",res=300)
## par(bty="n");par(cex.axis=2);par(las=0);par(mar=c(4,4,2,1));par(mfrow = c(1,1));par(bg="white");par(mgp=c(3,1,0));par(oma=c(1,1,1,1))
## lineplot.CI(istim,potency,roiid,data=roidf[roidf$stimfreq == 2 & roidf$roitype == "spine",],xlab="Stimulus number",ylab = "Probability of release",cex=1,legend=FALSE,axis=FALSE,xaxt='n',yaxt = 'n')
## title("Stim freq: 20 Hz; ROI type: spine",line = 1)                 # position the title
## axis(1,at=c(1,2,3,4,5,6,7,8),labels=as.character(c("1","2","3","4","5","6","7","8")),tick=T,lwd=1,cex.axis=1,xpd=T,las=1,padj=0,hadj=0)
## axis(2,at=c(0,0.2,0.4,0.6,0.8,1),labels=as.character(c("0","0.2","0.4","0.6","0.8","1")),tick=T,lwd=1,cex.axis=1,xpd=F,las=1)
## dev.off()
## ## try some plotting
## options("width"= 170);
## par(mar=c(4,6,4,2));par(mgp=c(4,1,0));par(lwd = 1); #(bottom, left,top,right)
## par(mfrow = c(1,1))
## par(bg="white");
## dev.new(width=5, height=4)
## ## ---------------
## roidf1 = roidf[roidf[,"roitype"]== "spine" & roidf["stimfreq"] == 2 & roidf[,"istim"] <= 8,]
## plot(roidf1[,"istim"],roidf1[,"peak"])
## ## --------------
## ## plotting PPF Peak
## roiidspines = unique(roidf[roidf$roitype == "spine","roiid"])
## roiidspine = roiidspines[2]
## stimfreq = 2
## plotdata = roidf[roidf$stimfreq==stimfreq & roidf$roitype == "spine" & roidf$roiid == toString(roiidspine),]
## plotsavepath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/plots/"
## plotsavepath = paste(c(plotsavepath,"peak_vs_stim_",toString(roiidspine),"_",toString(stimfreq),"Hz.png"),collapse = "")
## png(plotsavepath,width=20,height=10,units="cm",bg="white",res=300)
## p <- ggplot(plotdata, aes(x=istim,y=peak,fill=roiid))
## p <- p + geom_point(aes(x=istim,y=peak),shape=21,size=3,position = position_jitterdodge(dodge.width=1,jitter.width=1,jitter.height=0),show.legend=FALSE)
## p <- p + geom_line(stat = 'summary', fun.y = 'mean', size = 1,show.legend=FALSE)
## p <- p + labs(title=paste(c(toString(roiidspine),"_",toString(stimfreq),"Hz"),collapse=""))
## p <- p + scale_x_continuous(name ="Stimulus number", breaks = c(1,2,3,4,5,6,7,8),labels=c("1","2","3","4","5","6","7","8"),limits=c(1,8))
## p <- p + scale_y_continuous(name = expression("Peak amplitude"~"("*"\u0394"*"F/F)"), breaks=c(0,0.5,1),labels=c("0","0.5","1"),limits=c(0,1))
## ## p <- p + scale_y_continuous(name = expression("Peak amplitude"~"("*"\u0394"*"F/F)"), breaks=c(0,0.5,1,1.5),labels=c("0","0.5","1","1.5"),limits=c(0,1.5))
## p <- p + theme_bw() + theme(axis.line.x = element_line(color = "black",size = 1),
##                             axis.line.y = element_line(colour = "black", size = 1),
##                             axis.text.x = element_text(color = "black", size = 20),
##                             axis.text.y = element_text(color = "black",size = 20, family = "Arial"),
##                             axis.ticks.y = element_line(size = 1.5),
##                             axis.ticks.x = element_line(size = 1.5),
##                             axis.title.x = element_text(color = "black",size = 20),
##                             axis.title.y = element_text(color = "black",size = 20),
##                             axis.ticks.length = unit(.3, "cm"),
##                             ## panel.grid.major = element_blank(),
##                             ## panel.grid.minor = element_blank(),
##                             panel.border = element_blank(),
##                             panel.background = element_blank(),
##                             plot.background = element_blank(),
##                             plot.margin = margin(1,1,1,1,"cm"), #trbl
##                             plot.title = element_text(hjust = 0.5),
##                             legend.position = "none")
## print(p)
## dev.off()
## ## p <- p + scale_fill_manual(values = c("white","darkgrey"))
## ## p <- p + geom_bar(position = 'dodge', stat = 'summary', fun.y = 'mean', width = 0.8)
## ## p <- p + geom_bar(stat = 'summary', fun.y = 'mean', width = 0.7, position = position_dodge(width=0.8),color="black")

## ## p <- p + geom_point(aes(x = GroupOrdered,group = interaction(Invivo,Exvivo)), size = 5, shape = 21, position = position_jitterdodge(jitter.width = 0.5, jitter.height=0.1, dodge.width=0.9))

## ## p <- p + scale_color_manual(values = c("orange","black"))
## p <- p + geom_errorbar(stat = 'summary', fun.data = 'mean_se', width = 0.1, size = 1, position = position_dodge(width=0.9),color='black');
## ## p <- p + theme_bw() + theme(axis.line = element_line(colour = "black"), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), panel.border = element_blank(), panel.background = element_blank())
## p <- p + theme_bw() + theme(axis.line.x = element_blank(),
##                             axis.text.x = element_blank(),
##                             axis.line.y = element_line(colour = "black", size = 1.5),
##                             axis.ticks.x = element_blank(),
##                             axis.title.x = element_blank(),
##                             axis.ticks.length = unit(.3, "cm"),
##                             axis.ticks.y = element_line(size = 1.5),
##                             axis.title.y = element_blank(),
##                             axis.text.y = element_text(color = "black",size = 25, family = "Helvettica"),
##                             panel.grid.major = element_blank(),
##                             panel.grid.minor = element_blank(),
##                             panel.border = element_blank(),
##                             panel.background = element_blank(),
##                             plot.background = element_blank(),
##                             plot.margin = margin(1,1,1,1,"cm"),
##                             legend.position = "none")
## p <- p + scale_y_continuous(limits = c(0,3), expand = c(0,0))
## ## png("/home/anup/goofy/projects/data/els/figures/np_review/ca1ss7050.png",width=12,height=18,units="cm",bg="transparent",res=300)
## print(p)
## ## dev.off()
