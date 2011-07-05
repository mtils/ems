'''
Created on 05.07.2011

@author: michi
'''

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4, \
    QApplication, QTextDocument, QStyle, QAbstractTextDocumentLayout

class HtmlDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        
        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        
        #print options.text
        doc = QTextDocument()
        doc.setHtml(options.text)
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
    
    def sizeHint(self, option, index):
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        
        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QSize(doc.idealWidth(), doc.size().height())