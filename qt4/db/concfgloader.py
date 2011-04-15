'''
Created on 17.02.2011

@author: michi
'''
from ems.qt4.config import QConfig

class QConCfgLoader(QConfig):
    def getCfg(self,name=''):
        profile = self.getProfile(name)
        try:
            name = self.getProfileName(name)
        except KeyError:
            name = 'No Name'
        conCfg = {'name':name}
        for prop in profile:
            conCfg[prop]  = profile[prop]
        return conCfg