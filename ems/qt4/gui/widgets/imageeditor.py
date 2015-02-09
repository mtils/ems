#coding=utf-8
import os

from PyQt4.QtCore import pyqtSignal, QString, Qt, QEvent, QRectF, QResource,\
    QRect, QPoint, QSize
from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,\
    QVBoxLayout, QPixmap, QBrush, QColor, QToolBar, QSlider, QLabel, QWidget,\
    QHBoxLayout, QSpinBox, QPushButton, QAction, QApplication, QStyle,\
    QFileDialog, QIcon, QLineEdit, QSizePolicy, QPalette, QPainter, QPen, QImage

from ems.qt4.application import MainApplication
from ems.qt4.gui.widgets.dialogable import DialogableWidget
from ems.qt4.systeminfo import SystemInfo
from ems.qt4.gui.widgets.input.spinboxlabel import SpinBoxLabel

class CropOverlay(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setPalette(QPalette(Qt.transparent))
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFocusPolicy(Qt.NoFocus)
        parent.installEventFilter(self)
        self.resize(parent.size())
        self._aspectRatio = (1,1)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor(0,0,0,180)
        brush = QBrush(color, Qt.SolidPattern)

        targetRect = self.targetRect()

        myRect = self.rect()
        
        #painter.fillRect(self.rect(), brush)
        #painter.eraseRect(targetRect)
        
        #return
        topRect = QRect(self.pos(),QPoint(myRect.bottomRight().x(),
                                           targetRect.topLeft().y()-1))
        
        bottomRect = QRect(QPoint(self.pos().x(),
                                   targetRect.bottomRight().y()+1),
                            myRect.bottomRight())
        
        leftRect = QRect(QPoint(self.pos().x(),
                                 topRect.bottomLeft().y()+1),
                                 targetRect.bottomLeft())
        
        
        rightRect = QRect(targetRect.topRight(),
                                 QPoint(myRect.bottomRight().x(),
                                        targetRect.bottomRight().y()))
        
        painter.fillRect(topRect, brush)
        painter.fillRect(bottomRect, brush)
        painter.fillRect(leftRect, brush)
        painter.fillRect(rightRect, brush)
    
    def eventFilter(self, parent, event):
        if event.type() == QEvent.Resize:
            #self.parent().resizeEvent(event)
            #self.resize(self.parent().viewport().size())
            #return True
            self.resize(event.size())
            
            #print 'view',self.parent().size()
            #print 'viewport',self.parent().viewport().size()
            #print 'widget',self.parent().widget().size()
            #self.resize(self.parent().viewport().size())
        #elif event.type() == QEvent.LayoutRequest:
            #print event
        #elif event.type() not in (QEvent.Paint,):
            #print event.type()
        return False
    
    def setAspectRatio(self, horizontal, vertical):
        self._aspectRatio = (horizontal, vertical)
    
    def targetRect(self):
        myRect = self.rect()
        targetWidth = min(self.width(), self.height()) / 4 * 3
        #targetWidth = min(targetWidth, self.width(), self.height())
        holeOriginX = (myRect.width() / 2 - targetWidth / 2) + self.pos().x()
        holeOriginY = (myRect.height() / 2 - targetWidth / 2) + self.pos().y()
        targetRect = QRect(QPoint(holeOriginX, holeOriginY), QSize(targetWidth, targetWidth))
        
        return targetRect
    
    def setAspectRatio(self, horizontal, vertical):
        pass

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
        self.rsrcPath = ':/ImageEditor'
        self._rotation = 0
        
        self._cropOverlay = None
        
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

        prevViewportTL = self.view.mapToScene(self.view.viewport().rect().topLeft())
        prevViewportBR = self.view.mapToScene(self.view.viewport().rect().bottomRight())
        prevViewportCenter = QRectF(prevViewportTL, prevViewportBR).center()

        self.view.resetTransform()
        self.view.scale(zoomLevelFloat, zoomLevelFloat)
        self.view.rotate(float(self._rotation))
        pixmapRect = self._pixmapItem.mapRectToScene(self._pixmapItem.boundingRect())
        #print self._pixmapItem.mapRectToScene(pixmapRect)
        viewRect = QRectF(self.view.viewport().rect())
        sceneWidth = max(viewRect.width(), pixmapRect.width())
        sceneHeight = max(viewRect.height(), pixmapRect.height())
        sceneRect = QRectF(0.0, 0.0, sceneWidth, sceneHeight)
        #print sceneRect
        self.scene.setSceneRect(sceneRect)
        #self.view.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
        #self.view.centerOn(self.scene.sceneRect().center())

        self.view.centerOn(prevViewportCenter)
        #pixmapRect.moveCenter(self.scene.sceneRect().center())
        #self._pixmapItem.setPos(pixmapRect.topLeft())
        self._zoomLevel = zoomLevel
        self.zoomLevelChanged.emit(self._zoomLevel)
        self.setAutoZoomEnabled(False)
    
    def rotation(self):
        return self._rotation
    
    def setRotation(self, rotation):
        if self._rotation == rotation:
            return
        if rotation > 180 or rotation < -180:
            return
        self._rotation = rotation
        self.view.resetTransform()
        self.view.rotate(float(self._rotation))
        self.view.scale(float(self._zoomLevel)/100.0,float(self._zoomLevel)/100.0)
        self.rotationSlider.setValue(rotation)
    
    def setCropOverlayVisible(self, visible):
        self.cropOverlay().setVisible(visible)
        
    def cropOverlay(self):
        if self._cropOverlay is None:
            self._cropOverlay = CropOverlay(self.view)
        return self._cropOverlay
    
    def addStandardActions(self):

        res = QResource(self.rsrcPath + '/icons/frame_image.png')
        if not res.isValid():
            absPath = os.path.dirname(os.path.abspath(__file__))
            lastPart = ''
            path = []
            if os.sep == '/':
                path.append(os.sep)
            for part in absPath.split(os.sep):
                if part:
                    path.append(part)
                if lastPart == 'lib' and part == 'ems':
                    break
                lastPart = part
            path += ('qt4','gui','widgets','icons.rcc')
            rccPath = os.path.join(*path)

        self.openAction = QAction(self.trUtf8('Bild laden'), self)
        self.openAction.setIcon(QApplication.instance().style().standardIcon(QStyle.SP_DialogOpenButton))
        self.openAction.triggered.connect(self.openImage)
        self.addAction(self.openAction)
        
        self.cropAction = QAction(self.trUtf8('Bild zuschneiden'), self)
        self.cropAction.setIcon(QIcon(self.rsrcPath + '/icons/frame_image.png'))
        self.cropAction.setCheckable(True)
        self.cropAction.toggled.connect(self.cropImage)
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
    
    def cropImage(self, state):
        self.setCropOverlayVisible(state)
    
    def doCrop(self):
        
        #painter = QPainter(image)
        targetRect = self.cropOverlay().targetRect()
        aspectRatioFactor = float(targetRect.width()) / float(targetRect.height())
        width = self._pixmapItem.boundingRect().width()
        imageSize = QSize(width,width/int(round(aspectRatioFactor)))
        image = QImage(imageSize, QImage.Format_ARGB32)
        imagePainter = QPainter(image)
        imagePainter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        #imageSize = QSize(int(round(targetRect.width() / (self._zoomLevel/100))),
                          #int(round(targetRect.height() / (self._zoomLevel/100))))
        #print imageSize
        self.view.render(imagePainter, QRectF(image.rect()), targetRect)
        imagePainter.end()
        pixmap = QPixmap.fromImage(image)
        self.cropAction.setChecked(False)
        self.setPixmap(pixmap)
        self._performAutoZoom()

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
        
        self.viewContainer = QWidget(self)
        self.viewContainer.setLayout(QHBoxLayout(self.viewContainer))
        self.viewContainer.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.viewContainer)

        self.viewContainer.layout().addWidget(self.view)

        self.rotationBar = QWidget(self)
        self.viewContainer.layout().addWidget(self.rotationBar)
        self.rotationBar.setLayout(QVBoxLayout(self.rotationBar))
        self.rotationBar.layout().setContentsMargins(0,0,0,0)
        self.viewContainer.layout().addWidget(self.rotationBar)

        self.rotationSlider = QSlider(self.rotationBar)
        self.rotationBar.layout().addWidget(self.rotationSlider)
        self.rotationInput = SpinBoxLabel(self.rotationBar)
        self.rotationInput.setFrame(False)
        self.rotationInput.setSuffix(QString.fromUtf8(u' °'))

        self.rotationInput.setFixedSize(self.rotationInput.minimumSizeHint())
        
        self.rotationBar.layout().setAlignment(Qt.AlignCenter)
        self.rotationBar.layout().setAlignment(self.rotationSlider, Qt.AlignHCenter)
        self.rotationInput.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.rotationBar.layout().addWidget(self.rotationInput)
        
        self.rotationInput.setStyleSheet('background-color: transparent;')
        
        
        self.rotationInput.setRange(-180,180)
        self.rotationSlider.setRange(-180,180)
        self.rotationSlider.valueChanged.connect(self.rotationInput.setValue)
        self.rotationInput.valueChanged.connect(self.rotationSlider.setValue)
        self.rotationSlider.setValue(0)
        
        self.rotationSlider.valueChanged.connect(self.setRotation)
        
        self.scene.setBackgroundBrush(QBrush(QColor('#000')))
        self.view.setBackgroundBrush(QBrush(QColor('#000')))
        self.view.installEventFilter(self)
        self.view.viewport().installEventFilter(self)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

        self.zoomLevelInput = SpinBoxLabel(self.zoomBar)
        self.zoomBar.layout().addWidget(self.zoomLevelInput)
        self.zoomLevelInput.setMinimum(self._minimumZoomLevel)
        self.zoomLevelInput.setMaximum(self._maximumZoomLevel)
        self.zoomLevelInput.setValue(self._zoomLevel)
        self.zoomLevelInput.setSuffix(' %')
        self.zoomLevelInput.setFrame(False)
        self.zoomLevelInput.setStyleSheet('background-color: transparent;')
        
        self.zoomLevelInput.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.zoomLevelSlider.valueChanged.connect(self.zoomLevelInput.setValue)
        self.zoomLevelInput.valueChanged.connect(self.zoomLevelSlider.setValue)
        
        self.zoomLevelAuto = QPushButton(self.trUtf8('Einpassen'), self)
        self.zoomBar.layout().addWidget(self.zoomLevelAuto)
        self.zoomLevelAuto.setCheckable(True)
        self.zoomLevelAuto.setChecked(self._autoZoomEnabled)
        self.zoomLevelAuto.toggled.connect(self.setAutoZoomEnabled)
        
        #self.zoomBar.layout().addWidget(self.rotationInput)
        
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(self.view.AnchorViewCenter)
        self.view.setRenderHint(QPainter.Antialiasing)
    
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
        self.view.resetTransform()
        self._pixmapItem = QGraphicsPixmapItem(self._pixmap)

        #self._pixmapItem.setFlags(QGraphicsPixmapItem.ItemIsFocusable |
                                  #QGraphicsPixmapItem.ItemIsMovable |
                                  #QGraphicsPixmapItem.ItemIsSelectable)
        #self._pixmapItem.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(self._pixmapItem)
        self.setZoomLevel(100)
        self.setRotation(0)
        if self.isAutoZoomEnabled():
            self._performAutoZoom()
    
    def resizeEvent(self, event):
        prevViewportTL = self.view.mapToScene(self.view.viewport().rect().topLeft())
        prevViewportBR = self.view.mapToScene(self.view.viewport().rect().bottomRight())
        prevViewportCenter = QRectF(prevViewportTL, prevViewportBR).center()
        
        DialogableWidget.resizeEvent(self, event)
        if self._autoZoomEnabled:
            self._performAutoZoom()
        else:
            self.view.centerOn(prevViewportCenter)

    def _performAutoZoom(self):
        self.view.fitInView(self._pixmapItem, Qt.KeepAspectRatio)
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
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if self.cropAction.isChecked():
                self.doCrop()
        return DialogableWidget.keyPressEvent(self, event)