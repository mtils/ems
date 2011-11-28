'''
Created on 27.11.2011

@author: michi
'''
from PyQt4.QtCore import Qt

from PyQt4.QtGui import QDialog, QLineEdit, QLabel, QDoubleSpinBox, \
    QVBoxLayout, QFormLayout, QDialogButtonBox
from ems.qt4.location.geocoordinate import GeoCoordinate

class MarkerDialog(QDialog):
    _nameEdit = None
    
    _addressLabel = None
    
    _lonSpin = None
    
    _latSpin = None
    
    _marker = None
    
    _bb = None
    
    def __init__(self, marker, parent=None):
        super(MarkerDialog, self).__init__(parent)
        self._marker = marker
        
        vbox = QVBoxLayout()
        fm = QFormLayout()
        
        self._nameEdit = QLineEdit(self)
        
        self._nameEdit.setText(marker.name())
        marker.nameChanged.connect(self._nameEdit.setText)
        fm.addRow("Name", self._nameEdit)
        
        self._addressLabel = QLabel(self)
        self._setAddressLabel(marker.address())
        marker.addressChanged.connect(self._setAddressLabel)
        fm.addRow("Adresse", self._addressLabel)
        
        self._lonSpin = QDoubleSpinBox(self)
        self._lonSpin.setMinimum(-180.0)
        self._lonSpin.setMaximum(180.0)
        self._lonSpin.setDecimals(7)
        self._lonSpin.setValue(marker.coordinate().longitude())
        fm.addRow("Longitude", self._lonSpin)
        
        self._latSpin = QDoubleSpinBox(self)
        self._latSpin.setMinimum(-90.0)
        self._latSpin.setMaximum(90.0)
        self._latSpin.setDecimals(7)
        self._latSpin.setValue(marker.coordinate().latitude())
        fm.addRow("Latitude", self._latSpin)
        
        self._bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close,
                                    Qt.Horizontal, self)
        
        self._bb.accepted.connect(self.accept)
        self._bb.rejected.connect(self.reject)
        
        vbox.addLayout(fm)
        vbox.addWidget(self._bb)
        self.setLayout(vbox)
        self.setWindowTitle("Marker bearbeiten")
    
    def updateMarker(self):
        self._marker.setName(self._nameEdit.text())
        coord = GeoCoordinate(self._latSpin.value(), self._lonSpin.value())
        self._marker.setCoordinate(coord)
    
    def _setAddressLabel(self, address):
        
        addressFormat = self.tr("$street\n$city, $state $postcode\n$country")
        addressFormat.replace("$street", address.street())
        addressFormat.replace("$city", address.city())
        addressFormat.replace("$county", address.county())
        addressFormat.replace("$state", address.state())
        addressFormat.replace("$postcode", address.postcode())
        addressFormat.replace("$district", address.district())
        addressFormat.replace("$country", address.country())
        self._addressLabel.setText(addressFormat)