'''
Created on 12.03.2015

@author: Waetzold Plaum
'''
import copy
from PyQt4 import QtGui, QtCore
from PyLinXData import * 
from PyLinXGui import BEasyWidget


import PX_Templates as PX_Templ

class PX_Dialogue_SimpleStimulate(QtGui.QDialog):
    
    def __init__(self, parent, variable, mainController, drawWidget):
        
        super(PX_Dialogue_SimpleStimulate, self).__init__(parent)
        
        layout = QtGui.QVBoxLayout(self)
        
        StimulationFunction = variable.get(u"StimulationFunction")
        if StimulationFunction == None:
            StimulationFunction = u"Constant"
       
        init_list = copy.deepcopy(PX_Templ.PX_DiagData.StimForm[StimulationFunction])
        # Get Data 
        for dictVar in init_list:
            attr = dictVar[u"Name"]
            if variable.isAttr(attr):
                value = variable.get(attr)
            else:
                value = 0.0
            dictVar[u"Value"] = unicode(value)
                        
        self.setLayout(layout)
        self.variable = variable
        self.drawWidget = drawWidget
        self.mainController = mainController
        
        self.listFunctions = [u"Constant", u"Sine", u"Ramp", u"Pulse", u"Step", u"Random"]
        self.combo = QtGui.QComboBox(self)
        counter = 0
        index = 0
        for function in self.listFunctions:
            self.combo.addItem(function)
            if StimulationFunction == function:
                index = counter
            counter +=1
        self.combo.setCurrentIndex(index)
        self.combo.setEditText(StimulationFunction)
        self.combo.activated[str].connect(self.onActivated)
        self.layout().addWidget(self.combo)

        easyWidget = BEasyWidget.EasyWidget(init_list)
        self.layout().addWidget(easyWidget)
        self.formWidget    = easyWidget

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.buttons.accepted.connect(self.on_accept)
        self.buttons.rejected.connect(self.on_reject)
        self.layout().addWidget(self.buttons)
        self.result = False
        
    def on_reject(self):
        self.hide()
        
    def on_accept(self):
        self.result = True
        values = self.formWidget.getValues()
        #self.variable._BContainer__Attributes.update(values)
        #print "values", values
        strValues = repr(values).replace(" ", "")
        ustrExec = u"set " + self.variable.get(u"Name") + u". " + unicode(strValues)
        self.mainController.execCommand(ustrExec)
        self.hide()
    
    def onActivated(self, text):
        text = str(text)
        self.variable.set(u"StimulationFunction", text)
        init_list = PX_Templ.PX_DiagData.StimForm[text]
        formWidget_New = BEasyWidget.EasyWidget(init_list)
        self.formWidget.setParent(None)
        self.buttons.setParent(None)
        del  self.formWidget
        self.formWidget = formWidget_New
        self.layout().addWidget(formWidget_New)
        self.layout().addWidget(self.buttons)
        self.adjustSize() 
        self.repaint()
        
    @staticmethod
    def getParams(parent, variable, mainController, drawWidget):
        dialog = PX_Dialogue_SimpleStimulate(parent, variable, mainController, drawWidget)
        result = dialog.exec_()
        drawWidget.repaint() 
        return dialog.result