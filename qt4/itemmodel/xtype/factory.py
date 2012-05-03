'''
Created on 02.05.2012

@author: michi
'''
from ems.xtype.base import SequenceType, DictType, ObjectInstanceType #@UnresolvedImport

def getModelForXType(xType, parent=None):
    if isinstance(xType, SequenceType):
        if isinstance(xType.itemType, DictType):
            from ems.qt4.itemmodel.listofdictsmodel import ListOfDictsModel #@UnresolvedImport
            return ListOfDictsModel(xType, parent)
    
    if isinstance(xType, DictType):
        from ems.qt4.itemmodel.xtype.dictmodel import DictModel #@UnresolvedImport
        return DictModel(xType, parent)
    
    if isinstance(xType, ObjectInstanceType):
        from ems.qt4.itemmodel.xtype.objectinstancemodel import ObjectInstanceModel #@UnresolvedImport
        return ObjectInstanceModel(xType, parent)