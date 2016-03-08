
import sys, os, traceback

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QTableView, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QWidget

from examples.bootstrap.seeding.orm import Contact, Base
from examples.bootstrap.seeding.seeds import seed_contacts

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository

from ems.qt5.itemmodel.search_model import SearchModel


class TableManager(QWidget):

    selectedRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()

    def model(self):
        return self.view.model()

    def setModel(self, model):
        self.view.setModel(model)
        self.saveButton.clicked.connect(self.model().submit)
        self.cancelButton.clicked.connect(self.model().revert)

        self.saveButton.setEnabled(self.model().isDirty())
        self.cancelButton.setEnabled(self.model().isDirty())

        self.model().dirtyStateChanged.connect(self.saveButton.setEnabled)
        self.model().dirtyStateChanged.connect(self.cancelButton.setEnabled)

        self.view.selectionModel().currentRowChanged.connect(self._emitSelectedRow)
        model.error.connect(self._printError)

    def _setupUi(self):
        self.setLayout(QHBoxLayout())
        self.view = QTableView(self)
        self.view.setSelectionMode(self.view.ContiguousSelection)
        self.layout().addWidget(self.view)

        self.buttonContainer = QWidget(self)
        self.layout().addWidget(self.buttonContainer)

        self.buttonContainer.setLayout(QVBoxLayout())
        self.saveButton = QPushButton('&Save')
        self.buttonContainer.layout().addWidget(self.saveButton)

        self.cancelButton = QPushButton('&Cancel')
        self.buttonContainer.layout().addWidget(self.cancelButton)

        self.addButton = QPushButton('&Add')
        self.buttonContainer.layout().addWidget(self.addButton)

        self.removeButton = QPushButton('&Remove')
        self.buttonContainer.layout().addWidget(self.removeButton)

        self.buttonContainer.layout().addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.addButton.clicked.connect(self.addAfterLastSelected)
        self.removeButton.clicked.connect(self.removeSelected)

    def addAfterLastSelected(self):

        selectionModel = self.view.selectionModel()

        if not selectionModel.hasSelection():
            self.model().appendNew()
            return
        rows = self.collectSelectedRows()
        self.model().insertRows(max(rows)+1, len(rows))

    def removeSelected(self):

        selectionModel = self.view.selectionModel()

        if not selectionModel.hasSelection():
            return

        rows = self.collectSelectedRows()

        if not rows:
            return

        print(rows)

        self.model().removeRows(min(rows), len(rows))

    def collectSelectedRows(self):
        selectionModel = self.view.selectionModel()
        rows = set()
        for index in selectionModel.selectedIndexes():
            rows.add(index.row())

        return rows

    def selectRow(self, row):
        self.view.selectRow(row)

    def _emitSelectedRow(self, current, previous):
        self.selectedRowChanged.emit(current.row())


    def _printError(self, exc):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("TableManager ERROR: {}:{} {} Traceback:".format(fname, exc_tb.tb_lineno, exc))
        traceback.print_exc()