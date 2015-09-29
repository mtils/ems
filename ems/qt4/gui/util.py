'''
Created on 10.07.2011

@author: michi
'''
import sys

from PyQt4.QtCore import QObject, QRectF, QPointF, QSizeF, Qt

from PyQt4.QtGui import QTreeWidgetItem, QFontMetrics, QFont, QPrinter
from PyQt4.QtGui import QPalette, QDialogButtonBox, QVBoxLayout, QHBoxLayout
from PyQt4.QtGui import QFormLayout, QGridLayout

from ems.qt4.util import hassig


class FlatTreeBuilderMixin(QObject):
    def addItemFlat(self, textsOrItem, depth=0):
        if not hasattr(self, '_flatItemTree'):
            self._flatItemTree = {}
        if isinstance(textsOrItem, QTreeWidgetItem):
            treeWidgetItem = textsOrItem
        else:
            treeWidgetItem = QTreeWidgetItem(textsOrItem)
            
        self._flatItemTree[depth] = treeWidgetItem
        
        if depth == 0:
            self.addTopLevelItem(self._flatItemTree[depth])
        else:
            
            #newItem = QTreeWidgetItem(textsOrItem)
            self._flatItemTree[depth-1].addChild(treeWidgetItem)
            #self._flatItemTree[depth] = newItem

class QTextDocumentHelper(object):
    @staticmethod
    def printDocumentPaginated(doc, printer, painter):
        '''
        Print a QDextDocument and paginates it to a printer depending on its
        PageSize.
        This method is copied from QTextDocument.print(), which does not allow
        to use a predifined qpainter
        
        @param doc: The QTextDocument you wanna print
        @type doc: QTextDocument
        @param printer: The printer
        @type printer: QPrinter
        @param painter: The painter
        @type painter: QPainter
        @return: Returns the number of pages
        @rtype: int
        '''
        
        #Check that there is a valid device to print to
        if not painter.isActive():
            return
        
        
        if not doc.documentLayout():
            return
        
        body = QRectF(QPointF(0,0), doc.pageSize())
        pageNumberPos = QPointF()
        
        if doc.pageSize().isValid() and doc.pageSize().height() != sys.maxint:
            dev = doc.documentLayout().paintDevice()
            if not dev:
                raise TypeError("I need doc.documentLayout().paintDevice()")
            
            sourceDpiX = dev.logicalDpiX()
            sourceDpiY = dev.logicalDpiY()
            
            dpiScaleX = float(printer.logicalDpiX()) / sourceDpiX
            dpiScaleY = float(printer.logicalDpiY()) / sourceDpiY
            
            # scale to dpi
            painter.scale(dpiScaleX, dpiScaleY);

            scaledPageSize = doc.pageSize()
            scaledPageSize.setWidth(scaledPageSize.width() * dpiScaleX)
            scaledPageSize.setHeight(scaledPageSize.height() * dpiScaleY)
            
            printerPageSize = QSizeF(printer.width(), printer.height())
            
            # scale to page
            painter.scale(printerPageSize.width() / scaledPageSize.width(),
                          printerPageSize.height() / scaledPageSize.height())
            
        else:
            doc = doc.clone(doc)
            clonedDoc = doc.clone(doc)
            
            layout = doc.documentLayout()
            layout.setPaintDevice(painter.device())
            
            dpiy = painter.device().logicalDpiY()
            
            margin = int((2.0/2.54)*dpiy) # 2 cm margins
            
            fmt = doc.rootFrame().frameFormat()
            fmt.setMargin(margin)
            
            doc.rootFrame().setFrameFormat(fmt)
            
            body = QRectF(0, 0, painter.device().width(), painter.device().height())
            pageNumberPos = QPointF(body.width() - margin,
                                 body.height() - margin
                                 + QFontMetrics(doc.defaultFont(), painter.device()).ascent()
                                 + 5 * painter.device().logicalDpiY() / 72)
            
            font = QFont(doc.defaultFont())
            font.setPointSize(10) #we define 10pt to be a nice base size for printing
            clonedDoc.setDefaultFont(font)
            clonedDoc.setPageSize(body.size())
        
        docCopies = 0
        pageCopies = 0
        
        if printer.collateCopies() == True:
            docCopies = 1
            pageCopies = printer.numCopies()
        else:
            docCopies = printer.numCopies()
            pageCopies = 1
        
        
        fromPage = printer.fromPage()
        toPage = printer.toPage()
        ascending = True
        
        if fromPage == 0 and toPage == 0:
            fromPage = 1
            toPage = doc.pageCount()
        
        if printer.pageOrder() == QPrinter.LastPageFirst:
            tmp = fromPage
            fromPage = toPage
            toPage = tmp
            ascending = False
        
        for i in range(docCopies):
            
            page = fromPage
            while True:
                for j in range(pageCopies):
                    if printer.printerState() in (QPrinter.Aborted,
                                                  QPrinter.Error):
                        return
                    QTextDocumentHelper.printPage(page, painter, doc, body,
                                                  pageNumberPos)
                    if j < (pageCopies - 1):
                        printer.newPage()
                
                if page == toPage:
                    break
                
                if ascending:
                    page += 1
                else:
                    page -= 1
                
                printer.newPage()
                
            if i < (docCopies - 1):
                printer.newPage()
        
        return i
    
    @staticmethod
    def printPage(index, painter, doc, body, pageNumberPos):
        painter.save()
        painter.translate(body.left(), body.top() - (index - 1) * body.height())
        view = QRectF(0, (index - 1) * body.height(), body.width(), body.height())
        
        layout = doc.documentLayout()
        ctx = doc.documentLayout().PaintContext()
        
        painter.setClipRect(view)
        ctx.clip = view
        
        '''don't use the system palette text as default text color, on HP/UX
        for example that's white, and white text on white paper doesn't
        look that nice'''
        ctx.palette.setColor(QPalette.Text, Qt.black)
        
        layout.draw(painter, ctx)
        
#        if not pageNumberPos.isNull():
#            painter.setClipping(False)
#            painter.setFont(QFont(doc.defaultFont()))
#            pageString = QString.number(index)
        painter.restore()

def _addButtonBox2Dialog(dlg):

    layout = dlg.layout()

    if layout is None:
        raise TypeError("The Widget needs a layout to assign the buttons")

    if hasattr(dlg, 'dialogButtonHint'):
        dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
        dlg.dialogButtonHint.layout().addWidget(dlg.buttonBox)
        return dlg.buttonBox

    if isinstance(layout, QVBoxLayout):
        dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
        layout.addWidget(dlg.buttonBox)

    if isinstance(layout, QGridLayout):
        dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
        layout.addWidget(dlg.buttonBox, layout.rowCount(), 0,
                            1, layout.columnCount())

    if isinstance(layout, QFormLayout):
        dlg.buttonBox = QDialogButtonBox(Qt.Horizontal)
        layout.addRow(dlg.buttonBox)

    if isinstance(layout, QHBoxLayout):
        dlg.buttonBox = QDialogButtonBox(Qt.Vertical)
        layout.addWidget(dlg.buttonBox)

    return dlg.buttonBox

def to_dialog(widget):

    widget._isDialog = True

    widget.setWindowFlags(widget.windowFlags() | Qt.Dialog)

    widget.buttonBox = _addButtonBox2Dialog(widget)

    widget.buttonBox.setStandardButtons(QDialogButtonBox.Apply |\
                                        QDialogButtonBox.Cancel)
    widget.acceptButton = widget.buttonBox.button(QDialogButtonBox.Apply)
    widget.rejectButton = widget.buttonBox.button(QDialogButtonBox.Cancel)

    if hassig(widget,'validationChanged'):
        widget.validationChanged.connect(widget.acceptButton.setEnabled)

    if hasattr(widget, 'accept') and callable(widget.accept):
        widget.acceptButton.clicked.connect(widget.accept)

    if hasattr(widget, 'reject') and callable(widget.reject):
        widget.rejectButton.clicked.connect(widget.reject)

    return widget