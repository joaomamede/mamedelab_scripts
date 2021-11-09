import pims
import numpy as np
import dask
import dask.array
import warnings
import cupy as cp
__author__ = """João Mamede"""
__email__ = "jmamede@rush.edu"

def initialize_reader(fn,iterator='t',bundler='cyx', ch =0, **kwargs):
    """
    Read File and returns a pims object while allowing to set iterator and
    frame shape output

    Parameters
    ----------
    fn : str
        A string with one or multiple filenames, read pims multireader
        for details.
    iterator: str
        slice to iterate, defaults to time 't'.
    bundler: str
        slice shape to output, defaults to 'yx'.
    ch:  int
        only output a one channel as default, defaults to 0.

    Returns
    -------
    array : pims.bioformats.BioformatsReader
        A pims reader to access the contents of all image files in
        the predefined channel
    """

    # reader = pims.open(fn)
    # BioformatsReader(filename, meta=True, java_memory='512m', read_mode='auto', series=0)
    # reader = pims.bioformats.BioformatsReader(fn,meta=False,java_memory='2048m')
    # reader.iter_axes = iterator  # 't' is the default already
    # reader.bundle_axes = bundler
    # print(reader)

    # reader.default_coords['c'] = ch
    # return reader
    print(fn)
    return pims.TiffStack_tifffile(fn)
    # return pims.open(fn)


def _read_frame(pims_reader,i, arrayfunc=np.asanyarray,**kwargs):
    """
    Read File and returns a pims object while allowing to set
    iterator and frame shape output.

    Parameters
    ----------
    pims_reader : object
        Pims reader object
    i: int
        the file coordinate to output as selected by the initializer
        iterator and default channel

    Returns
    -------
    array : pims.frame.Frame
        Array with the data in the reader current
        shape and default_coords.
    """
    # print(pims_reader._filename)
    #The input "i" is a slice????
    # print("pims",i)
    return arrayfunc(pims_reader[i])


def time_stack(fn,ch=0, iterator='t',bundler='cyx',arraytype="numpy",**kwargs):
    if arraytype == "numpy":
        arrayfunc = np.asanyarray
    elif arraytype == "cupy":   # pragma: no cover
        import cupy
        arrayfunc = cupy.asanyarray

    # type(test)
    #you have to get the reader outside of here
    reader = initialize_reader(fn,
            ch=ch,iterator=iterator,bundler=bundler
            )

    shape = (len(reader),) + reader.frame_shape
    # shape = (3,143,2044,2048)
    dtype = np.dtype(reader.pixel_type)
    # print('Shapy',shape)


    a = []
    # print(type(a))
    for i in range(shape[0]):
        # print("loopy",i)
        a.append( dask.array.from_delayed(
            dask.delayed(_read_frame)(reader,i, arrayfunc=arrayfunc),
            shape[1:],
            dtype,
            meta=arrayfunc([])
        ))
    # print("out of loop")
    a = dask.array.stack(a)
    # a = a.reshape(143,3,2044, 2048)
    return a

def stitch(filelist,nrows=5,ncolumns=5,progression='snake'):
    import dask.array
    import dask
    pannel = []
    for i in range(ncolumns):
        if progression == 'straight':
            pannel.append(dask.array.concatenate(
                [time_stack(filename,bundler='cyx') for filename in filelist[i*nrows:i*nrows+nrows]]
            , axis=2)
            )
        elif progression == 'snake':
            #0 false any other # True
            if (i+1) % 2:
                print(i,'odd',filelist[i*nrows:i*nrows+nrows])
                pannel.append(dask.array.concatenate(
                    [time_stack(filename,bundler='cyx') for filename in filelist[i*nrows:i*nrows+nrows]]
                , axis=2)
                )
            else:
                print('even',np.flip(filelist[i*nrows:i*nrows+nrows]))
                pannel.append(dask.array.concatenate(
                    [time_stack(filename,bundler='cyx') for filename in np.flip(filelist[i*nrows:i*nrows+nrows])]
                , axis=2)
                )
    return dask.array.concatenate(pannel, axis=1)


# vmin=np.percentile(imgs[0],0.1),
# vmax=np.percentile(imgs[0],99.9)
def convert16to8bits(x,display_min=1000,display_max=65000,_GPU=True):
    if _GPU:
        import cupy as cp
    else: import numpy as cp
    def display(image, display_min, display_max): # copied from Bi Rico
    # Here I set copy=True in order to ensure the original image is not
    # modified. If you don't mind modifying the original image, you can
    # set copy=False or skip this step.
        # image = cp.array(image, copy=FalseTrue)
        image.clip(display_min, display_max, out=image)
        image -= display_min
        cp.floor_divide(image, (display_max - display_min + 1) / 256,
                        out=image, casting='unsafe')
        return image.astype(cp.uint8)

    lut = cp.arange(2**16, dtype='uint16')
    lut = display(lut, display_min, display_max)
    if _GPU:
        return cp.asnumpy(cp.take(lut, x))
    else:
        return cp.take(lut,x)

def export():
    plt.imshow(rgb[1,3,:2044,:2048])
    import tifffile as tf
    with tf.TiffWriter("/home/jmamede/Data/test.tiff",
                        bigtiff=True,
                        imagej=False,) as tif:
        for time in range(rgb.shape[1]):
             tif.save(rgb[:,time,:,:].compute(),
                    compress= 3,
                    photometric='minisblack',
                    metadata= None,
                    contiguous=False,
                )
    tif.close()

def pimsmeta2OMEXML(reader, xlen=1, ylen=1, project=False, time_offset=0, maxT=None, _pixeltype = None, verbose=False):
#     from apeer_ometiff_library import omexmlClass
    import aicsimageio.vendor.omexml as omexmlClass
    import re , os, sys

    #Missing TODO:
    #<Image>,  Name = "ImageName"
    #Instrument ID and Detector ID and Objective
#     frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'wsCameraName']

    # Objective settings with Refractive Index
        #Pixels,
            #Channel Color = RGB###, EmissionWavelength, Name of Channel.
            #Plane  ExposureTime, Position X, Y, Z (Z is easy as it's in nd2reader metadata)
    def writeplanes(pixel, SizeT=1, SizeZ=1, SizeC=1, order='TZCYX', verbose=False):

        if order == 'TZCYX' or order == 'XYCZT':
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
                        pixel.Plane(counter).DeltaT = np.float(reader.metadata.PlaneDeltaT(0,counter)) + time_offset
                        if verbose: print(pixel.Plane(counter).DeltaT)
                        try:
                            pixel.Plane(counter).PositionZ = reader.metadata.PlanePositionZ(0,counter)
                            if verbose: print(pixel.Plane(counter).PositionZ)
                        except: print("No position Z")
                        try:
                            pixel.Plane(counter).PositionX = reader.metadata.PlanePositionX(0,counter)
                        except: print("No position X")
                        try:
                            pixel.Plane(counter).PositionY = reader.metadata.PlanePositionY(0,counter)
                        except: print("No position Y")
#                         pixel.Plane(counter).ExposureTime =
#                         pixel.Plane(counter).PositionX =
#                         pixel.Plane(counter).PositionY =
#                         pixel.Plane(counter).
                        counter = counter + 1


        return pixel

    #make a metadata var
    bfmeta = reader.metadata
    scalex = reader.metadata.PixelsPhysicalSizeX(0)
    scaley = scalex

    if not project:
        scalez = reader.metadata.PixelsPhysicalSizeZ(0)
    if _pixeltype is not None:
        pixeltype = reader.metadata.PixelsType(0)
    else: pixeltype = _pixeltype
    # dimorder = 'TZCYX'
    dimorder = reader.metadata.PixelsDimensionOrder(0)

    omexml = omexmlClass.OMEXML()

    omexml.image(0).Name = os.path.basename(reader.filename)
    p = omexml.image(0).Pixels

    p.SizeX = reader.sizes['x']*xlen
    p.SizeY = reader.sizes['y']*ylen
    p.SizeC = reader.sizes['c']
    if maxT == None:
        try:
            p.SizeT = reader.sizes['t'] ################# concat #########
            maxT = p.SizeT
        except:
            print("Single T")
            maxT = 1
    else: p.SizeT = maxT

    p.PhysicalSizeX = np.float(scalex)
    p.PhysicalSizeY = np.float(scaley)
    p.PixelType = pixeltype
    p.channel_count = reader.sizes['c']



    #I am using separate files for each visit point
    #, if you want one tiff with all visit points (possibly good for panels)
    #you will need to update this section

    for c in range(p.SizeC):
        try:
            p.Channel(c).Name = str(reader.metadata.ChannelEmissionWavelength(0,c))
        except: p.Channel(c).Name = str(reader.metadata.ChannelName(0,c))

        clr = {'miRFsP670':  65535 , 'mirfp670':  65535 ,'AF647': 65535,'a647': 65535,'Cy5': 65535,'640 nm': 65535,'pqbp1-AF647': 65535,
               'farRED-EM': 65535, 'mirfp67-': 65535,'Cy5 (Em)': 65535,
               'mruby3' : -16776961,'mRuby3' : -16776961,'mRuby' : -16776961,'RED-EM' : -16776961,'555 nm' : -16776961,'TRITC': -16776961, 'Cy3': -16776961,
                           'FITc': 16711935,   'fitc': 16711935,'GFP': 16711935,'FITC': 16711935,'GREEN-EM': 16711935, '470 nm': 16711935,'FITC (Em)': 16711935,'Igfp': 16711935, 'AF488': 16711935,'pre-paGFP': 16711935,'pre-paGFP': 16711935,'post-PAGFP':-16776961,'PAGFP':-16776961,
               'DAPI': 65535, 'Cgas-DY405': 65535, 'DAPI (Em)': 65535,'igfp': 16711935,}

        p.Channel(c).Color = clr[p.Channel(c).Name]
        p.Channel(c).ChannelEmissionWavelength = clr[p.Channel(c).Name]
        if pixeltype == 'unit8':
            #this is not related, fix in the future
            p.Channel(c).SamplesPerPixel = 1
        if pixeltype == 'unit16':
            p.Channel(c).SamplesPerPixel = 1

    if project:
        p.SizeZ = 1
        if verbose: print(maxT)
        p.plane_count = 1 * maxT * p.SizeC #* SizeV
        p = writeplanes(p, SizeT=maxT, SizeZ=1, SizeC=p.SizeC, order=dimorder, verbose=verbose)
    else:
        p.SizeZ = reader.sizes['z']
        p.plane_count = p.SizeZ * maxT * p.SizeC #* SizeV
        p = writeplanes(p, SizeT=maxT, SizeZ=p.SizeZ, SizeC=p.SizeC, order=dimorder, verbose=verbose)


    p.populate_TiffData()
#     omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))

    return omexml
