import imageanalysis as imganal
import javabridge
import bioformats

# imagepath = '/Users/macbookair/goofy//data/beiquelab/linescan_testdata.czi'
# imagepath = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/S2C1/Image 98 Block 1.czi'
# imagepath = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 16 Block 1.czi'
# imagepath = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/Image 111 Block 1.czi'
# imagepath = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/Image 113 Block 1.czi'
# imagepath = '/Volumes/GoogleDrive/Team Drives/Beique Lab/CURRENT LAB MEMBERS/Anup/data_anup/zen_computer/20190415/C3/Image 10 Block 1.czi'
# imagepath = '/Volumes/GoogleDrive/Team Drives/Beique Lab/CURRENT LAB MEMBERS/Anup/data_anup/zen_computer/20190416/S2C1S1/Image 111 Block 1.czi'
# filepath = '/Volumes/GoogleDrive/Team Drives/Beique Lab/CURRENT LAB MEMBERS/Anup/data_anup/zen_computer/20190416/S2C1S1/files_list.txt'
filepath = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/Image 11 Block 1.czi'
# filepaths = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190415/C3/iglusnfr_linescans.txt'
# filepaths = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/S2C1S1/iglusnfr_linescans.txt"
# filepaths = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190417/S2C1/iglusnfr_linescans.txt"
# filepaths = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190418/S1E3/iglusnfr_linescans.txt"
# filepath = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190418/S1E3/Image 46 Block 1.czi"
# filepaths = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_linescans_set1.txt'
# lsts = imganal.LinescanTimeseriesCZI(filepath)
# lsts.displayImage()
# lsts.save_figure()

if(__name__ == "__main__"):

    # javabridge.start_vm(class_path=bioformats.JARS)
    javabridge.start_vm(class_path=bioformats.JARS,run_headless=True,max_heap_size='2G')

    # print("Oops!",sys.exc_info()[0],"occured.")
    # print('Error in javabridge section')
    # exit()


    lsts = imganal.ZeissLinescanImageTimeseries(filepath)
    lsts.linescan_image_display('/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture')
    input('enter a key')
    
    # with open(filepaths,'r') as f:
    #     for line in f:
    #         print('Image path:',line.strip())
    #         print('length:',len(line.strip()))
    #         filename = line.strip()
    #         if (filename[0] != '#'):
    #             lsts = imganal.ZeissLinescanImageTimeseries(line.strip())
    #             # lsts.print_metadata()
    #             # lsts.linescan_image_csv_out(0,'/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture')

    
print('Closing javabridge....')
javabridge.kill_vm()
