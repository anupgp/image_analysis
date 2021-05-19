import numpy as np
import scipy.signal
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
# from scipy.signal import convolve
from scipy.ndimage import convolve
from scipy.ndimage import gaussian_filter
import os

def convolve_crazy(img,order=3,threshold=200):
    
    kernel1 = np.diag(np.ones(order))
    kernel2 = np.flip(np.diag(np.ones(order)),axis=-1)
    kernel3 = np.concatenate((np.ones((order,1)),np.zeros((order,1)),np.zeros((order,1))),axis=1)
    kernel4 = np.concatenate((np.zeros((order,1)),np.ones((order,1)),np.zeros((order,1))),axis=1)
    kernel5 = np.concatenate((np.zeros((order,1)),np.zeros((order,1)),np.ones((order,1))),axis=1)
    kernel6 = np.concatenate((np.ones((1,order)),np.zeros((1,order)),np.zeros((1,order))),axis=0)
    kernel7 = np.concatenate((np.zeros((1,order)),np.ones((1,order)),np.zeros((1,order))),axis=0)
    kernel8 = np.concatenate((np.zeros((1,order)),np.zeros((1,order)),np.ones((1,order))),axis=0)
    kernels = [kernel1,kernel2,kernel3,kernel4,kernel5,kernel6,kernel7,kernel8]
    img2 = np.zeros(img.shape)
    img[np.where(img<threshold)] = 0
    for kernel in kernels:
        print(kernel)
        if(len(img.shape)==3):
            kernel = kernel[:,:,None]
        imgc = scipy.signal.convolve(img,kernel,mode='same')
        imgc[np.where(imgc<threshold)] = 0
        img2 = img2 + imgc

    print(img2.shape)
    return(img2)

def convolve_supercrazy(img,order=3,threshold=200):
    
    kernel1 = np.diag(np.ones(order))
    kernel2 = np.flip(np.diag(np.ones(order)),axis=-1)
    kernel3 = np.concatenate((np.ones((order,1)),np.zeros((order,1)),np.zeros((order,1))),axis=1)
    kernel4 = np.concatenate((np.zeros((order,1)),np.ones((order,1)),np.zeros((order,1))),axis=1)
    kernel5 = np.concatenate((np.zeros((order,1)),np.zeros((order,1)),np.ones((order,1))),axis=1)
    kernel6 = np.concatenate((np.ones((1,order)),np.zeros((1,order)),np.zeros((1,order))),axis=0)
    kernel7 = np.concatenate((np.zeros((1,order)),np.ones((1,order)),np.zeros((1,order))),axis=0)
    kernel8 = np.concatenate((np.zeros((1,order)),np.zeros((1,order)),np.ones((1,order))),axis=0)
    kernels = [kernel1,kernel2,kernel3,kernel4,kernel5,kernel6,kernel7,kernel8]
    img2 = np.zeros(img.shape)
    img[np.where(img<threshold)] = 0
    for kernel in kernels:
        print(kernel)
        if(len(img.shape)==3):
            kernel = kernel[:,:,None]
        imgc = scipy.signal.convolve(img,kernel,mode='same')
        imgc[np.where(imgc<threshold)] = 0
        img2 = img2 + imgc

    print(img2.shape)
    return(img2)


def neuron_spine_plot(img1,sizeX,scaleX,img2,title=[],savepath=[]):
    # display the maximum projected framescan image
    if(len(img1.shape)>3):
        # stack of images XYZC
        kernel = np.array([[[-1,-1,-1],[-1,4,-1],[-1,-1,-1]],[[-1,-1,-1],[-1,4,-1],[-1,-1,-1]],[[-1,-1,-1],[-1,4,-1],[-1,-1,-1]]])
        img1 = np.max(img1,axis=-2)
        print(img1.shape)
        input()
        # kernel = np.array([[1,0,1,0,1],[0,1,1,1,0],[1,1,1,1,1],[0,1,1,1,0],[1,0,1,0,1]])
        # kernel = np.array([[-1,1,1,1,-1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]])
        # kernel = np.diag([1,1,1])
        # kernel =  np.flip(np.diag([1,1,1]),axis=-1)
        # kernel = np.ones((3,3),dtype=np.int)
        # kernel4d = kernel[:,:,None,None]
        # I = np.zeros((5,5))
        # I[2,2] = 1
        # img1 = gaussian_filter(img1,sigma=2)
        
        img1 = convolve(img1,kernel)

        # img1 = np.concatenate((convolve_crazy(img1[:,:,:,0])[:,:,:,np.newaxis],convolve_crazy(img1[:,:,:,1])[:,:,:,np.newaxis]),axis=-1)
        
    #     print(img1.shape)
    #     img1c0 = np.max(img1[:,:,10:-10,0],axis=-1).astype('int')
    #     img1c1 = np.max(img1[:,:,10:-10:,1],axis=-1).astype('int')
    # else:
    #     img1c0 = img1(img1[:,:,0])
    #     img1c1 = img1(img1[:,:,1])
    #     # ----------
    # img1f = np.concatenate([img1c0[:,:,np.newaxis],img1c1[:,:,np.newaxis]],axis=-1)
    # img1f = np.max(img1f,axis=-1)
    # # img1f = np.max(img1f,axis=-1) - np.median(img1f,axis=-1) 
    # # img1f[np.where(img1f<230)] = 0
    # # img1f = medfilt(img1f,3)
    # # img1f = image_hist_equalization(img1f).astype('int')
    # # -------------
    # if(img2 is None):
    #     img2 = np.random.randint(0,255,img1.shape[0:3])

    # img2 = np.concatenate((convolve_crazy(img2[:,:,0],3,15)[:,:,np.newaxis],convolve_crazy(img2[:,:,1],3,15)[:,:,np.newaxis]),axis=-1)
    # img2c0 = img2[:,:,0]
    # img2c1 = img2[:,:,1]

    # img2f = np.sum(np.concatenate([img2c0[:,:,np.newaxis],img2c1[:,:,np.newaxis]],axis=-1),axis=-1)
    # img2f = np.round(pow(img2f,1.2))
    # img2f[img2f>255] = 255
    
    # img2f[np.where(img2f<20)] = 0
    # img2f = medfilt(img2f,3)
    # img2f = image_hist_equalization(img2f).astype('int')
    # img2f = medfilt(scipy.ndimage.zoom(img2f,3,order=0),3)
    # maxprojz = np.max(self.img[:,:,:,0],axis=-1) # maxmimum projection along Z
    # avgprojz = np.mean(self.img[:,:,:,0], axis=-1) # maxmimum projection along Z
    # medprojz = np.median(self.img[:,:,:,0], axis=-1) # maxmimum projection along Z
    
    # projz = image_hist_equalization(maxprojz)
    # projz = np.concatenate([np.ones(img0.shape)[:,:,np.newaxis],np.zeros(img0.shape)[:,:,np.newaxis],np.zeros(img0.shape)[:,:,np.newaxis]],axis=-1)
    # projz = np.concatenate([max0[:,:,np.newaxis],max1[:,:,np.newaxis],np.zeros(max0.shape)[:,:,np.newaxis]],axis=-1)
    # projz = np.concatenate([max0[:,:,np.newaxis],np.zeros(max0.shape)[:,:,np.newaxis],np.zeros(max0.shape)[:,:,np.newaxis]],axis=-1)
    # maxprojy = img.max(axis=1) # maxmimum projection along Z
    # maxprojy = np.flip(maxprojy,1)
    # maxprojx = img.max(axis=0) # maxmimum projection along Z
    # maxprojx = np.swapaxes(maxprojx,0,1)
    # maxprojx = np.flip(maxprojx,0)
    # add scale bar
    barX = np.round(20E-6/scaleX)
    offsetX = 30
    offsetY = 30
    scalebarX = np.arange(offsetX+10,offsetX+10+barX)
    fh = plt.figure(figsize=(8,5),constrained_layout=False) # width,height
    widths = [5,3]
    heights = [5]
    gsh = fh.add_gridspec(ncols=2,nrows=1,width_ratios=widths,height_ratios=heights)
    gsh.update(wspace=0.0,hspace=0.0)
    ah = fh.add_subplot(gsh[0,0])
    # ah = fh.add_subplot(111)
    ah.plot(scalebarX,np.ones(len(scalebarX))*(offsetY),color="white",linewidth=3)
    ah.text(offsetX,offsetY+35,r"$20\ \mu m$",color="white",fontsize=16)
    ah.axis('off')
    ah.imshow(img1,cmap="hot")
    # draw rectangle
    img1rect = Rectangle((235,260),20,50,linewidth=1,edgecolor="w",facecolor='none')
    ah.add_patch(img1rect)
    ah = fh.add_subplot(gsh[0,1])
    ah.axis('off')
    xlims_img2 = [80,380]
    # ah.imshow(img2f[:,xlims_img2[0]:xlims_img2[1]],cmap="hot")
    # offsetX = 30
    # offsetY = 30
    # scalebarX = np.arange(0+offsetX,80+offsetX+barX)
    # ah.plot(scalebarX,np.ones(len(scalebarX))*offsetY,color="w",linewidth=3)
    # ah.text(offsetX,offsetY+35,r"$20\ \mu m$",color="white",fontsize=16)
    # ah = fh.add_subplot(gsh[1,0])
    # ah.imshow(maxprojx)
    # ah.plot(scalebarX,np.ones(len(scalebarX))*offsetY,color="black",linewidth=2)
    # ah.text(sizeX-offsetX-round(barX/1.5),offsetY+20,r"$100\ \mu m$",)
    # ah.axis('off')
    if (os.path.isdir(savepath) and len(title)>0):
        print('Path to save found!')
        print('Saving as:', savepath+'/'+title+'.png')
        plt.savefig(savepath+'/'+title+'.png',dpi=600)
    else:
        print('Path to save or title not found!')
    return(fh,ah)
