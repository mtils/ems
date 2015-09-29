'''
Created on 19.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, Qt
from PyQt4.QtGui import QComboBox, QItemDelegate, QStyledItemDelegate, QWidget

from sqlalchemy.orm import object_mapper
from sqlalchemy.sql.expression import BooleanClauseList, and_
from sqlalchemy.util import symbol

from ems import qt4
from ems.qt4.util import variant_to_pyobject #@UnresolvedImport
from ems.qt4.itemmodel.sa.representative_model import RepresentativeModel #@UnresolvedImport
from ems.qt4.itemmodel.sa.representative_model import RepresentativeModelMatch #@UnresolvedImport
from ems.qt4.gui.widgets.bigcombo import BigComboBox #@UnresolvedImport
from ems.qt4.gui.mapper.sa.delegate.many2one import Many2OneComboMapperDelegate, Many2OneDelegate #@UnresolvedImport

from base import BaseStrategy #@UnresolvedImport


class ComboBoxRelationDelegate(QItemDelegate):
    def __init__(self, fkColumnName, itemModel, parent=None):
        super(ComboBoxRelationDelegate, self).__init__(parent)
        self._fkColumnName = fkColumnName
        self._itemModel = itemModel
        self._index2Fk = {}
        self._fk2Index = {}
        self.rebuildCurrentIndexHash()
        
    def setEditorData(self, editor, index):
        #print "setEditorData %s" % index.data().toString()
        currentIndex = self._fk2Index[variant_to_pyobject(index.data())]
        #print "currentIndex %s" % currentIndex
        #print self._itemModel.data(self._itemModel.index(index.row(),0)).toString()
        editor.setCurrentIndex(currentIndex)
        #super(ComboBoxRelationDelegate, self).setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        #print "setModelData %s" % index.data().toString()
        fkVal = self._index2Fk[editor.currentIndex()]
        model.setData(index, QVariant(fkVal))
        #super(ComboBoxRelationDelegate, self).setModelData(editor, model, index)
    
    def rebuildCurrentIndexHash(self):
        self._index2Fk.clear()
        for i in range(self._itemModel.rowCount()):
            variant = self._itemModel.data(self._itemModel.index(i,0),
                                           qt4.ForeignKeysRole)
            fkVal = variant_to_pyobject(variant)
            self._index2Fk[i] = fkVal
            self._fk2Index[fkVal] = i


    
#    def paint(self, painter, model, index):
#        #print "paint"
#        super(ComboBoxRelationDelegate, self).paint(painter, model, index)

        
class Many2OneComboStrategy(BaseStrategy):
    
    ormModelCache = {}
    maxEntriesForNormalCombo = 300
    
    def getRemoteClass(self, mapper, rProperty):
        direction = mapper.getRealRelationSymbol(rProperty)
        if direction is symbol('MANYTOONE'):
            return rProperty.mapper.class_manager.class_
        else:
            raise TypeError("Many2OneComboStrategy needs a MANYTOONE Relation")
    
    def getForeignKey(self, rProperty):
        return  rProperty.remote_side[0].key
    
    def buildSelectClauses(self, rProperty):
        clauses = []
        if isinstance(rProperty.primaryjoin, BooleanClauseList):
            if len(rProperty.primaryjoin) > 1:
                for clause in rProperty.primaryjoin:
                    try:
                        if isinstance(clause.right.value, (basestring, int, float, bool)):
                            clauses.append(clause)
                        #print "Clause: %s right %s" % (clause, type(clause.right.value))
                    except AttributeError:
                        pass
                    
        return clauses
            #print "Multiple Join Conditions %s" % len(rProperty.primaryjoin)
        #print type(rProperty.primaryjoin)
    
    def _getObjModel(self, mapper, propertyName, rProperty, matchModel=False):
        #objMapper = object_mapper(prototype)
        remoteClass = self.getRemoteClass(mapper, rProperty)

        session = None

        if mapper.session:
            session = mapper.session
        elif mapper.model.session:
            session = mapper.model.session
        
        if session is None:
            raise TypeError("Please Assign a session to the mapper")
        
        clauses = self.buildSelectClauses(rProperty)
        
        if len(clauses):
            if len(clauses) > 1:
                conj = clauses[0]
            else:
                conj = and_()
                for clause in clauses:
                    conj.append(clause)
                    
            query = session.query(remoteClass).filter(conj)
        else:
            query = session.query(remoteClass)
            
        
        orderByCol = remoteClass.__ormDecorator__().getDefaultOrderByProperty(remoteClass)
        
        if orderByCol is not None:
            query = query.order_by(remoteClass.__dict__[orderByCol])
        
        itemCount = query.count()
        
        fk = self.getForeignKey(rProperty)
        
        if itemCount > self.maxEntriesForNormalCombo:
            return RepresentativeModelMatch(session, remoteClass, fk,
                                            query, nullEntry="")
        else:
            return RepresentativeModel(session, remoteClass, fk,
                                       query, nullEntry="Auswahl...")
        
    
    def getWidget(self, mapper, propertyName, rProperty, parent=None):
        
        model = self._getObjModel(mapper, propertyName, rProperty)
        
        if isinstance(model, RepresentativeModelMatch):
            widget = BigComboBox(model, parent=parent)
            widget.setItemDelegate(Many2OneDelegate(widget))
            return widget
        else:
            widget = QComboBox(parent)
            widget.setModel(model)
            widget.setItemDelegate(Many2OneDelegate(widget))
            return widget
        
        return QWidget(parent)
        
    def map(self, mapper, widget, propertyName, rProperty):
        if isinstance(widget, QComboBox):

            model = self._getObjModel(mapper, propertyName, rProperty)
            
            col = mapper.model.columnOfName(propertyName)
            
            widget.setModel(model)
            mapper.dataWidgetMapper.addMapping(widget, col)
            
        else:
            raise TypeError("Many2OneComboStrategy can only handle QCombobox")
    
    def getDelegateForItem(self, mapper, propertyName, rProperty, parent=None):
        return Many2OneComboMapperDelegate(mapper, propertyName, parent)
    
    def getProperty(self, prototype, propertyName):
        objMapper = object_mapper(prototype)
        return objMapper.get_property(propertyName)
        