'''
Created on 05.07.2011

@author: michi
'''

from PyQt4.QtCore import QSize, QRect, QPoint
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4, \
    QApplication, QTextDocument, QStyle, QAbstractTextDocumentLayout, QIcon,\
    QPainter

class IconViewDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        
        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        self.iconSize = QSize(60,60)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        options.text = ""
        myIcon = QIcon(options.icon)
        options.icon = QIcon()
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        leftTop = QPoint(options.rect.center().x()-self.iconSize.width()/2,
                         options.rect.center().y()-self.iconSize.height()/2)
        noTextRect = QRect( leftTop, self.iconSize)
        painter.drawImage(noTextRect, myIcon.pixmap(self.iconSize).toImage())
        
        
#        textRect = style.subElementRect(QStyle.SE_ItemViewItemText,
#                                        options)
        
        #painter.save()
        #painter.translate(textRect.topLeft())
        #painter.setClipRect(textRect.translated(-textRect.topLeft()))
        #painter.setClipRect(textRect)
        
        #doc.documentLayout().draw(painter, ctx)
        
        #painter.restore()
    
    def sizeHint_(self, option, index, manualText=None):
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        
        doc = QTextDocument()
        if manualText is None:
            doc.setHtml(options.text)
        else:
            doc.setHtml(manualText)
        #doc.setTextWidth(options.rect.width())
        #print options.rect.width(), doc.idealWidth(), doc.size().width()
        #return QSize(doc.size().width(),doc.size().height())
        #return QSize(doc.idealWidth(), doc.size().height())
        return QSize(doc.idealWidth(), doc.size().height())