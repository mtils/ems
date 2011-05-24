from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import  QDialog, QApplication, QGraphicsScene
from PyQt4.QtDeclarative import QDeclarativeView

from RectTestDialogUi import Ui_RectTestDialog

class RectTestDialog(QDialog,Ui_RectTestDialog):
    
    """
    Class Docs goes here
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.inBuddySetAction = False
        self.setupUi()
        for letter in ('X','Y','Z'):
            self.connect(self.__getattribute__('axis3d' + letter + 'Input'),
                         SIGNAL('valueChanged(int)'),
                         self.updateBuddyInput)
            self.connect(self.__getattribute__('axis3d' + letter + 'Input2'),
                         SIGNAL('valueChanged(double)'),
                         self.updateBuddyInput)
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
        senderName = self.sender().objectName()
        print "%s: %s" % (senderName, value)
    
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