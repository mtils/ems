from PyQt4.QtCore import QObject, pyqtSignal, QString, QEvent, Qt

class MouseEventEmitter(QObject):
    
    '''
       Emit the objectName
    '''
    doubleClicked = pyqtSignal(QString, Qt.MouseButtons)
    
    pressed = pyqtSignal(QString, Qt.MouseButtons)
    
    released = pyqtSignal(QString, Qt.MouseButtons)
    
    hoverEntered = pyqtSignal(QString)
    
    hoverLeaved = pyqtSignal(QString)
    
    _sourceObject = None
    
    _hoverEventsEnabled = False
    
    def __init__(self, sourceObject=None, parent=None):
        if sourceObject and parent is None:
            parent = sourceObject
        QObject.__init__(self, parent)
        if isinstance(sourceObject, QObject):
            self.setSourceObject(sourceObject)
    
    
    def sourceObject(self):
        return self._sourceObject
    

    def setSourceObject(self, sourceObject):
        '''
        @param: sourceObject QObject
        @return: self for fluid syntax
        @rtype: MouseEventEmitter
        '''
        if isinstance(self._sourceObject, QObject):
            self._sourceObject.removeEventFilter(self)
        self._sourceObject = sourceObject
        self._sourceObject.installEventFilter(self)
        if self._hoverEventsEnabled:
            self._sourceObject.setAttribute(Qt.WA_Hover, True)
        
        return self
    
    def setHoverEventsEnabled(self, enabled=True):
        self._hoverEventsEnabled = True
        if isinstance(self._sourceObject, QObject):
            self._sourceObject.setAttribute(Qt.WA_Hover, True)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonDblClick:
            self.doubleClicked.emit(obj.objectName(), event.button())
        if event.type() == QEvent.MouseButtonPress:
            self.pressed.emit(obj.objectName(), event.button())
        if event.type() == QEvent.MouseButtonRelease:
            self.released.emit(obj.objectName(), event.button())
        if event.type() == QEvent.HoverEnter:
            self.hoverEntered.emit(obj.objectName())
        if event.type() == QEvent.HoverLeave:
            self.hoverLeaved.emit(obj.objectName())
        return QObject.eventFilter(self, obj, event)