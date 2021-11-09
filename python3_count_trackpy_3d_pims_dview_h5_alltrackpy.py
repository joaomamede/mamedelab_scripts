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

# ============================================================================
# ficheiro = files_labels[1]
# ficheiro
# ============================================================================



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
    #for blobs/dots
    plot = True
    #for cell mask0 pqbp1 bkground
    cells=3
#    virus=0
    #INmruby3
    label=1
    #PQBP1
    chan1=0
    #IN
    chan2=1
    #iGFP
    chan3=2
    #Nono
    chan4=3
    label_tres = 3.25e4
    chan2_tres = label_tres
    #label_tres = 2060
    #label_tres = filters.threshold_otsu(reader[label])
    #Ag3
    #irrelevant for this one!!

    chan1_tres =  1e4
    #s15
    chan2_tres =  4e4
    chan3_tres =  1e10
    #cGAS
    chan4_tres =  5e5
    #nono
    #chan4_tres = 337
    #chan4_tres = 175

    print("Working on ", ficheiro)
    reader = pims.bioformats.BioformatsReader(ficheiro,java_memory='1024m')
    reader
    #reader = pims.ReaderSequence(ficheiro, pims.bioformats.BioformatsReader)
    meta = reader.metadata
    # nseries = meta.ImageCount()
    #the reader has a bug and makes t instead of m/v when it's a single Z file
    nseries = meta.ImageCount()

    df = pd.DataFrame()
    if plot:
        f, axarr = plt.subplots(2,2)

    s=1
    for s in range(nseries):
        print("Working on Point", s)

        # if ficheiro == '/run/media/jmamede/Joao/pqbp1/Nono/Nono2021/deco/anal/A09 - Deconvolved 100 iterations, Type Richardson-Lucy-MaxIP.nd2' and s>=7:
        #     print(s)
        #     break
        reader.series = s
        #if z>1: else
    #    reader.bundle_axes = 'zyx'

        reader.bundle_axes = 'zyx'
        reader.iter_axes = 'c'
        # reader[0].ndim
        #if z>1 then : else, nothinga
        #zproject = np.max(reader[cells], axis=0)
        #zproject = reader[cells]
        # cells_mask = cell_mask(np.max(reader[cells],axis=0),np.max(np.mean(reader[cells]),axis=0)*0.7,10000)
        # cells_masks = np.ones(reader[cells].shape)
        cell_model = cellpose_model()
        # cellpose_model(GPU=True,model_type='cyto'):



        cells_masks = cellpose_mask(np.max(reader[cells],axis=0),cell_model,size=2500,flow_threshold=0.8,diam=200,cell_prob=-2)
        # cells_masks = cellpose_mask(reader[cells],cell_model,size=2500,flow_threshold=0.8,diam=200,cell_prob=-2,_bin=False)

        # cells_masks.shape

        #cells_mask = cell_mask(zproject,np.mean(zproject),size=2000)
        #cells_mask = cell_mask(zproject,1000,size=2000)
        # plt.imshow(cells_mask)
        #if plot: axarr[0,1].imshow(cells_mask)

        #for 3D this needs a np.broadcast_to
        #make loops from metadata to be auto
        #comment for 2D
        #cm3d = np.repeat(cells_mask[np.newaxis,...],reader.frame_shape[0], axis=0)
        #
        # if plot:
        #     f, axarr = plt.subplots(2,2)
        #     # axarr[0,0].imshow(cells_mask,
        #     #           cmap='gray')
        #     axarr[0,0].imshow(reader[label],vmin=np.mean(reader[label])/2,
        #               vmax=np.mean(reader[label])*5,cmap='gray')
        #     axarr[0,1].imshow(reader[chan1],vmin=np.mean(reader[chan1])/2,
        #               vmax=np.mean(reader[chan1])*5,cmap='gray')
        #     axarr[0,2].imshow(reader[chan4],vmin=np.mean(reader[chan4])/2,
        #       vmax=np.mean(reader[chan4])*10,cmap='gray')
    #    pla_img = multiply(reader[PLA],cm3d)




        Null, coords1 = make_labels_trackpy(reader[chan1],mass=chan1_tres,size=13,_numba=True,_round=False)
        Null, coords2 = make_labels_trackpy(reader[chan2],mass=chan2_tres,size=13,_numba=True,_round=False)
        Null, coords3 = make_labels_trackpy(reader[chan3],mass=chan3_tres,size=13,_numba=True,_round=False)
        Null, coords4 = make_labels_trackpy(reader[chan4],mass=chan4_tres,size=13,_numba=True,_round=False)
        # ~ labels = np.searchsorted(np.unique(labels), labels)

        try:
            coords1 = coords1[~np.isnan(coords1).any(axis=1)]
            coords2 = coords2[~np.isnan(coords2).any(axis=1)]
            coords3 = coords3[~np.isnan(coords3).any(axis=1)]
            coords4 = coords4[~np.isnan(coords4).any(axis=1)]
        except TypeError: print("NanRemovalFailed")
        # coords3[0]
        #values_at_coords will be a list saying which one is the label.
        #if cellpose different labels = different cells
        #if mamede mean function 1«cells 0«glass
        # %matplotlib qt5
        # if plot:
        #     f, axarr = plt.subplots(2,2) # ,figsize=(30,20)
        #
        #     axarr[0,0].imshow(np.max(reader[0],axis=0))
        #     axarr[0,0].scatter(coords3[:,2],coords3[:,1],color='red')
        #     axarr[0,1].imshow(cells_masks)
        #     axarr[0,1].scatter(coords3[:,2],coords3[:,1])
        # #need to do for each color

        
        #So far this is only 2D masking
        points_in_which_mask = []
        for coords in [coords1,coords2,coords3,coords4]:
            # points_in_which_mask.append(points_in_mask(np.flip(coords[:,1:3],axis=1),cells_masks))
            points_in_which_mask.append(points_in_mask(coords[:,1:3],cells_masks))

            # points_in_which_mask[2]

        # np.flip(Insides[:,1:3],axis=1)
        # Insides - 0 is X, 1 is Y, 2 is X

        # %matplotlib qt5
        if plot:
             # ,figsize=(30,20)

            axarr[0,0].imshow(np.max(reader[2],axis=0))
            axarr[0,0].scatter(coords2[:,2],coords2[:,1],color='red')
            axarr[0,1].imshow(cells_masks)
            axarr[0,1].scatter(coords2[:,2],coords2[:,1])
            axarr[1,1].imshow(cells_masks)
            Insides = coords2[points_in_which_mask[1] >0]
            axarr[1,1].scatter(Insides[:,2],Insides[:,1])
            # axarr[1,1].scatter(coords_int[:,0],coords_int[:,1])
            plt.draw()
            print("Saving: "+ficheiro[:-3]+str(s)+'.png')
            f.savefig(ficheiro[:-3]+'_'+str(s)+'.png', dpi=600)
            plt.clf()

        # labels_tp = multiply(labels_tp,cells_mask)
        # chan1_tp = multiply(chan1_tp,cells_mask)
        # chan3_tp = multiply(chan3_tp,cells_mask)
        # chan4_tp = multiply(chan4_tp,cells_mask)
        # del cells_mask
        #resort indexes

        # labels_tp = np.searchsorted(np.unique(labels_tp), labels_tp)
        # chan1_tp = np.searchsorted(np.unique(chan1_tp), chan1_tp)
        # chan3_tp = np.searchsorted(np.unique(chan3_tp), chan3_tp)
        # chan4_tp = np.searchsorted(np.unique(chan4_tp), chan4_tp)
        # print(coords)

        # if plot:
        #     axarr[1,0].imshow(reader[label],vmin=np.mean(reader[label])/2,
        #               vmax=np.mean(reader[label])*5,cmap='gray')
        #     axarr[1,0].scatter(coords[:,1],coords[:,0],marker='.', facecolors='none', color='r')
        #     axarr[1,1].imshow(reader[chan1],vmin=np.mean(reader[chan1])/2,
        #               vmax=np.mean(reader[chan1])*5,cmap='gray')
        #     axarr[1,1].scatter(coords1[:,1],coords1[:,0],marker='.', facecolors='none', color='b')
        #     axarr[1,2].imshow(reader[chan4],vmin=np.mean(reader[chan4])/2,
        #               vmax=np.mean(reader[chan1])*5,cmap='gray')
        #     axarr[1,2].scatter(coords4[:,1],coords4[:,0],marker='.', facecolors='none', color='g')
            # axarr[1,0].imshow(labels_tp,cmap='jet',alpha=0.2)

        #I should adapt for Z (or make the image cubic before doing this)
        # ~ spacing : iterable of floats, optional
        # ~ Spacing between voxels in each spatial dimension. If None, then the spacing between pixels/voxels in each dimension is assumed 1.

        # ~ labels_tp = make_labels_rw(label_real,minsmask,maxsmask)

        try:
            #rolling if needed
            # data_chan1 = othercolor(np.roll(reader[chan1],-2,axis=0),labels_tp)
            # data_chan1 = othercolor(reader[chan1],chan1_tp)
            # data_chan2 = othercolor(reader[label],labels_tp)
            # data_chan3 = othercolor(reader[chan3],chan3_tp)
            # data_chan4 = othercolor(reader[chan4],chan4_tp)

    #        data_virus = othercolor(virus_img,labels_tp)
            # ~ data_b = othercolor(blue[i],labels_tp)
            base=os.path.basename(ficheiro)
            base =  base.split('_')[1]
            # coords1.shape

            data_chan1 = pd.DataFrame()

            #fix this visit point thing
            # df['VisitP'] = str(s)
            # data_chan1['Filename']=ficheiro
            # data_chan1['PlateRow']= base
            # data_chan1['VisitP']=s
            try:
                data_chan1['x'] = coords1[:,2]
                data_chan1['y'] = coords1[:,1]
                data_chan1['z'] = coords1[:,0]
                data_chan1['Threshold']= chan1_tres
                data_chan1['Wavelength'] = meta.ChannelName(0,chan1)
                data_chan1['CellID'] =  points_in_which_mask[0]
            except: 'Wrong at:',ficheiro, ' Data1'
            # data_chan1['PlateRow']= base


            data_chan2 = pd.DataFrame()
            # data_chan2['Filename']=ficheiro
            # data_chan2['VisitP']=s
            # data_chan2['PlateRow']= base
            try:
                data_chan2['x'] = coords2[:,2]
                data_chan2['y'] = coords2[:,1]
                data_chan2['z'] = coords2[:,0]
                data_chan2['Threshold']= chan2_tres
                data_chan2['Wavelength'] = meta.ChannelName(0,chan2)
                data_chan2['CellID'] =  points_in_which_mask[1]
            except: 'Wrong at:',ficheiro,' Data2'
            # data_chan2['PlateRow']= base


            data_chan3 = pd.DataFrame()
            # data_chan3['Filename']=ficheiro
            # data_chan3['VisitP']=s
            # data_chan3['PlateRow']= base
            try:
                data_chan3['x'] = coords3[:,2]
                data_chan3['y'] = coords3[:,1]
                data_chan3['z'] = coords3[:,0]
                data_chan3['Threshold']= chan3_tres
                data_chan3['Wavelength'] = meta.ChannelName(0,chan3)
                data_chan3['CellID'] =  points_in_which_mask[2]
            except: 'Wrong at:',ficheiro,' Data3'
            # data_chan3['PlateRow']= base


            data_chan4 = pd.DataFrame()
            # data_chan4['Filename']=ficheiro
            # data_chan4['Series']=s
            # data_chan4['Filename']=ficheiro
            # data_chan4['VisitP']=s
            # data_chan4['PlateRow']= base
            try:
                data_chan4['x'] = coords4[:,2]
                data_chan4['y'] = coords4[:,1]
                data_chan4['z'] = coords4[:,0]
                data_chan4['Threshold']= chan4_tres
                # data_chan4['PlateRow']= base
                data_chan4['Wavelength'] = meta.ChannelName(0,chan4)
                data_chan4['CellID'] =  points_in_which_mask[3]
            except: 'Wrong at:',ficheiro,' Data4'
            # data_chan4
            #df1.merge(df2, left_on='lkey', right_on='rkey',
            #           suffixes=('_left', '_right'))

            # data_chan1 = pd.DataFrame.from_dict(data_chan1).add_suffix(
            # ' '+str(data_chan1['Wavelength']))
            # #, ignore_index = True)
            # data_chan2 = pd.DataFrame.from_dict(data_chan2).add_suffix(
            # ' '+str(data_chan2['Wavelength']))
            # data_chan3 = pd.DataFrame.from_dict(data_chan3).add_suffix(
            # ' '+str(data_chan3['Wavelength']))
            # data_chan4 = pd.DataFrame.from_dict(data_chan4).add_suffix(
            # ' '+str(data_chan4['Wavelength']))
            # data_chan1 = df.append(pd.DataFrame.from_dict(data_chan1).add_suffix(
            # ' '+str(data_chan1['Wavelength'])) )
            # #, ignore_index = True)
            # data_chan2 = df.join(pd.DataFrame.from_dict(data_chan2).add_suffix(
            # ' '+str(data_chan2['Wavelength'])))
            # data_chan3 = df.join(pd.DataFrame.from_dict(data_chan3).add_suffix(
            # ' '+str(data_chan3['Wavelength'])))
            # data_chan4 = df.join(pd.DataFrame.from_dict(data_chan4).add_suffix(
            # ' '+str(data_chan4['Wavelength'])))
            df_series = pd.DataFrame()
            # df['Filename']= ficheiro
            # df['PlateRow']= base
            # #fix this visit point thing
            # df['VisitP'] = str(s)

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

    print(len(df.index))
    return df

os.getcwd()
def main():

    # files_labels = glob.glob(os.getcwd()+'/*PRJ.ome.tiff')
    files_labels = glob.glob("/run/media/jmamede/Joao/pqbp1/Nono/Nono2021/PlateJuly2021/Plate3/*.nd2")
    # files_labels = glob.glob("./*.nd2")
    files_labels.sort()
    files_labels

    # files_labels.pop)

    # ficheiro = files_labels[16]
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

    for i in range(len(result)):
        result[i].to_csv('Nono'+str(i)+'.csv')


    for line in result:
        df = df.append(line, ignore_index = True)

    store = pd.HDFStore('stored_data_trackpy_forNN2.h5')
    store['df'] = df  # save it


if __name__ == "__main__":
    main()
