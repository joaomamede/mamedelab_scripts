import scipy.ndimage as ndi
#import cv2
import numpy as np
#import matplotlib.pyplot as plt
#import pims
#import libtiff
#import time
#import csv
_8bit = float(2**8-1)
_16bit = float(2**16-1)
ratio = _8bit /_16bit

def points_in_mask(coords,mask):
    import numpy as np
    # coords_int = np.round(coords).astype(int)  # or np.floor, depends
    coords_int = np.floor(coords).astype(int)  # or np.floor, depends
    try:
        values_at_coords = mask[tuple(coords_int.T)]
    except: values_at_coords = []
    # .astype(np.int)
    # values_at_coords = mask[tuple(coords_int)].astype(np.int)
    print(values_at_coords)
    return values_at_coords


def multiply(real_events, image):
    import numpy as np
    image = real_events*image
    return image

def make_labels_ws(image,min_vol,max_vol):
    from skimage.morphology import watershed
    from skimage.feature import peak_local_max

    distance = ndi.distance_transform_edt(image)
        #if image3D, else:
    if image.ndim == 2:
        sizestruct = (3,3)
    elif image.ndim == 3:
        sizestruct = (2, 5, 5)
    local_maxi = peak_local_max(distance, indices=False,
                                footprint=np.ones(sizestruct),
                                #footprint=np.ones((2,5,5)),
                                labels=image)
    markers = ndi.label(local_maxi)[0]
#    markers = measure.label(local_maxi)
    labels = watershed(-distance, markers, mask=image)

    if min_vol> 0:
        areas = ndi.sum(image, labels, np.arange(labels.max()+1))
        mask = np.logical_and(areas < max_vol , areas > min_vol)
        remove = mask[labels]
        labels[~remove] = 0
        labels = np.searchsorted(np.unique(labels), labels)

    return labels
def make_labels(image,min_vol,max_vol):
    import scipy.ndimage as ndi
    import numpy as np
    #~ image_op = ndi.binary_opening(sand, iterations=2)
    labels, nb = ndi.label(image)
    areas = ndi.sum(image, labels, np.arange(labels.max()+1))

    #~ mask = areas < max_vol
    mask = np.logical_and(areas < max_vol , areas > min_vol)
    remove = mask[labels]#.ravel()].reshape(labels.shape)
    #- is needed because I'm asking for what to keep not what to remove
    labels[~remove] = 0
    labels = np.searchsorted(np.unique(labels), labels)
    #~ plt.imshow(labels)
    #~ plt.show()
    return labels


def make_labels_trackpy(image,mass,size=9,_separation=3,_numba=True,max_mass=0,_round=True):
    import trackpy as tp
    import scipy.ndimage as ndi
    from scipy.ndimage.morphology import binary_dilation

    if image.ndim == 2:
        _size = size
    elif image.ndim == 3:
        _size = (3, size, size)
        # _size = (9, size, size)
     # ~ dotrack(ficheiro, plotgraph=True,_numba=True,massa=1500,tamanho=13,dist=250,memoria=1,stub=3,frame=19,colourIDX=0):
    if image.ndim == 2:
        if _numba:
            f = tp.locate(image,diameter=size,separation=_separation,minmass=mass,engine='numba')
        else:
            f = tp.locate(image,diameter=size,separation=_separation, minmass=mass)
    elif image.ndim == 3:
        if _numba:
            f = tp.locate(image,diameter=_size,separation = (3, 3, 3),
                minmass=mass,engine='numba')
        else:
            f = tp.locate(image,diameter=_size,separation = (3, 3, 3),
                minmass=mass)
            # size = (11, 13, 13)

    if max_mass > 0:
        f = f[f['mass'] <= max_mass]
    #outputsomehow is 3D, we want 2
    if image.ndim == 2:
        coords = np.dstack((round(f.y),round(f.x)))[0].astype(int)
    elif image.ndim == 3:
        coords = np.dstack((round(f.z),round(f.y),round(f.x)))[0].astype(int)



    #this is super slow
    # ~ masks = tp.masks.mask_image(coords,np.ones(image.shape),size/2)

    #This is faster
    if image.ndim == 2:
        r = (size-1)/2 # Radius of circles
        #make 3D compat
        disk_mask = tp.masks.binary_mask(r,image.ndim)
        # Initialize output array and set the maskcenters as 1s
        out = np.zeros(image.shape,dtype=bool)
        #check if there's a problem with subpixel masking
        out[coords[:,0],coords[:,1]] = 1
        # Use binary dilation to get the desired output
        out = binary_dilation(out,disk_mask)
        labels, nb = ndi.label(out)

        if _round:
            return labels, coords
        else:
            if image.ndim == 2:
                coords = np.dstack((f.y,f.x))[0]
                return labels, coords
    elif image.ndim == 3:
            coords = np.dstack((f.z,f.y,f.x))[0]
            return None, coords



def make_labels_trackpy_links(image,j,size=5):
    import trackpy as tp
    import scipy.ndimage as ndi
    from scipy.ndimage.morphology import binary_dilation


    #outputsomehow is 3D, we want 2
    coords = np.dstack((round(j.y),round(j.x)))[0].astype(int)

    #this is super slow
    # ~ masks = tp.masks.mask_image(coords,np.ones(image.shape),size/2)

    #This is faster
    r = (size-1)/2 # Radius of circles
    #make 3D compat
    disk_mask = tp.masks.binary_mask(r,image.ndim)
    # Initialize output array and set the maskcenters as 1s
    out = np.zeros(image.shape,dtype=bool)
    #check if there's a problem with subpixel masking
    out[coords[:,0],coords[:,1]] = 1
    # Use binary dilation to get the desired output
    out = binary_dilation(out,disk_mask)


    labels, nb = ndi.label(out)

    return labels, coords

def make_labels_rw(image,min_vol,max_vol):
    from skimage.feature import peak_local_max
    from skimage.segmentation import random_walker

    distance = ndi.distance_transform_edt(image)
    #if image3D, else:
    local_maxi = peak_local_max(distance, indices=False,
                                footprint=np.ones((3,3)),
                                #footprint=np.ones((2,5,5)),
                                labels=image)
    markers = ndi.label(local_maxi)[0]
#    markers = measure.label(local_maxi)
    markers[~image] = -1
    labels = random_walker(image, markers)

    if min_vol> 0:
        areas = ndi.sum(image, labels, np.arange(labels.max()+1))
        mask = np.logical_and(areas < max_vol , areas > min_vol)
        remove = mask[labels]
        labels[~remove] = 0
        labels = np.searchsorted(np.unique(labels), labels)

    return labels
# ~ def make_labels_rw(image):
    # ~ distance = ndi.distance_transform_edt(image)
    # ~ local_maxi = peak_local_max(distance, indices=False,
    # ~ footprint=np.ones((3,3)),labels=image)
    #markers = skimage.morphology.label(local_maxi)
    # ~ markers = measure.label(local_maxi)
    # ~ labels = skimage.segmentation.random_walker(-distance, markers)

    # ~ return labels

def simple_labels(image):
    labels, nb = ndi.label(image)
    return labels




def mean_calc(values,value_max):
    import numpy as np
    #Only the ones above threshold will be averaged don't worry about
    #the b>value_max because the threshold is the same.
    a = np.asarray([value['MeanIntensity'] for value in values])
    b = np.asarray([value['MaxIntensity'] for value in values])
    return np.mean(a[b > value_max])

def mean_calc_total(values):
    import numpy as np
    return np.mean([value['MeanIntensity'] for value in values])

def max_calc_total(values):
    import numpy as np
    return np.mean([value['MaxIntensity'] for value in values])

def listify(data,datatype):
    if datatype == 'max': datatype = 'MaxIntensity'
    elif datatype == 'mean': datatype = 'MeanIntensity'
    return np.asarray([value[datatype] for value in data])

def rebin(arr, new_shape):
    from PIL import Image
    return np.array(Image.fromarray(arr).resize(new_shape,resample=Image.NEAREST))

def cellpose_model(GPU=True,model_type='cyto'):
    from cellpose import models
    return models.Cellpose(gpu=GPU, model_type=model_type)

def cellpose_mask(image,model,flow_threshold=0.4,size=0,diam=200,cell_prob=0,model_type='cyto',GPU=True,_bin=True):
    '''diameter = None For auto!!
    #higher flow tres means more cells
    #cell_prob_threshole lower means more cells
    #cellpose defaults are diameter=30.0, do_3D=False,, flow_thres = 0.4 min_size=15 stitch threshold 0.0
    #cell_prob_threhole= 0
    #
    #add *kargs here please! if means I could pass anything to cellpose'''
    from cellpose import models

    def rebin(arr, new_shape):
        from PIL import Image
        return np.array(Image.fromarray(arr).resize(new_shape,resample=Image.NEAREST))


    def size_removal(image,size):
        from skimage import morphology
        import numpy as np

        return morphology.remove_small_objects(image,size)


    # DEFINE CELLPOSE MODEL
    # model_type='cyto' or model_type='nuclei'
    newsize = (int(image.shape[1]/2),int(image.shape[0]/2))

    if _bin:
    #if image.ndim[0] > 1022 and image.ndim[1] > 1024:
        img = rebin(np.asarray(image),newsize)
    else:
        img = np.asarray(image)

    # print(img.shape)
    # if diameter is set to None, the size of the cells is estimated on a per image basis
    # you can set the average cell `diameter` in pixels yourself (recommended)
    # diameter can be a list or a single number for all images
    # cellprob_threshold=-8
    channels = [0,0]
    masks, flows, styles, diams = model.eval(img, diameter=diam, channels=channels,flow_threshold=flow_threshold,cellprob_threshold=cell_prob)

    if size != 0:
        masks = size_removal(masks,size)
    if _bin:  masks = rebin(np.asarray(masks),image.shape)
    return masks



def cell_mask(image,treshold,size=0):
    import scipy.ndimage as ndi
    import numpy as np

    def size_removal(image,size):
        from skimage import morphology
        #import scipy.ndimage as ndi
        import numpy as np


        #older version
        # ~ labels, nb = ndi.label(image)
        #areas = ndi.sum(np.ones(image.shape), image, np.arange(image.max()+1))
        #mask = areas < size
        # ~ mask = np.logical_and(areas < max_vol , areas > min_vol)
        #remove = mask[image]#.ravel()].reshape(labels.shape)

        #this time is remove the ones we do not want
        #image[remove] = 0

        # ~ labels[~remove] = 1
        #image = np.searchsorted(np.unique(image), image)
        return morphology.remove_small_objects(image,size)

    cell = image > treshold
    cell = ndi.median_filter(cell,8)

    #DV!
    if image.ndim == 2:
        sizestruct = (13,13)
    elif image.ndim == 3:
        sizestruct = (3, 13, 13)
    cell = ndi.binary_opening(cell,
    structure=np.ones(sizestruct))
    cell = ndi.binary_closing(cell,iterations=13)


    #Maite!
#    cell = ndi.binary_opening(cell,
#    structure=np.ones((15,15)))
#    cell = ndi.binary_closing(cell,iterations=5)
    #this is pretty much the size, ill dilate for nearby events
    #~ cell = ndi.morphology.binary_dilation(cell,
    #~ iterations=5)
    #~ cell = np.ones(image.shape)
    if size != 0:
        cell = size_removal(cell,size)
    return cell


#~ @v.parallel(block=True)
def othercolor(colour,labels):
    import numpy as np
    import scipy.ndimage as ndi
    #This gives an array with max mean and stdev values per each label

    data = {}
    data['max'] = ndi.maximum(colour,labels,np.arange(1,labels.max()+1))
    data['mean'] = ndi.mean(colour,labels,np.arange(1,labels.max()+1))
    data['stdev'] = ndi.standard_deviation(colour,labels,np.arange(1,labels.max()+1))
    data['median'] = ndi.median(colour,labels,np.arange(1,labels.max()+1))
    try:
        temp = np.array(ndi.measurements.center_of_mass(
            colour,labels,np.arange(1,labels.max()+1)))
        # ~ print(temp[:,0])
        data['COMY'] = temp[:,0]
        data['COMX'] = temp[:,1]
    except: 'Something went wrong with centroids'
    return data


def othercolor2(colour,labels,treshold):
    import numpy as np
    import scipy.ndimage as ndi
    '''Output: A dict() with max mean and stdev values per each label'''

    data = {}
    data['max'] = ndi.maximum(colour,labels,np.arange(1,labels.max()+1))
    data['mean'] = ndi.mean(colour,labels,np.arange(1,labels.max()+1))
    data['stdev'] = ndi.standard_deviation(colour,labels,np.arange(1,labels.max()+1))
    data['median'] = ndi.median(colour,labels,np.arange(1,labels.max()+1))
    data['mean_pos'] = data['mean'][data['max'] > treshold]
    data['median_pos'] = data['median'][data['max'] > treshold]
    data['stdev_pos'] = data['stdev'][data['max'] > treshold]
    data['max_pos'] = data['max'][data['max'] > treshold]

    return data

def contrast_img(img,min_,max_ ):
    img[img>max_]=max_
    img[img<min_]=min_
    img -= min_
    img = img * (_16bit/float(max_-min_))
    return img


def convert16to8bits_gpu(x,display_min=0,display_max=2**16-1):
    import cupy as cp
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
    return cp.asnumpy(cp.take(lut, x))

def convert16to8bits(x,display_min=0,display_max=2**16-1):
    def display(image, display_min, display_max): # copied from Bi Rico
    # Here I set copy=True in order to ensure the original image is not
    # modified. If you don't mind modifying the original image, you can
    # set copy=False or skip this step.
        # image = cp.array(image, copy=FalseTrue)
        image.clip(display_min, display_max, out=image)
        image -= display_min
        np.floor_divide(image, (display_max - display_min + 1) / 256,
                        out=image, casting='unsafe')
        return image.astype(np.uint8)

    lut = np.arange(2**16, dtype='uint16')
    lut = display(lut, display_min, display_max)
    return np.take(lut, x)
