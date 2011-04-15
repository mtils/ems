'''
Created on 24.10.2010

@author: michi
'''

class OptionsProperty(object):
    
    '''
    classdocs
    '''
    
    def get_options(self):
        return self.__options

    def set_options(self, value):
        self.__options = value

    def del_options(self):
        del self.__options
    
    options = property(get_options, set_options, del_options, "options's docstring")
    
    def getOption(self,option):
        return self.__options[option]

    def setOption(self, option, value):
        self.__options[option] = value