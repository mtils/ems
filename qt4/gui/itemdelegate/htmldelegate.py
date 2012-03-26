'''
Created on 05.07.2011

@author: michi
'''

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4, \
    QApplication, QTextDocument, QStyle, QAbstractTextDocumentLayout

class HtmlDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index, manualText=None):
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        
        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        
        
        doc = QTextDocument()
        if manualText is None:
            doc.setHtml(options.text)
        else:
            doc.setHtml(manualText)
        #doc.setPlainText(options.text)
        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        
        ctx = QAbstractTextDocumentLayout.PaintContext()
        #print ctx
        
        textRect = style.subElementRect(QStyle.SE_ItemViewItemText,
                                        options)
        
        painter.save()
        painter.translate(textRect.topLeft())
        #painter.setClipRect(textRect.translated(-textRect.topLeft()))
        #painter.setClipRect(textRect)
        
        doc.documentLayout().draw(painter, ctx)
        
        painter.restore()
    
    def sizeHint(self, option, index, manualText=None):
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