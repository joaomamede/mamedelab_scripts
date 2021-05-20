import scipy.ndimage as ndi
#import cv2
import numpy as np
import matplotlib.pyplot as plt
import pims
#import libtiff
import time,sys
import csv
# ~ import skimage
# ~ from skimage.morphology import watershed
# ~ from skimage.feature import peak_local_max
# ~ from skimage import measure
import glob,os
#from mayavi import mlab
import pandas as pd
from ipyparallel import Client
c = Client()
#~ v = c[:]
c.load_balanced_view()
c
# =============================================================================
# myfile = open('count_ndi_mask_max.csv', 'wb')
# wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#
# =============================================================================
plot = True

def crunch_data(ficheiro):
    import os
    import matplotlib.pyplot as plt
    from skimage import filters
    import pims
    import sys
    import numpy as np
    sys.path.insert(0,'/home/jmamede/scripts')
    from support_pla import othercolor, cell_mask, multiply,  make_labels_trackpy
    import pandas as pd
    #for blobs/dots
    plot = True
    #for cell mask0 pqbp1 bkground
    cells=2
#    virus=0
    #INmruby3
    label=2
    #PQBP1
    chan1=0
    #iGFP
    chan2=1
    #INmRuby3
    chan3=2
    #cGAS
    chan4=3
    label_tres = 300
    chan2_tres = label_tres
    #label_tres = 2060
    #label_tres = filters.threshold_otsu(reader[label])
    #Ag3
    #irrelevant for this one!!

    chan1_tres = 300
    #s15
    chan2_tres = 475
    chan3_tres = 190
    #cGAS
    chan4_tres = 700
    #nono
    #chan4_tres = 337
    #chan4_tres = 175


    reader = pims.bioformats.BioformatsReader(ficheiro,java_memory='1024m')
    #reader = pims.ReaderSequence(ficheiro, pims.bioformats.BioformatsReader)
    meta = reader.metadata
    nseries = meta.ImageCount()

    if plot: f, axarr = plt.subplots(2,2)

    df = pd.DataFrame()

    s=0
    #for s in range(nseries):
        #reader.series = s
        #if z>1: else
    #    reader.bundle_axes = 'zyx'

    reader.bundle_axes = 'yx'
    reader.iter_axes = 'c'

    #if z>1 then : else, nothinga
    #zproject = np.max(reader[cells], axis=0)
    #zproject = reader[cells]
    # cells_mask = cell_mask(reader[cells],np.mean(reader[cells])*0.9,15000)
    cells_masks = np.ones(reader[cells].shape)
    #cells_mask = cell_mask(zproject,np.mean(zproject),size=2000)
    #cells_mask = cell_mask(zproject,1000,size=2000)

    #if plot: axarr[0,1].imshow(cells_mask)

    #for 3D this needs a np.broadcast_to
    #make loops from metadata to be auto
    #comment for 2D
    #cm3d = np.repeat(cells_mask[np.newaxis,...],reader.frame_shape[0], axis=0)

    if plot:
        axarr[0,0].imshow(cells_mask,
                  cmap='gray')
        axarr[0,1].imshow(reader[label],vmin=np.mean(reader[label])/2,
                  vmax=np.mean(reader[label])*5,cmap='gray')
        axarr[1,0].imshow(reader[cells],vmin=np.mean(reader[cells])/2,
          vmax=np.mean(reader[cells])*10,cmap='gray')
#    pla_img = multiply(reader[PLA],cm3d)


    labels_tp, coords = make_labels_trackpy(reader[label],mass=1000,size=7,_numba=True)
    # ~ labels = np.searchsorted(np.unique(labels), labels)


    labels_tp = multiply(labels_tp,cells_mask)
    del cells_mask
    #resort indexes
    labels_tp = np.searchsorted(np.unique(labels_tp), labels_tp)


    if plot:
        axarr[1,1].imshow(reader[label],vmin=np.mean(reader[label])/2,
                  vmax=np.mean(reader[label])*5,cmap='gray')
        axarr[1,1].imshow(labels_tp,cmap='jet',alpha=0.2)
        plt.draw()
        print("Saving: "+ficheiro[:-3]+'.png')
        f.savefig(ficheiro[:-3]+'.png', dpi=600)
    #I should adapt for Z (or make the image cubic before doing this)
    # ~ spacing : iterable of floats, optional
    # ~ Spacing between voxels in each spatial dimension. If None, then the spacing between pixels/voxels in each dimension is assumed 1.

    # ~ labels_tp = make_labels_rw(label_real,minsmask,maxsmask)

    try:

        data_chan1 = othercolor(np.roll(reader[chan1],-2,axis=0),labels_tp)
        data_chan2 = othercolor(reader[chan2],labels_tp)
        data_chan3 = othercolor(reader[chan3],labels_tp)
        data_chan4 = othercolor(reader[chan4],labels_tp)
+
#        data_virus = othercolor(virus_img,labels_tp)
        # ~ data_b = othercolor(blue[i],labels_tp)
        base=os.path.basename(ficheiro)
        base = base[0:4].strip('_v').strip('_')

        #data_chan1['Series']=s
        data_chan1['Threshold']= chan1_tres
        data_chan1['Wavelength'] = meta.ChannelName(0,chan1)


        #data_chan2['Filename']=ficheiro
        #data_chan2['Series']=s
        data_chan2['Threshold']= chan2_tres
        data_chan2['Wavelength'] = meta.ChannelName(0,chan2)
        #data_chan2['PlateRow']= base

        #data_chan3['Filename']=ficheiro
        #data_chan3['Series']=s
        data_chan3['Threshold']= chan3_tres
        data_chan3['Wavelength'] = meta.ChannelName(0,chan3)
        #data_chan3['PlateRow']= base

        #data_chan4['Filename']=ficheiro
        #data_chan4['Series']=s
        data_chan4['Threshold']= chan4_tres
        data_chan4['Wavelength'] = meta.ChannelName(0,chan4)
        #data_chan4['PlateRow']= base

        #df1.merge(df2, left_on='lkey', right_on='rkey',
        #           suffixes=('_left', '_right'))
        df = df.append(pd.DataFrame.from_dict(data_chan1).add_suffix(
        ' '+str(data_chan1['Wavelength'])) )
        #, ignore_index = True)
        df = df.join(pd.DataFrame.from_dict(data_chan2).add_suffix(
        ' '+str(data_chan2['Wavelength'])))
        df = df.join(pd.DataFrame.from_dict(data_chan3).add_suffix(
        ' '+str(data_chan3['Wavelength'])))
        df = df.join(pd.DataFrame.from_dict(data_chan4).add_suffix(
        ' '+str(data_chan4['Wavelength'])))

        df['Filename']= ficheiro
        df['PlateRow']= base
        #fix this visit point thing
        df['VisitP'] = os.path.basename(ficheiro)[3:7].strip('_')

                # df = df.append(pd.DataFrame.from_dict(data_chan1), ignore_index = True)
        # df = df.append(pd.DataFrame.from_dict(data_chan2), ignore_index = True)
        # df = df.append(pd.DataFrame.from_dict(data_chan3), ignore_index = True)
        # df = df.append(pd.DataFrame.from_dict(data_chan4), ignore_index = True)
    except ValueError:
        print(ValueError, 'Something went wrong with', ficheiro)

    #check HERE! Why the counts start at 1 and not 0?

    print(len(df.index))
    return df
# =============================================================================
#         counts_chan1 = data_chan1['max'] > chan1_tres
#         chan1_nb = len(counts_chan1[counts_chan1 == True])
#
#         counts_chan2 = data_chan2['max'] > chan2_tres
#         chan2_nb = len(counts_chan2[counts_chan2 == True])
#
#     #    counts_chan3 = data_chan3['max'] > chan3_tres
#     #    chan3_nb = len(counts_chan3[counts_chan3 == True])
#
#         counts_chan4 = data_chan4['max'] > chan4_tres
#         chan4_nb = len(counts_chan4[counts_chan4 == True])
#
#         dual_12 = np.logical_and(counts_chan1,counts_chan2)
#         dual_12_nb = len(dual_12[dual_12 == True])
#
#         dual_14 = np.logical_and(counts_chan1,counts_chan4)
#         dual_14_nb = len(dual_14[dual_14 == True])
#
#         dual_24 = np.logical_and(counts_chan2,counts_chan4)
#         dual_24_nb = len(dual_24[dual_24 == True])
#
#         triple = np.logical_and(np.logical_and(dual_12,dual_14),dual_24)
#         #other one is faster
#     #    triple = np.logical_and.reduce((dual12,dual14,dual24))
#
#         triple_nb = len(triple[triple == True])
#
#         print ficheiro,'series_',s, 'chan1:',chan1_nb,'chan2', chan2_nb, 'chan4', chan4_nb,
#         'dual12:',dual_12_nb,'dual14:',dual_14_nb,'dual24:',dual_24_nb, 'triple',
#         triple_nb
#
#         #~ print data_r
#         # ~ plot = plot2d(data_gr,data_b,gr_tres,b_tres)
#         #~ plt.show()
#         # ~ plot.savefig(red._filepaths[i]+'.png')
#         #~ plot.show()
#         # ~ plot.cla()
#     #~
#         print ficheiro
#     #     yield [ficheiro,s,np.max(labels_tp), chan1_nb, chan2_nb,chan4_nb,dual_12_nb,
#     #             dual_14_nb,dual_24_nb,triple_nb,
#     # np.mean(data_chan1['mean']),np.mean(data_chan2['mean']),np.mean(data_chan4['mean']),
#     # np.mean(data_chan1['max']),np.mean(data_chan2['max']),np.mean(data_chan4['max']),
#     # np.mean(data_chan1['stdev']),np.mean(data_chan2['stdev']),np.mean(data_chan4['stdev'])
#     # ]
#         return [ficheiro,s,np.max(labels_tp), chan1_nb, chan2_nb,chan4_nb,dual_12_nb,
#                 dual_14_nb,dual_24_nb,triple_nb,
#     np.mean(data_chan1['mean']),np.mean(data_chan2['mean']),np.mean(data_chan4['mean']),
#     np.mean(data_chan1['max']),np.mean(data_chan2['max']),np.mean(data_chan4['max']),
#     np.mean(data_chan1['stdev']),np.mean(data_chan2['stdev']),np.mean(data_chan4['stdev'])
#     ]
# =============================================================================
os.getcwd()
def main():

    # files_labels = glob.glob(os.getcwd()+'/*PRJ.ome.tiff')
    files_labels = glob.glob("/run/media/jmamede/Joao/till/fixed40x/prj/*PRJ.ome.tiff")
    files_labels.sort()
    files_labels

    #faz uma cell mask que tenha de ter o nucleo dentro como mask

# =============================================================================
#     wr.writerow(['File','Series','Label_nb',
#     'chan1_nb','chan2_nb','chan4_nb','dual_12_nb',
#     'dual_14_nb','dual_24_nb','triple_nb',
#     'Mean Chan1','Mean Chan2', 'Mean_Chan4',
#     'Max Chan1','Max Chan2','Max Chan4',
#     'StDev Chan1', 'StDev Chan2', 'StDev Chan4'])
# =============================================================================
    v = c[:]
    res = v.map(crunch_data,files_labels)

    stdout0 = res.stdout

    while not res.ready():
        # check if stdout changed for any kernel
        if res.stdout != stdout0:
            for i in range(0,len(res.stdout)):
                if res.stdout[i] != stdout0[i]:
                    # print only new stdout's without previous message and remove '\n' at the end
                    print(('kernel ' + str(i) + ': ' + res.stdout[i][len(stdout0[i]):-1]))

                    # set stdout0 to last output for new comparison
                    stdout0 =  res.stdout
        else:
            continue
# =============================================================================
#     for ficheiro in files_labels:
#         wr.writerow(crunch_data(ficheiro))
# =============================================================================
    result = res.get()
    df = pd.DataFrame()
    for line in result:
        df = df.append(line, ignore_index = True)

    store = pd.HDFStore('stored_data_trackpy_segm.h5')
    store['df'] = df  # save it


if __name__ == "__main__":
    main()
