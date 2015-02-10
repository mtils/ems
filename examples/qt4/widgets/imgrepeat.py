#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

from PyQt4 import QtGui
from ems.qt4.gui.itemdelegate import ImgRepeatDelegate

def populateTableWidget(tableWidget):
    staticData = (
        ("Mass in B-Minor", "Baroque", "J.S. Bach", 5),
        ("Three More Foxes", "Jazz", "Maynard Ferguson", 3),
        ("Sex Bomb", "Pop", "Tom Jones", 2),
        ("Barbie Girl", "Pop", "Aqua", 4),
    )

    for row, (title, genre, artist, rating) in enumerate(staticData):
        item0 = QtGui.QTableWidgetItem(title)
        item1 = QtGui.QTableWidgetItem(genre)
        item2 = QtGui.QTableWidgetItem(artist)
        item3 = QtGui.QTableWidgetItem()
        item3.setData(0, rating)
        tableWidget.setItem(row, 0, item0)
        tableWidget.setItem(row, 1, item1)
        tableWidget.setItem(row, 2, item2)
        tableWidget.setItem(row, 3, item3)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    if len(sys.argv) < 2:
        print('Please provide an img file to repeat')
        sys.exit()

    tableWidget = QtGui.QTableWidget(4, 4)
    img = QtGui.QImage(sys.argv[1])
    tableWidget.setItemDelegateForColumn(3,ImgRepeatDelegate(img,maxValue=5,initialImgSize=24,
                                                             reversedMode=True))
    tableWidget.setEditTriggers(
            QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.SelectedClicked)
    tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    headerLabels = ("Title", "Genre", "Artist", "Rating")
    tableWidget.setHorizontalHeaderLabels(headerLabels)

    populateTableWidget(tableWidget)

    tableWidget.resizeColumnsToContents()
    tableWidget.resize(500, 300)
    tableWidget.show()

    sys.exit(app.exec_())
