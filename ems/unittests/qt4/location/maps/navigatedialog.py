#coding=utf-8
'''
Created on 19.11.2011

@author: michi
'''
from PyQt4.QtGui import QDialog, QLineEdit, QComboBox, QFormLayout, QVBoxLayout,\
    QDialogButtonBox
from ems.qt4.location.maps.georouterequest import GeoRouteRequest

class NavigateDialog(QDialog):
    
    _addressEdit = None
    
    _modeCombo = None
    
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        
        formLayout = QFormLayout()
        vbox = QVBoxLayout()
        
        self._addressEdit = QLineEdit(self)
        formLayout.addRow("Adresse",self._addressEdit)
        
        self._modeCombo = QComboBox(self)
        self._modeCombo.addItem("Auto", GeoRouteRequest.CarTravel)
        self._modeCombo.addItem("Zu Fuss", GeoRouteRequest.PedestrianTravel)
        self._modeCombo.addItem("Fahrrad", GeoRouteRequest.BicycleTravel)
        self._modeCombo.addItem(self.trUtf8(u"Öffentlicher Nahverkehr"),
                                GeoRouteRequest.PublicTransitTravel)
        formLayout.addRow("Fortbewegungsmittel", self._modeCombo)
        
        self._bb = QDialogButtonBox(self)
        self._bb.addButton(QDialogButtonBox.Ok)
        self._bb.addButton(QDialogButtonBox.Cancel)
        self._bb.accepted.connect(self.accept)
        self._bb.rejected.connect(self.reject)
        
        vbox.addLayout(formLayout)
        vbox.addWidget(self._bb)
        
        self.setLayout(vbox)
        self.setWindowTitle("Richtungen zur Adresse")
    
    def destinationAddress(self):
        return self._addressEdit.text()
    
    def travelMode(self):
        v = self._modeCombo.itemData(self._modeCombo.currentIndex())
        return v.toInt()[0]