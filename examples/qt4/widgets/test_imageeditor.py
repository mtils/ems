#coding=utf-8
from ems.qt4.application import MainApplication
from ems.qt4.gui.widgets.imageeditor import ImageEditor
import sys

if __name__ == '__main__':

    import sys

    app = MainApplication(sys.argv)

    fileName = sys.argv[1] if len(sys.argv) > 1 else None

    dlg = ImageEditor.toDialog(fileName)
    dlg.show()
    app.exec_()