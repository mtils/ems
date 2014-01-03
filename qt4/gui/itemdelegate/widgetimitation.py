
from PyQt4.QtCore import QSize, QRect
from PyQt4.QtGui import QStyledItemDelegate, QProgressBar, QStyleOptionViewItemV4,\
    QApplication, QStyle

class ProgressBarDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self._styleSheet = ''
        self._minimum = 0
        self._maximum = 100
        self._renderer = None
        self.horizontalMargin = 3
        self.verticalMargin = 3

    def minimum(self):
        if self._renderer:
            return self._renderer.minimum()
        return self._minimum

    def setMinimum(self, minimum):
        if self._renderer:
            self._renderer.setMinimum(minimum)
        self._minimum = minimum

    def maximum(self):
        if self._renderer:
            return self._renderer.maximum()
        return self._maximum

    def setMaximum(self, maximum):
        if self._renderer:
            self._renderer.setMaximum(maximum)
        self._maximum = maximum

    def styleSheet(self):
        if self._renderer:
            return self._renderer.styleSheet()
        return self._styleSheet
    
    def setStyleSheet(self, styleSheet):
        if self._renderer:
            self._renderer.setStyleSheet(styleSheet)
        self._styleSheet = styleSheet


    def renderer(self):
        if self._renderer is None:
            self._renderer = QProgressBar()
            self._renderer.setMinimum(self._minimum)
            self._renderer.setMaximum(self._maximum)
            self._renderer.setStyleSheet(self._styleSheet)
        return self._renderer

    def paint(self, painter, option, index):

        styleOption = QStyleOptionViewItemV4(option)
        self.initStyleOption(styleOption, index)
        styleOption.text = ''

        style = QApplication.style() if option.widget is None \
            else option.widget.style()

        style.drawControl(QStyle.CE_ItemViewItem, styleOption, painter)

        value = int(round(index.data().toFloat()[0]))

        targetRect = QRect(option.rect)
        center = option.rect.center()

        targetRect.setWidth(targetRect.width()-2*self.horizontalMargin)
        targetRect.setHeight(targetRect.height()-2*self.verticalMargin)
        targetRect.moveCenter(center)

        renderer = self.renderer()
        renderer.resize(targetRect.size())
        renderer.setValue(value)

        painter.save()
        painter.translate(targetRect.topLeft())
        renderer.render(painter)
        painter.restore()