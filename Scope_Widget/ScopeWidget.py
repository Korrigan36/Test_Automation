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

#The following is required to get the logo on the task bar, not sure why, internet code
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
    
    #Instrument Types is a dictionary
    instrumentList = []
    instrumentTypes = {}
    instrumentKey = "Uninitialized Key"

    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.configInstrument = Instrument()
        self.instrumentList = self.configInstrument.listInstruments()
        self.instrumentTypes = self.configInstrument.listInstrumentTypes()

        self.initUI()

    def initUI(self): 
        
        self.setGeometry(300, 300, 1000, 400)
        self.setWindowTitle('Tektronix Channel Label Widget')
        self.setWindowIcon(QIcon('Steam_icon_logo.gif')) 
        
        instrumentGroupBox  = QGroupBox()
        instrumentGrid      = QGridLayout()
        
        self.scopeComboBox = QComboBox()
        for index in range (0, len(self.instrumentList)):
            self.scopeComboBox.addItem(self.instrumentList[index].rstrip())    
        instrumentGrid.addWidget(self.scopeComboBox, 0, 0)
        
        self.enetButton = QCheckBox("Ethernet")
        instrumentGrid.addWidget(self.enetButton, 1, 0)
        

        self.enetListBox = QLineEdit()
        self.enetListBox.setText("172.18.18.24")
        instrumentGrid.addWidget(self.enetListBox, 1, 1)

        self.initScopeButton = QPushButton('Initialize Scope', self)
        self.initScopeButton.clicked[bool].connect(self.initScope)
        
        instrumentGrid.addWidget(self.initScopeButton, 2, 0)

        scopeLabel = QLabel(self)
        scopeLabel.setText("Scope Type")
        instrumentGrid.addWidget(scopeLabel, 3, 0)

        self.scopeIDN = QLabel(self)
        self.scopeIDN.setText(self.instrumentName)
        instrumentGrid.addWidget(self.scopeIDN, 4, 0)
        
        instrumentGroupBox.setLayout(instrumentGrid)

        startButtonGroupBox  = QGroupBox()
        startButtonLayout    = QHBoxLayout()
        self.startStopButton = QPushButton('Set Labels', self)
        
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
        self.ch1ListBox.setText("GFX @ Slammer")
        listBoxGrid.addWidget(self.ch1ListBox, 0, 1)

        self.ch2Label = QLabel(self)
        self.ch2Label.setText("CH2")
        listBoxGrid.addWidget(self.ch2Label, 1, 0)
        
        self.ch2ListBox = QLineEdit()
        self.ch2ListBox.setText("Sig Gen")
        listBoxGrid.addWidget(self.ch2ListBox, 1, 1)

        self.ch3Label = QLabel(self)
        self.ch3Label.setText("CH3")
        listBoxGrid.addWidget(self.ch3Label, 2, 0)
        
        self.ch3ListBox = QLineEdit()
        self.ch3ListBox.setText("Vin")
        listBoxGrid.addWidget(self.ch3ListBox, 2, 1)

        self.ch4Label = QLabel(self)
        self.ch4Label.setText("CH4")
        listBoxGrid.addWidget(self.ch4Label, 3, 0)
        
        self.ch4ListBox = QLineEdit()
        self.ch4ListBox.setText("VBAT")
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
        self.annotationListBox.setText("25A Load Step, 5A DC Load")
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
        
        if self.enetButton.isChecked():
            self.instrumentName = self.enetListBox.text()
        else:
            self.instrumentName = self.scopeComboBox.currentText()

        self.scope, self.scopeName = self.configInstrument.initInstrument(self.instrumentName)
        
        if self.scope != None:
        
            print ("Configured Scope: " + self.scopeName)
            
            self.scopeIDN.setText(self.scopeName)
    
            self.startStopButton.setEnabled(True)
            
        else:
            print("Instrument init failed: " + self.scopeName)

    def startStopTest(self):
        
        
        self.scope.setLabel(1, self.ch1ListBox.text())
        self.scope.setLabel(2, self.ch2ListBox.text())
        self.scope.setLabel(3, self.ch3ListBox.text())
        self.scope.setLabel(4, self.ch4ListBox.text())

        self.scope.scope_SetAnnotation( self.annotationListBox.text(), 580, 720)

    def closeEvent(self, event):
        print("Closing Device")
        self.scope.closeDevice() 
      
if __name__ == '__main__':
    
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    ex = MainWindow()
    app.exec_()  
