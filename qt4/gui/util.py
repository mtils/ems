'''
Created on 10.07.2011

@author: michi
'''

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QTreeWidgetItem

class FlatTreeBuilderMixin(QObject):
    def addItemFlat(self, textsOrItem, depth=0):
        if not hasattr(self, '_flatItemTree'):
            self._flatItemTree = {}
        if isinstance(textsOrItem, QTreeWidgetItem):
            treeWidgetItem = textsOrItem
        else:
            treeWidgetItem = QTreeWidgetItem(textsOrItem)
            
        self._flatItemTree[depth] = treeWidgetItem
        
        if depth == 0:
            self.addTopLevelItem(self._flatItemTree[depth])
        else:
            
            #newItem = QTreeWidgetItem(textsOrItem)
            self._flatItemTree[depth-1].addChild(treeWidgetItem)
            #self._flatItemTree[depth] = newItem