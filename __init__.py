'''
Created on 30.10.2014

@author: Waetzold Plaum
'''
# General Libraries - alphabedic order
import copy
import cProfile
import ctypes
import inspect
import jsonpickle
import os
from PyQt4 import QtGui, QtCore, uic, Qt
import sys
import threading
import Queue
import codecs

# Project specific Libraries - alphabedic order
from PyLinXData import * 
from PyLinXGui import *
from PyLinXCtl import *
from PyLinXCodeGen import *
import PyLinXGui.PX_Templates as PX_Templ
import PyLinXData.PyLinXHelper as helper

class PyLinXMain(QtGui.QMainWindow):

    def __init__(self):
 
        super(PyLinXMain, self).__init__()
        
        reload(sys) 
        sys.setdefaultencoding('utf8')
        
        uiString = u".//Recources//Ui//PyLinX_v0_3.ui"
        self.ui = uic.loadUi(uiString)
        self.ui.setWindowIcon(QtGui.QIcon(r"pylinx_16.png"))
        self.ui.setWindowTitle('PyLinX')
        self.runThreadMessageQueue = Queue.Queue()
        QtGui.QApplication.setStyle( QtGui.QStyleFactory.create('cleanlooks') )
        
        
        # Main Data Structures

        self.mainController = PyLinXMainController.PyLinXMainController(mainWindow = self )
        self.mainController.set(u"LogLevel",1)
        self.mainController._BContainer__Attributes[u"bSimulationMode"] = False
        _rootGraphics = self.mainController.getb(u"rootGraphics")
        
        # ExampleData

        testvar  = PyLinXDataObjects.PX_PlottableVarElement(_rootGraphics, u"TestVar_0", 150,90, 15)
        testvar2 = PyLinXDataObjects.PX_PlottableVarElement(_rootGraphics, u"Variable_id4", 150,140, 15)
        testvar3 = PyLinXDataObjects.PX_PlottableVarElement(_rootGraphics, u"Variable_id3", 400,100, 15)
        plusOperator = PyLinXDataObjects.PX_PlottableBasicOperator(_rootGraphics , u"+",  300,100 )
        con  = PyLinXDataObjects.PX_PlottableConnector(_rootGraphics, testvar.ID,plusOperator.ID,   idxInPin=1)
        con2 = PyLinXDataObjects.PX_PlottableConnector(_rootGraphics, testvar2.ID,plusOperator.ID,  idxInPin=0)
        con3 = PyLinXDataObjects.PX_PlottableConnector(_rootGraphics, plusOperator.ID,testvar3.ID,  idxInPin=0)
#         print con.ID
#         print con2.ID
#         print con3.ID
#         
#         _rootGraphics.ls()
#         con.lsAttr()
#         con2.lsAttr()
#         con3.lsAttr()
        
        
                
        self.mainController.set(u"bConnectorPloting", False)     

        # Configuration
        
        # idx that indicates the selected tool
        self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
        # ID of the connector which is actually drawn
        self.mainController.set(u"ID_activeConnector", -1)
        # idx of the last selected Data-Viewer
        self.mainController.set(u"idxLastSelectedDataViewer", -1)
        self.mainController.set(u"idxOutPinConnectorPloting", None)

        # run Engine
        
        self.runEngine = None
        
        
        # Drawing GUI
        
        # Events
        
        self.stopRunEvent = threading.Event()
        self.repaintEvent = threading.Event()
        
        
        scrollingArea = QtGui.QScrollArea()
        horizongalLayout2 = QtGui.QHBoxLayout()
        drawWidget = PX_Widget_MainDrawArea.DrawWidget(self.mainController, self, self.repaintEvent )        
        self.drawWidget = drawWidget
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background,PX_Templ.color.background)
        drawWidget.setAutoFillBackground(True)
        drawWidget.setPalette(pal)
        
        
        self.mainController.set(u"bSimulationMode", False)
        
        #drawWidget.setBaseSize(1500,480)
        horizongalLayout2.addWidget(drawWidget)
        scrollingArea.setLayout(horizongalLayout2)
        horizongalLayout2.setSizeConstraint(1)
        #scrollingArea.setLineWidth(6)
        scrollingArea.setContentsMargins(-30,-30,-30,-30)
        #scrollingArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        #scrollingArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scrollingArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollingArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        
        # Has effect
        #scrollingArea.setFixedWidth(1000)
        scrollingArea.setMinimumWidth(500)
        self.ui.horizontalLayout.addWidget(scrollingArea)
        scrollingArea.setWidgetResizable(True)
        scrollingArea.setAutoFillBackground(False)
        #scrollingArea.setViewportMargins(0,0,0,0)
        self.ui.splitter.setStretchFactor(1,1)

        ## new UI
        if uiString == u"PyLinX_v0_4.ui":
            self.ui.tabWidget.setTabText(0,u"Elements")
            self.ui.tabWidget.setTabText(1,u"Libraries")
        
        #self.scene.addWidget(self.drawWidget)
        #self.ui.graphicsView.setScene(self.scene)

        self.ui.show()
        
        # Connecting Actions
        ####################
        
        # Menu-Bar
            
            # Programm
        
        self.ui.actionClose.triggered.connect(self.closeApplication)
        
            # Project
        
        self.ui.actionNewProject.triggered.connect(self.on_actionNewProject)
        self.ui.actionLoadProject.triggered.connect(self.on_actionLoadProject)
        self.ui.actionSave.triggered.connect(self.on_actionSave)
        self.ui.actionSave_As.triggered.connect(self.on_actionSave_As)
        
        # Tool-Bar
        
        self.ui.actionNewElement.triggered.connect(self.on_actionNewElement)
        self.ui.actionNewElement.setCheckable(True)
        self.ui.actionOsci.setCheckable(True)
        self.ui.actionNewPlus.triggered.connect(self.on_actionNewPlus)
        self.ui.actionNewMinus.triggered.connect(self.on_actionNewMinus)
        self.ui.actionNewMultiplication.triggered.connect(self.on_actionNewMultiplication)
        self.ui.actionNewDivision.triggered.connect(self.on_actionNewDivision)
        
        self.ui.actionOsci.triggered.connect(self.on_actionOsci)
        self.ui.actionNewPlus.setCheckable(True)
        self.ui.actionNewMinus.setCheckable(True)
        self.ui.actionNewMultiplication.setCheckable(True)
        self.ui.actionNewDivision.setCheckable(True)
        self.ui.actionRun.setEnabled(False)
        self.ui.actionOsci.setEnabled(False)
        self.ui.actionActivate_Simulation_Mode.triggered.connect(self.on_Activate_Simulation_Mode)
        self.ui.actionRun.triggered.connect(self.on_run)
        self.ui.actionStop.triggered.connect(self.on_stop)
        

        self.ui.resize(800,600)
        
        
######################
# Methods
#####################


# Callbacks
####################

    def closeApplication(self):
        
        print "CLOSE!"
        if QtGui.QMessageBox.question(None, u"", u"Soll PyLinX wirklich beendet werden?", \
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,QtGui.QMessageBox.No)\
                 == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
            
    def on_actionNewElement(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newVarElement) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewPlus(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newPlus) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)

    def on_actionNewMinus(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newMinus) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewMultiplication(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newMultiplication) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_actionNewDivision(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newDivision) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)

            
    def on_actionSave(self):
        rootGraphics = self.mainController.getb(u"rootGraphics")
        if rootGraphics .isAttr(u"strSavePath"):
            strSavePath = rootGraphics.get(u"strSavePath")
            self.__saveProject(strSavePath)
        else:
            self.on_actionSave_As()

    
    def on_actionSave_As(self):
        if self.mainController.isAttr(u"strSavePath"):
            strSavePath_old = self.mainController.get(u"strSavePath")
            (strPath, strSavePath_old_file) = os.path.split(strSavePath_old)
        else:
            strPath = os.getcwd()
        strSavePath= self.__showFileSaveSelectionDialog(strPath, bDir = False, strExt = u"pson", strHeader =u"Select File to save Project...")
        (strSavePath_base,strSavePath_ext) = os.path.splitext(strSavePath)
        if not  strSavePath_ext == u".pson":
            strSavePath = strSavePath_base + u".pson"
        self.__saveProject(strSavePath)

     
    def __saveProject(self, strSavePath):    
        
        _file = codecs.open(strSavePath, encoding='utf-8', mode='w')
        project = self.mainController.getb(u"rootGraphics")
        project._BContainer__parent = None
        pickledObject = jsonpickle.encode(project, keys=True, unpicklable=False)
        _file.write(pickledObject)
        _file.close()
        rootGraphics = self.mainController.getb(u"rootGraphics")
        rootGraphics.set(u"strSavePath", strSavePath)  

   
    def on_actionLoadProject(self):
        strPath = os.getcwd()
        strSavePath= self.__showFileSelectionLoadDialog(strPath, bDir = False,strHeader ="Select File to load Project...")  
        _file = open(strSavePath)
        
        newProject = jsonpickle.decode(_file.read(), keys=True)
        oldProject = self.mainController.getb(u"rootGraphics")
        self.mainController.paste(newProject,u"rootGraphics",  bForceOverwrite = True)
        self.drawWidget.newProject(newProject)
        del oldProject
        self.mainController.set(u"bSimulationMode", False)
        maxID = newProject.getMaxID()
        PyLinXDataObjects.PX_IdObject._PX_IdObject__ID = maxID + 1
        self.drawWidget.repaint()
    
    def on_actionNewProject(self):
        rootGraphicsNew = PyLinXDataObjects.PX_PlottableObject(u"rootGraphics")
        self.mainController.delete(u"rootGraphics")
        self.mainController.set(u"bSimulationMode", False)
        self.mainController.paste(rootGraphicsNew)
        self.drawWidget.activeGraphics = rootGraphicsNew
        self.drawWidget.repaint()

    def __showFileSaveSelectionDialog(self,strPath = None, bDir = False, strExt= None, strHeader = None):
        
        if strPath == None:
            strPath = os.getcwd()
        if strHeader == None:
            if bDir:
                strHeader = u"Select Directory..."
            else:
                strHeader = u"Select File..."
        if bDir:
            strExt = strPath,QtGui.QFileDialog.ShowDirsOnly            
        return unicode(QtGui.QFileDialog.getSaveFileName(self.ui,strHeader,strPath,strExt))
    

    def __showFileSelectionLoadDialog(self, strPath = None, bDir = False, strExt = u"", strHeader = None):
        if strPath == None:
            strPath = os.getcwd()
        if strHeader == None:
            if bDir:
                strHeader = u"Select Directory..."
            else:
                strHeader = u"Select File..."
        if bDir:
            strExt = strPath,QtGui.QFileDialog.ShowDirsOnly            
        return unicode(QtGui.QFileDialog.getOpenFileName(self.ui,strHeader,strPath,strExt))
        
        
    def on_Activate_Simulation_Mode(self):
        
        bSimulationMode = self.mainController.get(u"bSimulationMode")
        if bSimulationMode:
            #self.mainController.set(u"bSimulationMode", False)
            self.mainController.execCommand(u"set @mainController.bSimulationMode False")
        else:
#             runEngine = PyLinXRunEngine.PX_CodeGenerator(self.mainController, self)
#             self.mainController.paste(runEngine, bForceOverwrite=True)
            #self.mainController.set(u"bSimulationMode", True)
            self.mainController.execCommand(u"set @mainController.bSimulationMode True")
        self.drawWidget.repaint()
        
    def on_run(self):
        
        self.runEngine = self.mainController.getb(u"PX_CodeGeerator")
        self.runEngine.startRun(self.drawWidget, self.stopRunEvent, self.repaintEvent)
        self.mainController.set(u"bSimulationRunning", True)
        
    def on_actionOsci(self):
        
        if self.mainController.get(u"idxToolSelected") == helper.ToolSelected.none:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.newVarDispObj) 
        else:
            self.mainController.set(u"idxToolSelected", helper.ToolSelected.none)
            
    def on_stop(self):
        self.runThreadMessageQueue.put(u"stopRun")
        

def run():
    app = QtGui.QApplication(sys.argv)
    obj = PyLinXMain()   
    app.exec_()
    
    
if __name__ == '__main__':
    
    PROFILE = False
    
    if PROFILE:
        cProfile.run('run()')
    else:
        run()
