'''
Created on 27.10.2010

@author: michi
'''
from copy import copy
from ems.converter.preprocessor import PreProcessor


class AttributeSet(PreProcessor):
    
    def __init__(self):
        self._attributeSets = {}
        pass
    def interpret(self,xmlDict):
        self.iterateDict(xmlDict)
#        pprint(xmlDict)
#        raise SystemExit
        pass
    
    def iterateDict(self,xmlDict,iteration=0):
        iteration += 1
        if xmlDict['tag'] == 'attribute-set':
            self.converter.ignoreToplevelTag('attribute-set')
            self._createAttributeSet(xmlDict)
        if xmlDict['tag'] == 'element':
            if xmlDict['attributes'].has_key('use-attribute-sets'):
                for attributeSetName in xmlDict['attributes']['use-attribute-sets'].split(' '):
                    try:
                        self._addAttributeSetToTag(xmlDict['children'], attributeSetName)
                    except LookupError:
                        raise SyntaxError("Unknown attribute-set \"%s\" in element" % attributeSetName)
            
        for child in xmlDict['children']:
            self.iterateDict(child, iteration)
    
    def _addAttributeSetToTag(self,tagChildren,attributeSetName):
        for attributeNode in self._attributeSets[attributeSetName]:
            tagChildren.append(copy(attributeNode))

    def _createAttributeSet(self,attributeSet):
        if attributeSet['attributes'].has_key('name'):
            name = attributeSet['attributes']['name']
            if not self._attributeSets.has_key(name):
                self._attributeSets[name] = []
                if len(attributeSet['children']):
                    for child in attributeSet['children']:
                        if child['tag'] == 'attribute':
                            self._attributeSets[name].append(copy(child))
                        else:
                            raise SyntaxError("An attribute-set can only have attribute childs")
                            
                else:
                    raise SyntaxError("An attribute-set needs a name Attribute")
            else:
                raise SyntaxError("The attribute-set named \"%s\" is already defined" % name)
        else:
            raise SyntaxError("An attribute-set needs a name Attribute")
        pass
    
    def notify(self,eventType):
        if eventType == self.startProcess:
            self._attributeSets.clear()
                
            