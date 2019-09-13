import linescan_classes


linescanfile1 = '/Users/macbookair/Downloads/Image 46.czi'
linescanfile2 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/C3/Image 11 Block 1.czi'
linescanfile3 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 11 Block 1.czi'
linescanfile4 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190726/S1C1S1/2hz/Image 46.czi'
linescanfile5 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/Image 113 Block 1.czi'
# linescanfile6 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/Image 111.czi'

imagepath = '/Users/macbookair/goofy//data/beiquelab/linescan_testdata.czi'
# snfr = ZeissLinescan(filepath)
# print(snfr.lsts)
framefile = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190702/S1C1/Image 2.czi'
lineselect1 = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190829/s1c1s1/Image 30.czi'
lineselect2 = '/Volumes/Anup_2TB//raw_data/beiquelab/zen/data_anup/20190417/S2C1/Image 64.czi'
# frame =ZeissFramescan(lineselect)
# frame.read_single_framescan_with_czifile()
linescan = linescan_classes.ZeissClass(linescanfile5)
# linescan.get_lineselect_image()
linescan.select_roi_linescan()


# linescan.show_metadata()
# linescan.select_roi_linescan()
