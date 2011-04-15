'''
Created on 25.10.2010

@author: michi
'''
from ems.converter.modifier import Modifier,ModifierException

class Concat(Modifier):
    '''
    classdocs
    '''
    def interpret(self,params):
        if isinstance(params, dict):
            raise ModifierException("No named params for concat")
        if isinstance(params, list):
            return "".join(params)
        else:
            raise ValueError("No dict with params was send to concat")

    def __str__(self):
        '''
        Returns a string reprasentation
        '''
        return "concat"