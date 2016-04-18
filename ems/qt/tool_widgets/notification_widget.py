
from six import text_type

from ems.qt import QtWidgets, QtCore, QtGui
from ems.qt5.util import QError


Qt = QtCore.Qt
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
pyqtSlot = QtCore.pyqtSlot
QEvent = QtCore.QEvent
QTimeLine = QtCore.QTimeLine
QAction = QtWidgets.QAction
QGridLayout = QtWidgets.QGridLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QLabel = QtWidgets.QLabel
QFrame = QtWidgets.QFrame
QPainter = QtGui.QPainter
QToolButton = QtWidgets.QToolButton
QStyle = QtWidgets.QStyle
QIcon = QtGui.QIcon
QPixmap = QtGui.QPixmap
QSizePolicy = QtWidgets.QSizePolicy
QPoint = QtCore.QPoint
QWidget = QtWidgets.QWidget
QRegion = QtGui.QRegion
QColor = QtGui.QColor
QPainter = QtGui.QPainter


class NotificationWidget(QFrame):

    Success = 'Success'

    Information = 'Information'

    Warning = 'Warning'

    Error = 'Error'

    linkActivated = pyqtSignal(text_type)

    linkHovered = pyqtSignal(text_type)

    hideAnimationFinished = pyqtSignal()

    showAnimationFinished = pyqtSignal()

    def __init__(self, parent, text=None):
        super(NotificationWidget, self).__init__(parent)
        self._messageType = self.Information
        self._iconLabel = QLabel()
        self._textLabel = QLabel()
        self._closeButton = QToolButton()
        self._timeLine = QTimeLine()
        self._icon = QIcon()
        self._wordWrap = True
        self._buttons = []
        self._contentSnapShot = QPixmap()
        self._content = None
        self.init()
        if text:
            self.setText(text)

    def getText(self):
        return self._textLabel.text()

    def setText(self, text):
        if text == self._textLabel.text():
            return
        self._textLabel.setText(text)
        self.updateGeometry()

    text = pyqtProperty(text_type, getText, setText)

    def getMessageType(self):
        return self._messageType

    def setMessageType(self, messageType):
        if self._messageType == messageType:
            return
        self._messageType = messageType

        bg0 = QColor()
        bg1 = QColor()
        bg2 = QColor()
        border = QColor()
        fg = QColor()

        if messageType == self.Success:
            bg1.setRgb(0, 110, 40)
        elif messageType == self.Information:
            bg1 = self.palette().highlight().color()
        elif messageType == self.Warning:
            bg1.setRgb(176, 128, 0)
        elif messageType == self.Error:
            bg1.setRgb(191, 3, 3)

        # Colors
        fg = self.palette().highlightedText().color()
        bg0 = bg1.lighter(110)
        bg2 = bg1.darker(110)
        border = self._darkShade(bg1);

        styleSheet = '''
        .QFrame {{
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {0},
                /*stop: 0.1 {1},*/
                stop: 1.0 {2});
            border-radius: 5px;
            border: 1px solid {3};
            margin: {4}px;
        }}
        .QLabel {{ color: {5}; }}
        '''
        styleSheet = styleSheet.format(
            bg0.name(),
            bg1.name(),
            bg2.name(),
            border.name(),
            self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, None, self) - 1,
            fg.name()
        )
        self._content.setStyleSheet(styleSheet)

    def success(self, msg, actions=None):
        self.setMessageType(self.Success)
        self.setText(msg)
        self.animatedShow()

    def information(self, msg, actions=None):
        self.setMessageType(self.Information)
        self.setText(msg)
        self.animatedShow()

    def warning(self, msg, actions=None):
        self.setMessageType(self.Warning)
        self.setText(msg)
        self.animatedShow()

    @pyqtSlot(text_type)
    @pyqtSlot(QError)
    def error(self, msg, actions=None):
        self.setMessageType(self.Error)
        msg = msg.message if isinstance(msg, QError) else msg
        self.setText(msg)
        self.animatedShow()

    def sizeHint(self):
        self.ensurePolished()
        return self._content.sizeHint()

    def minimumSizeHint(self):
        self.ensurePolished()
        return self._content.minimumSizeHint()

    def event(self, event):
        if (event.type() == QEvent.Polish) and not self._content.layout():
            self._createLayout()

        return super(NotificationWidget, self).event(event)

    def resizeEvent(self, event):
        super(NotificationWidget, self).resizeEvent(event)
        if self._timeLine.state() == QTimeLine.NotRunning:
            self._content.resize(self.width(), self.bestContentHeight())

    def heightForWidth(self, width):
        self.ensurePolished()
        return self._content.heightForWidth(width)

    def paintEvent(self, event):
        super(NotificationWidget, self).paintEvent(event)
        if not self._timeLine.state() == QTimeLine.Running:
            return
        painter = QPainter(self)
        painter.setOpacity(self._timeLine.currentValue() * self._timeLine.currentValue())
        painter.drawPixmap(0, 0,self._contentSnapShot);

    def getWordWrap(self):
        return self._wordWrap

    def setWordWrap(self, wordWrap):
        if self._wordWrap == wordWrap:
            return
        self._wordWrap = wordWrap
        self._textLabel.setWordWrap(wordWrap)
        policy = self.sizePolicy()
        policy.setHeightForWidth(wordWrap)
        self.setSizePolicy(policy)
        self.updateLayout()
        if wordWrap:
            self.setMinimumHeight(0)

    def isCloseButtonVisible(self):
        return self._closeButton.isVisible()

    def setCloseButtonVisible(self, visible):
        self._closeButton.setVisible(visible)
        self.updateGeometry()

    def addAction(self, action):
        super(NotificationWidget, self).addAction(action)
        self.updateLayout()

    def removeAction(self, action):
        super(NotificationWidget, self).removeAction(action)
        self.updateLayout()

    def show(self):
        return super(NotificationWidget, self).show()

    def animatedShow(self):

        if not self.style().styleHint(QStyle.SH_Widget_Animate, None, self):
            self.show()
            self.showAnimationFinished.emit()
            return

        if self.isVisible():
            return

        super(NotificationWidget, self).show()
        self.setFixedHeight(0)
        wantedHeight = self.bestContentHeight()
        self._content.setGeometry(0, -wantedHeight, self.width(), wantedHeight)

        self._updateSnapShot()

        self._timeLine.setDirection(QTimeLine.Forward)
        if self._timeLine.state() == QTimeLine.NotRunning:
            self._timeLine.start()

    def animateHide(self):

        if not self.style().styleHint(QStyle.SH_Widget_Animate, None, self):
            self.hide()
            self.hideAnimationFinished.emit()
            return

        if not self.isVisible():
            self.hide()
            return

        self._content.move(0, -self._content.height())
        self._updateSnapShot();

        self._timeLine.setDirection(QTimeLine.Backward)
        if self._timeLine.state() == QTimeLine.NotRunning:
            self._timeLine.start()

    def isHideAnimationRunning(self):
        return (self._timeLine.direction() == QTimeLine.Backward) and (self._timeLine.state() == QTimeLine.Running)

    def isShowAnimationRunning(self):
        return (self._timeLine.direction() == QTimeLine.Forward) and (self._timeLine.state() == QTimeLine.Running)

    def icon(self):
        return self._icon

    def setIcon(self, icon):
        if self._icon is icon:
            return
        self._icon = icon
        if self._icon.isNull():
            self._iconLabel.hide()
            return

        size = self.style().pixelMetric(QStyle.PM_ToolBarIconSize)
        self._iconLabel.setPixmap(self._icon.pixmap(size))
        self._iconLabel.show()

    def init(self):

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self._timeLine = QTimeLine(500, self)
        self._timeLine.valueChanged.connect(self._slotTimeChanged)
        self._timeLine.finished.connect(self._slotTimeFinished)
        self._content = QFrame(self)
        self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._wordWrap = False

        self._iconLabel = QLabel(self._content)
        self._iconLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._iconLabel.hide()

        self._textLabel = QLabel(self._content)
        self._textLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._textLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._textLabel.linkActivated.connect(self.linkActivated)
        self._textLabel.linkHovered.connect(self.linkHovered)

        self._closeAction = QAction(self)
        self._closeAction.setText(self.tr('&Close'))
        self._closeAction.setToolTip(self.tr('Close message'))
        self._closeAction.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))

        self._closeAction.triggered.connect(self.animateHide)

        self._closeButton = QToolButton(self._content)
        self._closeButton.setAutoRaise(True)
        self._closeButton.setDefaultAction(self._closeAction)

    def _createLayout(self):
        layout = self._content.layout()
        del layout
        self._content.resize(self.size())

        for button in self._buttons:
            del button

        self._buttons = []

        for action in self.actions():
            button = QToolButton(self._content)
            button.setDefaultAction(action)
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self._buttons.append(button)

        self._closeButton.setAutoRaise(len(self._buttons) == 0)

        if self._wordWrap:

            layout = QGridLayout(self._content)
            # Set alignment to make sure icon does not move down if text wraps
            layout.addWidget(self._iconLabel, 0, 0, 1, 1, Qt.AlignHCenter | Qt.AlignTop)
            layout.addWidget(self._textLabel, 0, 1)

            buttonLayout = QHBoxLayout()
            buttonLayout.addStretch()
            for button in self._buttons:
                button.show()
                buttonLayout.addWidget(button)

            buttonLayout.addWidget(self._closeButton)
            layout.addItem(buttonLayout, 1, 0, 1, 2)

        else:
            layout = QHBoxLayout(self._content)
            layout.addWidget(self._iconLabel)
            layout.addWidget(self._textLabel)

            for button in self._buttons:
                layout.addWidget(button)


            layout.addWidget(self._closeButton)

        if self.isVisible():
            self.setFixedHeight(self._content.sizeHint().height())

        self.updateGeometry()

    def updateLayout(self):
        if self._content.layout():
            self._createLayout()

    def _updateSnapShot(self):
        self._contentSnapShot = QPixmap(self._content.size()) # *devicePixelRatio
         #self._contentSnapShot.setDevicePixelRatio(q.devicePixelRatio())
        self._contentSnapShot.fill(Qt.transparent)
        self._content.render(self._contentSnapShot, QPoint(), QRegion(), QWidget.DrawChildren)


    def _darkShade(self, c):

        contrast = 0.7
        darkAmount = 0.0

        if c.lightnessF() < 0.006: # too dark
            darkAmount = 0.02 + 0.40 * contrast
        elif c.lightnessF() > 0.93: # too bright
            darkAmount = -0.06 - 0.60 * contrast
        else:
            darkAmount = (-c.lightnessF()) * (0.55 + contrast * 0.35)

        v = c.lightnessF() + darkAmount
        v = (v if v < 1.0 else 1.0) if v > 0.0 else 0.0

        c.setHsvF(c.hslHueF(), c.hslSaturationF(), v);
        return c


    def _slotTimeChanged(self, value):
        self.setFixedHeight(min(value * 2, 1.0) * self._content.height())
        self.update()

    def _slotTimeFinished(self):
        if self._timeLine.direction() == QTimeLine.Forward:
            # Show
            # We set the whole geometry here, because it may be wrong if a
            # KMessageWidget is shown right when the toplevel window is created.
            self._content.setGeometry(0, 0, self.width(), self.bestContentHeight())

            # notify about finished animation
            self.showAnimationFinished.emit()
        else:
            # hide and notify about finished animation
            self.hide()
            self.hideAnimationFinished.emit()

    def bestContentHeight(self):

        height = self._content.heightForWidth(self.width())
        if height == -1:
            height = self._content.sizeHint().height()

        return height
