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
plot = True

def crunch_data(ficheiro):
    import os
    import matplotlib.pyplot as plt
    from skimage import filters
    import pims
    import sys
    import numpy as np
    sys.path.insert(0,'/home/jmamede/scripts')
    from support_pla import othercolor, cell_mask, multiply, points_in_mask
    from support_pla import make_labels_trackpy,cellpose_mask,cellpose_model
    import pandas as pd
    import scipy.ndimage as ndi
    #for blobs/dots
    plot = True
    #for cell mask0 pqbp1 bkground
    cells=3
#    virus=0
    #INmruby3
    label=1
    #PQBP1
    chan1=0
    #iGFP
    chan2=1
    #INmRuby3
    chan3=2
    #cGAS
    chan4=3
    label_tres = 3.25e4
    chan2_tres = label_tres
    #label_tres = 2060
    #label_tres = filters.threshold_otsu(reader[label])
    #Ag3
    #irrelevant for this one!!

    chan1_tres =  5e4
    #s15
    chan2_tres =  2e5
    chan3_tres =  3.5e5
    #cGAS
    chan4_tres =  5e20
    #nono
    #chan4_tres = 337
    #chan4_tres = 175


    reader = pims.bioformats.BioformatsReader(ficheiro,java_memory='1024m')
    #reader = pims.ReaderSequence(ficheiro, pims.bioformats.BioformatsReader)
    meta = reader.metadata
    nseries = meta.ImageCount()

    if plot: f, axarr = plt.subplots(2,2)

    df = pd.DataFrame()

    # s=0
    for s in range(nseries):
        reader.series = s
        #if z>1: else
        #    reader.bundle_axes = 'zyx'

        reader.bundle_axes = 'zyx'
        reader.iter_axes = 'c'

        #if z>1 then : else, nothing
        #zproject = np.max(reader[cells], axis=0)
        #zproject = reader[cells]

        #cells_mask = cell_mask(zproject,np.mean(zproject),size=2000)
        #cells_mask = cell_mask(zproject,1000,size=2000)



        # ~ cells_mask = cell_mask(reader[cells],np.mean(reader[cells])*0.85,15000)
        cell_model = cellpose_model()
        # cellpose_model(GPU=True,model_type='cyto'):



        cells_masks = cellpose_mask(np.max(reader[cells],axis=0),cell_model,size=2500,flow_threshold=0.8,diam=200,cell_prob=-2)
        # cells_masks = cellpose_mask(reader[cells],cell_model,size=2500,flow_threshold=0.8,diam=200,cell_prob=-2,_bin=False)

        # ~ cells_mask = np.ones(reader[cells].shape)
        #if plot: axarr[0,1].imshow(cells_mask)
        #don't need to mask because outside of cells is 0 and does not contribute to sum
        areas = ndi.sum(np.ones(cells_masks.shape), cells_masks, np.arange(cells_masks.max()+1))

        chan1_sum  = ndi.sum(reader[chan1], cells_masks, np.arange(cells_masks.max()+1))
        chan2_sum  = ndi.sum(reader[chan2], cells_masks, np.arange(cells_masks.max()+1))
        chan3_sum  = ndi.sum(reader[chan3], cells_masks, np.arange(cells_masks.max()+1))
        chan4_sum  = ndi.sum(reader[chan4], cells_masks, np.arange(cells_masks.max()+1))

        chan1_max  = ndi.maximum(reader[chan1], cells_masks, np.arange(cells_masks.max()+1))
        chan2_max  = ndi.maximum(reader[chan2], cells_masks, np.arange(cells_masks.max()+1))
        chan3_max  = ndi.maximum(reader[chan3], cells_masks, np.arange(cells_masks.max()+1))
        chan4_max  = ndi.maximum(reader[chan4], cells_masks, np.arange(cells_masks.max()+1))

        # ~ PQBP1sum = ndi.sum(rebin(reader[chan1],(1022,1024)), cells_masks, np.arange(cells_masks.max()+1))
        chan1_mean = chan1_sum/areas
        chan2_mean = chan2_sum/areas
        chan3_mean = chan3_sum/areas
        chan4_mean = chan4_sum/areas
        # ~ PQBP1mean = PQBP1sum/areas
        #+1??
        cells_idx = np.arange(1,cells_masks.max()+2)
        #for 3D this needs a np.broadcast_to
        #make loops from metadata to be auto
        #comment for 2D
        #cm3d = np.repeat(cells_mask[np.newaxis,...],reader.frame_shape[0], axis=0)

        if plot:
            # f, axarr = plt.subplots(2,2) # ,figsize=(30,20)
            img_to_show = np.max(reader[cells],axis=0)
            axarr[0,0].imshow(img_to_show)
            # axarr[0,0].scatter(coords3[:,2],coords3[:,1],color='red')
            axarr[0,1].imshow(cells_masks)
            # axarr[0,1].scatter(coords3[:,2],coords3[:,1])
            axarr[1,1].imshow(cells_masks)
            # Insides = coords3[points_in_which_mask[2] >0]
            axarr[0,1].imshow(img_to_show,vmin=np.mean(img_to_show)/2,
                vmax=np.mean(img_to_show)*5,cmap='gray')
            axarr[1,0].imshow(img_to_show,vmin=np.mean(img_to_show)/2,
                          vmax=np.mean(img_to_show)*10,cmap='gray')
    #    pla_img = multiply(reader[PLA],cm3d)


        # ~ labels_tp, coords = make_labels_trackpy(reader[label],mass=175,size=7,_numba=True)
        # ~ labels = np.searchsorted(np.unique(labels), labels)


        # ~ labels_tp = multiply(labels_tp,cells_mask)
        # ~ del cells_mask
        #resort indexes
        # ~ labels_tp = np.searchsorted(np.unique(labels_tp), labels_tp)


        if plot:
            # axarr[1,1].imshow(labels_tp)
            plt.draw()
            print("Saving: "+ficheiro[:-3]+'.png')
            f.savefig(ficheiro[:-3]+'cells.png', dpi=600)
        #I should adapt for Z (or make the image cubic before doing this)
        # ~ spacing : iterable of floats, optional
        # ~ Spacing between voxels in each spatial dimension. If None, then the spacing between pixels/voxels in each dimension is assumed 1.

        # ~ labels_tp = make_labels_rw(label_real,minsmask,maxsmask)

        try:

            # ~ data_chan1 = othercolor(reader[chan1],labels_tp)
            # ~ data_chan2 = othercolor(reader[chan2],labels_tp)
            # ~ data_chan3 = othercolor(reader[chan3],labels_tp)
            # ~ data_chan4 = othercolor(reader[chan4],labels_tp)

    #        data_virus = othercolor(virus_img,labels_tp)
            # ~ data_b = othercolor(blue[i],labels_tp)
            base=os.path.basename(ficheiro)
            base =  base.split('_')[1]
            # listcells = pd.DataFrame()

            data_chan1 = pd.DataFrame()

            try:

                data_chan1['Id'] = cells_idx
                data_chan1['Sum'] = chan1_sum
                data_chan1['Mean'] = chan1_mean
                data_chan1['Max'] = chan1_max
                data_chan1['Wavelength'] = meta.ChannelName(0,chan1)
            except: 'Wrong at:',ficheiro, ' Data1'

            data_chan2 = pd.DataFrame()

            try:
                data_chan2['Id'] = cells_idx
                data_chan2['Sum'] = chan2_sum
                data_chan2['Mean'] = chan2_mean
                data_chan2['Max'] = chan2_max
                data_chan2['Wavelength'] = meta.ChannelName(0,chan2)
            except: 'Wrong at:',ficheiro, ' Data1'

            data_chan3 = pd.DataFrame()
            try:
                data_chan3['Id'] = cells_idx
                data_chan3['Sum'] = chan3_sum
                data_chan3['Mean'] = chan3_mean
                data_chan3['Max'] = chan3_max
                data_chan3['Wavelength'] = meta.ChannelName(0,chan3)
            except: 'Wrong at:',ficheiro, ' Data1'

            data_chan4 = pd.DataFrame()
            try:
                data_chan4['Id'] = cells_idx
                data_chan4['Sum'] = chan4_sum
                data_chan4['Mean'] = chan4_mean
                data_chan4['Max'] = chan4_max
                data_chan4['Wavelength'] = meta.ChannelName(0,chan4)
            except: 'Wrong at:',ficheiro, ' Data1'

            df_series = pd.DataFrame()


            df_series = df_series.append(pd.DataFrame.from_dict(data_chan1), ignore_index = True)
            df_series = df_series.append(pd.DataFrame.from_dict(data_chan2), ignore_index = True)
            df_series = df_series.append(pd.DataFrame.from_dict(data_chan3), ignore_index = True)
            df_series = df_series.append(pd.DataFrame.from_dict(data_chan4), ignore_index = True)

            df_series['PlateRow']= base
            df_series['Filename']= ficheiro
            # #fix this visit point thing
            df_series['VisitP'] = str(s)

            df = df.append(df_series, ignore_index = True)



        except ValueError:
            print(ValueError, 'Something went wrong with', ficheiro)

        #check HERE! Why the counts start at 1 and not 0?

        # ~ print(len(df.index))
    return df

# =============================================================================

def main():

    files_labels = glob.glob("/run/media/jmamede/Joao/pqbp1/Nono/Nono2021/PlateJuly2021/Plate2/*.nd2")
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

    store = pd.HDFStore('stored_data_Cells_idx.h5')
    store['df'] = df  # save it


if __name__ == "__main__":
    main()
