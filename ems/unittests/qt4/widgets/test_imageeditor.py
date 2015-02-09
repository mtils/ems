#coding=utf-8
from ems.qt4.application import MainApplication
from ems.qt4.gui.widgets.imageeditor import ImageEditor

if __name__ == '__main__':

    import sys

    app = MainApplication(sys.argv)

    fileName = '/home/michi/Medien/Bilder/03072011422.jpg'
    fileName = '/home/michi/Medien/Bilder/22.4.2011 192.jpg'
    fileName = '/home/michi/Medien/Bilder/03042011038.jpg'

    dlg = ImageEditor.toDialog(fileName)
    dlg.show()
    app.exec_()