'''
Created on 04.08.2011

@author: michi
'''
from PyQt4.QtGui import QStyledItemDelegate, QComboBox, QApplication, QCheckBox,\
    QSpinBox, QDoubleSpinBox
from PyQt4.QtCore import QVariant, QLocale, QObject, Qt

from ems.qt4.itemmodel.querybuilder_model import QueryBuilderModel #@UnresolvedImport
from ems.qt4.gui.widgets.tableview.addable_tableview import AddableTableView #@UnresolvedImport
from ems.qt4.gui.itemdelegate.genericdelegate import GenericDelegate #@UnresolvedImport
from ems.qt4.gui.widgets.treecombo import TreeComboBox #@UnresolvedImport
from ems.qt4.util import variant_to_pyobject #@UnresolvedImport
from ems.qt4.gui.widgets.bigcombo import BigComboBox #@UnresolvedImport

class RowBuilderBackend(QObject):
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
    
    def populateFieldInput(self, fieldInput):
        pass
            
    def rowAdded(self, row):
        pass
    
    def getDisplayedFieldText(self, data):
        return data.toString()
    
    def getDisplayedOperatorText(self, data):
        return data.toString()
    
    def getDisplayedValueText(self, property, value):
        return value.toString()
    
    def onFieldInputCurrentFieldChanged(self, searchRow, item):
        pass
    
    def buildQuery(self, criterias):
        raise NotImplementedError("Please create a buildQuery Method")
    
    def setEditorData(self, editor, index):
        pass
    
class FieldSelectDelegate(QStyledItemDelegate):
    def __init__(self, builderBackend, parent=None):
        self.builderBackend = builderBackend
        QStyledItemDelegate.__init__(self, parent)
        
        self._currentText = ""
    
    def displayText(self, string, locale):
        return self._currentText
    
    def paint(self, painter, option, index):
        self._currentText = self.builderBackend.getDisplayedFieldText(index.data())
        QStyledItemDelegate.paint(self, painter, option, index)
    
    def createEditor(self, parent, option, index):
        editor = TreeComboBox(parent)
        self.builderBackend.populateFieldInput(editor)
        return editor
    
    def setModelData(self, editor, model, index):
        data = editor.itemData(editor.currentIndex())
        model.setData(index, data)
    
    def setEditorData(self, editor, index):
        editor.setCurrentIndex(editor.findData(index.data()))
        
        
class ConjunctionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.conjunctions = ['AND','OR']
        self.translation = {
                            'AND':'Und',
                            'OR':'Oder',
                            'NO_CONJUNCTION_POSSIBLE':'' 
                            }
        
        self._currentText = u''

    def displayText(self, string, locale):
        return self._currentText
    
    def paint(self, painter, option, index):
        if index.row() == 0 and index.column() == 0:
            self._currentText = self.translation['NO_CONJUNCTION_POSSIBLE']
        else:
            self._currentText = self.translation[unicode(index.data().toString())]
        #self.displayText(self.translation[unicode(index.data().toString())],QLocale())
        
        QStyledItemDelegate.paint(self, painter, option, index)
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        for conj in self.conjunctions:
            editor.addItem(self.trUtf8(self.translation[conj]),
                           QVariant(conj))
        
        return editor
    
    def setModelData(self, editor, model, index):
        data = editor.itemData(editor.currentIndex())
        model.setData(index, data)
    
    def setEditorData(self, editor, index):
        editor.setCurrentIndex(editor.findData(index.data()))
        
        #QStyledItemDelegate.setModelData(self, editor, model, index)

class OperatorDelegate(QStyledItemDelegate):
    def __init__(self, builderBackend, model, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.builderBackend = builderBackend
        self._currentText = u''
        self._model = model

    def displayText(self, string, locale):
        return self._currentText
        
    
    def paint(self, painter, option, index):
        self._currentText = self.builderBackend.getDisplayedOperatorText(index.data())
        QStyledItemDelegate.paint(self, painter, option, index)
    
    def createEditor(self, parent, option, index):
        propertyIndex = self._model.index(index.row(), 1)
        field = unicode(self._model.data(propertyIndex).toString())
        
        editor = QComboBox(parent)
        self.builderBackend.populateOperatorCombo(editor, field)
                
        return editor
    
    def setModelData(self, editor, model, index):
        data = editor.itemData(editor.currentIndex())
        model.setData(index, data)
    
    def setEditorData(self, editor, index):
        res = editor.findData(index.data())
        if res < 0:
            res = 0
        editor.setCurrentIndex(res)

class ValueDelegate(QStyledItemDelegate):
    def __init__(self, builderBackend, model, parent=None):
        QStyledItemDelegate.__init__(self, parent)
        self.builderBackend = builderBackend
        self._currentText = u''
        self._model = model

    def displayText(self, string, locale):
        return self._currentText
    
    def paint(self, painter, option, index):
        propertyIndex = self._model.index(index.row(), 1)
        field = unicode(self._model.data(propertyIndex).toString())
        
        self._currentText = self.builderBackend.getDisplayedValueText(field, index.data())
        QStyledItemDelegate.paint(self, painter, option, index)
    
    def createEditor(self, parent, option, index):
        prevIndex = self._model.index(index.row(), index.column()-2)
        field = unicode(self._model.data(prevIndex).toString())
        
        editor =  self.builderBackend.getValueEditor(parent, field)
        editor.setParent(parent)
                
        return editor
    
    def extractValueOfWidget(self, widget):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, TreeComboBox):
            return variant_to_pyobject(widget.value())
        if isinstance(widget, BigComboBox):
            return variant_to_pyobject(widget.value())
        if isinstance(widget, QComboBox):
            return variant_to_pyobject(widget.itemData(widget.currentIndex(), Qt.UserRole))
        if hasattr(widget, 'value') and callable(widget.value):
            return widget.value()
        if hasattr(widget, 'text') and callable(widget.text):
            return widget.text()
    
    def setModelData(self, editor, model, index):
        model.setData(index, QVariant(self.extractValueOfWidget(editor)))
    
    def setEditorData(self, editor, index):
        return self.builderBackend.setEditorData(editor, index)
#        res = editor.findData(index.data())
#        if res < 0:
#            res = 0
#        editor.setCurrentIndex(res)

class QueryBuilderTableView(AddableTableView):
    def __init__(self, addIcon, removeIcon, builderBackend, parent=None):
        AddableTableView.__init__(self, addIcon, removeIcon, parent)
        self.builderBackend = builderBackend
        self.setModel(QueryBuilderModel(self))
        self.verticalHeader().addRowButtonClicked.connect(self.model().appendRow)
        self.verticalHeader().removeRowButtonClicked.connect(self.model().removeRow)
        self.setItemDelegate(GenericDelegate(self))
        self.itemDelegate().insertColumnDelegate(0,ConjunctionDelegate())
        fieldDelegate = FieldSelectDelegate(builderBackend)
        self.itemDelegate().insertColumnDelegate(1,fieldDelegate)
        operatorDelegate = OperatorDelegate(builderBackend, self.model())
        self.itemDelegate().insertColumnDelegate(2,operatorDelegate)
        valueDelegate = ValueDelegate(builderBackend, self.model())
        self.itemDelegate().insertColumnDelegate(3,valueDelegate)
    
    def buildFilter(self, *args, **kwargs):
        return self.builderBackend.buildFilter(self.model().clauses,*args, **kwargs)
    