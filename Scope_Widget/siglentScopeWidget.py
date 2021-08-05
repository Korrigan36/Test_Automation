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
from instrumentConfig import Instrument
       
#For some reason the following code needs to be here for the Steam icon to show on the taskbar.
#Google code, don't know why.
import ctypes
myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)        

class MainWindow(QWidget):

    instrumentName = "Unitialized Instrument"
    
   
    instrumentList = []
    #Instrument Types is a dictionary
    instrumentTypes = {}
    instrumentKey = "Uninitialized Key"
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.configInstrument = Instrument()
        self.instrumentList = self.configInstrument.listInstruments()
        self.instrumentTypes = self.configInstrument.listInstrumentTypes()

        self.initUI()


    def initUI(self): 
        
        self.setGeometry(300, 300, 500, 600)
        self.setWindowTitle('Tektronix Channel Label Widget')
        self.setWindowIcon(QIcon('Steam_icon_logo.gif')) 
        
        instrumentGroupBox  = QGroupBox()
        instrumentGrid      = QGridLayout()
        
        self.scopeComboBox = QComboBox()
        for index in range (0, len(self.instrumentList)):
            self.scopeComboBox.addItem(self.instrumentList[index].rstrip())    
        instrumentGrid.addWidget(self.scopeComboBox, 0, 0)
        
        self.initScopeButton = QPushButton('Initialize Scope', self)
        self.initScopeButton.clicked[bool].connect(self.initScope)
        
        instrumentGrid.addWidget(self.initScopeButton, 1, 0)

        scopeLabel = QLabel(self)
        scopeLabel.setText("Scope Type")
        instrumentGrid.addWidget(scopeLabel, 2, 0)

        self.scopeIDN = QLabel(self)
        self.scopeIDN.setText(self.instrumentName)
        instrumentGrid.addWidget(self.scopeIDN, 3, 0)
        
        instrumentGroupBox.setLayout(instrumentGrid)
        
        instrumentGroupBox.setLayout(instrumentGrid)

        startButtonGroupBox  = QGroupBox()
        startButtonLayout    = QHBoxLayout()
        self.startStopButton = QPushButton('Test Scope Connection', self)
        
        self.startStopButton.clicked[bool].connect(self.startStopTest)
        self.startStopButton.setEnabled(False)
        startButtonLayout.addWidget(self.startStopButton)


        self.getScopeShot = QPushButton('Get Scope Shot', self)
        

        pictureGroupBox  = QGroupBox()
        pictureLayout    = QHBoxLayout()
        self.pictLabel = QLabel(self)
        pictureLayout.addWidget(self.pictLabel)
        pictureGroupBox.setLayout(pictureLayout)

        self.getScopeShot.clicked[bool].connect(self.scopeShot)
        self.getScopeShot.setEnabled(False)
        startButtonLayout.addWidget(self.getScopeShot)

        startButtonGroupBox.setLayout(startButtonLayout)

        grid = QGridLayout()
        grid.addWidget(instrumentGroupBox, 0, 0)
        grid.addWidget(startButtonGroupBox, 1, 0)
        grid.addWidget(pictureGroupBox, 2, 0)

        self.setLayout(grid)

        self.show()

    def initScope(self):
        
        self.instrumentName = self.scopeComboBox.currentText()
        
        # self.scope, self.scopeName = self.configInstrument.initInstrument(self.instrumentName)
        self.scope, self.scopeName = self.configInstrument.initInstrument("172.18.18.24")
        
        print ("Configured Scope: " + self.scopeName)
        
        self.scopeIDN.setText(self.scopeName)

        self.startStopButton.setEnabled(True)
        self.getScopeShot.setEnabled(True)

    def startStopTest(self):
        
        self.scope.setState(1, "ON")
        self.scope.setState(2, "ON")
        self.scope.setState(3, "ON")
        self.scope.setState(4, "ON")
        
        self.scope.setBandwidth(1, "ON")
        self.scope.setBandwidth(2, "ON")
        self.scope.setBandwidth(3, "ON")
        self.scope.setBandwidth(4, "ON")
        
        #Siglent library hard codes trigger level to mV
        self.scope.setEdgeTrigger(3, 50, "FALL")
        
    def scopeShot(self):
        print ("Get Scope Shot")
        self.scope.clear()
        print ("ReadIDN Returns: " + str(self.scope.readIDN()))
        print ("next line")
        self.scope.clear()
    
        self.scope.scopeScreenCaptureCopyToPC("siglentImage.png")
        
        # loading image 
        self.pixmap = QPixmap("siglentImage.png") 
  
        # adding image to label 
        self.pictLabel.setText("Image Here") 
        self.pictLabel.setPixmap(self.pixmap) 
  
        # Optional, resize label to image size 
        self.pictLabel.resize(self.pixmap.width(), 
                          self.pixmap.height()) 
  
                
if __name__ == '__main__':
    
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    ex = MainWindow()
    app.exec_()  
