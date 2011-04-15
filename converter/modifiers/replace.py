'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.modifier import Modifier,ModifierException

class Replace(Modifier):
    '''
    classdocs
    '''
    def interpret(self,params):
        if params.has_key('value') and params.has_key('search') and \
            params.has_key('replace'): 
            if isinstance(params['value'], basestring):
                if isinstance(params['search'], basestring):
                    return params['value'].replace(params['search'],params['replace'])
            else:
                raise ModifierException("All params of replace have to be str")
            
        else:
            raise ModifierException(
                "Modifier 'replace' needs 3 params: value, search and replace")

    def __str__(self):
        '''
        Returns a string reprasentation
        '''
        return "replace"