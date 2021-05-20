import os,sys
# ~ sys.path.append(os.path.abspath("/home/jmamede/scripts/"))
# ~ import javabridge
# ~ import bioformats#, pims
import pims
from skimage import filters
import numpy as np
import matplotlib.pyplot as plt
import glob
import bioformats.omexml as ome
import tifffile
import scipy.ndimage as ndi
# ~ def contrast_img(img,min_,max_ ): 
    # ~ img[img>max_]=max_
    # ~ img[img<min_]=min_
    # ~ img -= min_
    # ~ img = img * (_16bit/float(max_-min_))
    # ~ return img
    
    
# ~ javabridge.start_vm(class_path=bioformats.JARS)

def pimsmeta2OMEXML(frames, project=False):
#     from apeer_ometiff_library import omexmlClass
    import aicsimageio.vendor.omexml as omexmlClass
    import re , os
    
    #Missing TODO:
    #<Image>,  Name = "ImageName"
    #Instrument ID and Detector ID and Objective 
#     frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'wsCameraName']

    # Objective settings with Refractive Index
        #Pixels, 
            #Channel Color = RGB###, EmissionWavelength, Name of Channel.
            #Plane  ExposureTime, Position X, Y, Z (Z is easy as it's in nd2reader metadata)
    def writeplanes(pixel, SizeT=1, SizeZ=1, SizeC=1, order='TZCYX', verbose=False):

        if order == 'TZCYX':

            pixel.DimensionOrder = omexmlClass.DO_XYCZT
            counter = 0
            for t in range(SizeT):
                for z in range(SizeZ):
                    for c in range(SizeC):

                        if verbose:
                            print('Write PlaneTable: ', t, z, c),
                            sys.stdout.flush()

                        pixel.Plane(counter).TheT = t
                        pixel.Plane(counter).TheZ = z
                        pixel.Plane(counter).TheC = c
                        #check basically because of triggered acquisition the arrays shouldn't have the size of "channel"
                        pixel.Plane(counter).DeltaT = frames.metadata.PlaneDeltaT(0,counter)
                        pixel.Plane(counter).PositionZ = frames.metadata.PlanePositionZ(0,counter)
                        pixel.Plane(counter).PositionX = frames.metadata.PlanePositionX(0,counter)
                        pixel.Plane(counter).PositionY = frames.metadata.PlanePositionY(0,counter)
#                         pixel.Plane(counter).ExposureTime = 
#                         pixel.Plane(counter).PositionX =
#                         pixel.Plane(counter).PositionY = 
#                         pixel.Plane(counter).
                        counter = counter + 1
                        
    
        return pixel
    
    #make a metadata var
    bfmeta = frames.metadata

    # extra_meta = reader.parser._raw_metadata.image_text_info[b'SLxImageTextInfo'][b'TextInfoItem_5'].decode()
    # extra_meta = re.split(',|;|\r\n',extra_meta)
    # extra_dict = dict()
    # for line in extra_meta: 
        # line = line.strip().strip('- ')
        # keyvalue = str.split(line,':') 
        # if len(keyvalue) > 1: 
            # key = keyvalue[0] 
            # value = keyvalue[1] 
            # extra_dict[key] = value
#     Series = nd2meta['fields_of_view'][-1]+1
    scalex = frames.metadata.PixelsPhysicalSizeX(0)
    scaley = scalex
    
    
    
    if not project:
#         scalez = round(nd2meta['z_coordinates'][1]-nd2meta['z_coordinates'][0],3)
#         scalez = frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'ppNextLevelEx'][b''][b'ppNextLevelEx'][b''][b'uLoopPars'][b'dZStep']
        scalez = frames.metadata.PixelsPhysicalSizeZ(0)
    pixeltype = frames.metadata.PixelsType(0)
    # dimorder = 'TZCYX'
    dimorder = frames.metadata.PixelsDimensionOrder(0)
# print(a)
    omexml = omexmlClass.OMEXML()
#     omexml.image_count = 1
#     omexml.image_count = reader.sizes['v']
    #Try to find if PIMS outputs the filename somehow.
    omexml.image(0).Name = os.path.basename(frames.filename)
#     for i in range(frames.sizes['t']):
    p = omexml.image(0).Pixels
    p.SizeX = frames.sizes['x']
#     p.SizeX = 2044
    p.SizeY = frames.sizes['y']
    p.SizeC = frames.sizes['c']
    
    try:
        p.SizeT = frames.sizes['t']
    except: print("Single T")
    
    if project:
        p.SizeZ = 1
    else:
        p.SizeZ = frames.sizes['z']
        
    p.PhysicalSizeX = np.float(scalex)
    p.PhysicalSizeY = np.float(scaley)
    if not project:
        p.PhysicalSizeZ = np.float(scalez)
    p.PixelType = pixeltype
    p.channel_count = frames.sizes['c']
    
    if project:
        p.plane_count = 1 * p.SizeT * p.SizeC #* SizeV
    else:
        p.plane_count = p.SizeZ * p.SizeT * p.SizeC #* SizeV


    #I am using separate files for each visit point
    #, if you want one tiff with all visit points (possibly good for panels) 
    #you will need to update this section
    
    if project:
        p = writeplanes(p, SizeT=p.SizeT, SizeZ=1, SizeC=p.SizeC, order=dimorder)
    else:
        p = writeplanes(p, SizeT=p.SizeT, SizeZ=p.SizeZ, SizeC=p.SizeC, order=dimorder)
    for c in range(p.SizeC):
        p.Channel(c).Name = str(frames.metadata.ChannelEmissionWavelength(0,c))
        clr = {'527.0': 16711935,'447.0':  65535,'603.0' : -16776961,'679.0':  16711935, 'miRFP670':  65535 ,'555 nm' : -16776961,'mRuby3' : -16776961,'mRuby' : -16776961, 'a647': 65535,'GFP': 16711935,'FITC': 16711935,'DAPI': 65535,'470 nm': 16711935}
        try:
            p.Channel(c).Color = clr[p.Channel(c).Name]
        except: "didn't pick up all colors"
#         p.Channel(c).EmissionWavelength =
        if pixeltype == 'unit8':
            p.Channel(c).SamplesPerPixel = 1
        if pixeltype == 'unit16':
            p.Channel(c).SamplesPerPixel = 2
            
    p.populate_TiffData()
#     omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))

    return omexml

def crunch_data(ficheiro):
        # ~ image, scale = bioformats.load_image(ficheiro,rescale=False,wants_max_intensity=True)
    reader = pims.bioformats.BioformatsReader(ficheiro,java_memory='1024m')
    meta = reader.metadata
    reader.bundle_axes = 'zyx'
    reader.iter_axes = 'c'
        
    chan0 = reader[0]
    chan1 = reader[1]
    chan2  = reader[2]
    chan3  = reader[3]
    chan0 = np.roll(chan0,-7, axis=2) #fix axis for 3D
    chan0 = np.roll(chan0,-13, axis=1)
    chan0 = ndi.rotate(chan0, -0.35, reshape=False, axes=(1,2), mode="nearest") #axes=(1,2) for Zstack
    chan3 = np.roll(chan3,-7, axis=2) #fix axis for 3D
    chan3 = np.roll(chan3,-13, axis=1)
    chan3 = ndi.rotate(chan3, -0.35, reshape=False, axes=(1,2), mode="nearest")
    
    img5d = np.stack((chan0,chan1,chan2,chan3),axis=1)    #img5d = img5d.flatten()
    #img5d = np.stack((chan0,chan1,chan2,chan3),axis=1)    #img5d = img5d.flatten()
    img5d = np.expand_dims(img5d, axis=0)
    # ~ img5d = np.expand_dims(img5d, axis=0)
    
    # ~ img5d = np.swapaxes(img5d,0,1)
    #img5d = np.swapaxes(img5d,1,2)
    #img5d = img5d.flatten()
    # ~ cgas = np.roll(mp.roll(cgas,-6,axis=0),-1,axis=1)
    print("writing", ficheiro[:-2]+'ome.tiff')
    # ~ dimorder = 'TCZXY'
    #imorder = 'ZCYX'
    output_file = ficheiro[:-2]+'ome.tif'
    # ~ xml = pimsmeta2OMEXML(reader,project=True)
    xml = pimsmeta2OMEXML(reader)
    tifffile.imsave(output_file, img5d
                            , description = xml.to_xml()
                            , photometric='minisblack'
                            #, datetime= True
                            , metadata= None
                            , contiguous=False
                            )
    # ~ bioformats.write_image(ficheiro[:-2]+'tiff', np.dstack((pqbp1,ruby,igfp,cgas)),
    # ~ u'uint16')
    
    
 
    

    
def main():

    ficheiros = glob.glob('./*ALX.dv')
    ficheiros.sort()
    for a in ficheiros:
        crunch_data(a)
        print("a fazer:"), a

if __name__ == "__main__":
    main()
