import czifile as zen
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import javabridge
import bioformats
from bioformats import log4j
import xml.etree.ElementTree as ET
import common_functions as comfun

class Imaging:
       def __init__(self,path):
              comfun.exit_if_file_not_found(path)
              self.path = path
              self.read_metadata()
              
       def read_metadata(self):
              omexmlstr = bioformats.get_omexml_metadata(self.path)
              omexml = bioformats.OMEXML(omexmlstr)
              # orgmetadata = bioformats.OMEXML.OriginalMetadata(omexml)
              root = ET.fromstring(omexmlstr)
              print(omexml)
              tree = ET.ElementTree(root)
              self.channel_count = omexml.image().Pixels.channel_count
              self.channel_names = []
              # populate channel_names
              for i in np.arange(0,self.channel_count,1):
                     self.channel_names.append(omexml.image().Pixels.Channel(i).Name)
              # print('image_count:',omexml.get_image_count())
              # print('image physical sizex unit',omexml.image().Pixels.get_PhysicalSizeXUnit())
              # print('image physical sizex',omexml.image().Pixels.get_PhysicalSizeX()) 
              # print('image sizex',omexml.image().Pixels.get_SizeX())
              # print('image physical sizey unit',omexml.image().Pixels.get_PhysicalSizeYUnit())
              # print('image physical sizey',omexml.image().Pixels.get_PhysicalSizeY())               
              # print('image sizey',omexml.image().Pixels.get_SizeY())
              # print('image sizez',omexml.image().Pixels.get_SizeZ())
              # print('image sixec',omexml.image().Pixels.get_SizeC())
              # print('image sizet',omexml.image().Pixels.get_SizeT())
              # print('image dimensions',omexml.image().Pixels.get_DimensionOrder())

              tagprefix= '{http://www.openmicroscopy.org/Schemas/OME/2016-06}'

              for child1 in root:
                     print('Child1: ',child1.tag,'\t',child1.attrib)
                     for child2 in child1:
                            print('Child2: ',child2.tag,'\t',child2.attrib)
                            count=0
                            for child3 in child2:
                                   print('Child3: ',child3.tag,child3.attrib)
                                   if (count >=10):
                                          break;
                                   if(child3.tag == tagprefix+'Plane'):
                                          count = count + 1
                                   for child4 in child3:
                                          print('Child4: ',child4.tag,child4.attrib)
                                          for child5 in child4:
                                                 print('Child5: ',child5.tag,child5.attrib)
                                                 for child6 in child5:
                                                        print('Child6: ',child6.tag,child6.attrib)

                            print('-----------------------------------')
                     print('====================================')
              # for elem1 in root.iter():
              #        for 
              #        print(elem.tag,elem.attrib)
              
              
class Linescan(Imaging):
       pass

javabridge.start_vm(class_path=bioformats.JARS,run_headless=True)


# def extract_zeiss_metadata(imagepath):
#        omexmlstr = bioformats.get_omexml_metadata(imagepath)
#        root = ET.fromstring(omexmlstr)
#        tree = ET.ElementTree(root)
#        tree.write('/Users/macbookair/goofy/data/beiquelab/omexmltest.xml')
#        # print(root.tag)
#        # print(root.attrib)
#        # print(ET.tostring(root, encoding='utf8').decode('utf8'))
#        for child in root:
#               print(child.tag, child.attrib)
#        # for elem in root.iter():
#        #        print(elem.tag,elem.attrib)
#        for elem in root.iter('Image'):
#               print(elem.attrib)
       

       # print(xmldoc.nodeName)
       # print(xmldoc.firstChild.tagName)
       # elementlist = xmldoc.getElementsByTagName('Key')
       # print(elementlist)
       # print(xmldoc.toxml())
       # for an_element in elementlist:
       #        an_element_type = an_element.getAttribute('Key')
       # for child in root.childNodes:
       #        print(child.toxml())
       # print(root.tag)
       
       # print(type(omexmlstr))
       # ome = bioformats.OMEXML(omexmlstr) # be sure everything is ascii
       # print(type(ome))
       # print(dir(ome.StructuredAnnotations))
       # print(dir(ome))
       # print(ome.original_metadata.iter_items())
       # print(orgmetadata)
       # iome = ome.image(0) # e.g. first image
       # print(ome.image().get_Name())
       # print(ome.image().Pixels.get_SizeX())
       # print(ome.image().Pixels.get_SizeY())
       # print(ome.image().Pixels.get_SizeT())
       # print(ome.image().get_AcquisitionDate())
       # print(dir(ome.Image))
       # print(ome.structured_annotations.keys())
            
try:
    log4j.basic_config()
    imagepath = "/Volumes/Anup_2TB/raw_data/beiquelab/zen/data_anup/20190418/S1E3/Image 41 Block 1.czi"
    linescan1 = Linescan(imagepath)
    print(linescan1.path)
    print(linescan1.channel_count)
    print(linescan1.channel_names)
    # image  = zen.imread(imagepath)
    # print(image.shape)
    # imagepart = image[0,0,0,0:1000,0,0,0:512,0]
    # print(imagepart.shape)
    # imagepart = np.reshape(imagepart[0,0,0,0:1000,0,0,0,0],(0,1001))
    # plt.imshow(imagepart,interpolation='nearest')
    # plt.show()
    # extract_zeiss_metadata(imagepath)

    # img = []
    # for zcoord in range(0,41):
    #     reader = bioformats.load_image(input_image1,c=None, z=zcoord, t=0, series=None, index=None, rescale=True, wants_max_intensity=False, channel_names=None)
    #     img.append(reader)
    # print(np.shape(img))
    
    # cap = cv.VideoCapture(0) # Capture video from camera
    # # Get the width and height of frame
    # width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
             
    # height,width,layers=img[1].shape
    # print(height,width,layers)
    # fps = 1
    # fourcc = cv.VideoWriter_fourcc(*'mp4v')
    # is_color= True
    # video = cv.VideoWriter(outpath+'video.mp4',fourcc,fps,(width,height))

    # for j in range(0,41):
    #     video.write(np.uint8(img[j]))

    # while(cap.isOpened()):
    #     ret, frame = cap.read()
    #     if ret == True:
    #         # frame = cv.flip(frame,0)

    #         # write the flipped frame
    #         video.write(frame)

    #         cv.imshow('frame',frame)
    #         if (cv.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
    #             break
    #     else:
    #         break

    # video.release()
    # cap.release()
     # cv.destroyAllWindows()

    
    # plt.imshow(reader,interpolation='nearest')
    # plt.show()
    # omexmlstr = bioformats.get_omexml_metadata(input_image1)
    #o=bioformats.OMEXML(omexmlstr)
    # ome = bioformats.OMEXML(omexmlstr) # be sure everything is ascii
finally:
    javabridge.kill_vm()



 # |      >>> pixels = md.image().Pixels
 # |      >>> channel_count = pixels.SizeC
 # |      >>> stack_count = pixels.SizeZ
 # |      >>> timepoint_count = pixels.SizeTg
