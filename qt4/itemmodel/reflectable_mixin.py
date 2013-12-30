'''
Created on 21.03.2012

@author: michi
'''
from PyQt4.QtCore import QModelIndex
from ems import qt4
from ems.qt4.util import variant_to_pyobject

class ReflectableMixin(object):

    Horizontal = 1
    Vertical = 2

    def direction(self):
        """
        @brief Returns the direction of this model.
               A Direction describes the layout of this model.
               Horizontal is when Columns are aligned Horizontal (as columns)
               Vertical is when Columns are aligned Vertical (as rows)
        :returns: int
        """
        return ReflectableMixin.Horizontal

    def columnType(self, column):
        '''
        Returns XType of column

        @param column: The column (index.column())
        @type column: int
        @rtype: XType
        :returns: XType
        '''
        raise NotImplementedError("Please implement columnType")
    
    def nameOfColumn(self, column):
        '''
        Returns the name of column
        
        @param column: The column (index.column())
        @type column: int
        @rtype: str
        '''
        raise NotImplementedError("Please implement nameOfColumn")
    
    def columnOfName(self, column):
        '''
        Returns the column of columnName column
        @param column: The columnName
        @type column: str
        @rtype: int
        '''
        raise NotImplementedError("Please implement columnOfName")

    def rowType(self, row):
        '''
        Returns XType of row

        @param row: The row (index.row())
        @type row: int
        @rtype: XType
        :returns: XType
        '''
        raise NotImplementedError("Please implement rowType")

    def nameOfRow(self, row):
        '''
        Returns the name of the row (if Direction is Vertical)

        @param row: The row (index.row())
        @type row: int
        @rtype: str
        '''
        raise NotImplementedError("Please implement nameOfRow")
    
    def rowOfName(self, name):
        '''
        Returns the row of columnName name (if Direction is Vertical)
        @param name: The columnName
        @type column: str
        @rtype: int
        '''
        raise NotImplementedError("Please implement rowOfName")

    def columnNameOfIndex(self, index, parentIndex=QModelIndex()):
        return variant_to_pyobject(self.data(index, qt4.ColumnNameRole))

    def indexOfColumnName(self, name, position=0):
        if self.direction() == ReflectableMixin.Horizontal:
            return self.index(position, self.columnOfName(name))
        if self.direction() == ReflectableMixin.Vertical:
            return self.index(self.rowOfName(name), position)
