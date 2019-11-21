import zeissImageClasses as zeiss
from zeissImageClasses import compress_filename
from matplotlib import pyplot as plt
import h5py

fnlsts = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/S2C1/Image 63.czi"
fnlsls = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/S2C1/Image 62.czi"
datasavepath = '/Volumes/Anup_2TB/iglusnfr_analysis/2hz'

zfilelsts = zeiss.Image(fnlsts)
zfilelsls = zeiss.Image(fnlsls)
# print(zfile.img_type)
# zeissImageClasses.show_metadata(zfilelsls.metadata)
print('Filename line select: ',fnlsls,'Metadata attach image')
zeiss.show_metadata(zfilelsls.attachimage_metadata)
# print('--------------------------------------')
# print(zfile.attachment_names)
# X and Y are flipped to match the image orientation
x1 = zfilelsls.attachimage_metadata['X1']
y1 = zfilelsls.attachimage_metadata['Y1']
x2 = zfilelsls.attachimage_metadata['X2']
y2 = zfilelsls.attachimage_metadata['Y2']
fh1,ah1 = zeiss.display_lineselect_image(zfilelsls.attachimage,1,x1,y1,x2,y2,title=compress_filename(fnlsls,3),savepath=datasavepath)
# fh1,ah1 = zeiss.display_lineselect_image(zfilelsls.attachimage,1,title=compress_filename(fnlsls,3),savepath=datasavepath)
# -----------------
fh2,ah2 = zfilelsts.select_roi_linescan()
plt.show()
zfilelsts.extract_roi()
print(zfilelsts.roidf)
zfilelsts.save_roi_to_csvfile(fname=compress_filename(fnlsts,3),savepath=datasavepath)
print(zfilelsts.coords)
