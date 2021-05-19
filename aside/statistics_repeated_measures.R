## source("/Users/macbookair/goofy/codes/image_analysis/iglusnfr_roidf_analysis.R")
## compute statistics: repeated measures 
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
statdata = roidf[roidf$stimfreq==stimfreq & roidf$roitype == "spine" & roidf$roiid %in% roiidselect & roidf$trial == trial,]
plotdata = plotdata[,columns]                           #reduce plotdata columns
colnames(plotdata) = c(colnames(plotdata)[1:3],"param") #rename parameter column name to "param"
