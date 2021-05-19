## source("/Users/macbookair/goofy/codes/image_analysis/iglusnfr_roidf_analysis.R");
## plot histograms
## omit roiid[5]: 20190417_S2C1_spine_1: not enough data
## omit 20190726_S1C1S1_spine_2, 20190801_S1C1S2_spine_1: peak amplitude too small
roiidspines = unique(roidf[roidf$roitype == "spine","roiid"])
roiidomit2hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1","20190418_S1E3_spine_1")
roiidomit8hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1")
roiidomit20hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1")
stimfreq = 2
if (stimfreq ==2){
    roiidselect = roiidspines[!roiidspines %in% roiidomit2hz]
}
if (stimfreq == 8){
    roiidselect = roiidspines[!roiidspines %in% roiidomit8hz]
}
if (stimfreq == 20){
    roiidselect = roiidspines[!roiidspines %in% roiidomit20hz]
}
## -------
roiid = roiidselect[5]
param = "peak"
## plotdata = roidf[roidf$stimfreq>=stimfreq & roidf$roiid %in% roiid & roidf$istim ==1 & roidf$ipeak == TRUE,]
plotdata = roidf[roidf$stimfreq>=stimfreq & roidf$istim ==1 & roidf$ipeak == TRUE,]
plotdata = plotdata[,c("roiid","trial","istim",param)]
colnames(plotdata) = c(colnames(plotdata)[1:3],"param") #rename parameter column name to "param"
minval = min(plotdata$param,na.rm = TRUE)
maxval = max(plotdata$param,na.rm = TRUE)
nbreaks = 20
breaks = seq(minval,maxval,(maxval-minval)/nbreaks)
h = hist(plotdata$param,breaks,right=TRUE,plot = FALSE)
histdf = as.data.frame(cbind(breaks = h$breaks[2:length(breaks)],counts = h$counts))
## plotting
plotsavepath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/plots/hist_"
plotsavepath = paste(c(plotsavepath,param,"_vs_stim_",toString(stimfreq),"Hz.png"),collapse = "")
## png(plotsavepath,width=20,height=10,units="cm",bg="white",res=300)
p <- ggplot(histdf, aes(x=breaks,y=counts))
p <- p + geom_bar(stat="identity")
p <- p + labs(title=paste(c(toString(stimfreq),"Hz"),collapse=""))
p <- p + scale_x_continuous(name = expression("Peak amplitude"~"("*"\u0394"*"F/F)"))
## p <- p + scale_y_continuous(name = expression("Frequency"),limits = c(0,15))
p <- p + theme_bw() + theme(axis.line.x = element_line(color = "black",size = 1),
                            axis.line.y = element_line(colour = "black", size = 1),
                            axis.text.x = element_text(color = "black", size = 20),
                            axis.text.y = element_text(color = "black",size = 20, family = "Arial"),
                            axis.ticks.y = element_line(size = 1.5),
                            axis.ticks.x = element_line(size = 1.5),
                            axis.title.x = element_text(color = "black",size = 20,vjust = -0.5),
                            axis.title.y = element_text(color = "black",size = 20,hjust = 0.5,vjust= 0.5),
                            axis.ticks.length = unit(.3, "cm"),
                            ## panel.grid.major = element_blank(),
                            ## panel.grid.minor = element_blank(),
                            panel.border = element_blank(),
                            panel.background = element_blank(),
                            plot.background = element_blank(),
                            plot.margin = margin(1,1,1,1,"cm"), #trbl
                            plot.title = element_text(hjust = 0.5,size = 20),
                            legend.position = "none")
print(p)
## dev.off()
