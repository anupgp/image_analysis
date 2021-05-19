from io import BytesIO
from matplotlib import pyplot
import czifile

print(czifile.__version__)

file_lineselect = '/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190829/s1c1s1/Image 30.czi'

with czifile.CziFile(file_lineselect) as czi:
    print(czi)
    print(czi.metadata())

    line_scan = czi.asarray()

    for attachment in czi.attachments():
        print(attachment)

    embedded_czifile = czifile.CziFile(
        BytesIO(
            next(
                attachment for attachment in czi.attachments()
                if attachment.attachment_entry.name == 'Image'
            ).data(raw=True)
        )
    )

    print(embedded_czifile)
    print(embedded_czifile.metadata())

    embedded_image = embedded_czifile.asarray()


for line in line_scan.squeeze():
    pyplot.plot(line)
for image in embedded_image.squeeze():
    pyplot.figure()
    pyplot.imshow(image)
pyplot.show()
