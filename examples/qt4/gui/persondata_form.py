

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QTableView, QApplication, QWidget, QVBoxLayout
from PyQt4.QtGui import QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox

class PersonDataForm(QWidget):

    def __init__(self, parent=None):
        super(PersonDataForm, self).__init__(parent)

        self._setupUi()


    def _setupUi(self):

        self.setLayout(QVBoxLayout())

        self.forenameInput = QLineEdit(self)
        self.forenameInput.setObjectName('forenameInput')
        self.layout().addWidget(self.forenameInput)

        self.surnameInput = QLineEdit(self)
        self.surnameInput.setObjectName('surnameInput')
        self.layout().addWidget(self.surnameInput)

        self.ageInput = QSpinBox(self)
        self.ageInput.setObjectName('ageInput')
        self.ageInput.setRange(0, 200)
        self.layout().addWidget(self.ageInput)

        self.weightInput = QDoubleSpinBox(self)
        self.weightInput.setObjectName('weightInput')
        self.weightInput.setRange(0.0, 1000.0)
        self.layout().addWidget(self.weightInput)

        self.incomeInput = QDoubleSpinBox(self)
        self.incomeInput.setObjectName('incomeInput')
        self.incomeInput.setRange(0.0, 1000.0)
        self.layout().addWidget(self.incomeInput)

        self.marriedInput = QCheckBox(self)
        self.marriedInput.setObjectName('marriedInput')
        self.layout().addWidget(self.marriedInput)