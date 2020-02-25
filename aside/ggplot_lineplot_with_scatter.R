## source("/Users/macbookair/goofy/codes/image_analysis/iglusnfr_roidf_analysis.R")
## plotting average and sem with scatter plot
roiidspines = unique(roidf[roidf$roitype == "spine","roiid"])
roiidspines2 = c(
    "20190415_C3_spine_1",              # included in V2
    "20190415_C3_spine_2",              # included in V2
    "20190416_S2C1S1_spine_1",          # included in V2
    "20190416_S2C1S1_spine_2",          # included in V2
    "20190417_S2C1_spine_1",            # 20190417_S2C1_spine_1  - discarded: not enough data
    "20190417_S2C1_spine_2",            # included in V2
    "20190418_S1E1_spine_1",            # 20190418_S1E1_spine_1 discarded - no data for 8 & 20 hz
    "20190418_S1E3_spine_1",            # no data for 2 Hz. included 
    "20190418_S1E4_spine_2",            # included ok spine
    "20190725_S1C1S1_spine_2",          # included ok spine
    "20190726_S1C1S1_spine_2",          # 20190726_S1C1S1_spine_2 - discarded
    "20190801_S1C1S2_spine_1")          # 20190801_S1C1S2_spine_1 - discarded
roiidspine = toString(roiidspines[8])
stimfreq = 20
param = "peak"
columns = c("roiid","trial","istim",param)
## plotdata = roidf[roidf$stimfreq==stimfreq & roidf$roitype == "spine" & roidf$isuccess == TRUE & roidf$iselect ==TRUE,]
plotdata = roidf[roidf$stimfreq==stimfreq & roidf$roitype == "spine" & roidf$roiid == roiidspine & roidf$isuccess ==TRUE,]
## plotdata = roidf[roidf$stimfreq==stimfreq & roidf$roitype == "spine" & roidf$roiid == roiidspine,]
ntrials = round(mean(plotdata$ntrials),2)
plotdata = plotdata[,columns]                           #reduce plotdata columns
colnames(plotdata) = c(colnames(plotdata)[1:3],"param") #rename parameter column name to "param"
if (param %in% c("risetime2","decaytime2"))
    {plotdata$param = plotdata$param*1000                    # change time units to msec
 }
plotsavepath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/plots/"
## plotsavepath = paste(c(plotsavepath,param,"_vs_stim_",toString(roiidspine),"_",toString(stimfreq),"Hz.png"),collapse = "")
## png(plotsavepath,width=20,height=10,units="cm",bg="white",res=300)
p <- ggplot(plotdata, aes(x=istim,y=param,fill=roiid))
p <- p + geom_point(aes(x=istim,y=param,fill=roiid),shape=21,size=3,show.legend=FALSE)
p <- p + geom_line(stat = 'summary', fun.y = 'mean', size = 1,show.legend=FALSE)
p <- p + geom_errorbar(stat = 'summary', fun.data = 'mean_se', width = 0, size = 1, color='black');
p <- p + labs(title=paste(c(toString(roiidspine),"_",toString(stimfreq),"Hz",'      ntrials: ',toString(ntrials)),collapse=""))
p <- p + scale_x_continuous(name ="Stimulus number", breaks = c(1,2,3,4,5,6,7,8),labels=c("1","2","3","4","5","6","7","8"),limits=c(1,8))
if(param == "peak2"){
    ## p <- p + scale_y_continuous(name = expression("Peak amplitude"~"("*"\u0394"*"F/F)"), breaks=c(0,0.5,1,1.5),labels=c("0","0.5","1","1.5"),limits=c(0,1.5))
    ## p <- p + scale_y_continuous(name = expression("Peak amplitude"~"("*"\u0394"*"F/F)"), breaks=c(0,0.5,1),labels=c("0","0.5","1"),limits=c(0,1))
}
if(param == "risetime2"){
    p <- p + scale_y_continuous(name = expression("Risetime"~"("*"ms)"), breaks=c(0,10,20,30),labels=c("0","10","20","30"),limits=c(0,30))
}
if(param == "decaytime2"){
    p <- p + scale_y_continuous(name = expression("Decaytime"~"("*"ms)"), breaks=c(0,200,400,600,800,1000),labels=c("0","200","400","600","800","1000"),limits=c(0,1000))
}
p <- p + theme_bw() + theme(axis.line.x = element_line(color = "black",size = 1),
                            axis.line.y = element_line(colour = "black", size = 1),
                            axis.text.x = element_text(color = "black", size = 20),
                            axis.text.y = element_text(color = "black",size = 20, family = "Arial"),
                            axis.ticks.y = element_line(size = 1.5),
                            axis.ticks.x = element_line(size = 1.5),
                            axis.title.x = element_text(color = "black",size = 20),
                            axis.title.y = element_text(color = "black",size = 20),
                            axis.ticks.length = unit(.3, "cm"),
                            ## panel.grid.major = element_blank(),
                            ## panel.grid.minor = element_blank(),
                            panel.border = element_blank(),
                            panel.background = element_blank(),
                            plot.background = element_blank(),
                            plot.margin = margin(1,1,1,1,"cm"), #trbl
                            plot.title = element_text(hjust = 0.5),
                            legend.position = "none")
print(p)
## dev.off()
