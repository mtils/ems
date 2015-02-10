#coding=utf-8

import os.path
from PyQt4.QtCore import SIGNAL, QString, pyqtSignal, QUrl
from PyQt4.QtGui import  QDialog, QApplication, QGraphicsScene, QFileDialog, \
    QVector3D
from PyQt4.QtDeclarative import QDeclarativeView

from RectTestDialogUi import Ui_RectTestDialog #@UnresolvedImport

class RectTestDialog(QDialog,Ui_RectTestDialog):
    
    fileValidationChanged = pyqtSignal(bool)
    """
    Class Docs goes here
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.rObject = None
        self.inBuddySetAction = False
        self.currentInputFile = None
        self.setupUi()
        self.valid = False
        for letter in ('X','Y','Z'):
            self.connect(self.__getattribute__('axis3d' + letter + 'Input'),
                         SIGNAL('valueChanged(int)'),
                         self.updateBuddyInput)
            self.connect(self.__getattribute__('axis3d' + letter + 'Input2'),
                         SIGNAL('valueChanged(double)'),
                         self.updateBuddyInput)
        self.connect(self.fileInput2, SIGNAL("clicked()"),
                     self.onFileInput2Clicked)
        
        self.connect(self.fileInput, SIGNAL("textChanged(QString)"),
                     self.validateInputFile)
        
        self.connect(self, SIGNAL("fileValidationChanged(bool)"),
                     self.onFileValidationChange)
        self.fileInput.setText(os.path.join(os.path.dirname(__file__),'vector3dtest.qml'))
    
    def onFileValidationChange(self, valid):
        if valid:
            self.qmlView.setSource(QUrl.fromLocalFile(self.currentInputFile))
            self.rObject = self.qmlView.rootObject()
            
        else:
            print "Datei nicht valide"
    
    def validateInputFile(self, fileName):
        fileName = unicode(fileName)
        if os.path.isfile(fileName):
            if fileName.endswith(".qml"):
                self.currentInputFile = unicode(fileName)
                self.fileValidationChanged.emit(True)
                self.valid = True
                return
        self.fileValidationChanged.emit(False)
        self.valid = False
        
        
        
    def onFileInput2Clicked(self):
        caption = QString.fromUtf8("QML-Datei auswählen ")
        fileName = QFileDialog.getOpenFileName(self, caption)
        self.fileInput.setText(fileName)
        
    
        
    def setupUi(self):
        Ui_RectTestDialog.setupUi(self,self)
        self.qmlView.setOptimizationFlags(QDeclarativeView.DontSavePainterState)
        self.qmlView.setViewportUpdateMode(QDeclarativeView.BoundingRectViewportUpdate)
        self.qmlView.scene().setItemIndexMethod(QGraphicsScene.NoIndex)
        self.qmlView.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        for widget in (self.angleInput2,self.heightInput2,
                       self.widthInput2, self.xInput2,self.yInput2):
            
            self.connect(widget, SIGNAL("valueChanged(int)"),
                         self.setQmlValue)
        for widget in (self.axis3dXInput2,
                       self.axis3dYInput2,self.axis3dZInput2):
            self.connect(widget, SIGNAL("valueChanged(double)"),
                         self.setQmlValue)
        
        for widget in (self.colorInput,):
            self.connect(widget, SIGNAL("textChanged(QString)"),
                         self.setQmlValue)
    
    
    def setQmlValue(self, value):
        if not self.valid:
            return
        senderName = self.sender().objectName()
        for typ in ('x','y','width','height'):
            buildedSenderName = typ + 'Input2'
            if buildedSenderName == senderName:
                self.rObject.setValue(typ,value)
        if senderName == 'angleInput2':
            self.rObject.setRotationValue('angle',value)
        for letter in ('X','Y','Z'):
            buildedSenderName = 'axis3d' + letter + 'Input2'
            if senderName == buildedSenderName:
                self.rObject.setValue('axis3d',
                                      QVector3D(self.axis3dXInput2.value(),
                                                self.axis3dYInput2.value(),
                                                self.axis3dZInput2.value()))
        
            
        
            
        
        #print "%s: %s" % (senderName, value)
    
    def updateBuddyInput(self, value):
        sender = self.sender()
        objectName = unicode(sender.objectName())
        if objectName[-1] == '2':
            buddy = objectName[0:-1]
            buddyValue = int(value * 100)
        else:
            buddy = objectName + '2'
            buddyValue = float(value) / 100.0
        buddyWidget = self.__getattribute__(buddy)
        if (buddyWidget.value() != buddyValue) and not self.inBuddySetAction:
            self.inBuddySetAction = True
            buddyWidget.setValue(buddyValue)
            self.inBuddySetAction = False

if __name__ == '__main__':
    import sys
    app = QApplication([])
    dlg = RectTestDialog()
    dlg.show()
    sys.exit(app.exec_())