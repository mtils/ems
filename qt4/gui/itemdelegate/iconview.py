'''
Created on 05.07.2011

@author: michi
'''

from PyQt4.QtCore import QSize, QRect, QPoint, Qt, QString
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4, \
    QApplication, QTextDocument, QStyle, QAbstractTextDocumentLayout, QIcon,\
    QPainter, QFontMetrics, QPalette,QColor
from ems.qt4.util import variant_to_pyobject

class IconViewDelegate(QStyledItemDelegate):
    
    def __init__(self, *args, **kwargs):
        QStyledItemDelegate.__init__(self, *args, **kwargs)
        self.drawText = True
        self.alwaysUseActiveStyle = False
        self.additionalItemFeatures = None
        self.textAlignment = None

    def paint(self, painter, option, index):
        options = QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        options.showDecorationSelected = True

        style = QApplication.style() if options.widget is None \
            else options.widget.style()

        if self.alwaysUseActiveStyle:
            options.state = options.state | QStyle.State_Active

        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        #options.decorationAlignment = Qt.AlignCenter | Qt.AlignBottom
        options.decorationPosition = QStyleOptionViewItemV4.Top
        #options.direction = Qt.RightToLeft

        if not self.drawText:
            options.text = ""
            options.displayAlignment = Qt.AlignCenter | Qt.AlignVCenter
            style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        else:
            options.displayAlignment = Qt.AlignCenter | Qt.AlignVCenter
            if self.additionalItemFeatures is not None:
                options.features = options.features | self.additionalItemFeatures
            
            
            #options.WrapText = True
            
            style.drawControl(QStyle.CE_ItemViewItem, options, painter)

    def calculateTextSize(self, text=None):
        if text is None:
            text = 'XXXXXXXXXXXX'
        options = QStyleOptionViewItemV4()
        fm = options.fontMetrics
        
        #QApplication.style().sizeFromContents(QStyle.CT_ItemViewItem)
        #print self.paintEngine()
        #print self.paintEngine().painter()
        
        #painter = self.paintEngine().painter()
        #fm = painter.fontMetrics()
        return fm.size(Qt.TextSingleLine, QString.fromUtf8(text))
            
    
    def sizeHint__(self, option, index):
        sizeHint = QStyledItemDelegate.sizeHint(self, option, index)
        return sizeHint
    
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