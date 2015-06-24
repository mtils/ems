
from PyQt4.QtCore import Qt, QString, QSize, QRect, QRectF, pyqtSignal
from PyQt4.QtGui import QWidget, QLabel, QStyle, QPushButton, QSizePolicy
from PyQt4.QtGui import QApplication, QTextOption, QGridLayout, QLayout, QPen
from PyQt4.QtGui import QPalette, QColor, QPainterPath, QPainter, QBitmap
from PyQt4.QtGui import QBrush, QPixmap, QGraphicsDropShadowEffect


class BalloonTip(QWidget):

    titleChanged = pyqtSignal(QString)

    stateChanged = pyqtSignal(int)

    NONE = 0

    INFO = 1

    WARNING = 2

    ERROR = 3

    def __init__(self, parent):

        super(BalloonTip, self).__init__(parent, Qt.ToolTip)

        self._state = self.INFO

        self._setupUi()

    def getTitle(self):
        return self.titleLabel.text()

    def setTitle(self, title):
        if title == self.titleLabel.text():
            return
        self.titleLabel.setText(title)
        self.titleChanged.emit(QString.fromUtf8(title))

    title = property(getTitle, setTitle)

    def getState(self):
        return self._state

    def setState(self, state):
        if self._state == state:
            return
        self._state = state
        self.stateChanged.emit(state)

    state = property(getState, setState)

    def _setupUi(self):

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.titleLabel = QLabel(parent=self)
        self.titleLabel.installEventFilter(self)
        self.titleLabel.setText("Title")
        font = self.titleLabel.font()
        font.setBold(True)
        self.titleLabel.setFont(font)

        iconSize = self.style().pixelMetric(QStyle.PM_SmallIconSize)
        closeButtonSize = self.style().pixelMetric(QStyle.PM_SmallIconSize) - 2

        self.closeButton = QPushButton(parent=self)
        self.closeButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.closeButton.setIconSize(QSize(closeButtonSize, closeButtonSize))
        self.closeButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.closeButton.setFixedSize(closeButtonSize, closeButtonSize)

        self.closeButton.clicked.connect(self.close)

        self.msgLabel = QLabel(parent=self)
        self.msgLabel.installEventFilter(self)
        self.msgLabel.setText('Dis is da message')
        self.msgLabel.setTextFormat(Qt.PlainText)
        self.msgLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        widthLimit = QApplication.desktop().availableGeometry(self.msgLabel).size().width() / 2

        self._correctLabelIfToWide(self.msgLabel, widthLimit)

        icon = self.stateIcon()

        layout = QGridLayout()

        if not icon.isNull():
            self.iconLabel = QLabel(parent=self)
            self.iconLabel.setPixmap(icon.pixmap(iconSize, iconSize))
            self.iconLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.iconLabel.setMargin(2)
            layout.addWidget(self.iconLabel, 0, 0)
            layout.addWidget(self.titleLabel, 0, 1)
        else:
            layout.addWidget(self.titleLabel, 0, 0, 1, 2)

        layout.addWidget(self.closeButton, 0, 2)
        layout.addWidget(self.msgLabel)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setMargin(3)
        self.setLayout(layout)

        self._updatePaletteColors()

    def stateIcon(self):

        if self.state == self.INFO:
            return self.style().standardIcon(QStyle.SP_MessageBoxInformation)

        if self.state == self.WARNING:
            return self.style().standardIcon(QStyle.SP_MessageBoxWarning)

        if self.state == self.ERROR:
            return self.style().standardIcon(QStyle.SP_MessageBoxCritical)

    def _correctLabelIfToWide(self, label, widthLimit):

        if label.sizeHint().width() < widthLimit:
            return

        label.setWordWrap(True)

        # Disabled because access to QLabelPrivate
        #if label.sizeHint().width() > widthLimit:
            #label.d_func().ensureTextControl()
            #control = label.d_func().control
            #textOption = control.document().defaultTextOption()
            #opt.setWrapMode(QTextOption.WrapAnywhere)
            #control.document().setDefaultTextOption(opt)

        label.setFixedSize(widthLimit, label.heightForWidth(widthLimit))

    def balloon(self, pos, duration, showArrow=None):

        screen = QApplication.desktop().screenGeometry(pos)
        sizeHint = self.sizeHint()

        border = 1
        ah = 18; ao = 18; aw = 18; rc = 7

        arrowAtTop = (pos.y() + sizeHint.height() + ah < screen.height())
        arrowAtLeft = (pos.x() + sizeHint.width() - ao < screen.width())
        arrowAtTop = False
        print arrowAtTop, arrowAtLeft

        self.setContentsMargins(
            border + 3,
            border + (ah if arrowAtTop else 0),
            border + 3,
            border + (0 if arrowAtTop else ah)
        )

        self.updateGeometry()

        sizeHint = self.sizeHint()

        if not arrowAtTop:
            ml = mt = 0
            mr = sizeHint.width() - 1
            mb = sizeHint.height() - ah - 1
        else:
            ml = 0
            mt = ah
            mr = sizeHint.width() - 1
            mb = sizeHint.height() - 1

        path = QPainterPath()

        path.moveTo(ml + rc, mt)

        if arrowAtTop and arrowAtLeft:
            if showArrow:
                path.lineTo(ml + ao, mt);
                path.lineTo(ml + ao, mt - ah);
                path.lineTo(ml + ao + aw, mt);
            self.move(max(pos.x() - ao, screen.left() + 2), pos.y());

        elif arrowAtTop and not arrowAtLeft:
            if showArrow:
                path.lineTo(mr - ao - aw, mt)
                path.lineTo(mr - ao, mt - ah)
                path.lineTo(mr - ao, mt)
            self.move(min(pos.x() - sizeHint.width() + ao, screen.right() - sizeHint.width() - 2), pos.y())


        path.lineTo(mr - rc, mt)
        path.arcTo(QRectF(mr - rc*2, mt, rc*2, rc*2), 90, -90)
        path.lineTo(mr, mb - rc)
        path.arcTo(QRectF(mr - rc*2, mb - rc*2, rc*2, rc*2), 0, -90)

        if not arrowAtTop and not arrowAtLeft:
            if showArrow:
                path.lineTo(mr - ao, mb)
                path.lineTo(mr - ao, mb + ah)
                path.lineTo(mr - ao - aw, mb)

            self.move(min(pos.x() - sizeHint.width() + ao, screen.right() - sizeHint.width() - 2),
                      pos.y() - sizeHint.height());
        elif not arrowAtTop and arrowAtLeft:
            if showArrow:
                path.lineTo(ao + aw, mb)
                path.lineTo(ao, mb + ah)
                path.lineTo(ao, mb)

            self.move(max(pos.x() - ao, screen.x() + 2), pos.y() - sizeHint.height())

        path.lineTo(ml + rc, mb)
        path.arcTo(QRectF(ml, mb - rc*2, rc*2, rc*2), -90, -90)
        path.lineTo(ml, mt + rc)
        path.arcTo(QRectF(ml, mt, rc*2, rc*2), 180, -90)

        # Set the mask
        self.bitmap = QBitmap(self.sizeHint())
        self.bitmap.fill(Qt.color0)
        painter1 = QPainter(self.bitmap)
        painter1.setPen(QPen(Qt.color1, border))
        painter1.setBrush(QBrush(Qt.color1))
        painter1.drawPath(path)
        self.setMask(self.bitmap)

        self._updatePaletteColors()

        # Draw the border
        self.pixmap = QPixmap(sizeHint)
        painter2 = QPainter(self.pixmap)
        painter2.setPen(QPen(self.palette().color(QPalette.Window).darker(160), border))
        painter2.setBrush(self.palette().color(QPalette.Window))
        painter2.drawPath(path);

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    def resizeEvent(self, event):
        super(BalloonTip, self).resizeEvent(event)

    def eventFilter(self, qobject, event):

        if hasattr(qobject, 'isWindow') and qobject.isWindow() and event.type() == event.Move:
            self.move(self.pos() + (event.pos() - event.oldPos()))

        if event.type() == event.Hide:
            self.close()

        return super(BalloonTip, self).eventFilter(qobject, event)

    def _updatePaletteColors(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 225))
        palette.setColor(QPalette.WindowText, Qt.black)
        self.setPalette(palette)
