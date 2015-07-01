
from PyQt4.QtCore import QRect, Qt, QLine
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4
from PyQt4.QtGui import qApp, QStyle, QPen, QColor

class MultiRoleDelegate(QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        super(MultiRoleDelegate, self).__init__(*args, **kwargs)
        self.roles = [Qt.DisplayRole]

    def paint(self, painter, option, index):

        roleCount = len(self.roles)
        newHeight = int(round(float(option.rect.height()) / float(roleCount)))

        styleOptions = []

        for idx, role in enumerate(self.roles):

            styleOption = QStyleOptionViewItemV4(option)
            styleOption.rect = QRect(option.rect)
            styleOption.rect.setHeight(newHeight)
            styleOption.rect.moveTop(styleOption.rect.top() + idx*newHeight)
            styleOption.text = index.data(role).toString()

            widget = self.parent()

            widget.style().drawControl(QStyle.CE_ItemViewItem, styleOption, painter, widget)

            if idx != 0:
                painter.save()
                pen = QPen(QColor(220,220,220))
                pen.setStyle(Qt.DotLine)
                painter.setPen(pen)
                painter.drawLine(styleOption.rect.topLeft(), styleOption.rect.topRight())
                painter.restore()


    def sizeHint(self, option, index):
        sizeHint = super(MultiRoleDelegate, self).sizeHint(option, index)
        sizeHint.setHeight(sizeHint.height()*len(self.roles))
        return sizeHint
