import numpy as np
from nd2reader import ND2Reader
import traitlets
from ipywidgets import widgets
from IPython.display import display
from tkinter import Tk, filedialog
# import dask
# import dask.array as da
# from pims import ND2_Reader as ND2Reader
# import aicsimageio.vendor.omexml as ome
from ipywidgets import interact


def tick_choices(Project,Zstack,append,_ram):
    return Project,Zstack,append,_ram

class SelectFilesButton(object):
    """A file widget that leverages tkinter.filedialog."""

    def __init__(self):
        super(SelectFilesButton, self).__init__()
        # Add the selected_files trait

        # Create the button.
        self.button = widgets.Button(description = 'Select Files', icon = "square-o")
        self.button.add_traits(files=traitlets.traitlets.List())
        self.button.pick = False
#         self.description = "Select Files"
#         self.icon = "square-o"
        self.button.style.button_color = "orange"

        self.button2 = widgets.Button(description = 'Select Directory', icon = "square-o")
#         self.button2.add_traits(directory=traitlets.traitlets.List())
#         self.description = "Select Files"
#         self.icon = "square-o"
        self.button2.style.button_color = "orange"
        self.button2.pick = False
        # Set on click behavior.
        self.button.on_click(self.select_files)
        self.button2.on_click(self.select_directory)
        display(self.button)
        display(self.button2)

    @staticmethod
    def select_files(b):
        """Generate instance of tkinter.filedialog.

        Parameters
        ----------
        b : obj:
            An instance of ipywidgets.widgets.Button
        """
        # Create Tk root
        root = Tk()
        # Hide the main window
        root.withdraw()
        # Raise the root to the top of all windows.
        root.call('wm', 'attributes', '.', '-topmost', True)
        # List of selected fileswill be set to b.value
        b.files = filedialog.askopenfilename(multiple=True)
        b.pick = True
        b.description = "Files Selected"
        b.icon = "check-square-o"
        b.style.button_color = "lightgreen"

    @staticmethod
    def select_directory(c):
        """Generate instance of tkinter.filedialog.

        Parameters
        ----------
        c : obj:
            An instance of ipywidgets.widgets.Button
        """
        # Create Tk root
        root = Tk()
        # Hide the main window
        root.withdraw()
        # Raise the root to the top of all windows.
        root.call('wm', 'attributes', '.', '-topmost', True)
        # List of selected fileswill be set to b.value
        c.files = filedialog.askdirectory()
        c.pick = True
        c.description = "Directory Selected"
        c.icon = "check-square-o"
        c.style.button_color = "lightgreen"



def update_progress(progress):
    from IPython.display import clear_output
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    block = int(round(bar_length * progress))

    clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(text)

# for lens
#     reader.parser._raw_metadata.image_calibration

# import re


def Nd2meta2OMEXML(reader, project=False, time_offset=0, maxT=None, visit=0,**kwargs):
#     from apeer_ometiff_library import omexmlClass
    import aicsimageio.vendor.omexml as omexmlClass
    import re
    import sys,os

    #Missing TODO:
    #<Image>,  Name = "ImageName"
    #Instrument ID and Detector ID and Objective
    #     frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'wsCameraName']

    # Objective settings with Refractive Index
    #Pixels,
    #Channel Color = RGB###, EmissionWavelength, Name of Channel.
    #Plane  ExposureTime, Position X, Y, Z (Z is easy as it's in nd2reader metadata)
    def fetch_extra_metadata(reader):
        import re
        extra_meta = reader.parser._raw_metadata.image_text_info[b'SLxImageTextInfo'][b'TextInfoItem_5'].decode()
        extra_meta = re.split(',|;|\r\n',extra_meta)
        extra_dict = dict()

        for line in extra_meta:
            line = line.strip().strip('- ')
            keyvalue = str.split(line,':')
            if len(keyvalue) > 1:
                key = keyvalue[0]
                value = keyvalue[1]
                extra_dict[key] = value

        return extra_dict

    def writeplanes(pixel, v, SizeT=1, SizeZ=1, SizeC=1, SizeV=1, order='TZCYX', verbose=False, **kwargs):
        if order == 'TZCYX':
            pixel.DimensionOrder = omexmlClass.DO_XYCZT
            counter = 0

            for t in range(SizeT):
                for z in range(SizeZ):
                    for c in range(SizeC):
                        if verbose:
                            print('Write PlaneTable: ', t, v, z, c),
                            sys.stdout.flush()

                        pixel.Plane(counter).TheT = t
                        pixel.Plane(counter).TheZ = z
                        pixel.Plane(counter).TheC = c
                        #check basically because of triggered acquisition the arrays shouldn't have the size of "channel"
                        #nd2reader spits ms /1000
                        #okay, this changes from triggered to non triggered I need to find a way to check if it was a triggered exp
                        #Fix to skip V's when they are not in the file
                        timesteps = reader.timesteps/1000
                        if timesteps.shape[0] == reader.sizes['t']*reader.sizes['v']*reader.sizes['z']:
                            pass
                        else: timesteps = timesteps[:reader.sizes['t']*reader.sizes['v']*reader.sizes['z']]

                        timesteps = timesteps.reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))

                        pixel.Plane(counter).DeltaT = timesteps[t,v,z] + time_offset
                        if verbose:
                            print(timesteps[t,v,z],pixel.Plane(counter).DeltaT)
                            sys.stdout.flush()


                        #since I'm reshaping, I don't need to adapt for projections because the "z" will always be 0
                        #in that case
                        z_coords = np.array(
                            nd2meta['z_coordinates']).reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))
                        if nd2meta['z_coordinates'] != None:
                            pixel.Plane(counter).PositionZ = z_coords[t,v,z]
                            if verbose:
                                print("z:",pixel.Plane(counter).PositionZ)
                                sys.stdout.flush()
                        else:
                            pixel.Plane(counter).PositionZ = nd2meta['z_levels'][z] * np.float(pixel.PhysicalSizeZ)


                        try:
                            x_coords = np.array(
                                 nd2meta['x_coordinates']).reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))

                            pixel.Plane(counter).PositionX = x_coords[t,v,z]
                        except: print("No position X")
                        try:
                            y_coords = np.array(
                                nd2meta['y_coordinates']).reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))
                            pixel.Plane(counter).PositionY = y_coords[t,v,z]
                        except: print("No position Y")
#                         pixel.Plane(counter).ExposureTime =
#                         pixel.Plane(counter).PositionX =
#                         pixel.Plane(counter).PositionY =
                        counter = counter + 1
        return pixel

    #make a metadata var
    nd2meta = reader.metadata
    timesteps = reader.timesteps
    extra_dict = fetch_extra_metadata(reader)
#     Series = nd2meta['fields_of_view'][-1]+1
    scalex = nd2meta['pixel_microns']
    scaley = scalex

    if not project:
#         scalez = round(nd2meta['z_coordinates'][1]-nd2meta['z_coordinates'][0],3)
#         scalez = frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'ppNextLevelEx'][b''][b'ppNextLevelEx'][b''][b'uLoopPars'][b'dZStep']
        scalez = extra_dict['Step'].split()[0]
    pixeltype = 'uint16'
    dimorder = 'TZCYX'
# print(a)
    omexml = omexmlClass.OMEXML()
#     omexml.image_count = 1
#     omexml.image_count = reader.sizes['v']
    omexml.image(0).Name = os.path.basename(reader.filename)
    p = omexml.image(0).Pixels

    p.SizeX = reader.sizes['x']
    p.SizeY = reader.sizes['y']
    p.SizeC = reader.sizes['c']
    SizeV = reader.sizes['v']
    if maxT == None:
        p.SizeT = reader.sizes['t']
        maxT = p.SizeT
    else: p.SizeT = maxT

    p.PhysicalSizeX = np.float(scalex)
    p.PhysicalSizeY = np.float(scaley)

    if not project:
        p.PhysicalSizeZ = np.float(scalez)
    p.PixelType = pixeltype
    p.channel_count = reader.sizes['c']


    #I am using separate files for each visit point
    #, if you want one tiff with all visit points (possibly good for panels)
    #you will need to update this section
    for c in range(p.SizeC):
        p.Channel(c).Name = nd2meta['channels'][c]
        # try to automate by wavelenght one day, this basically sets the colour
        # to be automatically shown in Fiji/Image/NIS-elements
        clr = {'miRFsP670':  65535 , 'mirfp670':  65535 ,'AF647': 65535,'a647': 65535,'Cy5': 65535,'640 nm': 65535,'pqbp1-AF647': 65535,
               'farRED-EM': 65535, 'mirfp67-': 65535,'Cy5 (Em)': 65535,
               'mruby3' : -16776961,'mRuby3' : -16776961,'mRuby' : -16776961,'RED-EM' : -16776961,'555 nm' : -16776961,'TRITC': -16776961, 'Cy3': -16776961,
                           'FITc': 16711935,   'fitc': 16711935,'GFP': 16711935,'FITC': 16711935,'GREEN-EM': 16711935, '470 nm': 16711935,'FITC (Em)': 16711935,'Igfp': 16711935, 'AF488': 16711935,'pre-paGFP': 16711935,'pre-paGFP': 16711935,'post-PAGFP':-16776961,'PAGFP':-16776961,
               'DAPI': 65535, 'Cgas-DY405': 65535, 'DAPI (Em)': 65535,'igfp': 16711935,}
        if p.Channel(c).Name in clr:
            p.Channel(c).Color = clr[p.Channel(c).Name]
            p.Channel(c).ChannelEmissionWavelength = clr[p.Channel(c).Name]
        else:
            print('Warning, color is not defined in the dictionary, defaulting to green')
            p.Channel(c).Color = 16711935
            p.Channel(c).ChannelEmissionWavelength = 16711935
        #Get this from metadata or ExtraData
        # p.Channel(c).EmissionWavelength =
        if pixeltype == 'unit8':
            #We never do averaging, update this if you do
            p.Channel(c).SamplesPerPixel = 1
        if pixeltype == 'unit16':
            p.Channel(c).SamplesPerPixel = 1


    if project:
        p.SizeZ = 1
        p.plane_count = 1 * maxT * p.SizeC #* SizeV
        p = writeplanes(p, v=visit, SizeT=maxT, SizeZ=1, SizeC=p.SizeC, SizeV=reader.sizes['v'], timesteps=timesteps,  order=dimorder)
    else:
        p.SizeZ = reader.sizes['z']
        p.plane_count = p.SizeZ * maxT * p.SizeC #* SizeV
        p = writeplanes(p, v=visit, SizeT=maxT, SizeZ=p.SizeZ, SizeC=p.SizeC, SizeV=reader.sizes['v'], timesteps=timesteps, order=dimorder)

    p.populate_TiffData()
    # omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))
#     print(p.SizeT, p.SizeC, p.SizeZ)
#     print(omexml.to_xml())
    return omexml


def pims_nd2meta2OMEXML(reader, project=False, time_offset=0, maxT=None, visit=0,**kwargs):
#     from apeer_ometiff_library import omexmlClass
    import aicsimageio.vendor.omexml as omexmlClass
    import re
    import sys,os

    #Missing TODO:
    #<Image>,  Name = "ImageName"
    #Instrument ID and Detector ID and Objective
    #     frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'wsCameraName']

    # Objective settings with Refractive Index
    #Pixels,
    #Channel Color = RGB###, EmissionWavelength, Name of Channel.
    #Plane  ExposureTime, Position X, Y, Z (Z is easy as it's in nd2reader metadata)


    def writeplanes(pixel, v, SizeT=1, SizeZ=1, SizeC=1, SizeV=1, order='TZCYX', verbose=False, **kwargs):
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
                        #nd2reader spits ms /1000
                        #okay, this changes from triggered to non triggered I need to find a way to check if it was a triggered exp
                        #Fix to skip V's when they are not in the file

#                         print('tvzc',t,v,z,c)
                        pixel.Plane(counter).DeltaT = timesteps[t] + time_offset
#                         print(timesteps[v,t,z],pixel.Plane(counter).DeltaT)
#                         z_coords = np.array(
#                             nd2meta['z_coordinates']).reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))
#                         if nd2meta['z_coordinates'] != None:
                        pixel.Plane(counter).PositionZ = z_coords[z]
                        print("z:",pixel.Plane(counter).PositionZ)
#                         else:
#                             pixel.Plane(counter).PositionZ = nd2meta['z_levels'][z] * np.float(pixel.PhysicalSizeZ)
#                         pixel.Plane(counter).ExposureTime =
#                         pixel.Plane(counter).PositionX =
#                         pixel.Plane(counter).PositionY =
                        counter = counter + 1
        return pixel

    #make a metadata var
    nd2meta = reader.metadata

    reader.iter_axes = 't'  # 't' is the default already
    reader.bundle_axes = 'zyx'  # when 'z' is available, this will be default
    for i in range(reader.sizes['t']):
        timesteps = reader[i].metadata['t_ms'][0]/1000

#     extra_dict = fetch_extra_metadata(reader)
#     Series = nd2meta['fields_of_view'][-1]+1
    scalex = nd2meta['calibration_um']
    scaley = scalex

    if not project:
#         scalez = round(nd2meta['z_coordinates'][1]-nd2meta['z_coordinates'][0],3)
#         scalez = frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'ppNextLevelEx'][b''][b'ppNextLevelEx'][b''][b'uLoopPars'][b'dZStep']
        scalez = reader[0].metadata['z_um'][1]-reader[0].metadata['z_um'][0]
        z_coords = reader[0].metadata['z_um']

    pixeltype = 'uint16'
    dimorder = 'TZCYX'
# print(a)
    omexml = omexmlClass.OMEXML()
#     omexml.image_count = 1
#     omexml.image_count = reader.sizes['v']
    omexml.image(0).Name = os.path.basename(reader.filename)
    p = omexml.image(0).Pixels

    p.SizeX = reader.sizes['x']
    p.SizeY = reader.sizes['y']
    p.SizeC = reader.sizes['c']
#     SizeV = reader.sizes['v']
    if maxT == None:
        p.SizeT = reader.sizes['t']
        maxT = p.SizeT
    else: p.SizeT = maxT

    p.PhysicalSizeX = np.float(scalex)
    p.PhysicalSizeY = np.float(scaley)

    if not project:
        p.PhysicalSizeZ = np.float(scalez)
    p.PixelType = pixeltype
    p.channel_count = reader.sizes['c']





    #I am using separate files for each visit point
    #, if you want one tiff with all visit points (possibly good for panels)
    #you will need to update this section
    for c in range(p.SizeC):
        p.Channel(c).Name = reader.metadata['plane_'+str(i)]['name']
        # try to automate by wavelenght one day, this basically sets the colour
        # to be automatically shown in Fiji/Image/NIS-elements
        clr = {'miRFP670':  65535 , 'mirfp670':  65535 , 'a647': 65535,'Cy5': 65535,
               'farRED-EM': 65535, 'mirfp67-': 65535,'Cy5 (Em)': 65535,
               'mRuby3' : -16776961,'mRuby' : -16776961,'RED-EM' : -16776961,'555 nm' : -16776961,'TRITC': -16776961,
               'GFP': 16711935,'FITC': 16711935,'GREEN-EM': 16711935, '470 nm': 16711935,'FITC (Em)': 16711935,
               'DAPI': 65535,}
        p.Channel(c).Color = clr[p.Channel(c).Name]
        p.Channel(c).ChannelEmissionWavelength = reader.metadata['plane_'+str(i)]['emission_nm']
        #Get this from metadata or ExtraData
        # p.Channel(c).EmissionWavelength =
        if pixeltype == 'unit8':
            #We never do averaging, update this if you do
            p.Channel(c).SamplesPerPixel = 1
        if pixeltype == 'unit16':
            p.Channel(c).SamplesPerPixel = 1


    if project:
        p.SizeZ = 1
        p.plane_count = 1 * maxT * p.SizeC #* SizeV
        p = writeplanes(p, v=visit, SizeT=maxT, SizeZ=1, SizeC=p.SizeC, SizeV=reader.sizes['m'], timesteps=timesteps,  order=dimorder)
    else:
        p.SizeZ = reader.sizes['z']
        p.plane_count = p.SizeZ * maxT * p.SizeC #* SizeV
        p = writeplanes(p, v=visit, SizeT=maxT, SizeZ=p.SizeZ, SizeC=p.SizeC, SizeV=reader.sizes['m'], timesteps=timesteps, order=dimorder)

    p.populate_TiffData()
    # omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))
#     print(p.SizeT, p.SizeC, p.SizeZ)
#     print(omexml.to_xml())
    return omexml


def Nd2meta2OMEXMLonce(reader, project=False, time_offset=0, maxT=None, visit=0,**kwargs):
#     from apeer_ometiff_library import omexmlClass
    import aicsimageio.vendor.omexml as omexmlClass
    import re
    import sys,os

    #Missing TODO:
    #<Image>,  Name = "ImageName"
    #Instrument ID and Detector ID and Objective
    #     frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'wsCameraName']

    # Objective settings with Refractive Index
    #Pixels,
    #Channel Color = RGB###, EmissionWavelength, Name of Channel.
    #Plane  ExposureTime, Position X, Y, Z (Z is easy as it's in nd2reader metadata)


    def writeplanes(pixel, v, SizeT=1, SizeZ=1, SizeC=1, SizeV=1, order='TZCYX', verbose=False, **kwargs):
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
                        #nd2reader spits ms /1000
                        #okay, this changes from triggered to non triggered I need to find a way to check if it was a triggered exp
                        #Fix to skip V's when they are not in the file
                        timesteps = reader.timesteps/1000
                        timesteps = timesteps.reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))
                        pixel.Plane(counter).DeltaT = timesteps[t,v,z] + time_offset

                        if verbose:
                            print('tvzc',t,v,z,c)
                            print(timesteps[v,t,z],pixel.Plane(counter).DeltaT)
                            sys.stdout.flush()

                        z_coords = np.array(
                            nd2meta['z_coordinates']).reshape((reader.sizes['t'],reader.sizes['v'],reader.sizes['z']))
                        if nd2meta['z_coordinates'] != None:
                            pixel.Plane(counter).PositionZ = z_coords[t,v,z]
                            if verbose:
                                print("z:",pixel.Plane(counter).PositionZ)
                                sys.stdout.flush()

                        else:
                            pixel.Plane(counter).PositionZ = nd2meta['z_levels'][z] * np.float(pixel.PhysicalSizeZ)
#                         pixel.Plane(counter).ExposureTime =
#                         pixel.Plane(counter).PositionX =
#                         pixel.Plane(counter).PositionY =
                        counter = counter + 1
        return pixel

    #make a metadata var
    nd2meta = reader.metadata
#     extra_dict = fetch_extra_metadata(reader)
#     Series = nd2meta['fields_of_view'][-1]+1
    scalex = nd2meta['pixel_microns']
    scaley = scalex

    if not project:
#         scalez = round(nd2meta['z_coordinates'][1]-nd2meta['z_coordinates'][0],3)
#         scalez = frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'ppNextLevelEx'][b''][b'ppNextLevelEx'][b''][b'uLoopPars'][b'dZStep']
        scalez = 0.5
    pixeltype = 'uint16'
    dimorder = 'TZCYX'
# print(a)
    omexml = omexmlClass.OMEXML()
#     omexml.image_count = 1
#     omexml.image_count = reader.sizes['v']
    omexml.image(0).Name = os.path.basename(reader.filename)
    p = omexml.image(0).Pixels

    p.SizeX = reader.sizes['x']
    p.SizeY = reader.sizes['y']
    p.SizeC = reader.sizes['c']
    SizeV = reader.sizes['v']
    if maxT == None:
        p.SizeT = reader.sizes['t']
        maxT = p.SizeT
        print(maxT)
    else: p.SizeT = maxT

    p.PhysicalSizeX = np.float(scalex)
    p.PhysicalSizeY = np.float(scaley)

    if not project:
        p.PhysicalSizeZ = np.float(scalez)
    p.PixelType = pixeltype
    p.channel_count = reader.sizes['c']


    #I am using separate files for each visit point
    #, if you want one tiff with all visit points (possibly good for panels)
    #you will need to update this section
    for c in range(p.SizeC):
        p.Channel(c).Name = nd2meta['channels'][c]
        # try to automate by wavelenght one day, this basically sets the colour
        # to be automatically shown in Fiji/Image/NIS-elements
        clr = {'miRFP670':  65535 , 'mirfp670':  65535 , 'a647': 65535,
               'farRED-EM': 65535, 'mirfp67-': 65535,'Cy5 (Em)': 65535,
               'mRuby3' : -16776961,'mRuby' : -16776961,'RED-EM' : -16776961,'555 nm' : -16776961,
               'GFP': 16711935,'FITC': 16711935,'GREEN-EM': 16711935, '470 nm': 16711935,'FITC (Em)': 16711935,
               'DAPI': 65535,}
        p.Channel(c).Color = clr[p.Channel(c).Name]
        p.Channel(c).ChannelEmissionWavelength = clr[p.Channel(c).Name]
        #Get this from metadata or ExtraData
        # p.Channel(c).EmissionWavelength =
        if pixeltype == 'unit8':
            #We never do averaging, update this if you do
            p.Channel(c).SamplesPerPixel = 1
        if pixeltype == 'unit16':
            p.Channel(c).SamplesPerPixel = 1


    if project:
        p.SizeZ = 1
        p.plane_count = 1 * maxT * p.SizeC #* SizeV
        p = writeplanes(p, v,SizeT=maxT, SizeZ=1, SizeC=p.SizeC, order=dimorder)
    else:
        p.SizeZ = 23
        p.plane_count = p.SizeZ * maxT * p.SizeC #* SizeV
        p = writeplanes(p, v,SizeT=maxT, SizeZ=p.SizeZ, SizeC=p.SizeC, order=dimorder)

    p.populate_TiffData()
    # omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))
#     print(p.SizeT, p.SizeC, p.SizeZ)
#     print(omexml.to_xml())
    return omexml


def pimsmeta2OMEXML(reader, project=False, time_offset=0, maxT=None, verbose=False):
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
                        print(pixel.Plane(counter).DeltaT)
                        try:
                            pixel.Plane(counter).PositionZ = reader.metadata.PlanePositionZ(0,counter)
                            print(pixel.Plane(counter).PositionZ)
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

    pixeltype = reader.metadata.PixelsType(0)
    # dimorder = 'TZCYX'
    dimorder = reader.metadata.PixelsDimensionOrder(0)

    omexml = omexmlClass.OMEXML()

    omexml.image(0).Name = os.path.basename(reader.filename)
    p = omexml.image(0).Pixels

    p.SizeX = reader.sizes['x']
    p.SizeY = reader.sizes['y']
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
        print(maxT)
        p.plane_count = 1 * maxT * p.SizeC #* SizeV
        p = writeplanes(p, SizeT=maxT, SizeZ=1, SizeC=p.SizeC, order=dimorder, verbose=verbose)
    else:
        p.SizeZ = reader.sizes['z']
        p.plane_count = p.SizeZ * maxT * p.SizeC #* SizeV
        p = writeplanes(p, SizeT=maxT, SizeZ=p.SizeZ, SizeC=p.SizeC, order=dimorder, verbose=verbose)


    p.populate_TiffData()
#     omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))

    return omexml


def Concat_OMEXML(filelist, project=False):
#     from apeer_ometiff_library import omexmlClass
    import aicsimageio.vendor.omexml as omexmlClass
    import re , os, sys
    import numpy as np
    import pims

    #Missing TODO:
    #<Image>,  Name = "ImageName"
    #Instrument ID and Detector ID and Objective
#     frames.parser._raw_metadata.image_metadata[b'SLxExperiment'][b'wsCameraName']

    # Objective settings with Refractive Index
        #Pixels,
            #Channel Color = RGB###, EmissionWavelength, Name of Channel.
            #Plane  ExposureTime, Position X, Y, Z (Z is easy as it's in nd2reader metadata)
    def writeplanes(pixel,bfmeta, SizeT=1, SizeZ=1, SizeC=1, order='TZCYX', verbose=False, ):

        if order == 'TZCYX' or order == 'XYCZT':
            pixel.DimensionOrder = omexmlClass.DO_XYCZT
            counter = 0

            for t in range(SizeT):
                for z in range(SizeZ):
                    for c in range(SizeC):
                        if verbose:
                            print('Write PlaneTable: ', t, z, c, counter)
                            sys.stdout.flush()
                        print(fname)
                        pixel.Plane(counter).TheT = t
                        pixel.Plane(counter).TheZ = z
                        pixel.Plane(counter).TheC = c
                        #check basically because of triggered acquisition the arrays shouldn't have the size of "channel"
                        print(counter)
                        pixel.Plane(counter).DeltaT = np.float(bfmeta.PlaneDeltaT(0,counter))
                        try:
                            pixel.Plane(counter).PositionZ = reader.metadata.PlanePositionZ(0,counter)
                            print(pixel.Plane(counter).PositionZ)
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


    def writeextraplanes(pixel, T1=1, SizeT=1, SizeZ=1, SizeC=1, order='TZCYX', verbose=False):

        if order == 'TZCYX' or order == 'XYCZT':
            innercounter = 0
            counter = T1*SizeZ*SizeC
            for t in range(T1,T1+SizeT):
                for z in range(SizeZ):
                    for c in range(SizeC):
                        if verbose:
                            print('Write PlaneTable t,z,c,counter: ', t, z, c ,counter)
                            sys.stdout.flush()

                        pixel.Plane(counter).TheT = t
                        pixel.Plane(counter).TheZ = z
                        pixel.Plane(counter).TheC = c
                        #check basically because of triggered acquisition the arrays shouldn't have the size of "channel"
                        pixel.Plane(counter).DeltaT = np.float(reader.metadata.PlaneDeltaT(0,innercounter ))
                        pixel.Plane(counter).PositionZ = reader.metadata.PlanePositionZ(0,innercounter )
                        # pixel.Plane(counter).PositionX = reader.metadata.PlanePositionX(0,counter)
                        # pixel.Plane(counter).PositionY = reader.metadata.PlanePositionY(0,counter)
#                         pixel.Plane(counter).ExposureTime =
#                         pixel.Plane(counter).PositionX =
#                         pixel.Plane(counter).PositionY =
#                         pixel.Plane(counter).
                        counter += 1
                        innercounter += 1


        return pixel

    reader =   pims.bioformats.BioformatsReader(filelist[0],java_memory='1024m')
#     reader.iter_axes = 't'  # 't' is the default already
    # reader.bundle_axes = 'zyx'  # when 'z' is available, this will be default

    #make a metadata var
    bfmeta = reader.metadata
    scalex = reader.metadata.PixelsPhysicalSizeX(0)
    scaley = scalex

    if not project:
        scalez = reader.metadata.PixelsPhysicalSizeZ(0)

    pixeltype = reader.metadata.PixelsType(0)
    # dimorder = 'TZCYX'
    dimorder = reader.metadata.PixelsDimensionOrder(0)

    omexml = omexmlClass.OMEXML()

    omexml.image(0).Name = os.path.basename(reader.filename)
    p = omexml.image(0).Pixels

    p.SizeX = reader.sizes['x']
    p.SizeY = reader.sizes['y']
    p.SizeC = reader.sizes['c']




    p.PhysicalSizeX = np.float(scalex)
    p.PhysicalSizeY = np.float(scaley)
    p.PixelType = pixeltype
    p.channel_count = reader.sizes['c']
        #I am using separate files for each visit point
        #, if you want one tiff with all visit points (possibly good for panels)
        #you will need to update this section
    for c in range(p.SizeC):
        p.Channel(c).Name = str(reader.metadata.ChannelName(0,c))
        p.Channel(c).Color = reader.metadata.ChannelColor(0,c)
#         p.Channel(c).ChannelEmissionWavelength = float(reader.metadata.ChannelName(0,c))
#         print( p.Channel(c).Name, p.Channel(c).Color,p.Channel(c).ChannelEmissionWavelength )

        if pixeltype == 'unit8':
            #this is not related, fix in the future
            p.Channel(c).SamplesPerPixel = 1
        if pixeltype == 'unit16':
            p.Channel(c).SamplesPerPixel = 1


    time_total = 0
    for fname in filelist:
        reader =  pims.bioformats.BioformatsReader(fname,java_memory='1024m')
#     frames.iter_axes = 't'  # 't' is the default already
        # frames.bundle_axes = 'zyx'  # when 'z' is available, this will be default
        try:
            if reader.sizes['t'] > 0:
                time_total += reader.sizes['t']
        except: time_total += 1

    p.SizeT = time_total ################# concat #########
#     reader =  pims.bioformats.BioformatsReader(filelist[0],java_memory='1024m')
#     bfmeta = reader.metadata
    try:
        if reader.sizes['t'] > 0:
            sizeT_local += reader.sizes['t']
    except: sizeT_local = 1
    if project:
        p.SizeZ = 1
        p.plane_count = 1 * time_total * p.SizeC #* SizeV  ################# concat #########
        p = writeplanes(p, bfmeta, SizeT=sizeT_local, SizeZ=1, SizeC=p.SizeC, order=dimorder,verbose=False)  ################# concat #########
    else:
        p.PhysicalSizeZ = np.float(scalez)
        p.SizeZ = reader.sizes['z']
        p.plane_count = p.SizeZ * time_total * p.SizeC #* SizeV  ################# concat #########
        p = writeplanes(p, bfmeta, SizeT=sizeT_local, SizeZ=p.SizeZ, SizeC=p.SizeC, order=dimorder,verbose=False)  ################# concat #########



    filelist.pop(0)
    restartT = sizeT_local
    for fname in filelist:
        reader =  pims.bioformats.BioformatsReader(fname,java_memory='1024m')
        try:
            if reader.sizes['t'] > 0:
                sizeT_local += reader.sizes['t']
        except: sizeT_local = 1
#     frames.iter_axes = 't'  # 't' is the default already
        # frames.bundle_axes = 'zyx'  # when 'z' is available, this will be default
        try:
            if project:
                p = writeextraplanes(p, T1=restartT,SizeT=restartT+sizeT_local, SizeZ=1, SizeC=p.SizeC, order=dimorder,verbose=False)  ################# concat #########
            else:
                p = writeextraplanes(p, T1=restartT,SizeT=restartT+sizeT_local, SizeZ=p.SizeZ, SizeC=p.SizeC, order=dimorder,verbose=False)  ################# concat #########
            try:
                restartT += reader.sizes['t']
            except:
                print("Something Went wrong time problems")
                restartT += 1
        except: print("Something Went trong")






    p.populate_TiffData()
#     omexml.structured_annotations.add_original_metadata(omexmlClass.OM_SAMPLES_PER_PIXEL, str(p.SizeC))

    return omexml

def observer(img, i, *args):
    #mgs.append(img.max(axis=0))
    if i % 5 == 0:
        print('Observing iteration = {} (dtype = {}, max = {:.3f})'.format(i, img.dtype, img.max()))


def init_RL_algo(psfdims,pad_mode='none',pad_min=(0,0,0)):
    from flowdec import restoration as fd_restoration
    return  fd_restoration.RichardsonLucyDeconvolver(n_dims=psfdims
                                                    , pad_mode=pad_mode
                                                    ,pad_min=pad_min
    #                                                     ,observer_fn=observer
                                                    #,real_domain_fft=True
                                                    #,device='/cpu:0'
                                                   ).initialize()

def deconv(chunk, algo, psf ,iters=20, use_ram=False):
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession
    from flowdec import data as fd_data

    config = ConfigProto()
    if use_ram:
        config.gpu_options.allow_growth = True
        config.gpu_options.per_process_gpu_memory_fraction = 2

    return algo.run(fd_data.Acquisition(data=chunk, kernel=psf),
                                session_config=config ,
#                                 device_count={'GPU': 1},
                                niter=iters,
                               ).data

def depth_divide(xdivide=1,ydivide=1):
    if xdivide >1 and ydivide >1:
        depthdivide = (0,64,64)
    elif xdivide > 1 and ydivide == 1:
            depthdivide = (0,0,64)
    else:
            depthdivide = (0,0,0)

    return depthdivide

def get_deltaT(filename1,filename2):
    import datetime
    import pathlib
#     frames = ND2Reader(filelist[0])
#     a = frames.metadata['date']
#     frames = ND2Reader(filelist[1])
#     b = frames.metadata['date']
    fname1 = pathlib.Path(filename1)
    fname2 = pathlib.Path(filename2)

    mtime2 = datetime.datetime.fromtimestamp(fname2.stat().st_ctime)
    mtime1 = datetime.datetime.fromtimestamp(fname1.stat().st_ctime)
#     print(mtime2,mtime1)
#     print(fname2.stat().st_ctime - fname1.stat().st_ctime)
    return fname2.stat().st_ctime - fname1.stat().st_ctime


def tif_save_page(tif, frame, compression=None, description = None , photometric='minisblack',
                    metadata= None, contiguous=False):
    import tifffile
    if description is None:
        tif.save(frame, compression = compression,
          photometric = photometric, metadata= metadata,
          contiguous= contiguous,
      )
    else:
        tif.save(frame, compression = compression, description = description,
          photometric = photometric, metadata= metadata,
          contiguous= contiguous,
      )

def release_mem():
    from numba import cuda
    cuda.select_device(0)
    cuda.close()
    #the memory was released here!
    cuda.select_device(0)

def create_psf():
    pass
    # from flowdec import psf as fd_psf
    # from flowdec.nb import utils as nbutils
