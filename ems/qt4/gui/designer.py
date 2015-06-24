
from PyQt4.QtGui import QIcon, QStyle
from PyQt4.QtDesigner import QPyDesignerCustomWidgetPlugin

from inputs.filesystem import FileSelect, DirectorySelect


class FileSelectPlugin(QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super(FileSelectPlugin, self).__init__()

        self.initialized = False

    def initialize(self, core):

        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):

        return self.initialized

    def createWidget(self, parent):
        return FileSelect(parent)

    def name(self):
        return self.trUtf8(u"FileSelect")

    def group(self):
        return "PyQt Examples"

    def icon(self):
        return QStyle.standardIcon(QStyle.SP_DirOpenIcon)

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def domXml(self):
        return (
               '<widget class="FileSelect" name=\"FileSelect\">\n'
               " <property name=\"toolTip\" >\n"
               "  <string>Selects a file</string>\n"
               " </property>\n"
               " <property name=\"whatsThis\" >\n"
               "  <string>Allows the user to set a file path.</string>\n"
               " </property>\n"
               "</widget>\n"
               )

    def includeFile(self):
        return 'inputs.filesystem'