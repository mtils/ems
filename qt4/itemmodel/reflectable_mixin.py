'''
Created on 21.03.2012

@author: michi
'''

class ReflectableMixin(object):
    
    def columnType(self, column):
        '''
        Returns XType of column
        
        @param column: The column (index.column())
        @type column: int
        @rtype: XType
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