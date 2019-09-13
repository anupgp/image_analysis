import os
from scipy.signal import find_peaks
from scipy.signal import peak_widths
from scipy.signal import argrelextrema
import numpy as np

def message_and_exit_if_file_not_found(path):
    if(os.path.isfile(path) == False):
        print("File not found")
        print("Code will exit now")
        return(-1)

def check_path(path):
    if(os.path.isfile(path) == False):
        return(0)
    else:
        return(1)

def string_convert(astring):
    try:
        return(int(astring))
    except:
        try:
            return(float(astring))
        except:
            if (astring == 'True' or astring == 'true' or astring == 'TRUE'):
                return(True)
            elif (astring == 'False' or astring == 'false' or astring == 'FALSE'):
                return(False)
            else:
                return(astring)
            

def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))
    return([x1,y1,x2,y2])
    
def toggle_selector(event):
    print(' Key pressed.',event.key,toggle_selector.RS.active)
    
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)

def peak_props(y,**kwargs):
    # Find peak indices using find_peaks algorithm
    fp_args_needed = ["height","distance","prominence"]
    fp_args_passed = [fp_arg for fp_arg in fp_args_needed if fp_arg in kwargs.keys()]
    re_args_needed = ["order"]
    re_args_passed = [re_arg for re_arg in re_args_needed if re_arg in kwargs.keys()]

    if set(fp_args_needed) == set(fp_args_passed): 
        ihighs,_ = find_peaks(y,height=kwargs["height"],distance=kwargs["distance"],prominence = kwargs["prominence"])
    # Find peak indices using argrelextrema algorith
    elif set(re_args_needed) == set(re_args_passed):
        ihighs = argrelextrema(y,np.greater,order=kwargs["order"])[0]
    # ----------------------------
    # for each peak find the left and right minimas
    illows = np.zeros(len(ihighs),dtype=np.uint)
    irlows = np.zeros(len(ihighs),dtype=np.uint)
    illeft = 0
    ilright = ihighs[0]
    for i in np.arange(0,len(ihighs)):
        illow = np.argmin(y[illeft:ilright])+illeft
        irleft = ilright
        illeft = ihighs[i]
        if (i == len(ihighs)-1):
            irright = -1
        else:
            ilright = ihighs[i+1]
            irright = ihighs[i+1]
        irlow = np.argmin(y[irleft:irright])+irleft
        # print("illow:",illow,"irlow:",irlow)
        illows[i] = illow
        irlows[i] = irlow
    # print("ihighs",ihighs,"illows",illows,'irlows',irlows)
    # Find full-widths
    fullwidths = irlows-illows
    # compute full-width at half max
    hwh = np.zeros(len(ihighs),dtype=np.uint)
    ihwl = np.zeros(len(ihighs),dtype=np.uint)
    ihwr = np.zeros(len(ihighs),dtype=np.uint)
    for i in np.arange(0,len(ihighs)):
        height = y[ihighs[i]]
        halfamp  = (y[ihighs[i]] - np.max([y[illows[i]],y[irlows[i]]]))/2
        hwh[i] = y[ihighs[i]]-halfamp
        # print("hwh:", hwh[i])
        ihwl[i] = np.where(y[illows[i]:ihighs[i]]<=hwh[i])[0][-1]+illows[i]
        ihwr[i] = np.where(y[ihighs[i]:irlows[i]]>=hwh[i])[0][-1]+ihighs[i]
    halfwidths = [ihwl,ihwr]
    # print("halfwidths:",halfwidths)
    # print("halfheights:",hwh)
    # find peaks which have amplitude higher than threshold amplitude
    # For each peak find amplitude from the highest surrounding trough
    ihighs2 = np.zeros(0,dtype=np.uint8)
    illows2 = np.zeros(0,dtype=np.uint8)
    irlows2 = np.zeros(0,dtype=np.uint8)
    fullwidths2 = np.zeros(0,dtype=np.uint8)
    hwh2 = np.zeros(0,dtype=np.uint8)
    ihwl2 = np.zeros(0,dtype=np.uint8)
    ihwr2 = np.zeros(0,dtype=np.uint8)
    ampthres = kwargs["amp_thres"]
    for i in np.arange(0,len(ihighs)):
        amp = y[ihighs[i]] - np.min([y[illows[i]],y[irlows[i]]])
        if (amp >= ampthres):
            ihighs2 = np.append(ihighs2,ihighs[i])
            illows2 = np.append(illows2,illows[i])
            irlows2 = np.append(irlows2,irlows[i])
            ihwl2 = np.append(ihwl2,ihwl[i])
            ihwr2 = np.append(ihwr2,ihwr[i])
            hwh2 = np.append(hwh2,hwh[i])

    ihalfwidths2 = [ihwl2,ihwr2]
    return((ihighs2,illows2,irlows2,hwh2,ihalfwidths2))

