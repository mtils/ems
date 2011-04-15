'''
Created on 23.03.2011

@author: michi
'''
from PyQt4.QtGui import QApplication, QDialog, QVBoxLayout, QGraphicsView,\
QGraphicsScene

app = QApplication([])

dialog = QDialog()
dialog.show()

layout = QVBoxLayout(dialog)
view = QGraphicsView(dialog)
layout.addWidget(view)

scene = QGraphicsScene(dialog)
view.setScene(scene)