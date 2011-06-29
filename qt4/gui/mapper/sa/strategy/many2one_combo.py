'''
Created on 19.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QComboBox, QItemDelegate, QWidget

from sqlalchemy.orm import object_mapper
from sqlalchemy.sql.expression import BooleanClauseList, and_
from sqlalchemy.util import symbol

from ems import qt4
from ems.qt4.util import variant_to_pyobject #@UnresolvedImport
from ems.qt4.itemmodel.alchemyormmodel import AlchemyOrmModel
from ems.qt4.itemmodel.sa.representative_model import RepresentativeModel #@UnresolvedImport
from ems.qt4.itemmodel.sa.representative_model import RepresentativeModelMatch #@UnresolvedImport
from ems.qt4.gui.widgets.bigcombo import BigComboBox #@UnresolvedImport

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
        #print "fkVal: %s" % fkVal
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
        
        print self._index2Fk
        print self._fk2Index
        


    
#    def paint(self, painter, model, index):
#        #print "paint"
#        super(ComboBoxRelationDelegate, self).paint(painter, model, index)

        
class Many2OneComboStrategy(BaseStrategy):
    
    ormModelCache = {}
    maxEntriesForNormalCombo = 300
    
    def getRemoteClass(self, rProperty):
        direction = self.mapper.getRealRelationSymbol(rProperty)
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
    
    def _getObjModel(self, prototype, property, query=None, matchModel=False):
        objMapper = object_mapper(prototype)
        rProperty = objMapper.get_property(property)
        class_ = self.getRemoteClass(rProperty)
        
        fk = self.getForeignKey(rProperty)
        
        orderByCol = class_.__ormDecorator__().getDefaultOrderByProperty(prototype)
        if orderByCol is not None:
            query = query.order_by(class_.__dict__[orderByCol])
        
        if not matchModel:
            model = RepresentativeModel(self.mapper.session, class_, fk,
                                        query)
        else:
            model = RepresentativeModelMatch(self.mapper.session, class_, fk,
                                        query)
        return model

        
    
    def getWidget(self, prototype, property):
        rProperty = self.getProperty(prototype, property)
        class_ = self.getRemoteClass(rProperty)
        #print "ich werde aufgerufen %s" % class_.__name__ 
        if self.mapper.session is None:
            raise TypeError("Please Assign a session to the mapper")
        
        clauses = self.buildSelectClauses(rProperty)
        if len(clauses):
            if len(clauses) > 1:
                conj = clauses[0]
            else:
                conj = and_()
                for clause in clauses:
                    conj.append(clause)
                    
            query = self.mapper.session.query(class_).filter(conj)
        else:
            query = self.mapper.session.query(class_)
            
        count = query.count()
        if count < self.maxEntriesForNormalCombo:
            widget = QComboBox()
            widget.setModel(self._getObjModel(prototype,
                                              rProperty.key,
                                              query))
            return widget
            
        else:
            widget = BigComboBox(self._getObjModel(prototype,
                                              rProperty.key,
                                              query,
                                              True))
            return widget
        #print "%s: %s" % (class_, count)
        
        return QWidget()
    
    def map(self, widget, prototype, property):
        if isinstance(widget, QComboBox):
            rProperty = self.getProperty(prototype, property)
            fk = self.getForeignKey(rProperty)

            model = self._getObjModel(prototype, property)
            
            col = self.mapper.model.getIndexByPropertyName('gruppeId')
            
            delegate = ComboBoxRelationDelegate(fk, model, self)
            self.mapper.delegate.insertColumnDelegate(col,delegate)
            widget.setModel(model)
            self.mapper.dataWidgetMapper.addMapping(widget,
                                                    col)#,"currentIndex")
            #print prototype.__class__
            #print self.mapper.model.session
            #print "Ich mache im Moment ersma nuescht"
        else:
            raise TypeError("Many2OneComboStrategy can only handle QCombobox")
    
    def getProperty(self, prototype, propertyName):
        objMapper = object_mapper(prototype)
        return objMapper.get_property(propertyName)
        