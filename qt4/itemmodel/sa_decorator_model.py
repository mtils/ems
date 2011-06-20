'''
Created on 20.06.2011

@author: michi
'''
from PyQt4.QtCore import Qt, QVariant

class SADecoratorModel(object):
    def data(self, model, index, role=Qt.DisplayRole):
#        print "Isch bins %s" % role
        return QVariant()