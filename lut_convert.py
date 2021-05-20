import numpy as np
import cupy as cp
import timeit
rows, cols = 768, 1024
image = np.random.randint(100, 14000,
                             size=(1, rows, cols)).astype(np.uint16)
display_min = 1000
display_max = 10000

def display(image, display_min, display_max): # copied from Bi Rico
    # Here I set copy=True in order to ensure the original image is not
    # modified. If you don't mind modifying the original image, you can
    # set copy=False or skip this step.
    image = np.array(image, copy=True)
    image.clip(display_min, display_max, out=image)
    image -= display_min
    np.floor_divide(image, (display_max - display_min + 1) / 256,
                    out=image, casting='unsafe')
    return image.astype(np.uint8)

def lut_display(image, display_min, display_max) :
    lut = np.arange(2**16, dtype='uint16')
    lut = display(lut, display_min, display_max)
    return np.take(lut, image)


def displaycp(image2, display_min, display_max): # copied from Bi Rico
    # Here I set copy=True in order to ensure the original image is not
    # modified. If you don't mind modifying the original image, you can
    # set copy=False or skip this step.
    image2 = cp.array(image2, copy=True)
    image2.clip(display_min, display_max, out=image2)
    image2 -= display_min
    cp.floor_divide(image2, (display_max - display_min + 1) / 256,
                    out=image2, casting='unsafe')
    return image2.astype(cp.uint8)

def lut_displaycp(image2, display_min, display_max) :
    lut = cp.arange(2**16, dtype='uint16')
    lut = displaycp(lut, display_min, display_max)
    return cp.take(lut, image2)

np.all(display(image, display_min, display_max) ==
           lut_display(image, display_min, display_max))

imagecp = cp.asarray(image)
type(imagecp)

cp.all(displaycp(imagecp, display_min, display_max) ==
           lut_displaycp(imagecp, display_min, display_max))

np.all(cp.asnumpy(displaycp(imagecp, display_min, display_max)) ==
          display(image, display_min, display_max))
timeit.timeit('display(image, display_min, display_max)',
                  'from __main__ import display, image, display_min, display_max',
                   number=100)

timeit.timeit('lut_display(image, display_min, display_max)',
                  'from __main__ import lut_display, image, display_min, display_max',
                  number=100)

timeit.timeit('displaycp(imagecp, display_min, display_max)',
                  'from __main__ import displaycp, imagecp, display_min, display_max',
                   number=100)

timeit.timeit('lut_displaycp(imagecp, display_min, display_max)',
                  'from __main__ import lut_displaycp, imagecp, display_min, display_max',
                  number=100)
