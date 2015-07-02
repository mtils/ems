
import sys

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QTableView, QApplication, QDialog, QVBoxLayout
from PyQt4.QtGui import QDialogButtonBox, QHeaderView

from ems import qt4
from ems.qt4.gui.util import to_dialog
from ems.qt4.gui.widgets.itemview.itemview_editor import ItemViewEditor
from ems.qt4.gui.mapper.base import BaseMapper
from ems.qt4.gui.itemdelegate.multiroledelegate import MultiRoleDelegate
from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel
from ems.qt4.itemmodel.validator_model import RuleValidatorModel
from ems.validation.rule_validator import RuleValidator
from ems.qt4.gui.notification.balloon_form_notifier import BalloonFormNotifier

from examples.qt4.bootstrap.create_app import create_app, app_path
from examples.qt4.gui.persondata_form import PersonDataForm
from examples.qt4.gui.itemmodel.validator_model_example import rules
from examples.xtype.persondata import itemType, testData, listType


class ValidationModelEditor(ItemViewEditor):

    modelKeys = ('forename', 'surname', 'age', 'weight', 'income', 'married')

    def __init__(self, itemView, connectOwnMethods=True, parent=None):

        ItemViewEditor.__init__(self, itemView, connectOwnMethods=True, parent=None)
        self.rowEditingRequested.connect(self.onRowEditingRequested)

        self.editor = None

    def onRowEditingRequested(self, rows):

        if self.editor is None:
            self.editor = self._createEditor()

        self._editorMapper.setCurrentIndex(rows[0])
        self.editor.show()

    def _createEditor(self):

        editor = PersonDataForm(parent=self)
        editor.setWindowFlags(Qt.Dialog)
        editor.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                    Qt.Horizontal, editor)
        editor.layout().addWidget(editor.buttonBox)
        #editor.buttonBox.accepted.connect(editor.close)

        self._mapToModel(editor, self.itemView.model())

        self._mapToNotifier(editor, self.itemView.model())

        return editor

    def _mapToModel(self, editor, model):

        self._editorMapper = BaseMapper(model)

        for key in self.modelKeys:
            widget = getattr(editor,"{0}Input".format(key))
            self._editorMapper.addMapping(widget, key)

        self.firstSelectedRowChanged.connect(self._editorMapper.setCurrentIndex)

    def _mapToNotifier(self, editor, model):
        self.notifier = BalloonFormNotifier()

        for key in self.modelKeys:
            widget = getattr(editor,"{0}Input".format(key))
            self.notifier.map(key, widget)

        self.notifier.setModel(model)

        self._editorMapper.currentIndexChanged.connect(self.notifier.setCurrentModelRow)

def create_dialogs(app):

    app.srcModel = ListOfDictsModel(listType)
    app.srcModel.setModelData(testData)

    app.validatorModel = RuleValidatorModel()
    app.validatorModel.setSourceModel(app.srcModel)
    app.validatorModel.validator = app(RuleValidator)
    app.validatorModel.rules = rules

    tableView = QTableView()
    tableView.setModel(app.validatorModel)
    tableView.setItemDelegate(MultiRoleDelegate(tableView))
    tableView.horizontalHeader().setResizeMode(QHeaderView.Stretch)
    tableView.verticalHeader().setResizeMode(QHeaderView.Stretch)

    tableView.itemDelegate().roles.append(qt4.ValidationStateRole)
    tableView.itemDelegate().roles.append(qt4.ValidationMessageRole)

    app.itemView = ValidationModelEditor(tableView)

    app.dlg = QDialog()
    app.dlg.setLayout(QVBoxLayout())
    app.dlg.layout().setContentsMargins(0,0,0,0)
    app.dlg.layout().addWidget(app.itemView)

    app.dlg.baseModelView = QTableView(app.dlg)
    app.dlg.baseModelView.horizontalHeader().setResizeMode(QHeaderView.Stretch)
    app.dlg.baseModelView.verticalHeader().setResizeMode(QHeaderView.Stretch)
    app.dlg.baseModelView.setModel(app.srcModel)
    app.dlg.layout().addWidget(app.dlg.baseModelView)

    app.dlg.show()

if __name__ == '__main__':

    app = create_app(sys.argv, app_path)

    app.started += create_dialogs

    sys.exit(app.start(app_path, sys.argv))