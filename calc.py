# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 08:27:44 2014

@author: rttn
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pylab import *
from classes import *
import scipy.optimize as optimize

def noisePowerRadAv(im):
    """noisePowerRadAv(2D array), returns radius vector with
        axially averaged data. From CTQA-CP (Erlend Andersen)."""

    x,y=im.shape
    rran=np.arange(x)
    theta=np.linspace(0,np.pi/2.0,x*2,endpoint=False)
    r=np.zeros(x)
    for ang in theta:
        yran=np.rint(rran*np.sin(ang))
        xran=np.rint(rran*np.cos(ang))
        r+=np.ravel(im[[xran],[yran]])
    return r/float(x)

def func(data, c1, c2, c3, c4, c5, c6):
    """Helper function for 2D polynomial fit."""
    
    return c1 + c2*data[:,0] + c3*data[:,1] + c4 * data[:,0] ** 2 + \
        c5 * data[:,1] ** 2 + c6 * data[:,0] * data[:,1]

def easyfunc(x, y, c1, c2, c3, c4, c5, c6):
    """2D fit function."""
    
    return c1 + c2*x + c3*y + c4*x**2 + c5*y**2 + c6*x*y
    
def poly_sub(img):
    """Subtracts 2D polynomial from img.
    
    Original form: z = imgROI[x,y]. create roi_size^2 number of tuples with 
    values (x, y, z). Then to feed them to scipy.curve_fit."""
    
    img_size = np.shape(img)[0]

    xx, yy = np.meshgrid(range(img_size), range(img_size))

    xx, yy = xx.flatten(), yy.flatten()
    zz = img.flatten()

    # like zip: 
    # make (a1,b2,c3), (a2,b2,c2,),... from ((a1, a2, ...), (b1, b2, ...), ...)
    img_array = np.dstack((xx, yy, zz))[0]

    guess = [0, 0, 0, 0, 0, 0]
    
    params, pcov = optimize.curve_fit(func, img_array[:,:2], img_array[:,2], guess)
    
    # we need array of params: [1,2,3] = [[1,2,3], [1,2,3], [1,2,3], ...]
    p = np.resize(params, (img_size**2, len(params)))
    subtract_map = map(easyfunc, xx, yy, p[:,0], p[:,1], p[:,2], p[:,3], p[:,4], p[:,5])
    subtract_img = np.reshape(subtract_map, (img_size, img_size))
    
#    plt.imshow(img + np.multiply(5, subtract_img), interpolation = 'nearest', cmap=cm.gray)
#    plt.savefig('original_enhanced.png')
    
    return img - subtract_img
    
def getIRLevel(ds):
    manufacturer = ds.Manufacturer
    kernel = ds.ConvolutionKernel
    
    if "philips" in manufacturer.lower():
        try:        
            iDoseNumber = int(ds[0x1F7, 0x109B].value)
        except:
            iDoseNumber = 0
        
        IRLevel = iDoseNumber
            
    elif "toshiba" in manufacturer.lower():
        try:
            AIDR3D = str(ds[0x7005, 0x100B].value).strip()
        except:
            AIDR3D = "ORG"
            
            AIDR3D = "ORG"

        AIDR3D_names = {"ORG" : 0,
                    "AIDR 3D MILD" : 1,
                    "AIDR 3D STR" : 2,
                    "AIDR 3D STD" : 3}
        try:
            IRLevel = AIDR3D_names[AIDR3D]
        except KeyError:
            IRLevel = 0
        
    elif 'siemens' in manufacturer.lower():
        # B30f, I30f_1, I30f_3, I30f_5
        if type(kernel) == type([1,2]):
            kernel = "_".join(kernel)
        if "b" in kernel.lower():
            IRLevel = 0
        elif "_1" in kernel.lower():
            IRLevel = 1
        elif "_2" in kernel.lower():
            IRLevel = 2
        elif "_3" in kernel.lower():
            IRLevel = 3
        elif "_4" in kernel.lower():
            IRLevel = 4
        elif "_5" in kernel.lower():
            IRLevel = 5
        else:
            print "Couldn't find IRLevel for kernel {}.".format(kernel)
            
    else:
        IRLevel = "N/A"
            
    return IRLevel