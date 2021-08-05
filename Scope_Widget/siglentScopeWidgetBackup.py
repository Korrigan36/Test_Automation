# -*- coding: utf-8 -*-
"""
Created on 11/03/2020

@author: stevenp@valvesoftware.com
"""
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QRadioButton, QVBoxLayout, QCheckBox, QProgressBar,
    QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox, QInputDialog, QDialog, QDialogButtonBox, QSlider, QGridLayout, QHBoxLayout)
from PyQt5.QtGui import QIcon, QPainter, QPen, QFont, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal, pyqtSlot

#append the relative location you want to import from
sys.path.append("../Instrument_Libraries")
import scopeInstrument
from visaInstrument import VisaInstrument
        
#For some reason the following code needs to be here for the Steam icon to show on the taskbar.
#Google code, don't know why.
import ctypes
myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)        

class MainWindow(QWidget):
    
    instrumentName = "Unitialized Instrument"
    
    #The following variables allow us to keep a single dictionary in the VisaInstrument class that defines the type of instrument
    #supported and the specific models of that instrument. We parse this to get a short name that matches a portion
    #of the string returned by IDN. This is how we are choosing the appropriate instrument.
    #In this case were are going to get the choice of instrument strings from a Visa resource command and use them
    #to populate the combo box that lists all Visa instruments connected to our system. You could do this other ways
    #Such as hard code a short name. But hard coding a name requires you to know what's supported in the instrument library
    #and to reproduce the string exactly. 
    
    #The way it's done here we get a list of everything connected then see if it's one of our supported instruments.
    
    #Somehow we need to include the use of the serial number here in case a user has two of the same kind of scope
    
    #Visa Instruments is a list
    visaInstruments = []
    #Instrument Types is a dictionary
    instrumentTypes = {}
    instrumentKey = "Uninitialized Key"

    def __init__(self):
        super(MainWindow, self).__init__()
        
        #First we use the VisaInstrument class directly to get a list of instruments
        #and populate the combo box with the full names minus the newline
        #We need to actually instantiate a class object rather than just call the functions.
        #This creates all the variables etc.
        configVisa = VisaInstrument()
        self.visaInstruments = configVisa.listVisaInstruments()
        self.instrumentTypes = configVisa.listInstrumentTypes()
        self.initUI()


    def initUI(self): 
        
        self.setGeometry(300, 300, 1000, 400)
        self.setWindowTitle('Tektronix Channel Label Widget')
        self.setWindowIcon(QIcon('Steam_icon_logo.gif')) 
        
        instrumentGroupBox  = QGroupBox()
        instrumentGrid      = QGridLayout()
        
        self.scopeComboBox = QComboBox()
        for index in range (0, len(self.visaInstruments)):
            self.scopeComboBox.addItem(self.visaInstruments[index].rstrip())    
        instrumentGrid.addWidget(self.scopeComboBox, 0, 0)
        
        self.initScopeButton = QPushButton('Initialize Scope', self)
        self.initScopeButton.clicked[bool].connect(self.initScope)
        
        instrumentGrid.addWidget(self.initScopeButton, 1, 0)

        scopeLabel = QLabel(self)
        scopeLabel.setText("Scope Type")
        instrumentGrid.addWidget(scopeLabel, 2, 0)

        self.scopeIDN = QLabel(self)
        # self.scopeIDN.setGeometry(150, 40, 1000, 10)
        self.scopeIDN.setText(self.instrumentName)
        instrumentGrid.addWidget(self.scopeIDN, 3, 0)
        
        instrumentGroupBox.setLayout(instrumentGrid)

        startButtonGroupBox  = QGroupBox()
        startButtonLayout    = QHBoxLayout()
        self.startStopButton = QPushButton('Set Labels', self)
        
        # self.startStopButton.setGeometry(800, 70, 180, 50)
        self.startStopButton.clicked[bool].connect(self.startStopTest)
        self.startStopButton.setEnabled(False)
        startButtonLayout.addWidget(self.startStopButton)
        startButtonGroupBox.setLayout(startButtonLayout)

        listBoxGrid      = QGridLayout()
        listBoxGroupBox  = QGroupBox()

        self.ch1Label = QLabel(self)
        self.ch1Label.setText("CH1")
        listBoxGrid.addWidget(self.ch1Label, 0, 0)
        
        self.ch1ListBox = QLineEdit()
        self.ch1ListBox.setText("USB 5V")
        listBoxGrid.addWidget(self.ch1ListBox, 0, 1)

        self.ch2Label = QLabel(self)
        self.ch2Label.setText("CH2")
        listBoxGrid.addWidget(self.ch2Label, 1, 0)
        
        self.ch2ListBox = QLineEdit()
        self.ch2ListBox.setText("VCI")
        listBoxGrid.addWidget(self.ch2ListBox, 1, 1)

        self.ch3Label = QLabel(self)
        self.ch3Label.setText("CH3")
        listBoxGrid.addWidget(self.ch3Label, 2, 0)
        
        self.ch3ListBox = QLineEdit()
        self.ch3ListBox.setText("Reset")
        listBoxGrid.addWidget(self.ch3ListBox, 2, 1)

        self.ch4Label = QLabel(self)
        self.ch4Label.setText("CH4")
        listBoxGrid.addWidget(self.ch4Label, 3, 0)
        
        self.ch4ListBox = QLineEdit()
        self.ch4ListBox.setText("LCD_Reset")
        listBoxGrid.addWidget(self.ch4ListBox, 3, 1)

        self.ch5Label = QLabel(self)
        self.ch5Label.setText("CH5")
        listBoxGrid.addWidget(self.ch5Label, 4, 0)
        
        self.ch5ListBox = QLineEdit()
        self.ch5ListBox.setText("MSO58 Stuff Here")
        listBoxGrid.addWidget(self.ch5ListBox, 4, 1)

        self.ch6Label = QLabel(self)
        self.ch6Label.setText("CH6")
        listBoxGrid.addWidget(self.ch6Label, 5, 0)
        
        self.ch6ListBox = QLineEdit()
        self.ch6ListBox.setText("MSO58 Stuff Here")
        listBoxGrid.addWidget(self.ch6ListBox, 5, 1)

        self.ch7Label = QLabel(self)
        self.ch7Label.setText("CH7")
        listBoxGrid.addWidget(self.ch7Label, 6, 0)
        
        self.ch7ListBox = QLineEdit()
        self.ch7ListBox.setText("MSO58 Stuff Here")
        listBoxGrid.addWidget(self.ch7ListBox, 6, 1)

        self.ch8Label = QLabel(self)
        self.ch8Label.setText("CH8")
        listBoxGrid.addWidget(self.ch8Label, 7, 0)
        
        self.ch8ListBox = QLineEdit()
        self.ch8ListBox.setText("MSO58 Stuff Here")
        listBoxGrid.addWidget(self.ch8ListBox, 7, 1)


        listBoxGroupBox.setLayout(listBoxGrid)
        
        annotationGrid      = QGridLayout()
        annotationGroupBox  = QGroupBox()

        self.annotationLabel = QLabel(self)
        self.annotationLabel.setText("Scope Annotation")
        annotationGrid.addWidget(self.annotationLabel, 0, 0)
        
        self.annotationListBox = QLineEdit()
        self.annotationListBox.setText("USB Controller Port 5V Ripple No Load")
        annotationGrid.addWidget(self.annotationListBox, 0, 1)

        annotationGroupBox.setLayout(annotationGrid)
 

        grid = QGridLayout()
        grid.addWidget(instrumentGroupBox, 0, 0)
        grid.addWidget(listBoxGroupBox, 0, 1)
        grid.addWidget(startButtonGroupBox, 1, 0)
        grid.addWidget(annotationGroupBox, 1, 1)

        self.setLayout(grid)

        self.show()

    def initScope(self):
        
        #instrumentName is the full string returned by IDN using the configVisa object. This is stored in scopeComboBox
        #You could just hard code the name here as long as it matches what's in the dictionary in the VisaInstrument class
        #but that is prolematic as mentioned above.
        self.instrumentName = self.scopeComboBox.currentText()
        print ("Initializing Instrument Type: " + self.instrumentName)
        
        #This uses a dictionary created in the Visa class
        
        #Go through each name of each key to find a match with our chosen instrument
        for key in self.instrumentTypes:
            for nameIndex in range (0, len(self.instrumentTypes[key])):
                if self.instrumentTypes[key][nameIndex] in self.instrumentName:
                    #The Visa instrument class keeps track of the instrument types supported.
                    print ("Instrument type is: "  + key)
                    self.instrumentKey = key
                    #The Visa instrument class keeps a short name for each model of each type supported.
                    #The class function connectInstrument searches for this short name in the string returned by IDN
                    #We will want to use the serial number somehow in case a user has two of the same kind of scope
                    #Work on that later, for now we are just abstracting the scope instrument
                    self.scopeModel = self.instrumentTypes[key][nameIndex]
                    print ("The scope model is: " + self.scopeModel)
                    break
            # else:
            #     print ("Instrument key problem")    
        
        #Here is where we instantiate the instrument
        #We'll keep using instrument for the name since this is cut and past from the instrument widget.
        #But this variable can be called whatever you like. 
        # if self.instrumentKey == "KeyScope" or self.instrumentKey == "TekScope" or self.instrumentKey == "SigScope":
        if "Scope" in self.instrumentKey:
            self.instrument = scopeInstrument.ScopeDevice(self.instrumentKey)
        
        #Initialize Instrument
        #You won't find initializeInstrument in the scopeInstrument class or the tekScope class, it's embedded in the VisaInstrument class
        #It is also embedded in the niInstrument class. Any further types of instruments must also have this function.
        if self.instrument.initializeInstrument(self.instrumentName):
            self.instrumentName = self.instrument.instrumentName
            self.scopeIDN.setText(self.instrumentName)
            self.startStopButton.setEnabled(True)
        else:
            print ("Failed to Initialize Instrument")


    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False   
       
    def startStopTest(self):
        
        self.instrument.setState(1, "ON")
        self.instrument.setState(2, "ON")
        self.instrument.setState(3, "ON")
        self.instrument.setState(4, "ON")
        
        self.instrument.setBandwidth(1, "ON")
        self.instrument.setBandwidth(2, "ON")
        self.instrument.setBandwidth(3, "ON")
        self.instrument.setBandwidth(4, "ON")
        
        #Siglent library hard codes trigger level to mV
        self.instrument.setEdgeTrigger(3, 50, "FALL")
                
        # self.instrument.setLabel(1, self.ch1ListBox.text())
        # self.instrument.setLabel(2, self.ch2ListBox.text())
        # self.instrument.setLabel(3, self.ch3ListBox.text())
        # self.instrument.setLabel(4, self.ch4ListBox.text())

        # self.instrument.scope_SetAnnotation( self.annotationListBox.text(), 550, 720)

        
if __name__ == '__main__':
    
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    ex = MainWindow()
    app.exec_()  
