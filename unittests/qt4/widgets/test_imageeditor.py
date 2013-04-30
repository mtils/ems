#coding=utf-8
import os

from PyQt4.QtCore import pyqtSignal, QString, Qt, QEvent, QRectF
from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,\
    QVBoxLayout, QPixmap, QBrush, QColor, QToolBar, QSlider, QLabel, QWidget,\
    QHBoxLayout, QSpinBox, QPushButton, QAction, QApplication, QStyle,\
    QFileDialog, QIcon

from ems.qt4.gui.widgets.dialogable import DialogableWidget
from ems.qt4.systeminfo import SystemInfo
import ems.qt4.gui.widgets.icons

class ImageEditor(DialogableWidget):

    zoomLevelChanged = pyqtSignal(int)

    def __init__(self, pixmapOrPath=None, parent=None):
        DialogableWidget.__init__(self, parent)

        self._pixmap = QPixmap()
        self._pixmapItem = None
        self._zoomLevel = 100
        self._minimumZoomLevel = 10
        self._maximumZoomLevel = 500
        self._autoZoomEnabled = True
        self.rsrcPath = ':/imageEditor'

        self.setupUi()
        
        self.addStandardActions()

        if isinstance(pixmapOrPath, QPixmap):
            self.setPixmap(pixmapOrPath)
        if isinstance(pixmapOrPath, (basestring, QString)):
            self.loadPixmapFromPath(pixmapOrPath)

    def zoomLevel(self):
        return self._zoomLevel

    def setZoomLevel(self, zoomLevel):
        if self._zoomLevel == zoomLevel:
            return
        if zoomLevel > self._maximumZoomLevel or zoomLevel < self._minimumZoomLevel:
            return
        try:
            zoomLevelFloat = float(zoomLevel)/100.0
        except ZeroDivisionError:
            return
        
        #self._pixmapItem.resetTransform()
        #self._pixmapItem.setTransformOriginPoint(self._pixmapItem.boundingRect().center())
        #self._pixmapItem.scale(zoomLevelFloat, zoomLevelFloat)
        self.view.resetTransform()
        self.view.scale(zoomLevelFloat, zoomLevelFloat)
        pixmapRect = self._pixmapItem.mapRectToScene(self._pixmapItem.boundingRect())
        #print self._pixmapItem.mapRectToScene(pixmapRect)
        viewRect = QRectF(self.view.viewport().rect())
        sceneWidth = max(viewRect.width(), pixmapRect.width())
        sceneHeight = max(viewRect.height(), pixmapRect.height())
        sceneRect = QRectF(0.0, 0.0, sceneWidth, sceneHeight)
        #print sceneRect
        self.scene.setSceneRect(sceneRect)
        #self.view.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
        self.view.centerOn(self.scene.sceneRect().center())
        #pixmapRect.moveCenter(self.scene.sceneRect().center())
        #self._pixmapItem.setPos(pixmapRect.topLeft())
        self._zoomLevel = zoomLevel
        self.zoomLevelChanged.emit(self._zoomLevel)
        self.setAutoZoomEnabled(False)
    
    def addStandardActions(self):
        self.openAction = QAction(self.trUtf8('Bild laden'), self)
        self.openAction.setIcon(QApplication.instance().style().standardIcon(QStyle.SP_DialogOpenButton))
        self.openAction.triggered.connect(self.openImage)
        self.addAction(self.openAction)
        
        self.cropAction = QAction(self.trUtf8('Bild zuschneiden'), self)
        self.cropAction.setIcon(QIcon(':imageEdit/icons/frame_image.png'))
        self.cropAction.setCheckable(True)
        self.cropAction.triggered.connect(self.cropImage)
        self.addAction(self.cropAction)
        
    
    def openImage(self):
        filterString = SystemInfo.buildFilterString(SystemInfo.getSupportedExtensions(SystemInfo.Image))
        fileName = QFileDialog.getOpenFileName(self, self.trUtf8(u'Bilddatei auswählen'),'',
                                               self.trUtf8('Bilddateien %1').arg(QString.fromUtf8(filterString)))
        if not fileName:
            return
        
        fileName = unicode(fileName)
        if not os.path.exists(fileName):
            return
        
        self.loadPixmapFromPath(fileName)
    
    def cropImage(self):
        print "cropImage"
    
    def addAction(self, action, addToToolbar='main'):
        DialogableWidget.addAction(self, action)
        if addToToolbar == 'main':
            self.mainToolBar.addAction(action)

    def loadPixmapFromPath(self, path):
        self.setPixmap(QPixmap(path))

    def loadPixmapFromPixmap(self, pixmap):
        pass
    
    def eventFilter(self, view, event):
        if event.type() == QEvent.Wheel:
            #print "Wheel", event.delta()
            if event.modifiers() == Qt.ControlModifier:
                #prevAnchor = self.view.transformationAnchor()
                #self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                self.setZoomLevel(self._zoomLevel + int(event.delta()/10))
                #self.view.setTransformationAnchor(prevAnchor)
                return True
            elif event.modifiers() != Qt.NoModifier:
                return True
            
        return False

    def setupUi(self):
        self.setLayout(QVBoxLayout(self))
        self.mainToolBar = QToolBar(self)
        self.layout().addWidget(self.mainToolBar)

        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.layout().addWidget(self.view)
        self.scene.setBackgroundBrush(QBrush(QColor('#000')))
        self.view.setBackgroundBrush(QBrush(QColor('#000')))
        self.view.installEventFilter(self)
        self.view.viewport().installEventFilter(self)

        self.zoomBar = QWidget(self)
        self.zoomBar.setLayout(QHBoxLayout(self.zoomBar))
        self.layout().addWidget(self.zoomBar)
        self.zoomBar.layout().setContentsMargins(0,0,0,0)
        self.zoomLevelSlider = QSlider(Qt.Horizontal, self)
        self.zoomLevelSlider.setMinimum(self._minimumZoomLevel)
        self.zoomLevelSlider.setMaximum(self._maximumZoomLevel)
        self.zoomLevelSlider.setValue(self._zoomLevel)
        self.zoomLevelSlider.valueChanged.connect(self.setZoomLevel)
        self.zoomLevelChanged.connect(self.zoomLevelSlider.setValue)
        self.zoomBar.layout().addWidget(self.zoomLevelSlider)

        self.zoomLevelInput = QSpinBox(self.zoomBar)
        self.zoomBar.layout().addWidget(self.zoomLevelInput)
        self.zoomLevelInput.setMinimum(self._minimumZoomLevel)
        self.zoomLevelInput.setMaximum(self._maximumZoomLevel)
        self.zoomLevelInput.setValue(self._zoomLevel)
        self.zoomLevelInput.setSuffix(' %')
        self.zoomLevelSlider.valueChanged.connect(self.zoomLevelInput.setValue)
        self.zoomLevelInput.valueChanged.connect(self.zoomLevelSlider.setValue)
        
        self.zoomLevelAuto = QPushButton(self.trUtf8('Einpassen'), self)
        self.zoomBar.layout().addWidget(self.zoomLevelAuto)
        self.zoomLevelAuto.setCheckable(True)
        self.zoomLevelAuto.setChecked(self._autoZoomEnabled)
        self.zoomLevelAuto.toggled.connect(self.setAutoZoomEnabled)
        
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
    
    def isAutoZoomEnabled(self):
        return self._autoZoomEnabled
    
    def setAutoZoomEnabled(self, enabled):
        if self._autoZoomEnabled == enabled:
            return
        if enabled:
            self._performAutoZoom()
        self._autoZoomEnabled = enabled
        self.zoomLevelAuto.setChecked(self._autoZoomEnabled)

    def pixmap(self):
        return self._pixmap
    
    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.scene.clear()
        self._pixmapItem = QGraphicsPixmapItem(self._pixmap)
        #self._pixmapItem.setFlags(QGraphicsPixmapItem.ItemIsFocusable |
                                  #QGraphicsPixmapItem.ItemIsMovable |
                                  #QGraphicsPixmapItem.ItemIsSelectable)
        #self._pixmapItem.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(self._pixmapItem)
        self._performAutoZoom()
    
    def resizeEvent(self, event):
        DialogableWidget.resizeEvent(self, event)
        if self._autoZoomEnabled:
            self._performAutoZoom()
    
    def _performAutoZoom(self):
        #return
        self.view.fitInView(self._pixmapItem, Qt.KeepAspectRatio)
        tr = self.view.transform()
        ratio = float(self.view.viewport().rect().width()) / self.scene.sceneRect().width()
        zoomLevel = int(round(ratio*100))
        if zoomLevel < self._minimumZoomLevel:
            zoomLevel = self._minimumZoomLevel
        if zoomLevel > self._maximumZoomLevel:
            zoomLevel = self._maximumZoomLevel
        self._zoomLevel = zoomLevel

        for widget in (self.zoomLevelSlider, self.zoomLevelInput):
            widget.blockSignals(True)
            widget.setValue(self._zoomLevel)
            widget.blockSignals(False)
    
    def showEvent(self, event):
        DialogableWidget.showEvent(self, event)
        self._performAutoZoom()

    #def wheelEvent(self, event):
        #DialogableWidget.wheelEvent(self, event)
        #print "myOwnWheelEvent", event.delta()
        

if __name__ == '__main__':

    app = QApplication([])
    
    fileName = '/home/michi/Medien/Bilder/03072011422.jpg'
    fileName = '/home/michi/Medien/Bilder/22.4.2011 192.jpg'
    print __file__
    dlg = ImageEditor.toDialog(fileName)
    dlg.show()
    app.exec_()