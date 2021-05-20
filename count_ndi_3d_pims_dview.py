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

# =============================================================================
# myfile = open('count_ndi_mask_max.csv', 'wb')
# wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#
# =============================================================================


def crunch_data(ficheiro):
    import os
    from skimage import filters
    import pims
    import sys
    import numpy as np
    sys.path.insert(0,'/home/jmamede/scripts')
    from support_pla import *
    import pandas as pd
    #for blobs/dots
    plot = False
    minsmask=4
    maxsmask=100
    #for cell mask
    cells=3
#    virus=0
    label=2
    #tag
    chan1=0
    #IN
    chan2=1
    #GFP
    chan3=2
    #cGAS
    chan4=3
    label_tres = 275
    chan3_tres = label_tres
    #label_tres = 2060
    #label_tres = filters.threshold_otsu(reader[label])
    #pqbp1
    chan1_tres = 100
    #s15
    chan2_tres = 150
    #cGAS
    chan4_tres = 589
    #nono
    # chan4_tres = 337
    #chan4_tres = 175


    reader = pims.bioformats.BioformatsReader(ficheiro,java_memory='1024m')
    #reader = pims.ReaderSequence(ficheiro, pims.bioformats.BioformatsReader)
    meta = reader.metadata
    nseries = meta.ImageCount()
    plot = True
    if plot: f, axarr = plt.subplots(2,2)

    df = pd.DataFrame()

    # s=0
    for s in range(nseries):
        reader.series = s
        #if z>1: else
       #reader.bundle_axes = 'zyx'

        reader.bundle_axes = 'yx'
        reader.iter_axes = 'c'

        #if z>1 then : else, nothing
        #zproject = np.max(reader[cells], axis=0)
        #zproject = reader[cells]
    #    cells_mask = cell_mask(reader[cells],np.mean(reader[cells]),8000)
        #cells_mask = cell_mask(zproject,np.mean(zproject),size=100)

        #if plot: axarr[0,1].imshow(cells_mask)

        #for 3D this needs a np.broadcast_to
        #make loops from metadata to be auto
        #comment for 2D
        #cm3d = np.repeat(cells_mask[np.newaxis,...],reader.frame_shape[0], axis=0)
        #cm3d = cells_mask
        #label_img = reader[label]
        #label_img = np.roll(label_img,-2, axis=1)
        #label_img = np.roll(label_img,2, axis=0)
        #chan3_img = reader[chan3]
        #chan3_img = np.roll(chan3_img,-2, axis=1)
        #chan3_img = np.roll(chan3_img,2, axis=0)

        cm3d = np.ones(reader[label].shape)
        label_img = multiply(reader[label],cm3d)
        chan1_img = multiply(reader[chan1],cm3d)
        chan2_img = multiply(reader[chan2],cm3d)
        chan3_img = multiply(reader[chan3],cm3d)
        chan4_img = multiply(reader[chan4],cm3d)

        if plot: axarr[0,0].imshow(label_img,vmin=np.mean(label_img),
                      vmax=500,cmap='gray')
    #    pla_img = multiply(reader[PLA],cm3d)

        #for 2D, no
    #    label_img = multiply(reader[label],cells_mask)
    #    virus_img = multiply(reader[virus],cells_mask)
    #    pla_img = multiply(reader[PLA],cells_mask)

        #comment out for median filter prior to analysis
        #~ filtdat = ndi.median_filter(files_labels[i], size=(4,4))
        #comment out for manual

    #    otsu = filters.threshold_otsu(zproject)
    #    chan1_tres = filters.threshold_otsu(reader[chan1])
    #    chan2_tres = filters.threshold_otsu(reader[chan2])
    ##    chan3_tres = filters.threshold_otsu(reader[chan3])
    #    chan4_tres = filters.threshold_otsu(reader[chan4])
    #    label_tres = filters.threshold_otsu(reader[label])

        label_real = (label_img > label_tres)

        #no watershed or random walker
        # ~ labels_ws = make_labels(label_real,minsmask,maxsmask)
        #watershed labeling
        labels_ws = make_labels_ws(label_real,minsmask,maxsmask)

        #random walker labeling
        if plot:
            axarr[1,1].imshow(labels_ws)
            plt.draw()

            f.savefig('/tmp/'+ficheiro[-3]+'s'+str(s)+'.png')
        #I should adapt for Z (or make the image cubic before doing this)
        # ~ spacing : iterable of floats, optional
        # ~ Spacing between voxels in each spatial dimension. If None, then the spacing between pixels/voxels in each dimension is assumed 1.

        # ~ labels_ws = make_labels_rw(label_real,minsmask,maxsmask)

        try:

            data_chan1 = othercolor(chan1_img,labels_ws)
            data_chan2 = othercolor(chan2_img,labels_ws)
            data_chan3 = othercolor(chan3_img,labels_ws)
            data_chan4 = othercolor(chan4_img,labels_ws)

    #        data_virus = othercolor(virus_img,labels_ws)
            # ~ data_b = othercolor(blue[i],labels_ws)
            base=os.path.basename(ficheiro)

            all_data = {}

            all_data['max_chan1'] = data_chan1['max']
            all_data['stdev_chan1'] = data_chan1['stdev']
            all_data['median_chan1'] = data_chan1['median']
            all_data['mean_chan1'] = data_chan1['mean']
            all_data['wavelength1'] = int(meta.ChannelEmissionWavelength(0,chan1))

            all_data['max_chan2'] = data_chan2['max']
            all_data['stdev_chan2'] = data_chan2['stdev']
            all_data['median_chan2'] = data_chan2['median']
            all_data['mean_chan2'] = data_chan2['mean']
            all_data['wavelength2'] = int(meta.ChannelEmissionWavelength(0,chan2))


            all_data['max_chan3'] = data_chan3['max']
            all_data['stdev_chan3'] = data_chan3['stdev']
            all_data['median_chan3'] = data_chan3['median']
            all_data['mean_chan3'] = data_chan3['mean']
            all_data['wavelength3'] = int(meta.ChannelEmissionWavelength(0,chan3))

            all_data['max_chan4'] = data_chan3['max']
            all_data['stdev_chan4'] = data_chan3['stdev']
            all_data['median_chan4'] = data_chan3['median']
            all_data['mean_chan4'] = data_chan3['mean']
            all_data['wavelength4'] = int(meta.ChannelEmissionWavelength(0,chan4))

            all_data['filename'] = ficheiro
            all_data['series']= s
            all_data['thresholdlabel']= label_tres
            all_data['threshold1'] = chan1_tres
            all_data['threshold2'] = chan2_tres
            all_data['threshold3'] = chan3_tres
            all_data['labelchannel'] = int(meta.ChannelEmissionWavelength(0,label))

            #base = base[:1]
            # data_chan1['Filename']=ficheiro
            # data_chan1['Series']=s
            # data_chan1['Threshold']=label_tres
            # data_chan1['Wavelength'] = int(meta.ChannelEmissionWavelength(0,chan1))
            # #data_chan1['DNAug']= base
            #
            # data_chan2['Filename']=ficheiro
            # data_chan2['Series']=s
            # data_chan2['Threshold']=label_tres
            # data_chan2['Wavelength'] = int(meta.ChannelEmissionWavelength(0,chan2))
            # #data_chan2['DNAug']= base
            #
            # data_chan3['Filename']=ficheiro
            # data_chan3['Series']=s
            # data_chan3['Threshold']=label_tres
            # data_chan3['Wavelength'] = int(meta.ChannelEmissionWavelength(0,chan3))
            #data_chan3['DNAug']= base

            #data_chan4['Filename']=ficheiro
            #data_chan4['Series']=s
            #data_chan1['Threshold']=label_tres
            #data_chan4['Wavelength'] = int(meta.ChannelEmissionWavelength(0,chan4))

            df = df.append(pd.DataFrame.from_dict(all_data),ignore_index = True)
            # df = df.append(pd.DataFrame.from_dict(data_chan2), ignore_index = True)
            # df = df.append(pd.DataFrame.from_dict(data_chan3), ignore_index = True)
            #df = df.append(pd.DataFrame.from_dict(data_chan4), ignore_index = True)
        except ValueError:
            print ValueError, 'Something went wrong with', ficheiro

        #check HERE! Why the counts start at 1 and not 0?

    print len(df.index)
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
#     #     yield [ficheiro,s,np.max(labels_ws), chan1_nb, chan2_nb,chan4_nb,dual_12_nb,
#     #             dual_14_nb,dual_24_nb,triple_nb,
#     # np.mean(data_chan1['mean']),np.mean(data_chan2['mean']),np.mean(data_chan4['mean']),
#     # np.mean(data_chan1['max']),np.mean(data_chan2['max']),np.mean(data_chan4['max']),
#     # np.mean(data_chan1['stdev']),np.mean(data_chan2['stdev']),np.mean(data_chan4['stdev'])
#     # ]
#         return [ficheiro,s,np.max(labels_ws), chan1_nb, chan2_nb,chan4_nb,dual_12_nb,
#                 dual_14_nb,dual_24_nb,triple_nb,
#     np.mean(data_chan1['mean']),np.mean(data_chan2['mean']),np.mean(data_chan4['mean']),
#     np.mean(data_chan1['max']),np.mean(data_chan2['max']),np.mean(data_chan4['max']),
#     np.mean(data_chan1['stdev']),np.mean(data_chan2['stdev']),np.mean(data_chan4['stdev'])
#     ]
# =============================================================================

def main():

    files_labels = glob.glob(os.getcwd()+'/*PRJ.dv')
    files_labels.sort()


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
                    print('kernel ' + str(i) + ': ' + res.stdout[i][len(stdout0[i]):-1])

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
        df = df.append(line)

    store = pd.HDFStore('stored_data_THP1.h5')
    store['df'] = df  # save it


if __name__ == "__main__":
    main()
