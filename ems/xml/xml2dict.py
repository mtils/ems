'''
Created on 25.10.2010

@author: michi
'''
import xml.sax.handler

def createNode():
    return {'tag':'','attributes':{},'children':[],'cdata':''}
        
def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """
    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = createNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = createNode()
            self.current['tag'] = name
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
#                self.current._add_xml_attr(_name_mangle(k), v)
                self.current['attributes'][k] = v
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current['cdata'] = text
                
            obj = self.current
            self.current, self.text_parts = self.stack.pop()
            self.current['children'].append(obj)
        def characters(self, content):
            self.text_parts.append(content)
        
    builder = TreeBuilder()
    if isinstance(src,basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root