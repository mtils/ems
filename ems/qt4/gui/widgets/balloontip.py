
from PyQt4.QtCore import Qt, QString, QSize, QRect, QRectF, pyqtSignal, QObject
from PyQt4.QtGui import QWidget, QLabel, QStyle, QPushButton, QSizePolicy
from PyQt4.QtGui import QApplication, QTextOption, QGridLayout, QLayout, QPen
from PyQt4.QtGui import QPalette, QColor, QPainterPath, QPainter, QBitmap
from PyQt4.QtGui import QBrush, QPixmap, QGraphicsDropShadowEffect, QIcon


class BalloonTip(QWidget):

    titleChanged = pyqtSignal(QString)

    stateChanged = pyqtSignal(int)

    messageChanged = pyqtSignal(QString)

    NONE = 0

    INFO = 1

    WARNING = 2

    ERROR = 3

    SUCCESS = 4

    def __init__(self, parent, message=None, title=None, state=None):

        super(BalloonTip, self).__init__(parent)

        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._state = self.INFO

        self._globalPos = None

        self._arrowHeight = 18

        self._arrowWidth = 18

        self._arrowOffset = 18

        self._borderRadius = 7

        self._borderWidth = 1

        self._arrowAtTop = None

        self._arrowAtLeft = None

        self._windowEventFilter = WindowEventFilter(self)

        self._bubblePath = None

        self._showArrow = True

        self._stateColors = {
            self.SUCCESS: QColor( 60, 118,  61),
            self.INFO:    QColor( 49, 112, 143),
            self.WARNING: QColor(138, 109,  59),
            self.ERROR:   QColor(169,  68,  66)
        }

        self._stateBackgroundColors = {
            self.SUCCESS: QColor(223, 240, 216),
            self.INFO:    QColor(217, 237, 247),
            self.WARNING: QColor(252, 248, 227),
            self.ERROR:   QColor(242, 222, 222)
        }

        self.setParent(parent)

        if state is not None:
            self.state = state

        self._setupUi()

        if message is not None:
            self.message = message

        if title is not None:
            self.title = title

        self.titleChanged.connect(self.rebuildLayout)
        self.stateChanged.connect(self.rebuildLayout)
        self.messageChanged.connect(self.rebuildLayout)

    def getTitle(self):
        return self.titleLabel.text()

    def setTitle(self, title):
        title = title if isinstance(title, QString) else QString.fromUtf8(title)
        if title == self.titleLabel.text():
            return
        self.titleLabel.setText(title)
        self.titleChanged.emit(title)

    title = property(getTitle, setTitle)

    def getState(self):
        return self._state

    def setState(self, state):
        if self._state == state:
            return
        self._state = state
        self.stateChanged.emit(state)

    state = property(getState, setState)

    def getMessage(self):
        return self.msgLabel.text()

    def setMessage(self, msg):
        msg = msg if isinstance(msg, QString) else QString.fromUtf8(msg)
        if msg == self.msgLabel.text():
            return

        self.msgLabel.setText(msg)
        self.messageChanged.emit(msg)

    message = property(getMessage, setMessage)

    def getGlobalPos(self):

        if self._globalPos:
            return self._globalPos

        referencePoint = self.parent().rect().topRight()
        return self.parent().mapToGlobal(referencePoint)

    def setGlobalPos(self, pos):
        self._globalPos = pos

    globalPos = property(getGlobalPos, setGlobalPos)

    def isArrowAtTop(self):

        if self._arrowAtTop is not None:
            return self._arrowAtTop

        pos = self.globalPos
        screen = QApplication.desktop().screenGeometry(pos)
        self._arrowAtTop = (pos.y() + self.sizeHint().height() + self._arrowHeight < screen.height())

        return self._arrowAtTop

    def setArrowAtTop(self, atTop=True):
        self._arrowAtTop = atTop

    arrowAtTop = property(isArrowAtTop, setArrowAtTop)

    def isArrowAtLeft(self):

        if self._arrowAtLeft is not None:
            return self._arrowAtLeft

        pos = self.globalPos
        screen = QApplication.desktop().screenGeometry(pos)
        self._arrowAtLeft = (pos.x() + self.sizeHint().width() - self._arrowOffset < screen.width())

        return self._arrowAtLeft

    def setArrowAtLeft(self, atLeft=True):
        self._arrowAtLeft = atLeft

    arrowAtLeft = property(isArrowAtLeft, setArrowAtLeft)

    def textColor(self):
        return self._stateColors[self._state]

    def backgroundColor(self):
        return self._stateBackgroundColors[self._state]

    def _setupUi(self):

        self.titleLabel = QLabel(parent=self)
        self.titleLabel.installEventFilter(self)
        self.titleLabel.setText(self.getTitle())
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
        self.msgLabel.setText(self.getMessage())
        self.msgLabel.setTextFormat(Qt.PlainText)
        self.msgLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        widthLimit = QApplication.desktop().availableGeometry(self.msgLabel).size().width() / 2

        self._correctLabelIfToWide(self.msgLabel, widthLimit)

        self._buildWidgetLayout()

        self._updatePaletteColors()

    def stateIcon(self):

        if self.state == self.INFO:
            return self.style().standardIcon(QStyle.SP_MessageBoxInformation)

        if self.state == self.WARNING:
            return self.style().standardIcon(QStyle.SP_MessageBoxWarning)

        if self.state == self.ERROR:
            return self.style().standardIcon(QStyle.SP_MessageBoxCritical)

        return QIcon()

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

    def balloon(self, duration, showArrow=None):
        self.show()

    def bubblePath(self):

        if self._bubblePath is not None:
            return self._bubblePath

        pos = self.globalPos

        screen = QApplication.desktop().screenGeometry(pos)
        sizeHint = self.sizeHint()

        arrowAtTop = self.isArrowAtTop()
        arrowAtLeft = self.isArrowAtLeft()

        self.updateGeometry()

        sizeHint = self.sizeHint()

        doubleBorderRadius = self._borderRadius*2

        if not arrowAtTop:
            ml = mt = 0
            mr = sizeHint.width() - 1
            mb = sizeHint.height() - self._arrowHeight - 1
        else:
            ml = 0
            mt = self._arrowHeight
            mr = sizeHint.width() - 1
            mb = sizeHint.height() - 1

        path = QPainterPath()

        path.moveTo(ml + self._borderRadius, mt)

        if arrowAtTop and arrowAtLeft:
            if self._showArrow:
                path.lineTo(ml + self._arrowOffset, mt);
                path.lineTo(ml + self._arrowOffset, mt - self._arrowHeight);
                path.lineTo(ml + self._arrowOffset + self._arrowWidth, mt);

        elif arrowAtTop and not arrowAtLeft:
            if self._showArrow:
                path.lineTo(mr - self._arrowOffset - self._arrowWidth, mt)
                path.lineTo(mr - self._arrowOffset, mt - self._arrowHeight)
                path.lineTo(mr - self._arrowOffset, mt)


        path.lineTo(mr - self._borderRadius, mt)
        path.arcTo(QRectF(mr - doubleBorderRadius, mt, doubleBorderRadius, doubleBorderRadius), 90, -90)
        path.lineTo(mr, mb - self._borderRadius)
        path.arcTo(QRectF(mr - doubleBorderRadius, mb - doubleBorderRadius, doubleBorderRadius, doubleBorderRadius), 0, -90)

        if not arrowAtTop and not arrowAtLeft:
            if self._showArrow:
                path.lineTo(mr - self._arrowOffset, mb)
                path.lineTo(mr - self._arrowOffset, mb + self._arrowHeight)
                path.lineTo(mr - self._arrowOffset - self._arrowWidth, mb)

        elif not arrowAtTop and arrowAtLeft:
            if self._showArrow:
                path.lineTo(self._arrowOffset + self._arrowWidth, mb)
                path.lineTo(self._arrowOffset, mb + self._arrowHeight)
                path.lineTo(self._arrowOffset, mb)

        path.lineTo(ml + self._borderRadius, mb)
        path.arcTo(QRectF(ml, mb - doubleBorderRadius, doubleBorderRadius, doubleBorderRadius), -90, -90)
        path.lineTo(ml, mt + self._borderRadius)
        path.arcTo(QRectF(ml, mt, doubleBorderRadius, doubleBorderRadius), 180, -90)

        self._bubblePath = path

        return path

    

    def _correctPosition(self):

        pos = self.globalPos

        screen = QApplication.desktop().screenGeometry(pos)
        sizeHint = self.sizeHint()

        arrowAtTop = self.isArrowAtTop()
        arrowAtLeft = self.isArrowAtLeft()

        self.setContentsMargins(
            self._borderWidth + 3,
            self._borderWidth + (self._arrowHeight if arrowAtTop else 0),
            self._borderWidth + 3,
            self._borderWidth + (0 if arrowAtTop else self._arrowHeight)
        )

        self.updateGeometry()

        sizeHint = self.sizeHint()

        if arrowAtTop and arrowAtLeft:
            self.move(max(pos.x() - self._arrowOffset, screen.left() + 2), pos.y());

        elif arrowAtTop and not arrowAtLeft:
            self.move(min(pos.x() - sizeHint.width() + self._arrowOffset, screen.right() - sizeHint.width() - 2), pos.y())


        if not arrowAtTop and not arrowAtLeft:
            self.move(min(pos.x() - sizeHint.width() + self._arrowOffset, screen.right() - sizeHint.width() - 2),
                      pos.y() - sizeHint.height());
        elif not arrowAtTop and arrowAtLeft:
            self.move(max(pos.x() - self._arrowOffset, screen.x() + 2), pos.y() - sizeHint.height())

    def _drawMask(self, painterPath):

        self.bitmap = QBitmap(self.sizeHint())
        self.bitmap.fill(Qt.color0)
        painter1 = QPainter(self.bitmap)
        painter1.setPen(QPen(Qt.color1, self._borderWidth))
        painter1.setBrush(QBrush(Qt.color1))
        painter1.drawPath(painterPath)
        self.setMask(self.bitmap)

    def _drawBorder(self, painterPath):

        #self._updatePaletteColors()

        self.pixmap = QPixmap(self.sizeHint())
        painter2 = QPainter(self.pixmap)
        painter2.setPen(QPen(self.palette().color(QPalette.Window).darker(160), self._borderWidth))
        painter2.setBrush(self.palette().color(QPalette.Window))
        painter2.drawPath(painterPath);

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    def showEvent(self, event):
        self._repaintBalloon()

    def resizeEvent(self, event):
        super(BalloonTip, self).resizeEvent(event)

    def eventFilter(self, qobject, event):

        if event.type() == event.Hide:
            self.close()

        return super(BalloonTip, self).eventFilter(qobject, event)

    def _updatePaletteColors(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, self.backgroundColor())
        palette.setColor(QPalette.WindowText, self.textColor())
        self.setPalette(palette)

    def setParent(self, parent):

        if not isinstance(parent, QWidget):
            raise TypeError("Parent of BalloonTip has to be QWidget")

        window = parent.window()
        if window:
            window.installEventFilter(self._windowEventFilter)

        self.setWindowFlags(Qt.ToolTip)

        super(BalloonTip, self).setParent(parent)

    def _buildWidgetLayout(self):

        icon = self.stateIcon()
        iconSize = self.style().pixelMetric(QStyle.PM_SmallIconSize)

        self._invalidateLayout()

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

    def _invalidateLayout(self):

        layout = self.layout()
        if not layout:
            return

        del layout

    def _repaintBalloon(self):

        self._updatePaletteColors()

        self._bubblePath = None

        self._correctPosition()

        self._drawMask(self.bubblePath())

        self._drawBorder(self.bubblePath())

        self.updateGeometry()


    def rebuildLayout(self, *args, **kwargs):
        #self._buildWidgetLayout()
        self._repaintBalloon()
        self.updateGeometry()

class WindowEventFilter(QObject):

    def __init__(self, balloon):
        super(WindowEventFilter, self).__init__(balloon)

    def eventFilter(self, window, event):

        if event.type() in (event.Move, event.Resize):
            #self.parent().move(self.parent().pos() + (event.pos() - event.oldPos()))
            self.parent()._correctPosition()

        if event.type() == event.Hide:
            self.parent().close()

        return super(WindowEventFilter, self).eventFilter(window, event)