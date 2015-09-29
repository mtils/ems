#coding=utf-8
'''
Created on 04.03.2012

@author: michi
'''
import sys
import copy
import pprint

from PyQt4.QtCore import QString, QObject, Qt, QSize
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout, \
    QPushButton, QTableWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItemV4,\
    QDialog, QHeaderView

from ems.app import app
from ems import qt4
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.qt4.gui.mapper.base import BaseMapper
from ems.validation.rule_validator import RuleValidator
from ems.qt4.itemmodel.validator_model import RuleValidatorModel
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel
from ems.qt4.gui.itemdelegate.multiroledelegate import MultiRoleDelegate
from ems.qt4.itemmodel.buffered_model import BufferedModel

from examples.xtype.persondata import testData, listType

from examples.qt4.bootstrap.create_app import create_app

class ButtonSetter(QObject):

    def __init__(self, model, editor):
        super(ButtonSetter, self).__init__(editor)
        self._submitButton = None
        self._revertButton = None
        self.model = model
        self.editor = editor

        self.editor.isRowSelectedStateChanged.connect(self.enableAll)
        self.editor.firstSelectedRowChanged.connect(self.updateRowButtons)
        self.model.dirtyStateChanged[int, bool].connect(self.recheckCurrentRow)

    def enableAll(self, enable=True):

        if not enable:
            for button in (self.submitButton, self.revertButton):
                button.setEnabled(False)
            return

        self.updateRowButtons(self.editor.currentRow)

    def updateRowButtons(self, row):
        if row is None:
            return
        for button in (self.submitButton, self.revertButton):
            button.setEnabled(self.model.isDirty(row))

    def recheckCurrentRow(self, *args):
        self.updateRowButtons(self.editor.currentRow)

    @property
    def submitButton(self):
        return self._submitButton

    @submitButton.setter
    def submitButton(self, button):
        self._submitButton = button
        self._submitButton.clicked.connect(self.trySubmit)

    @property
    def revertButton(self):
        return self._revertButton

    @revertButton.setter
    def revertButton(self, button):
        self._revertButton = button
        self._revertButton.clicked.connect(self.tryRevert)

    def trySubmit(self):
        self.model.submitRow(self.editor.currentRow)

    def tryRevert(self):
        self.model.revertRow(self.editor.currentRow)

dlg = QDialog()
dlg.setLayout(QVBoxLayout(dlg))
dlg.setWindowTitle("List of Dicts Model")

dlg.bufferView = QTableView(dlg)
dlg.storageView = QTableView(dlg)


model = ListOfDictsModel(listType, dlg)

model.setKeyLabel('forename', QString.fromUtf8('Name'))
model.setKeyLabel('surname', QString.fromUtf8('Familienname'))
model.setKeyLabel('age', QString.fromUtf8('Alter'))
model.setKeyLabel('weight', QString.fromUtf8('Gewicht'))
model.setKeyLabel('income', QString.fromUtf8('Einkommen'))
model.setKeyLabel('married', QString.fromUtf8('Verheiratet'))

model.setModelData(testData)

bufferModel = BufferedModel(model)

dlg.editor = ItemViewEditor(dlg.bufferView, parent=dlg)

dlg.submitButton = QPushButton(dlg.editor.buttonContainer)
dlg.submitButton.setText('Submit')
dlg.submitButton.setEnabled(False)
dlg.editor.buttonContainer.layout().addWidget(dlg.submitButton)

dlg.revertButton = QPushButton(dlg.editor.buttonContainer)
dlg.revertButton.setText('Revert')
dlg.revertButton.setEnabled(False)
dlg.editor.buttonContainer.layout().addWidget(dlg.revertButton)

dlg.buttonSetter = ButtonSetter(bufferModel, dlg.editor)
dlg.buttonSetter.submitButton = dlg.submitButton
dlg.buttonSetter.revertButton = dlg.revertButton

dlg.layout().addWidget(dlg.editor)

dlg.layout().addWidget(dlg.storageView)

bufferModel.setSourceModel(model)
dlg.storageView.setModel(model)
dlg.bufferView.setModel(bufferModel)

dlg.mapper = BaseMapper(bufferModel)
dlg.delegate = dlg.mapper.getDelegateForItemView(dlg.bufferView)
dlg.bufferView.setItemDelegate(dlg.delegate)


dlg.show()
