import zeissImageClasses
from zeissImageClasses import compress_filename
from matplotlib import pyplot as plt
import h5py

fnlsts = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 5 Block 1.czi"
fnlsls = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 3.czi"

zfilelsts = zeissImageClasses.ZeissImageClass(fnlsts)
zfilelsls = zeissImageClasses.ZeissImageClass(fnlsls)
# print(zfile.img_type)
# zeissImageClasses.show_metadata(zfilelsls.metadata)
zeissImageClasses.show_metadata(zfilelsls.attachimage_metadata)
# print('--------------------------------------')

# print('--------------------------------------')
# print(zfile.attachment_names)
# X and Y are flipped to match the image orientation
x1 = zfilelsls.attachimage_metadata['X1']
y1 = zfilelsls.attachimage_metadata['Y1']
x2 = zfilelsls.attachimage_metadata['X2']
y2 = zfilelsls.attachimage_metadata['Y2']
# zeissImageClasses.display_lineselect_image(zfile.attachimage,1,x1,y1,x2,y2,zfile.img) # only linescan select
fh1,ah1 = zeissImageClasses.display_lineselect_image(zfilelsls.attachimage,1,x1,y1,x2,y2,title=compress_filename(fnlsls,3))
# fh1,ah1 = zeissImageClasses.display_lineselect_image(zfilelsls.attachimage,1,title=compress_filename(fnlsls,3))
# zeissImageClasses.display_lineselect_image(zfile.attachimage,1,title=compress_filename(infile,3),savepath='/Users/macbookair')
# zeissImageClasses.display_lineselect_image(zfile.img)
# zeissImageClasses.show_metadata(zfile.attachimage_metadata)
fh2,ah2 = zfilelsts.select_roi_linescan()
plt.show()
zfilelsts.extract_roi()
print(zfilelsts.roidf)
zfilelsts.save_roi_to_csvfile(fname=compress_filename(fnlsts,3),savepath='/Users/macbookair')
# linescan.save_roidf(fnameout)

# print(linescan.coords)


# linescan.show_metadata()
# linescan.select_roi_linescan()
