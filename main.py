# -*- coding: utf-8 -*-
"""
Created on Thu Dec 06 13:16:10 2012

@author: Helge Pettersen
"""

import dicom, os
import matplotlib.pyplot as plt
from math import *
import tkFileDialog

from nps import *
from GUI import *
from calc import *


######################
#     GET OPTIONS    #
######################

root = Tk()
mainmenu = MainMenu(root)
root.mainloop()
options = mainmenu.returnDictionary()

if not options:
    print "Program quit."

else:
    
    #############################
    #       GET DIRS            #
    #############################
    
    if not options['chooseDirs']: # choose files
        root = Tk()
        root.withdraw()
        input_files_tk = tkFileDialog.askopenfilenames(title="Velg DICOM-filer", multiple=1)
        input_files = root.splitlist(input_files_tk)        
        input_file_list = [os.path.abspath(k) for k in input_files]
        lastFolder = os.path.abspath(str("\\".join(input_file_list[0].split("\\")[:-1])))
        first_file = input_file_list[0]
    
        
    else: # Choose multiple directories
        input_dir = True
        input_dirs = set()
        names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh']
        while input_dir:
            
            # "Choose second directory" as text
            if len(input_dirs) + 1 > len(names):
                num_name = str(len(input_dirs) + 1) + "."
            else:
                num_name = names[len(input_dirs)]
                
            root = Tk()
            root.withdraw()
            input_dir = tkFileDialog.askdirectory(title="Choose the {} directory (Cancel to finish)".format(num_name),
                                                  initialdir = input_dir)
            
            if input_dir: 
                input_dirs.add(input_dir)
            
        input_dirs = list(input_dirs)
    
    
    ################################################################
    # ORGANIZE LISTS INTO DICTIONARY {FOLDER : [LIST OF FILES]}    #
    ################################################################
    
    folders_dict = {}
    if options['chooseDirs']:
        first_file = False
        for folder in input_dirs:
            for root, dirs, files in os.walk(folder):
                folderName = os.path.abspath(root) + "\\"
                
                if not folderName in folders_dict.keys() and files:
                    folders_dict[folderName] = []
                    
                for filename in files:
                    if not first_file:
                        first_file = folderName + filename
                    if not filename in folders_dict[folderName]:
                        folders_dict[folderName].append(filename)
    
    else:
        folders_dict[lastFolder + "\\"] = []
        for filename in input_file_list:
            folders_dict[lastFolder + "\\"].append(filename.split("\\")[-1])

    ####################
    #    CHOOSE ROI    #
    ####################
    
    if options['chooseROI']:
        firstImage = dicom.read_file(first_file)
        rectXY = span_selector(firstImage.pixel_array)
    else:
        rectXY = False
    
    ################
    #  RUN NPS     #
    ################
    
    noiseplots = {}
    
    fig = plt.figure(dpi=100, facecolor='white', figsize=(13, 8)) # dpi is the physical window size
    
    imageInfo = {}
    
    median = {}
    
    # har enten input_files som en filliste, eller input_dirs som er en liste med unike mapper
    
    
    #####################
    #     RUN NPS       #
    #####################
    
    for folder in sorted(folders_dict.keys()):
            noiseplots[folder], imageInfo[folder], median[folder] = NPS([folder + fname for fname in folders_dict[folder]], rectXY, options)
            
    
    filter_set = set()
    model_set = set()
    mas_set = set()
    IRLevel_set = set()
    
    for folder in folders_dict.keys():
        ds = imageInfo[folder]
        
    
        manufacturer = str(ds.Manufacturer)
        ConvolutionKernel = str(ds.ConvolutionKernel)
        exposure = str(ds.Exposure)
        model = str(ds.ManufacturerModelName)
        studydate = str(ds.StudyDate)
        slicethickness = str(ds.SliceThickness)
        kVp = str(ds.KVP)
        institution = str(ds.InstitutionName)
        
        IRLevel = getIRLevel(ds)
                
        filter_set.add(ConvolutionKernel)
        model_set.add(model)
        mas_set.add(exposure)
        IRLevel_set.add(IRLevel)
        
    ####################
    #    MAKE PLOTS    #
    ####################
    
    xlabel = options['plotXTitle']
    ylabel = options['plotYTitle'].replace("^2","$^2$")
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    
    plt.title(options['plotTitle'].replace("%manufacturer", manufacturer).replace("%filter",ConvolutionKernel).replace("%mas",exposure)\
                            .replace("%exposure", exposure).replace("%kvp", kVp).replace("%model", model) \
                            .replace("%institution", institution).replace("%studydate", studydate) \
                            .replace("%slicethickness", slicethickness).replace("IRLevel", str(IRLevel)))
    plots = [0]
    
    labels = []
    labelsMedian = []
    
    labelColors = ['y', 'c', 'b', 'k', 'g', 'r']
    labelMarkers = ['.', '-.', ':', '--', '-']
    
    for m in labelMarkers:
        for c in labelColors:
            labels.append("{}{}".format(c, m))
            labelsMedian.append("{}{}".format(c, m))
                
    # Må sortere filtrene, så dette er dessverre ikke godt nok
    #    for k,v in noiseplots.items():
    #        plots.append(plt.plot(v['x'], v['y'], labels.pop(), label="Filter %s" % k))
    
    for folder in sorted(folders_dict.keys()):
        ds = imageInfo[folder]
        
        manufacturer = str(ds.Manufacturer)
        ConvolutionKernel = ds.ConvolutionKernel
        if type(ConvolutionKernel) == type([1,2]):
            ConvolutionKernel = str(ConvolutionKernel[0])
        else:
             ConvolutionKernel = str(ds.ConvolutionKernel)
        exposure = str(ds.Exposure)
        model = str(ds.ManufacturerModelName)
        studydate = str(ds.StudyDate)
        slicethickness = str(ds.SliceThickness)
        kVp = str(ds.KVP)
        institution = str(ds.InstitutionName)
        
        IRLevel = getIRLevel(ds)
    
        label_str = ""
        
        if len(model_set) > 1:
            label_str += model
    
        if label_str:
            label_str += ", filter %s" % ConvolutionKernel
        else:
            label_str = "Filter %s" % ConvolutionKernel
            
        if len(IRLevel_set) > 1 or max(IRLevel_set)>0:
            label_str += ", IR {}".format(IRLevel)
        if len(mas_set) > 1:
            label_str += ", {} mAs".format(exposure)
        
        plots.append(plt.plot(noiseplots[folder]['x'], noiseplots[folder]['y'], labels.pop(),
                              label=label_str))
                              
        if options['showMedian']:
            plots.append(plt.plot([median[folder][0], median[folder][0]], [0, median[folder][1]], labelsMedian.pop()))
            
        if options['CSV']:
            CSVFileName = options['filenameCSV'].replace("%manufacturer", manufacturer).replace("%filter",ConvolutionKernel).replace("%mas",exposure)\
                            .replace("%exposure", exposure).replace("%kvp", kVp).replace("%model", model) \
                            .replace("%institution", institution).replace("%studydate", studydate) \
                            .replace("%slicethickness", slicethickness).replace("%IRLevel", str(IRLevel))
                            
            with open(CSVFileName, 'w') as CSVFile:
                    CSVFile.write('{};{}\n'.format(xlabel, ylabel))
                    for (x,y) in zip(noiseplots[folder]['x'], noiseplots[folder]['y']):
                        CSVFile.write('{x};{y}\n'.format(x=round(x,3), y=round(y,3)))
    plt.legend()
        
    #    plt.ylim((0, 20)) # 20 800 for 40 70
    #plt.xlim((0, 9))
    
    if options['PNG']:
        plt.savefig(options['filenamePNG'])
    
    plt.show()

    if not options['onscreen']:
        plt.close()