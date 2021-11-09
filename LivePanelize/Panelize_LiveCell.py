import pims
import numpy as np
import dask
import dask.array
import warnings
import cupy as cp
import glob
__author__ = """João Mamede"""
__email__ = "jmamede@rush.edu"
import sys
sys.path.insert(0,'/home/jmamede/scripts/LivePanelize/')
import Libraries

# filelist = glob.glob('/home/jmamede/Data/CaRuby3/20210128MDM*tiff')
filelist = glob.glob('/home/jmamede/Data/CaRuby3/20211102ghost/*.ome.tiff')
filelist.sort()

metadata = pims.Bioformats(filelist[0]).metadata
metadata.PlaneDeltaT(0,0)
timelist = []
for i in range(metadata.PlaneCount(0)):
    timelist.append(metadata.PlaneDeltaT(0,i))

timelist = np.asarray(timelist)
timelist = timelist.reshape((metadata.PlaneCount(0)//3,metadata.ChannelCount(0)))
timelist.shape
timelist = timelist[:,0]
del(metadata)


# all = []
filelist
all = Libraries.stitch(filelist,9,5)
# all8 = all.map_blocks(Libraries.convert16to8bits)
all8 = all
#can't reshape I don't know why, resclicing was the only way I found
green = all8[:-3:3]
red = all8[1:-2:3]
blue = all8[2:-1:3]
green.shape

#DETAIL IS HERE!!!!
rgb = dask.array.stack([red,blue,green],axis=0)
rgb
rgb = rgb[:,:,...].compute()

rgb.shape

import napari
# %gui qt
# rgb[2,2].shape
# napari.view_image(all[:,0,:,:,:])

#
# rmin = np.percentile(rgb[1,2].compute(),0.1)
# rmax = np.percentile(rgb[1,2].compute(),99.5)
# gmin = np.percentile(rgb[0,2].compute(),0.1)
# gmax = np.percentile(rgb[0,2].compute(),99.5)
# bmin = np.percentile(rgb[2,2].compute(),0.1)
# bmax = np.percentile(rgb[2,2].compute(),99.5)

rmin = np.percentile(rgb[1,2],0.5)
rmax = np.percentile(rgb[1,2],99.9)
gmin = np.percentile(rgb[0,2],0.5)
gmax = np.percentile(rgb[0,2],99.9)
bmin = np.percentile(rgb[2,2],0.5)
bmax = np.percentile(rgb[2,2],99.9)

# rmin = 1000
# rmax = 15000
# gmin = 1000
# gmax = 15000
# bmin = 1000
# bmax = 30000
import time
def update_slider(event):
    import time
    # only trigger if update comes from first axis (optional)
    print('inside')
        #ind_lambda = viewer.dims.indices[0]
    ind_lambda = v.dims.current_step[0]
    timestrg = "{0}".format(time.strftime('%H:%M:%S',time.gmtime(timelist[ind_lambda])))
    v.text_overlay.text = timestrg

v = napari.Viewer(show=True)
       # vmin=np.percentile(imgs[0],0.1),
       # vmax=np.percentile(imgs[0],99.9)
v.add_image(rgb[0,:],
            # rgb=True,
            scale=[0.22,0.22],
            contrast_limits=[gmin,gmax],
            blending='additive',
            colormap='green',
            name='HIV-iGFP',#, is_pyramid=False
                 )
v.add_image(rgb[1,:], contrast_limits=[rmin,rmax],
        blending='additive',
        colormap='red',
        name='CA-mRuby3',#, is_pyramid=False
        scale=[0.22,0.22],
             )
v.add_image(rgb[2,:], contrast_limits=[bmin,bmax],
        blending='additive',
        colormap='blue',
        name='Nucspot650',#, is_pyramid=False
        scale=[0.22,0.22],
             )
v.text_overlay.visible = True

v.text_overlay.text = "{0}".format(time.strftime('%H:%M:%S',time.gmtime(timelist[0])))
v.dims.events.current_step.connect(update_slider)
napari.run()


import pandas as pd
spots = pd.read_hdf('/run/media/jmamede/Joao/CAruby/20210406mdm-WOWO/Nuclei_spots3.h5')
v.add_points(spots,face_color='red',opacity=0.5,size=15)
# v.add_labels(nuclei_labels,
#  # contrast_limits=[bmin,bmax],
#         # blending='additive',
#         # colormap='blue',
#         name='Nuclei',#, is_pyramid=False
#              )



from napari_animation import AnimationWidget

animation_widget = AnimationWidget(v)
v.window.add_dock_widget(animation_widget, area='right')

#
#
# from naparimovie import Movie
# help(Movie)
# movie = Movie(myviewer=v)
# v.show()
# movie.inter_steps = 15
# movie.make_movie(name='/tmp/test.mp4',resolution = 300, fps=20)
