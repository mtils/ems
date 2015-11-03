'''
Created on 20.06.2011

@author: michi
'''
from __future__ import print_function
import datetime
from pprint import pformat

from PyQt4.QtCore import QVariant, pyqtSignal, QObject, Qt, QDateTime
from PyQt4.QtGui import QColor

from ems import qt4

class VariantContainer(tuple):
    '''
    This is an Container to protected the contents of an
    "varianted" PyObject
    
    If you do something like this:
    
    qValue = QVariant({'a':23}
    
    and then:
    
    pyValue = variant_to_pyobject(qValue)
    
    you get:
    
    {PyQt4.QtCore.QString(u'a':23)}
    
    ...which is mostly not what you want.
    
    so instead do:
    
    qValue = QVariant(VariantContainer({'a':23}))
    
    and variant_to_pyobject will return you original dict.
    The works because VariantContainer extends tuple which is immutable

    '''
    pass

def variant_to_pyobject(qvariant=None): 
    """Try to convert a QVariant to a python object as good as possible""" 

    if not isinstance(qvariant, QVariant):
        return qvariant

    if not qvariant: 
        return None 
    if qvariant.isNull(): 
        return None 
    type = qvariant.type() 
    if type == QVariant.String: 
        value = unicode(qvariant.toString()) 
    elif type == QVariant.Date: 
        value = qvariant.toDate() 
        value = datetime.date(year=value.year(), 
                              month=value.month(), 
                              day=value.day()) 
    elif type == QVariant.Int: 
        value = int(qvariant.toInt()[0]) 
    elif type == QVariant.LongLong: 
        value = int(qvariant.toLongLong()[0]) 
    elif type == QVariant.Double: 
        value = float(qvariant.toDouble()[0]) 
    elif type == QVariant.Bool: 
        value = bool(qvariant.toBool()) 
    elif type == QVariant.Time: 
        value = qvariant.toTime() 
        value = datetime.time(hour = value.hour(), 
                              minute = value.minute(), 
                              second = value.second()) 
    elif type == QVariant.DateTime: 
        value = qvariant.toDateTime() 
        value = value.toPyDateTime () 
    elif type == QVariant.Color: 
        value = QColor(qvariant) 
    else: 
        value = qvariant.toPyObject()
        if isinstance(value, VariantContainer):
            value = value[0]

    return value

def cast_to_variant(value):
    if isinstance(value, basestring):
        return QVariant(unicode(value))
    elif isinstance(value, datetime.datetime):
        return QVariant(QDateTime(value.year, value.month, value.day,
                                    value.hour, value.minute, value.second))
    elif isinstance(value, (dict, list)):
        return QVariant(VariantContainer((value,)))
    elif value is None:
        return QVariant()
    return QVariant(value)

def pyobject_to_variant(value):
    return cast_to_variant(value)

def hassig(obj, signalName):
#    if signalName == 'windowTitleChanged':
#        print "Hunulululu"
    if isinstance(obj, type):
        cls = obj
    else:
        cls = obj.__class__
        
    if cls.__dict__.has_key(signalName):
        try:
            if isinstance(cls.__dict__[signalName], pyqtSignal):
                return True
        except KeyError:
            pass
    else:
        #print "Class", cls,'has no signal named', signalName
        for parentCls in cls.__bases__:
            #print "PARENT CLASS",parentCls
            if not parentCls is cls:
                hasSignal = hassig(parentCls, signalName)
                if hasSignal:
                    return True
#                else:
#                    print "no.... parentClass", parentCls, "has:", hasSignal
    return False

class SignalPrinter(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.usePprint = False
    def printSignal(self, *args):
        if len(args) > 1:
            resJoin = []
            for arg in args:
                resJoin.append(self._formatResult(arg))
            output = u", ".join(resJoin)
        elif len(args) == 1:
            output = self._formatResult(args[0])

        print('SignalPrinter({0}): {1}'.format(self.sender().__class__.__name__,output))

    def _formatResult(self, result):
        if isinstance(result, QVariant):
            value = variant_to_pyobject(result)
        else:
            value = result
        if self.usePprint:
            return u"\n{0}".format(pformat(value))
        else:
            return str(value)

def findIndexesOfValue(model, value, inRow=None, inColumn=None,
                       role=Qt.DisplayRole, returnFirstHit=False):
    if inRow is None:
        rows = range(model.rowCount())
    else:
        rows = (inRow,)
    if inColumn is None:
        columns = range(model.columnCount())
    else:
        columns = (inColumn,)

    indexes = []

    for row in rows:
        for col in columns:
            index = model.index(row,col)
            if variant_to_pyobject(index.data(role)) == value:
                if returnFirstHit:
                    return index
                indexes.append(index)

    return indexes

def columnOfName(model, colName):

    for i in range(model.columnCount()):
        modelColName = variant_to_pyobject(model.headerData(i, Qt.Horizontal, qt4.ColumnNameRole))
        if modelColName == colName:
            return i

    return -1