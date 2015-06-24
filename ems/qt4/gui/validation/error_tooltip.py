
from PyQt4.QtCore import QPoint, Qt
from PyQt4.QtGui import QLabel, QGraphicsDropShadowEffect, qApp


class ErrorTooltip(QLabel):

    def __init__(self, widget):

        super(ErrorTooltip, self).__init__(widget.parentWidget())

        #self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.widget = widget

        self.hide()

        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(2,2)
        self.setGraphicsEffect(effect)

        self.setStyleSheet('''QLabel {
                                 background-color: #f2dede;
                                 border: #ebccd1;
                                 border-radius: 3px;
                                 padding: 3px;
                                 color: #a94442;
                                 }
                           ''')

    def showMessage(self, message):
        '''
        Show the widget.
        '''
        self.setText(message)
        self.adjustSize()
        self.update()
        self.show()

        labelGeo = self.geometry()
        #print self.parent()
        #print self.geometry()
        #print self.pos(), self.widget.pos()
        print self.contentsRect(), self.rect()
        #print self.widget.rect().topLeft()
        #print self.widget.rect()
        #print self.widget.mapToParent(self.widget.rect().topLeft())
        #newPos = self.widget.parentWidget().mapTo(self.widget, self.widget.rect().topLeft())
        #self.move(newPos)
        #self.move(self.widget.mapToParent(self.widget.contentsRect().topLeft()))
        self.move(self.widget.pos() - self.contentsRect().bottomLeft())