'''
Created on 02.11.2011

@author: michi
'''
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QGraphicsSimpleTextItem, QTransform

from geotiledmapobjectinfo import GeoTiledMapObjectInfo #@UnresolvedImport

class GeoTiledMapTextObjectInfo(GeoTiledMapObjectInfo):
    def __init__(self, mapData, mapObject):
        self.text = mapObject
        GeoTiledMapObjectInfo.__init__(self, mapData, mapObject)
        self.text.textChanged.connect(self.textChanged)
        self.text.fontChanged.connect(self.fontChanged)
        self.text.penChanged.connect(self.penChanged)
        self.text.brushChanged.connect(self.brushChanged)
        self.text.offsetChanged.connect(self.offsetChanged)
        self.text.alignmentChanged.connect(self.alignmentChanged)
        
        self.textItem = QGraphicsSimpleTextItem()
        self.graphicsItem = self.textItem
        
        self.penChanged(self.text.pen())
        self.brushChanged(self.text.brush())
        self.originChanged(self.text.origin())
        self.fontChanged(self.text.font())
        self.textChanged(self.text.text())
    
    def textChanged(self, text):
        self.textItem.setText(self.text.text())
        self._doAlignment()
        self.updateItem()
    
    def fontChanged(self, font):
        self.textItem.setFont(self.text.font())
        self._doAlignment()
        self.updateItem()
    
    def offsetChanged(self, offset):
        self._doAlignment()
        self.updateItem()
    
    def alignmentChanged(self, alignment):
        self._doAlignment()
        self.updateItem()
    
    def penChanged(self, pen):
        self.textItem.setPen(self.text.pen())
        self._doAlignment()
        self.updateItem()
    
    def brushChanged(self, brush):
        if self.textItem:
            self.textItem.setBrush(self.text.brush())
            self._doAlignment()
            self.updateItem()
    
    def _doAlignment(self):
        align = self.text.alignment()
        trans = QTransform()
        self.textItem.setTransform(trans)
        
        rect = self.textItem.boundingRect()
        center = rect.center()
        
        if align & Qt.AlignVCenter:
            trans.translate(0, -1 * center.y())
        elif align & Qt.AlignTop:
            trans.translate(0, -1 * rect.top())
        elif align & Qt.AlignBottom:
            trans.translate(0, -1 * rect.bottom())
        
        if align & Qt.AlignHCenter:
            trans.translate(-1 * center.x(), 0)
        elif align & Qt.AlignLeft:
            trans.translate(-1 * rect.left(), 0)
        elif align & Qt.AlignRight:
            trans.translate(-1 * rect.right(), 0)
        
        offset = self.text.offset()
        trans.translate(offset.x(), offset.y())
        self.textItem.setTransform(trans)