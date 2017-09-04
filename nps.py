# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 14:03:19 2014

@author: rttn
"""
from calc import *
import dicom, os
import numpy as np
from math import *
from time import strftime
from scipy.integrate import trapz

def NPS(input_file_list, rectXY, options):
    """Regner ut NPS-kurven for filene i folderName, og returnerer et 1D-graf."""
    
    imageInfo = dicom.ReadFile(input_file_list[0], stop_before_pixels=True)
    
    try:
        ConvolutionKernel = imageInfo.ConvolutionKernel
    except AttributeError:
        ConvolutionKernel = "N/A"
    
    IRLevel = getIRLevel(imageInfo)
    
    noiseplotList = [0]*len(input_file_list)
            
    for idx, imageFilename in enumerate(input_file_list):
        
        imageFile = dicom.ReadFile(imageFilename)
        raw_image = imageFile.pixel_array

        rescaleSlope = eval(str(imageFile.RescaleSlope))
        rescaleIntercept = eval(str(imageFile.RescaleIntercept))    
    
        raw_image = np.add(np.multiply(raw_image, rescaleSlope), rescaleIntercept)    
    
        if options['chooseROI']:
            (x1, x5) = rectXY[0]
            (y1, y5) = rectXY[1]
    
            dx = x5 - x1
            dy = y5 - y1
            
            assert dx == dy
    
            img_roi = raw_image[y1:y1+dy, x1:x1+dx]
        else:
            img_roi = raw_image
        
        if options['dcCorrection']:
            img_roi = np.subtract(img_roi, np.mean(img_roi))

        # imageFile.PixelSpacing: (x mm, y mm)
        pixelSpacing = float(imageFile.PixelSpacing[0])
        # pixelspacing er mm, img^2 er HU^2 cm^2
    
        noiseplotList[idx] = {}

        imgfft = False
        fft = False
    
#        _b += time.time() # before nroi    
    
        if options['nROI']: # 9 ROI calculation
            x1 = y1 = 0
            x5 = y5 = min(np.shape(img_roi))
            
            y2, y3, y4 = 0.25 * (y1+y5), 0.5 * (y1+y5), 0.75 * (y1+y5)
            x2, x3, x4 = 0.25 * (x1+x5), 0.5 * (x1+x5), 0.75 * (x1+x5)
    
    
    
            roiList =   [   [(x1, y3), (x3, y5)],
                            [(x2, y3), (x4, y5)],
                            [(x3, y3), (x5, y5)],
                            [(x1, y2), (x3, y4)],
                            [(x2, y2), (x4, y4)],
                            [(x3, y2), (x5, y4)],
                            [(x1, y1), (x3, y3)],
                            [(x2, y1), (x4, y3)],
                            [(x3, y1), (x5, y3)]    ]
            firstdx = 0
            firstdy = 0
            for roi in roiList:
                xfrom = roi[0][0]
                xto = roi[1][0]
                yfrom = roi[0][1]
                yto = roi[1][1]
                
                xfrom, xto, yfrom, yto = int(xfrom+.5), int(xto+.5), int(yfrom+.5), int(yto+.5)                
                
                dy = yto-yfrom
                dx = xto-xfrom
                
                if not firstdx + firstdy:
                    firstdx = dx
                    firstdy = dy
                
                if dx != dy or dx != firstdx:
                    continue

                
                img_sub_roi = img_roi[yfrom:yfrom+dy, xfrom:xfrom+dx] # y1:y2, x1:x2
                if options['dcCorrection']:
                    img_sub_roi = np.subtract(img_sub_roi, np.mean(img_sub_roi))
                    
                roi_size = np.shape(img_sub_roi)[0]
                
                
                if options['2dpoly']:
                    # Subtract 2D polynomial from ROI
                    img_sub_roi = poly_sub(img_sub_roi)
                    
                if options['zeropad']:
                    zeropadFactor = 3
                    ROIzeropad = np.zeros((roi_size*zeropadFactor, roi_size*zeropadFactor))
                    ROIzeropad[roi_size:2*roi_size, roi_size:2*roi_size] = img_sub_roi*zeropadFactor**2
                    img_sub_roi = ROIzeropad / float(zeropadFactor)
               
    #             for the first ROI, (img)fft is False, and np.add(False, x) == x.
                imgfft = np.add(imgfft, np.square(np.absolute(np.fft.fft2(img_sub_roi))) * (pixelSpacing**2 / (len(img_sub_roi)**2)) / 100.)
                fft = np.add(fft, np.fft.fftfreq(img_sub_roi.shape[0], d=float(pixelSpacing))) # 1/mm                
                
            # Average the plots
            imgfft = np.divide(imgfft, len(roiList))
            fft = np.divide(fft, len(roiList))
            
            try:
                FFT = noisePowerRadAv(imgfft)
            except IndexError:
                continue
            
        else: # Just one ROI calculation
            roi_size = np.shape(img_roi)[0]
            
            if options['2dpoly']:
                img_roi = poly_sub(img_roi)
                
            if options['zeropad']:
                zeropadFactor = 3
                ROIzeropad = np.zeros((roi_size*zeropadFactor, roi_size*zeropadFactor))
                ROIzeropad[roi_size:2*roi_size, roi_size:2*roi_size] = img_roi*zeropadFactor**2
                img_roi = ROIzeropad
                
            imgfft = np.square(np.absolute(np.fft.fft2(img_roi))) * (pixelSpacing**2 / (len(img_roi)**2)) / 100.
            fft = np.fft.fftfreq(img_roi.shape[0], d=float(pixelSpacing)) # 1/mm
            
            print "Max fft frequency: {} lp/mm.".format(np.max(fft))

            try:
                FFT = noisePowerRadAv(imgfft)
            except IndexError:
                continue
        
        # To get cm. Some scanners need another factor...
        fftMultiplyFactor = 10.
        
        noiseplotList[idx]['x'] = fft[fft>0]*fftMultiplyFactor
        noiseplotList[idx]['y'] = FFT[fft>0]
            
        # nå er imgfft i HU^2 CM^2 
    noiseplot = {}
    noiseplot['x'] = noiseplotList[0]['x']
    noiseplot['y'] = [0]*len(noiseplot['x'])
    
    
    # Find average over many images
    for idx, x in enumerate(noiseplotList[0]['x']):
        n = len(noiseplotList) # number of images in run
        y = 0
        for nplj in noiseplotList: # nplj['y'] is full NPS of one image
            y = np.add(nplj['y'][idx], y) # nplj['y'][idx] is one frequency
        # y is now total contribution to one fruequency for all images
        y /= float(n) # average contribution
        
        noiseplot['y'][idx] = y # save value
    
    if options['nnps']: # Divide NPS curve by AUC, we get normalized NPS
        x_width = noiseplot['x'][1] - noiseplot['x'][0]
        areaUnderNPSCurve = float( np.sum(noiseplot['y']) * x_width )
        noiseplot['y'] = np.divide(noiseplot['y'], areaUnderNPSCurve)
        
    ##############################
    #    CALCULATE MEDIAN VALUES #
    ##############################
    
    

#   Old method using x_width * y_value instead of trapzoid sums

#    delta_x = noiseplot['x'][1] - noiseplot['x'][0]    
#    for each in range(len(noiseplot['y'])):
##        weightedsum += noiseplot['x'][each] * noiseplot['y'][each]
#        weightedsum += delta_x * noiseplot['y'][each]
    
#    weightedsum = 0
#    for each in range(len(noiseplot['y'])):
##        if weightedsum + noiseplot['x'][each] * noiseplot['y'][each] < reference:
##            weightedsum += noiseplot['x'][each] * noiseplot['y'][each]
#            
#        if weightedsum + delta_x * noiseplot['y'][each] < reference:
#            weightedsum += delta_x * noiseplot['y'][each]
#
#        else:
#            y1 = weightedsum
##            y2 = weightedsum + noiseplot['x'][each] * noiseplot['y'][each]
#            y2 = weightedsum + delta_x * noiseplot['y'][each]
#
#            x1 = noiseplot['x'][each-1]
#            x2 = noiseplot['x'][each]         
#            dy = float(y2 - y1)
#            dx = x2 - x1
#            median_x = (dx/dy) * (reference - y1) + x1
#            
#            # to find interpolated y value for plotting
#            y1_value = noiseplot['y'][each-1]
#            y2_value = noiseplot['y'][each]
#            dy_value = float(y2_value - y1_value)
#            
#            median_y = y1_value + dy_value / dx * (median_x - x1)
#            
#            median = [median_x, median_y]
#
#            break

    weightedsum_trapz = trapz(noiseplot['y'], noiseplot['x'])
    reference_trapz = weightedsum_trapz / 2.
    
    for each in range(len(noiseplot['y'])):
        if trapz(noiseplot['y'][:each],  noiseplot['x'][:each]) < reference_trapz:
            continue
        else:
            y1 = trapz(noiseplot['y'][:each-1], noiseplot['x'][:each-1])
            y2 = trapz(noiseplot['y'][:each],  noiseplot['x'][:each])
            x1 = noiseplot['x'][each-1]
            x2 = noiseplot['x'][each]         
            dy = float(y2 - y1)
            dx = x2 - x1
            median_x = (dx/dy) * (reference_trapz - y1) + x1
            
            # to find interpolated y value for plotting
            y1_value = noiseplot['y'][each-1]
            y2_value = noiseplot['y'][each]
            dy_value = float(y2_value - y1_value)
            
            median_y = y1_value + dy_value / dx * (median_x - x1)
            
            median_trapz = [median_x, median_y]

            break
        
    #################################
    #   SAVE MEDIAN VALUES TO CSV   #
    #################################
    
    if options['medianValue']:
        fname = 'median_values.csv'        
    
        open(fname, 'a') # Touch file

        # Check for header
        headerExists = False
        with open(fname, 'r') as medianFile:
            for line in medianFile.readlines():
                if 'Filter' in line:
                    headerExists = True
    
        # Append the median value to medianFile
        with open(fname, 'a') as medianFile:
            if not headerExists:
                medianFile.write("Filter; IRLevel; Median value (lp/cm); Date (YYYY-MM-DD HH:MM:SS)\n")            
                    
            datestring = strftime("%Y-%m-%d %H:%M:%S")
            medianFile.write("{kernel}; {IRLevel}; {median}; {time}\n".format(kernel=ConvolutionKernel, 
                             IRLevel=IRLevel, median=round(median_x,2), time=datestring))
        
    return noiseplot, imageInfo, median_trapz