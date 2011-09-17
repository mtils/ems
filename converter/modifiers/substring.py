'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.modifier import Modifier,ModifierException

class Substring(Modifier):
    '''
    classdocs
    '''
    def interpret(self,params):
        if params.has_key('value'):
            if params.has_key('start'):
                if isinstance(params['start'], basestring):
                    start = int(params['start'])
                    if not params.has_key('count'):
                        return unicode(params['value'])[start:]
                    else:
                        count = int(params['count'])
                        return unicode(params['value'])[start:count]
        else:
            raise ModifierException("Modifier 'substring' needs a value param")

    def __str__(self):
        '''
        Returns a string reprasentation
        '''
        return "substring"