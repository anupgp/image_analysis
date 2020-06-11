import os
import sys
# sys.path.insert('/Users/macbookair/codes/')
import zeissImageClasses as zeiss
from zeissImageClasses import compress_filename
from matplotlib import pyplot as plt

datapath = '/Volumes/GoogleDrive/Shared drives/Beique Lab DATA/Imaging Data/LSM880 2P/Anup/'
resultpath = "/Users/macbookair/goofy/data/beiquelab/grant"
subfolder = '20190212/C1/'
# subfolder = '20190206/C1/'
fname_neuron = 'Image 24.czi'          # home field neuron
# fname_neuron = 'Image 35.czi'
fname_spine = 'Image 11.czi'          # zoom to spine
neuron = zeiss.Image(os.path.join(datapath,subfolder,fname_neuron))
spine = zeiss.Image(os.path.join(datapath,subfolder,fname_spine))
# fh1,ah1 = zeiss.display_image(neuron.img,channels=[],title=fname_neuron,savepath="")
fh1,ah1 = zeiss.neuron_spine_plot(img1=neuron.img,sizeX = neuron.metadata['SizeX'],scaleX = neuron.metadata['ScalingX'],img2=spine.img,title="neuron_spine3",savepath=resultpath)
plt.show()
