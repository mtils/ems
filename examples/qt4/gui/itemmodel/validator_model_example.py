
import sys, os.path

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout
from PyQt4.QtGui import QHeaderView

from examples.qt4.bootstrap.create_app import create_app, app_path
from ems.xtype.base import NumberType, StringType, BoolType, UnitType, DictType
from ems.validation.rule_validator import RuleValidator, SimpleMessageProvider
from ems.validation.registry import Registry
from ems.app import app
from ems import qt4
from ems.qt4.itemmodel.validator_model import RuleValidatorModel
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel
from examples.xtype.persondata import itemType, testData, listType
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel
from ems.qt4.gui.itemdelegate.multiroledelegate import MultiRoleDelegate

rules = {
    'forename': 'required|min:4|max:15',
    'surname' : 'min:3|max:46',
    'age'     : 'numeric|min:18|max:99',
    'weight'  : 'numeric|min:6|max:250',
    'income'  : 'numeric|between:150,250',
    'married' : 'required|bool',
}


dlg = QDialog()
dlg.setLayout(QVBoxLayout())

dlg.baseModelView = QTableView(dlg)

dlg.validationView = QTableView(dlg)
dlg.validationDelegate = MultiRoleDelegate(dlg.validationView)
dlg.validationDelegate.setParent(dlg.validationView)
dlg.validationView.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
dlg.validationView.horizontalHeader().setResizeMode(QHeaderView.Stretch)

dlg.validationView.setItemDelegate(dlg.validationDelegate)

dlg.validationDelegate.roles.append(qt4.ValidationStateRole)
dlg.validationDelegate.roles.append(qt4.ValidationMessageRole)

dlg.validationView.setEditTriggers(QTableView.AllEditTriggers)
dlg.layout().addWidget(dlg.validationView)
dlg.layout().addWidget(dlg.baseModelView)

dlg.srcModel = ListOfDictsModel(listType, dlg.validationView)
dlg.srcModel.setModelData(testData)

dlg.baseModelView.setModel(dlg.srcModel)
dlg.baseModelView.horizontalHeader().setResizeMode(QHeaderView.Stretch)

dlg.model = RuleValidatorModel(parent=dlg.validationView)
dlg.model.setSourceModel(dlg.srcModel)


dlg.model.validator = app(RuleValidator)
dlg.model.rules = rules

dlg.validationView.setModel(dlg.model)

dlg.resize(700, 500)

dlg.show()
