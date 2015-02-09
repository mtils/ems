'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.modifier import Modifier,ModifierException

class Join(Modifier):
    '''
    classdocs
    '''
    def interpret(self,params):
        if isinstance(params, dict):
            raise ModifierException("No named params for {0}".format(str(self)))
        if isinstance(params, list):
            i = 0
            delimiter = ""
            tiles = []
            for item in params:
                if i == 0:
                    delimiter = unicode(item)
                else:
                    if item:
                        tiles.append(unicode(item))
                i += 1
            return delimiter.join(tiles)
        else:
            raise ValueError("No dict with params was send to {0}".format(str(self)))

    def __str__(self):
        '''
        Returns a string reprasentation
        '''
        
        return "join"