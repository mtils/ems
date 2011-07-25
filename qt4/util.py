'''
Created on 20.06.2011

@author: michi
'''
from PyQt4.QtCore import QVariant, pyqtSignal
from PyQt4.QtGui import QColor

def variant_to_pyobject(qvariant=None): 
    """Try to convert a QVariant to a python object as good as possible""" 
    import datetime 
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
   
    return value

def hassig(obj, signalName):
    if hasattr(obj.__class__, signalName):
        if isinstance(obj.__class__.__dict__[signalName], pyqtSignal):
            return True
    return False