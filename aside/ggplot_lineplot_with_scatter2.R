source("/Users/macbookair/goofy/codes/image_analysis/loadlibraries.R")
## source("/Users/macbookair/goofy/codes/image_analysis/iglusnfr_roidf_analysis.R")
## plot probability of release

roiidspines = unique(roidf[roidf$roitype == "spine","roiid"])
roiidomit2hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1","20190418_S1E3_spine_1")
roiidomit8hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1")
roiidomit20hz = c("20190417_S2C1_spine_1","20190726_S1C1S1_spine_2","20190801_S1C1S2_spine_1","20190418_S1E1_spine_1")
stimfreq = 20
if (stimfreq ==2){
    roiidselect = roiidspines[!roiidspines %in% roiidomit2hz]
}
if (stimfreq == 8){
    roiidselect = roiidspines[!roiidspines %in% roiidomit8hz]
}
if (stimfreq == 20){
    roiidselect = roiidspines[!roiidspines %in% roiidomit20hz]
}
trial = 1                               #pr and potency is same for all trials
param = "potency"
columns = c("roiid","trial","istim",param)
plotdata = roidf[roidf$stimfreq==stimfreq & roidf$roitype == "spine" & roidf$roiid %in% roiidselect & roidf$trial == trial,]
plotdata = plotdata[,columns]                           #reduce plotdata columns
colnames(plotdata) = c(colnames(plotdata)[1:3],"param") #rename parameter column name to "param"
## add factors as new columns
plotdata = cbind(plotdata,istim_factor = as.factor(plotdata$istim))
plotdata = cbind(plotdata,roiid_factor = as.factor(as.character(plotdata$roiid)))
## create a dataframe for average and sem
plotavgsem = ddply(plotdata,.(istim),function(x){
    avg = mean(x$param,na.rm = TRUE);
    std = sd(x$param,na.rm = TRUE);
    nsamples = length(x$param);
    sem = std/sqrt(nsamples);
    print(length(x$param));
    dfout = as.data.frame(cbind(avg = avg,std = std,n = nsamples, sem = sem));
    return(dfout)})
## -----------
plotsavepath = "/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis/plots/"
plotsavepath = paste(c(plotsavepath,param,"_vs_stim_",toString(stimfreq),"Hz.png"),collapse = "")
## png(plotsavepath,width=20,height=10,units="cm",bg="white",res=300)
p <- ggplot(plotdata, aes(x=istim,y=param,fill=roiid))
## p <- p + geom_line(stat = 'summary', fun.y = 'mean', size = 1,show.legend=FALSE,color = 'grey')
p <- p + geom_line(aes(x=istim,y=param), size = 1,show.legend=FALSE,color = 'grey')
p <- p + geom_line(data = plotavgsem,aes(x=istim,y=avg),inherit.aes = FALSE, size = 1,show.legend=FALSE)
p <- p + geom_point(data = plotdata,aes(x=istim,y=param,fill=roiid),shape=21,size=3,show.legend=FALSE)
p <- p + geom_errorbar(data = plotavgsem, inherit.aes = FALSE,aes(x=istim,ymin = avg-sem,ymax = avg+sem),width = 0, size = 1, color='black');
p <- p + labs(title=paste(c(toString(stimfreq),"Hz"),collapse=""))
p <- p + scale_x_continuous(name ="Stimulus number", breaks = c(1,2,3,4,5,6,7,8),labels=c("1","2","3","4","5","6","7","8"),limits=c(1,8))
if (param == "potency"){
    p <- p + scale_y_continuous(name = expression("Potency"~"("*"\u0394"*"F/F)"), breaks=c(0,0.2,0.4,0.6,0.8),labels=c("0","0.2","0.4","0.6","0.8"),limits=c(0,0.8))}
if (param == "pr"){
    p <- p + scale_y_continuous(name = expression("Release probability"), breaks=c(0,0.2,0.4,0.6,0.8,1),labels=c("0","0.2","0.4","0.6","0.8","1"),limits=c(0,1))}
if (param == "npotency"){
    p <- p + scale_y_continuous(name = expression("Potency (normalized)"), breaks=c(0,1,2,3),labels=c("0","1","2","3"),limits=c(0,3))}
if (param == "npr"){
    p <- p + scale_y_continuous(name = expression("Release probability \n (normalized)"), breaks=c(0,1,2,3,4),labels=c("0","1","2","3","4"),limits=c(0,4))}
p <- p + theme_bw() + theme(axis.line.x = element_line(color = "black",size = 1),
                            axis.line.y = element_line(colour = "black", size = 1),
                            axis.text.x = element_text(color = "black", size = 20),
                            axis.text.y = element_text(color = "black",size = 20, family = "Arial"),
                            axis.ticks.y = element_line(size = 1.5),
                            axis.ticks.x = element_line(size = 1.5),
                            axis.title.x = element_text(color = "black",size = 20),
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
##  statistics
options(contrasts=c("contr.sum","contr.poly"));
a1 = aov(param ~ istim_factor,data=plotdata);summary(a1)
TukeyHSD(a1,"istim_factor")
## compact model
baselinemodel = lme(param ~ 1, random = ~1 | roiid_factor/istim_factor, data = plotdata, method = "ML")
## augmented model
istimmodel = lme(param ~ istim_factor, random = ~1 | roiid_factor/istim_factor, data = plotdata, method = "ML")
a2 = anova(baselinemodel,istimmodel)
## rmaov = aov(param ~ (istim_factor) + Error(istim), data = plotdata);
posthoc = glht(istimmodel,linfact = mcp(istim_factor= "Tukey"))
summary(posthoc)


