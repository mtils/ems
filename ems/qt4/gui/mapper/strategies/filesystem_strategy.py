
from PyQt4.QtGui import QStyledItemDelegate

from ems.xtype.base import FilesystemPathType
from ems.qt4.gui.mapper.base import BaseStrategy
from ems.qt4.gui.itemdelegate.xtypes.stringtype import StringTypeDelegate
from ems.qt4.gui.mapper.delegates.filesystem_delegate import FileInputDelegate
from ems.qt4.gui.inputs.filesystem import FileSelect


class FileSystemStrategy(BaseStrategy):

    def __init__(self, parent=None):
        super(BaseStrategy, self).__init__(parent)
        self._model = None
        self._mappedInput = None

    def match(self, param):
        return isinstance(param, FilesystemPathType)

    def getDelegateForItem(self, mapper, type_, parent=None):
        return StringTypeDelegate(type_, parent=parent)

    def getEditor(self, mapper, type_, parent=None):
        return FileSelect(parent=parent)

    def addMapping(self, mapper, widget, propertyName, type_):

        columnIndex = mapper.model.columnOfName(propertyName)

        widget.delegate = FileInputDelegate(widget, mapper.model, columnIndex, parent=widget)
        mapper.dataWidgetMapper.currentIndexChanged.connect(widget.delegate.setCurrentRow)

        #mapper.dataWidgetMapper.addMapping(widget.lineEdit, columnIndex)