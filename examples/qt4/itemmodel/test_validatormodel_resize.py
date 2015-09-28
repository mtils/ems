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
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.xtype.base import StringType, NumberType, UnitType, BoolType #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject
from ems.qt4.gui.mapper.base import BaseMapper #@UnresolvedImport
from ems.xtype.base import SequenceType, DictType #@UnresolvedImport
from ems.validation.rule_validator import RuleValidator
from ems.qt4.itemmodel.validator_model import RuleValidatorModel
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel
from ems.qt4.gui.itemdelegate.multiroledelegate import MultiRoleDelegate

from examples.xtype.persondata import testData, listType

from examples.qt4.bootstrap.create_app import create_app

rules = {
    'forename': 'required|min:4|max:15',
    'surname' : 'min:3|max:46',
    'age'     : 'numeric|min:18|max:99',
    'weight'  : 'numeric|min:6|max:250',
    'income'  : 'numeric|between:150,250',
    'married' : 'required|bool',
}

dlg = QDialog()
dlg.setLayout(QVBoxLayout(dlg))
dlg.setWindowTitle("List of Dicts Model")

dlg.view = QTableView(dlg)


dlg.validatorView = QTableView(dlg)

dlg.validatorModel = RuleValidatorModel(parent=dlg.validatorView)
dlg.validationDelegate = MultiRoleDelegate(dlg.validatorView)
dlg.validationDelegate.setParent(dlg.validatorView)
dlg.validatorView.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
dlg.validatorView.horizontalHeader().setResizeMode(QHeaderView.Stretch)
dlg.validationDelegate.roles.append(qt4.ValidationStateRole)
dlg.validationDelegate.roles.append(qt4.ValidationMessageRole)
dlg.validatorView.setItemDelegate(dlg.validationDelegate)

dlg.storageView = QTableView(dlg)


model = ListOfDictsModel(listType, dlg.view)

model.setKeyLabel('forename', QString.fromUtf8('Name'))
model.setKeyLabel('surname', QString.fromUtf8('Familienname'))
model.setKeyLabel('age', QString.fromUtf8('Alter'))
model.setKeyLabel('weight', QString.fromUtf8('Gewicht'))
model.setKeyLabel('income', QString.fromUtf8('Einkommen'))
model.setKeyLabel('married', QString.fromUtf8('Verheiratet'))

model.setModelData(testData)
dlg.validatorModel.validator = app(RuleValidator)
dlg.validatorModel.rules = rules

dlg.editor = ItemViewEditor(dlg.view, parent=dlg)
#dlg.view.setMinimumSize(640, 480)
dlg.layout().addWidget(dlg.editor)

dlg.layout().addWidget(dlg.validatorView)
dlg.layout().addWidget(dlg.storageView)

dlg.validatorModel.setSourceModel(model)
dlg.storageView.setModel(model)
dlg.validatorView.setModel(dlg.validatorModel)
dlg.view.setModel(dlg.validatorModel)

dlg.mapper = BaseMapper(dlg.validatorModel)
dlg.delegate = dlg.mapper.getDelegateForItemView(dlg.view)
dlg.view.setItemDelegate(dlg.delegate)


dlg.show()
