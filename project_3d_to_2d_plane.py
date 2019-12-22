import zeissImageClasses as zeiss
from zeissImageClasses import compress_filename
from matplotlib import pyplot as plt

fn3d = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190416/C1S1/Image 74.czi"
datasavepath = '/Users/macbookair/goofy/data/beiquelab/iglusnfr_ca1culture/iglusnfr_analysis'
fnamedepth = 3
figtitle=compress_filename(fn3d,fnamedepth)
figsavepath = datasavepath
zfile3d = zeiss.Image(fn3d)
print(zfile3d.img_type)
zeiss.show_metadata(zfile3d.metadata)
zfile3d.z_projection_2dmax(figtitle,figsavepath)
