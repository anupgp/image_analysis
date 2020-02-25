import olympus_image_classes as OIC
import oiffile
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter
import copy
import math

infile1 = "/Volumes/Anup_2TB/raw_data/beiquelab/o2p/imaging/20200213/C2/Image0046.oib"
# infile2 = "/Volumes/Anup_2TB/raw_data/beiquelab/o2p/imaging/20200213/C2/Image0047.oib"
# infile = "/Volumes/GoogleDrive/Shared drives/Beique Lab\ DATA/Imaging Data/Olympus 2P/Anup/20200213/C2/Image0024.oib"
oibfile1 = OIC.OlympusImageClass(infile1)
# oibfile2 = OIC.OlympusImageClass(infile2)
print(oibfile1.data.shape)
# img1 = oibfile1.data[0,30,:,:]
# img2 = oibfile2.data[0,30,:,:]
img3d = oibfile1.data[0,:,:,:]
img2d = np.max(img3d,axis=0)
img2dfgauss = np.max(gaussian_filter(img3d,sigma=0.5),axis=0)
img2dfmed = np.max(median_filter(img3d,3),axis=0)
# kernel = np.array([[0,1,0],[1,1,1],[0,1,0]])
# kernel = kernel/np.sum(kernel)
# imgfm = np.max(median_filter(imgz,size=3),axis=0)
# imgfc = np.max(signal.fftconvolve(imgzf,np.repeat(kernel[np.newaxis,::],imgzf.shape[0],axis=0),mode="same"),axis=0)

# corr = signal.correlate2d(img1,img2,boundary="symm",mode="same")
# zero pad the first image to half the dimensions of the second image
# img2 = np.pad(img2,pad_width=(int(img1.shape[0]/2),int(img1.shape[1]/2)),mode='constant',constant_values=0)
# mean substract array
# img1s = img1/np.mean(img1)
# img2s = img2/np.mean(img2) 
# corr = signal.fftconvolve(img2s,img1s[::-1,::-1],mode="same")
# x,y = np.unravel_index(np.argmax(corr,axis=None),corr.shape)
# print(x,y)
# img3 = copy.deepcopy(img2)
# img3[x-8:x-8+128,y:y+128] = img1
fh = plt.figure()
ah1 = fh.add_subplot(121)
ah2 = fh.add_subplot(122)
# ah3 = fh.add_subplot(223)
# ah4 = fh.add_subplot(224)
ah1.imshow(img2d,cmap="gray")
ah2.imshow(img2dfmed,cmap="gray")
# ah3.imshow(imgfm,cmap="gray")
# ah3.imshow(corr,cmap="gray")
# ah4.imshow(img3,cmap="gray")
plt.show()







    

