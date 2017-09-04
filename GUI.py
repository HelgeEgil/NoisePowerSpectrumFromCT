# -*- coding: utf-8 -*-
"""
Created on Wed Jul 09 13:03:22 2014

@author: rttn
"""

from Tkinter import *
import tkFileDialog
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from pylab import connect, show
from classes import *

class MainMenu(Frame):
    def __init__(self, parent):
            
        Frame.__init__(self, parent)
    
        self.parent = parent
        
        self.parent.protocol("WM_DELETE_WINDOW", self.myQuit)
        self.parent.title("Noise Power Spectrum Calculator")

        
        ###################
        # CONTAINERS      #
        ###################        
        
        # Create
        self.upperContainer = Frame(self, borderwidth=5, relief=RIDGE, height=40)
        self.middleContainer = Frame(self, borderwidth=5)
        self.bottomContainer = Frame(self, borderwidth=20)
        
        self.middleLeftContainer = Frame(self.middleContainer, borderwidth=5) 
        self.middleMiddleContainer = Frame(self.middleContainer, height=1, bg="grey", relief=SUNKEN)
        self.middleRightContainer = Frame(self.middleContainer, borderwidth=10, height=5)
        self.outputContainer = Frame(self.middleRightContainer, borderwidth=10)
        self.outputTitleContainer = Frame(self.outputContainer, borderwidth=0)
        self.frameOnScreen = Frame(self.outputContainer, borderwidth=0)
        self.frameCSV = Frame(self.outputContainer, borderwidth=0)
        self.framePNG = Frame(self.outputContainer, borderwidth=0)

        # And pack
        self.upperContainer.pack()
        self.middleContainer.pack()
        self.middleLeftContainer.pack(side=LEFT)
        self.middleMiddleContainer.pack(side=LEFT, fill=Y, padx=5, pady=5)
        self.middleRightContainer.pack(side=LEFT)
        
        self.outputContainer.pack(anchor=W)
        self.outputTitleContainer.pack(anchor=W)
        self.frameOnScreen.pack(anchor=W)
        self.framePNG.pack(anchor=W)
        self.frameCSV.pack(anchor=W)
        
        self.bottomContainer.pack()
        
        
        
        
        
        self.currentDir = StringVar()
        self.currentDir.set(os.path.abspath("."))

        self.label_title = Label(self.upperContainer, text="Noise Power Spectrum calculator")
        self.label_title.pack()

        #########################
        # CALCULATION OPTIONS   #
        #########################
        
        self.var_nnps = IntVar()
        self.var_2dpoly = IntVar()
        self.var_zeropad = IntVar()
        self.var_nROI = IntVar()
        self.var_chooseROI = IntVar()
        self.var_medianValue = IntVar()
        self.var_showMedianValue = IntVar()
        self.var_dcCorrection = IntVar()
        
        self.var_nROI.set(1)
        self.var_chooseROI.set(1)
        self.var_dcCorrection.set(1)
        
        self.optionsTitle = Label(self.middleLeftContainer, text="Calculation Options: ")
        
        self.check_nnps = Checkbutton(self.middleLeftContainer, text="Normalized NPS", variable=self.var_nnps, command=self.nnps_set)
        self.check_2dpoly = Checkbutton(self.middleLeftContainer, text="2D polynomial subtraction", variable=self.var_2dpoly)
        self.check_zeropad = Checkbutton(self.middleLeftContainer, text="Zero Padding", variable=self.var_zeropad)
        self.check_nROI = Checkbutton(self.middleLeftContainer, text="9 sub-ROIs", variable=self.var_nROI)
        self.check_dcCorrection = Checkbutton(self.middleLeftContainer, text="ROI DC correction", variable=self.var_dcCorrection)
        
        self.check_chooseROI = Checkbutton(self.middleLeftContainer, text="Choose ROI on screen", variable=self.var_chooseROI)
        self.check_medianValue = Checkbutton(self.middleLeftContainer, text="Save median value", variable=self.var_medianValue)
        self.check_showMedianValue = Checkbutton(self.middleLeftContainer, text="Show median value", variable=self.var_showMedianValue)
        
        self.optionsTitle.pack(anchor=W)
        self.check_nnps.pack(anchor=W)
        self.check_2dpoly.pack(anchor=W)
        self.check_zeropad.pack(anchor=W)
        self.check_nROI.pack(anchor=W)
        self.check_chooseROI.pack(anchor=W)
        self.check_dcCorrection.pack(anchor=W)
        self.check_medianValue.pack(anchor=W)
        self.check_showMedianValue.pack(anchor=W)
        
        
        ##########################
        # OUTPUT OPTIONS         #
        ##########################        
        
        self.label_output = Label(self.outputTitleContainer, text="Choose output format:")
        self.label_output.pack(anchor=W)

        self.var_onscreen = IntVar()
        self.var_png = IntVar()
        self.var_csv = IntVar()
        
        self.var_onscreen.set(1)
        
        self.check_onscreen = Checkbutton(self.frameOnScreen, text="On screen                          ", variable=self.var_onscreen, command=self.output_choose)
        self.check_png = Checkbutton(self.framePNG, text="PNG file", variable=self.var_png, command=self.output_choose)
        self.check_csv = Checkbutton(self.frameCSV, text="CSV file ", variable=self.var_csv, command=self.output_choose)
        
        self.check_onscreen.pack(anchor=W, side=LEFT)        
        self.check_png.pack(anchor=W, side=LEFT)
        self.check_csv.pack(anchor=W, side=LEFT)   

        self.varOutputFileNamePNG = StringVar(self, value="NPS_all.png")
        self.varOutputFileNameCSV = StringVar(self, value="NPS_%manufacturer_%filter.csv")

        self.labelOutputFileNamePNG = Label(self.framePNG, text="PNG Filename: ")
        self.labelOutputFileNameCSV = Label(self.frameCSV, text="CSV Filename:  ")

        self.entryOutputFileNamePNG = Entry(self.framePNG, textvariable = self.varOutputFileNamePNG, width=45)
        self.entryOutputFileNameCSV = Entry(self.frameCSV, textvariable = self.varOutputFileNameCSV, width=45)
        
        self.buttonGetOutputDir = Button(self.frameOnScreen, text="Get DIR", command=self.getDir)
        self.labelCurrentDir = Label(self.frameOnScreen, textvariable=self.currentDir)
                
            
                
                
        ##########################
        # PLOT OPTIONS           #
        ##########################
        
        self.label_plot_options = Label(self.middleRightContainer, text="Plot Options (%manufacturer, %filter, %mas, %kvp,\n %model, %institution, %studydate, %slicethickness, %IRLevel): ")
        self.label_plot_options.pack(anchor=W, side=TOP)
        
        
        self.frame_nps = Frame(self.middleRightContainer)      
        self.nps_title_text = Label(self.frame_nps, text="Title:           ")        
        self.var_plot_title = StringVar(self, value="Noise Power Spectrum: %manufacturer %model (%kvp kVp, %mas mAs)")
        self.entry_plot_title = Entry(self.frame_nps, textvariable=self.var_plot_title, width=62)
        self.frame_nps.pack(anchor=W, side=TOP)
        self.nps_title_text.pack(side=LEFT)
        self.entry_plot_title.pack(side=LEFT)
        
        
        self.frame_x_title = Frame(self.middleRightContainer)
        self.x_axis_text = Label(self.frame_x_title, text="X-axis title: ")
        self.var_plot_x_axis = StringVar(self, value="Spatial frequency [lp/cm]")
        self.entry_plot_x_axis = Entry(self.frame_x_title, textvariable=self.var_plot_x_axis, width=62)
        self.frame_x_title.pack(anchor=W)
        self.x_axis_text.pack(side=LEFT, anchor=W)
        self.entry_plot_x_axis.pack(side=LEFT, anchor=W)
        
        
        self.frame_y_title = Frame(self.middleRightContainer)
        self.y_axis_text = Label(self.frame_y_title, text="Y-axis title: ")
        self.var_plot_y_axis = StringVar(self, value="NPS [HU^2 cm^2]")
        self.entry_plot_y_axis = Entry(self.frame_y_title, textvariable=self.var_plot_y_axis, width=62)
        self.frame_y_title.pack(anchor=W)
        self.y_axis_text.pack(side=LEFT)
        self.entry_plot_y_axis.pack(side=LEFT)
        
        
        self.button_width = 20
        self.button_choose_images = Button(self.bottomContainer, text="Choose images", command=self.choose_images, width=self.button_width)
        self.button_choose_images.pack(side=LEFT)
        
        self.button_choose_directories = Button(self.bottomContainer, text="Multiple directories", command=self.choose_directories, width=self.button_width)
        self.button_choose_directories.pack(side=LEFT)
        
        self.button_cancel = Button(self.bottomContainer, text="Cancel", command=self.myQuit, width=self.button_width)
        self.button_cancel.pack()
        
        self.pack()
    

    
    ##################
    # FUNCTIONS      #
    ##################
    
    def output_choose(self):
        """Adds or removes filename Entries based on checkbutton input."""
        
        if self.var_png.get() or self.var_csv.get():
            self.buttonGetOutputDir.pack(side=LEFT)
            self.labelCurrentDir.pack(side=LEFT)
            
            if self.var_png.get():
                self.labelOutputFileNamePNG.pack(side=LEFT, anchor=E)
                self.entryOutputFileNamePNG.pack(side=LEFT, anchor=E)
            else:
                self.entryOutputFileNamePNG.pack_forget()
                self.labelOutputFileNamePNG.pack_forget()
                
            if self.var_csv.get():
                self.labelOutputFileNameCSV.pack(side=LEFT, anchor=E)
                self.entryOutputFileNameCSV.pack(side=LEFT, anchor=E)
            else:
                self.entryOutputFileNameCSV.pack_forget()
                self.labelOutputFileNameCSV.pack_forget()
        else:
            self.entryOutputFileNameCSV.pack_forget()
            self.entryOutputFileNamePNG.pack_forget()
            self.labelOutputFileNameCSV.pack_forget()
            self.labelOutputFileNamePNG.pack_forget()
            self.labelCurrentDir.pack_forget()
            self.buttonGetOutputDir.pack_forget()


    def getDir(self):
        self.currentDir.set(tkFileDialog.askdirectory(title="Get output file directory", initialdir=self.currentDir))
        self.labelCurrentDir.configure(text=self.currentDir)

    def nnps_set(self):
        """Edits text in X- and Y axis title based on (N)NPS calculation."""
        
        if self.var_nnps.get() == 0:
            self.var_plot_title.set(self.var_plot_title.get().replace("Normalized ", ""))
            self.var_plot_y_axis.set(self.var_plot_y_axis.get().replace("NNPS", "NPS").replace("cm", "HU^2 cm^2"))
        else:
            self.var_plot_title.set(self.var_plot_title.get().replace("Noise Power Spectrum", "Normalized Noise Power Spectrum"))
            self.var_plot_y_axis.set(self.var_plot_y_axis.get().replace("NPS", "NNPS").replace("HU^2 cm^2", "cm"))
            
    def choose_images(self):
        """Finalize the program, create dictionary on all options and close windows."""
        
        self.return_dictionary = {'nnps' : self.var_nnps.get(), '2dpoly' : self.var_2dpoly.get(),
                                  'zeropad' : self.var_zeropad.get(), 'nROI' : self.var_nROI.get(),
                                    'chooseROI' : self.var_chooseROI.get(), 'medianValue' : self.var_medianValue.get(),
                                    'plotTitle' : self.var_plot_title.get(), 'plotXTitle' : self.var_plot_x_axis.get(),
                                    'plotYTitle' : self.var_plot_y_axis.get(), 'onscreen':self.var_onscreen.get(),
                                    'PNG' : self.var_png.get(), 'CSV' : self.var_csv.get(),
                                    'filenamePNG' : self.varOutputFileNamePNG.get(), 'filenameCSV':self.varOutputFileNameCSV.get(),
                                    'outputDir':self.currentDir.get(), 'chooseDirs':False,
                                    'dcCorrection':self.var_dcCorrection.get(), 'showMedian':self.var_showMedianValue.get()}
        self.parent.destroy()
        self.quit()

    def choose_directories(self):
    
        self.return_dictionary = {'nnps' : self.var_nnps.get(), '2dpoly' : self.var_2dpoly.get(),
                              'zeropad' : self.var_zeropad.get(), 'nROI' : self.var_nROI.get(),
                                'chooseROI' : self.var_chooseROI.get(), 'medianValue' : self.var_medianValue.get(),
                                'plotTitle' : self.var_plot_title.get(), 'plotXTitle' : self.var_plot_x_axis.get(),
                                'plotYTitle' : self.var_plot_y_axis.get(), 'onscreen':self.var_onscreen.get(),
                                'PNG' : self.var_png.get(), 'CSV' : self.var_csv.get(),
                                'filenamePNG' : self.varOutputFileNamePNG.get(), 'filenameCSV':self.varOutputFileNameCSV.get(),
                                'outputDir':self.currentDir.get(), 'chooseDirs':True, 'dcCorrection':self.var_dcCorrection.get(),
                                'showMedian':self.var_showMedianValue.get()}
        
        self.parent.destroy()
        self.quit()        
        
    def myQuit(self):
        """Catches quitting by the "X" button. No options returned."""
        
        self.return_dictionary = False
        self.parent.destroy()
        self.quit()
        
    def returnDictionary(self):
        """Return the option dictionary."""
        
        return self.return_dictionary

def toggle_selector(event):
    """Activate and deactivate ROI selector."""
    
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print "Activated"
        toggle_selector.RS.set_active(False)
        
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print "Deactivated"
        toggle_selector.RS.set_active(True)
    
def onselect(eclick, erelease):
    """Close window when button is released. No further action is needed."""
    
    plt.close()
        
def span_selector(img):
    """Program to choose ROI. Load 2D array img, plot it, and allow the user to draw a QUADRATIC ROI."""
    fig, ax = plt.subplots()
    
    x_size, y_size = np.shape(img)
    
    x_from, x_to = int(3./8 * x_size), int(5./8 * x_size)
    y_from, y_to = int(3./8 * y_size), int(5./8 * y_size)

    medianROI = np.median(img[x_from:x_to, y_from:y_to])
    stdROI =       np.std(img[x_from:x_to, y_from:y_to])

    ax.imshow(img, cmap=cm.gray, vmin=medianROI - 25*stdROI, vmax=medianROI + 25*stdROI)
    ax.set_title("Press left mouse button and drag to choose ROI")
    
    # Nota bene: This class is a variation of RectangleSelector.
    #   With a constraint on only quadratic ROIs being possible.
    #   See file classes.py for this class.
    
    toggle_selector.RS = QuadraticSelector(ax, onselect, drawtype="box", rectprops=dict(edgecolor='red', linewidth=3, fill = False))
    connect('key_press_event', toggle_selector)
    show()
#    fig.close()
    return toggle_selector.RS.getQuad()