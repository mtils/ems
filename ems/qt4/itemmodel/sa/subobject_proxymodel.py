'''
Created on 22.09.2011

@author: michi
'''
from PyQt4.QtCore import QModelIndex, Qt
from ems.qt4.itemmodel.editable_proxymodel import EditableProxyModel #@UnresolvedImport

class SubObjectProxyModel(EditableProxyModel):
    def __init__(self, ormPropertyNameOrProperties=None, parent=None):
        EditableProxyModel.__init__(self, parent)
        
        self._ormPropertyName = ""
        self._properties = []
        self._proxy2SourceColumnMap = {}
        self._source2ProxyColumnMap = {}
        self._property2ProxyMap = {}
        self.sectionFriendlyNames = {}
         
        if ormPropertyNameOrProperties is not None:
            if isinstance(ormPropertyNameOrProperties, (list, tuple)):
                self.properties = ormPropertyNameOrProperties
            if isinstance(ormPropertyNameOrProperties, basestring):
                self.ormPropertyName = ormPropertyNameOrProperties

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and \
           self.sectionFriendlyNames.has_key(section) and \
           role == Qt.DisplayRole:
               return self.sectionFriendlyNames[section]
        return EditableProxyModel.headerData(self, section, orientation, role)

    @property
    def session(self):
        return self.sourceModel().session
    
    def setSourceModel(self, sourceModel):
        
        result = EditableProxyModel.setSourceModel(self, sourceModel)
        self._fillPropertyMaps()
        return result
    
    def getOrmPropertyName(self):
        return self._ormPropertyName
    
    def setOrmPropertyName(self, ormPropertyName):
        self._ormPropertyName = ormPropertyName
    
    ormPropertyName = property(getOrmPropertyName, setOrmPropertyName)
    
    def getProperties(self):
        return self._properties
    
    def setProperties(self, properties):
        self._properties = properties
        
        self._proxy2SourceColumnMap.clear()
        self._source2ProxyColumnMap.clear()
        self._property2ProxyMap.clear()
        
        i = 0
        for prop in self._properties:
            self._property2ProxyMap[prop] = i
            i += 1 
        
    def _getColumnMap(self, property):
        pass
    
    def _fillPropertyMaps(self):
        proxyCol = 0
        for prop in self._properties:
            sourceCol = self.sourceModel().columnOfName(prop)
            self._proxy2SourceColumnMap[proxyCol] = sourceCol
            self._source2ProxyColumnMap[sourceCol] = proxyCol
            proxyCol += 1
    properties = property(getProperties, setProperties)
    
    def columnCount(self, parentIndex=QModelIndex()):
        return len(self._properties)
    
    def mapFromSource(self, sourceIndex):
        if not len(self._source2ProxyColumnMap):
            self._fillPropertyMaps()
        try:
            proxyCol = self._source2ProxyColumnMap[sourceIndex.column()]
            return self.index(sourceIndex.row(), proxyCol)
        except KeyError:
            #raise KeyError("Could not map column {0}".format(sourceIndex.column()))
            pass
            return QModelIndex()
    
    def getObject(self, row):
        return self.sourceModel().getObject(row)
        
    
    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QModelIndex()
        
        if not len(self._proxy2SourceColumnMap):
            self._fillPropertyMaps()
        try:
            sourceCol = self._proxy2SourceColumnMap[proxyIndex.column()]
        except KeyError:
            raise KeyError("Could not map column {0}".format(proxyIndex.column()))
        #print "proxy: {0} source: {1}".format(proxyIndex.column(), sourceCol)
        return self.sourceModel().index(proxyIndex.row(), sourceCol)