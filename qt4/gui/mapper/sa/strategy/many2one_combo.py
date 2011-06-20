'''
Created on 19.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QComboBox, QItemDelegate

from sqlalchemy.orm import object_mapper
from sqlalchemy.util import symbol

from ems import qt4
from ems.qt4.util import variant_to_pyobject #@UnresolvedImport
from ems.qt4.itemmodel.alchemyormmodel import AlchemyOrmModel
from ems.qt4.itemmodel.sa.representative_model import RepresentativeModel #@UnresolvedImport

from base import BaseStrategy

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
    
    def _getObjModel(self, prototype, property):
        objMapper = object_mapper(prototype)
        rProperty = objMapper.get_property(property)
        if rProperty.direction is symbol('MANYTOONE'):
            #print rProperty.local_side
            #print "%s %s" % (rProperty.mapper, objMapper)
            class_ = rProperty.mapper.class_manager.class_
            #model = AlchemyOrmModel(self.mapper.model.session, class_, ['id','name'])
            #model = AlchemyOrmModel(self.mapper.model.session, class_, ['name','id'])
            fk = rProperty.remote_side[0].key

            model = RepresentativeModel(self.mapper.model.session, class_, fk)
            #print self.mapper.model.session.query(class_).all()
#            for i in range(model.rowCount()):
#                print model.data(model.index(i, 1)).toString()
            return model
#            for att in dir(rProperty.mapper):
#                print "%s %s %s" % (att,
#                                    rProperty.__getattribute__(att),
#                                    type(rProperty.__getattribute__(att)))
        else:
            raise TypeError("Many2OneComboStrategy needs a MANYTOONE Relation")
    
    def map(self, widget, prototype, property):
        if isinstance(widget, QComboBox):
            objMapper = object_mapper(prototype)
            rProperty = objMapper.get_property(property)
            fk = rProperty.remote_side[0].key
            #delegate = ComboBoxRelationDelegate()
            #widget.setItemDelegate(delegate)
            #widget.setProperty("currentIndex",0)
            #widget.setModel(AlchemyOrmModel())
            model = self._getObjModel(prototype, property)
            #widget.setModelColumn(1)
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