
import sys

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout

from ems.xtype.base import NumberType, StringType, BoolType, UnitType, DictType
from ems.validation.validator import RuleValidator, Registry, SimpleMessageProvider
from ems.qt4.itemmodel.validator_model import ValidatorModel
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel
from examples.xtype.persondata import itemType, testData, listType
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel


if __name__ == '__main__':

    app = QApplication(sys.argv)

    dlg = QDialog()
    dlg.setLayout(QVBoxLayout())
    dlg.tableView = QTableView(dlg)
    dlg.layout().addWidget(dlg.tableView)

    dlg.srcModel = ListOfDictsModel(listType, dlg.tableView)
    dlg.srcModel.setModelData(testData)

    dlg.model = ValidatorModel(parent=dlg.tableView)
    dlg.model.setSourceModel(dlg.srcModel)

    validator = RuleValidator()

    dlg.tableView.setModel(dlg.model)


    sys.exit(dlg.exec_())