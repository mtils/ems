'''
Created on 20.06.2011

@author: michi
'''
import datetime

from PyQt4.QtCore import QVariant, pyqtSignal
from PyQt4.QtGui import QColor

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