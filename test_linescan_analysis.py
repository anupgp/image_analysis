import linescan_classes
from matplotlib import pyplot as plt
import h5py

linescanfile1 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190704/S1C1E3/Image 23.czi'
linescanfile2 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190725/S1C1S1/20hz/Image 91.czi'
# linescanfile2 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/C3/Image 11 Block 1.czi'
linescanfile2 = '/Users/macbookair/goofy/codes/programing/python/image_analysis/sample_data/Image 11 Block 1.czi'
linescanfile4 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190726/S1C1S1/2hz/Image 46.czi'
# linescanfile5 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/Image 113 Block 1.czi'
linescanfile5 = '/Users/macbookair/goofy/codes/programing/python/image_analysis/sample_data/Image 113 Block 1.czi'
linescanfile6 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/Image 111.czi'

imagepath = '/Users/macbookair/goofy//data/beiquelab/linescan_testdata.czi'
# snfr = ZeissLinescan(filepath)
# print(snfr.lsts)
framefile = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190702/S1C1/Image 2.czi'
lineselect1 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190829/s1c1s1/Image 30.czi'
lineselect2 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/S2C1/Image 64.czi'
# frame =ZeissFramescan(lineselect)
# frame.read_single_framescan_with_czifile()
linescan = linescan_classes.ZeissClass(linescanfile2)
fh1,ah1 = linescan.get_lineselect_image()
fh2,ah2 = linescan.select_roi_linescan()
plt.show()
linescan.extract_roi()
print(linescan.roidf)
# print(linescan.coords)


# linescan.show_metadata()
# linescan.select_roi_linescan()
