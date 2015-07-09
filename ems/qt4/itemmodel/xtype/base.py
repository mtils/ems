'''
Created on 28.04.2012

@author: michi
'''
from copy import copy

from PyQt4.QtCore import Qt, QModelIndex, QVariant, QAbstractItemModel, QString
from PyQt4.QtCore import pyqtSignal

from ems.xtype.base import XType, ComplexType, SequenceType, NamedFieldType #@UnresolvedImport
from ems import qt4
from ems.qt4.util import VariantContainer, variant_to_pyobject
from ems.qt4.itemmodel.reflectable_mixin import ReflectableMixin #@UnresolvedImport
from ems.qt4.itemmodel.xtype.factory import getModelForXType #@UnresolvedImport

class AbstractXtypeItemModel(QAbstractItemModel, ReflectableMixin):

    dirtyStateChanged = pyqtSignal(bool)

    def __init__(self, xType, parent=None):
        ReflectableMixin.__init__(self)
        QAbstractItemModel.__init__(self, parent)

        self._modelData = []
        self._headerData = None
        if not isinstance(xType, ComplexType):
            raise TypeError('XTypeBaseInterface is only for ComplexType types')
        self._xType = xType
        self._keyLabels = {}
        self._fieldTitlesLong = {}
        self._fieldDescriptions = {}
        self.isEditable = True
        self._childModels = {}
        self._enabledFlagColumn = None
        self._isDirty = False

    def isDirty(self):
        return self._isDirty

    def _setDirty(self, dirty):
        if self._isDirty != dirty:
            self._isDirty = dirty
            self.dirtyStateChanged.emit(self._isDirty)

    def resetDirty(self):
        self._setDirty(False)

    @property
    def xType(self):
        return self._xType

    def _rowType(self):
        return self._xType

    def columnType(self, column):
        return self._rowType().keyType(column)

    def nameOfColumn(self, column):
        return self._rowType().keyName(column)

    def columnOfName(self, name):
        return self._rowType().keys().index(name)

    def columnCount(self, index=QModelIndex()):
        return len(self._rowType())

    def setEnabledFlagColumn(self, enabledFlagColumn):
        self._enabledFlagColumn = enabledFlagColumn

    def enabledFlagColumn(self):
        return self._enabledFlagColumn

    def rowCount(self, index=QModelIndex()):
        return len(self._modelData)

    def fieldTitleLong(self, fieldName):
        try:
            return self._fieldTitlesLong[fieldName]
        except KeyError:
            return self.getKeyLabel(fieldName)

    def setFieldTitleLong(self, fieldName, longTitle):
        self._fieldTitlesLong[fieldName] = longTitle
        try:
            i = self._rowType().keys().index(fieldName)
            self.headerDataChanged.emit(Qt.Horizontal, i, i)
        except ValueError:
            pass

    def setKeyLabel(self, key, label):
        self._keyLabels[key] = label
        try:
            i = self._rowType().keys().index(key)
            self.headerDataChanged.emit(Qt.Horizontal, i, i)
        except ValueError:
            pass
    
    def getRowAsDict(self, row):
        if not row < self.rowCount():
            return {}
        result = {}
        for col in range(self.columnCount()):
            colName = self.nameOfColumn(col)
            result[colName] = self._modelData[row][colName]
        return result
    
    def getKeyLabel(self, key):
        try:
             return self._keyLabels[key]
        except KeyError:
            return key
    
    def _getChildModelHash(self, index):
        return "{0}|{1}".format(index.row(), index.column())
    
    def childModel(self, index):
        childHash = self._getChildModelHash(index)
        if not self._childModels.has_key(childHash):
            xType = self.columnType(index.column())
            self._childModels[childHash] = getModelForXType(xType, self)
            colName = unicode(self.nameOfColumn(index.column()))
            keyPrefix = colName + '.'
            for key in self._keyLabels:
                if key.startswith(keyPrefix):
                    self._childModels[childHash].setKeyLabel(key[len(keyPrefix):],
                                                              self._keyLabels[key])
        return self._childModels[childHash]

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, object=0)

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if orientation == Qt.Horizontal:
            keyName = self.nameOfColumn(section)
            if role in (Qt.DisplayRole, qt4.FieldTitleRole):
                return QVariant(self.getKeyLabel(keyName))
            elif role == qt4.FieldTitleLongRole:
                return QVariant(self.fieldTitleLong(keyName))
            elif role == qt4.ColumnNameRole:
                return QVariant(keyName)

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(int(section + 1))

        return QVariant()

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return QVariant()

        keyName = self.nameOfColumn(index.column())

        if role in (Qt.DisplayRole, Qt.EditRole):
            try:
                value = self._pyData(index.row(), keyName, role)
                if not isinstance(value, (dict, list)):
                    return QVariant(value)
                else:
                    return QVariant(VariantContainer((value,)))
            except KeyError:
                return QVariant()
            except AttributeError:
                return QVariant()

        if role == qt4.ColumnNameRole:
            return QVariant(unicode(keyName))

        if role == qt4.RowObjectRole:
            return QVariant(self._pyData(index.row(), keyName, role))

        if role >= qt4.XTypeRole:
            xType = self.columnType(index.column())
            if role == qt4.XTypeRole:
                return QVariant(xType)
            if role == qt4.XTypeGroupRole:
                return QVariant(xType.group)
            if role == qt4.XTypeDefaultValueRole:
                return QVariant(xType.defaultValue)
            if role == qt4.XTypeCanBeNoneRole:
                return QVariant(xType.canBeNone)
            if role == qt4.XTypePrefixRole:
                try:
                    prefix = xType.strPrefix
                    if prefix:
                        return QVariant(QString.fromUtf8(prefix))
                    return QVariant("")
                except AttributeError:
                    return QVariant("")
            if role == qt4.XTypeSuffixRole:
                try:
                    suffix = xType.strSuffix
                    if suffix:
                        return QVariant(QString.fromUtf8(suffix))
                    return QVariant("")
                except AttributeError:
                    return QVariant("")

            if role == qt4.XTypeDecimalsSeparatorRole:
                try:
                    sep = xType.decimalsSeparator
                    if sep:
                        return QVariant(QString.fromUtf8(sep))
                    return QVariant("")
                except AttributeError:
                    return QVariant("")

            if role == qt4.XTypeThousandsSeparatorRole:
                try:
                    sep = xType.thousandsSeparator
                    if sep:
                        return QVariant(QString.fromUtf8(sep))
                    return QVariant("")
                except AttributeError:
                    return QVariant("")

            if role == qt4.XTypeDecimalsCountRole:
                try:
                    decCount = xType.decimalsCount
                    if decCount is None:
                        return QVariant()
                    return QVariant(decCount)
                except AttributeError:
                    return QVariant()

            if role == qt4.XTypeMinValueRole:
                try:
                    minValue = xType.minValue
                    if minValue is None:
                        return QVariant()
                    return QVariant(minValue)
                except AttributeError:
                    return QVariant()

            if role == qt4.XTypeMaxValueRole:
                try:
                    maxValue = xType.maxValue
                    if maxValue is None:
                        return QVariant()
                    return QVariant(maxValue)
                except AttributeError:
                    return QVariant()

            if role == qt4.XTypeMinLengthRole:
                try:
                    minLength = xType.minLength
                    if minLength is None:
                        return QVariant()
                    return QVariant(minLength)
                except AttributeError:
                    return QVariant()

            if role == qt4.XTypeMaxLengthRole:
                try:
                    maxLength = xType.maxLength
                    if maxLength is None:
                        return QVariant()
                    return QVariant(maxLength)
                except AttributeError:
                    return QVariant()

            if role == qt4.XTypeValueToUnitSpaceRole:
                try:
                    return QVariant(xType.value2UnitSpace)
                except AttributeError:
                    return QVariant()

            if role == qt4.XTypeUnitStrPositionRole:
                try:
                    return QVariant(xType.unitStrPosition)
                except AttributeError:
                    return QVariant()

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return False

        keyName = self.nameOfColumn(index.column())
        pyValue = variant_to_pyobject(value)

        if pyValue == self._pyData(index.row(), keyName, role):
            return False
        result = self._setPyData(index.row(), keyName, pyValue, role)
        if not result:
            return False

        self._setDirty(True)
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        itemIsEnabled = True
        if self._enabledFlagColumn is not None:
            itemIsEnabled = variant_to_pyobject(self.index(index.row(),
                                                           self._enabledFlagColumn).data())

        if not self.isEditable:
            if itemIsEnabled:
                return Qt.ItemIsSelectable | Qt.ItemIsEnabled
            return Qt.ItemIsSelectable

        xType = self.columnType(index.column())

        if not xType.canBeEdited:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

        if not itemIsEnabled:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled  | Qt.ItemIsEditable
    
    def parent(self, index):
        return QModelIndex()
    
    def pyData(self, index, role=Qt.DisplayRole):
        return variant_to_pyobject(self.data(index, role))
    
    def _pyData(self, row, keyName, role=Qt.EditRole):
        raise NotImplementedError('Please implement _pyData()')
    
    def _setPyData(self, row, keyName, value, role=Qt.EditRole):
        raise NotImplementedError('Please implement _setPyData()')
    
    def getRowTemplate(self, values=None):
        raise NotImplementedError('Please implement getRowTemplate()')
    
    def modelData(self):
        raise NotImplementedError('Please implement modelData()')
    
    def setModelData(self, modelData):
        raise NotImplementedError('Please implement setModelData()')
    
    def _appendToModelData(self, row):
        self._modelData.append(row)

class SingleRowModel(AbstractXtypeItemModel):

    def __init__(self, xType, parent=None):
        if not isinstance(xType, NamedFieldType):
            raise TypeError('SingleRowInterface is only for NamedFieldType types')
        AbstractXtypeItemModel.__init__(self, xType, parent)

    def insertRows(self, row, count, parent=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be inserted")
        rowCount = self.rowCount(parent)
        if rowCount > 0:
            return False

        self.beginInsertRows(parent, row, row)
        self._modelData.append(self.getRowTemplate())
        self.endInsertRows()

        self._setDirty(True)
        return True

    def removeRows(self, row, count, parentIndex=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be removed")

        rowCount = self.rowCount(parentIndex)

        if rowCount < 1:
            return False

        if not self._xType.canBeNone:
            return False

        self.beginRemoveRows(parentIndex, row, row)
        self._modelData.pop()
        self.endRemoveRows()
        self._setDirty(True)
        return True

    def modelData(self):
        try:
            return self._modelData[0]
        except IndexError:
            return None

    def setModelData(self, modelData):
        self.beginResetModel()

        self._modelData = []

        self._appendToModelData(self.getRowTemplate(values=modelData))

        self.endResetModel()
        self._setDirty(False)

    def __getitem__(self, key):
        return self._pyData(0, key, Qt.EditRole)

    def __setitem__(self, key, value):
        col = self.columnOfName(key)
        index = self.index(0, col)
        self.setData(index, QVariant(value))


class MultipleRowModel(AbstractXtypeItemModel):
    
    def __init__(self, xType, parent=None):
        if not isinstance(xType, SequenceType):
            raise TypeError('MultipleRowInterface is only for SequenceType types')
        if not isinstance(xType.itemType, ComplexType):
            raise TypeError('MultipleRowInterface is only for Sequences of ComplexType')
        AbstractXtypeItemModel.__init__(self, xType, parent)
        
    def _rowType(self):
        return self._xType.itemType
    
    def insertRows(self, row, count, parent=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be inserted")
        rowCount = self.rowCount(parent)
        if row != rowCount:
            raise NotImplementedError("Currently the row can be inserted at the end")
        
        if self._xType.maxLength is not None:
            if rowCount >= self._xType.maxLength:
                return False
            
        self.beginInsertRows(parent, row, row)
        self._modelData.append(self.getRowTemplate())
        self.endInsertRows()
        self._setDirty(True)
        return True
    
    def removeRows(self, row, count, parentIndex=QModelIndex()):
        if count > 1:
            raise NotImplementedError("Currently only one row can be removed")
        
        if self._xType.minLength is not None:
            if self.rowCount() <= self._xType.minLength:
                return False
        try:
            data = self._modelData[row]
        except IndexError:
            return False
        
        
        self.beginRemoveRows(parentIndex, row, row)
        self._modelData.pop(row)
        self.endRemoveRows()
        self._setDirty(True)
        return True
    
    def modelData(self):
        return self._modelData
    
    def setModelData(self, modelData):
        self.beginResetModel()
        
        self._modelData = []
        
        i = 0    
        for row in modelData:
            
            rowTpl = self.getRowTemplate(values=row)
            self._appendToModelData(rowTpl)
            
            i += 1
            if self._xType.maxLength is not None:
                if i >= self._xType.maxLength:
                    break
            
        
        self.endResetModel()
        self._setDirty(False)
    
    def rowCount(self, index=QModelIndex()):
        
        rowCount = len(self._modelData)
        if rowCount == 0:
            
            if len(self._xType.defaultValue):
                self._modelData = copy(self._xType.defaultValue)
                
            elif self._xType.defaultLength != 0:
                for i in range(self._xType.defaultLength):
                    self._modelData.append(self.getRowTemplate())
                    
            rowCount = len(self._modelData)
        
        return rowCount

class DictGetSetInterface(object):
    def _pyData(self, row, keyName, role=Qt.EditRole):
        if role in (Qt.EditRole, Qt.DisplayRole):
            return self._modelData[row][keyName]
        elif role == qt4.RowObjectRole:
            return self._modelData[row]
    
    def _setPyData(self, row, keyName, value, role=Qt.EditRole):
        self._modelData[row][keyName] = value
        return True
    
    def getRowTemplate(self, values=None):
        template = {}
#        if self._rowType().defaultValue:
#            #template = self._rowType().defaultValue
#            print self._rowType().defaultValue
        for key in self._rowType().keys():
            xType = self._rowType().keyType(key)
            if isinstance(values, dict) and values.has_key(key):
                template[key] = values[key]
            elif isinstance(xType, XType):
                template[key] = xType.defaultValue
            else:
                template[key] = None
        return template

class ObjectGetSetInterface(object):
    def _pyData(self, row, keyName, role=Qt.EditRole):
        if role in (Qt.EditRole, Qt.DisplayRole):
            return self._modelData[row].__getattribute__(keyName)
        elif role == qt4.RowObjectRole:
            return QVariant(self._modelData[row])

    def _setPyData(self, row, keyName, value, role=Qt.EditRole):
        self._modelData[row].__setattr__(keyName, value)
        return True

    def getRowTemplate(self, values=None):
        if isinstance(values, self._rowType().cls):
            return values
        template = self._rowType().cls.__new__(self._rowType().cls)
        for key in self._rowType().keys():
            xType = self._rowType().keyType(key)
            if isinstance(values, self._rowType().cls):
                template.__setattr__(key, values.__getattribute__(key))
            elif isinstance(xType, XType):
                template.__setattr__(key, xType.defaultValue)
            else:
                template.__setattr__(key, None)
        return template
    
    def getRowObject(self, row):
        try:
            return self._modelData[row]
        except KeyError:
            pass

class SingleRowDictModel(DictGetSetInterface, SingleRowModel):
    pass

class MultipleRowDictModel(DictGetSetInterface, MultipleRowModel):
    pass

class SingleRowObjectModel(ObjectGetSetInterface, SingleRowModel):
    pass

class MultipleRowObjectModel(ObjectGetSetInterface, MultipleRowModel):
    pass

class DictOfDictsModel(DictGetSetInterface, SingleRowModel):
    def __init__(self, xType, parent=None):
        newXType = self._buildFlatXType(xType)

        #for key in newXType:
            #print key

        self._originalXType = xType
        super(DictOfDictsModel, self).__init__(newXType, parent)

    def _buildFlatXType(self, originalXType, newXType=None, nameStack=None):

        if newXType is None:
            newXType = NamedFieldType()

        if nameStack is None:
            nameStack = []

        for key in originalXType:
            nameStack.append(key)
            name = u".".join(nameStack)
            newXType[name] = originalXType[key]
            if isinstance(originalXType[key], ComplexType):
                if isinstance(originalXType[key], NamedFieldType):
                    self._buildFlatXType(originalXType[key], newXType, nameStack)
                else:
                    raise TypeError("Every xtype in DictOfDictsModel has to be scalar or NamedFieldType/DictType")

            nameStack.pop()
        return newXType

    @staticmethod
    def _getNestedDict(pathStack, dct):
        while pathStack:
            i = pathStack.pop(0)
            if not i in dct:
                dct[i] = {}
            dct = dct[i]
        return [dct]

    @staticmethod
    def _fillNestedDict(pathStack, dct, value):
        try:
            name = pathStack.pop(0)
        except IndexError:
            return
        if name in dct:
            if not dct[name]:
                dct[name] = value
            else:
                DictOfDictsModel._fillNestedDict(pathStack, dct[name], value)

    @staticmethod
    def _buildFlatDict(dct, newDict=None, nameStack=None):
        if newDict is None:
            newDict = {}
        if nameStack is None:
            nameStack = []

        for key in dct:
            nameStack.append(key)
            name = u".".join(nameStack)
            if not isinstance(dct[key], dict):
                newDict[name] = dct[key]
            else:
                DictOfDictsModel._buildFlatDict(dct[key], newDict, nameStack)
            nameStack.pop()
        return newDict

    def modelData(self):

        if not len(self._modelData):
            return None

        modelData = {}

        for name in sorted(self._modelData[0].keys()):
            nameStack = name.split('.')
            node = self._getNestedDict(nameStack, modelData)

        for name in sorted(self._modelData[0].keys()):
            nameStack = name.split('.')
            self._fillNestedDict(nameStack, modelData, self._modelData[0][name])
        return modelData
    
    def setModelData(self, modelData):
        converted = self._buildFlatDict(modelData)
        return super(DictOfDictsModel, self).setModelData(converted)
