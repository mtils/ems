'''
Created on 23.03.2011

@author: michi
'''

import math

from PyQt4.QtCore import QPointF,QSize
from PyQt4.QtGui import QPolygonF

class Star(QPolygonF):
    
    def __init__(self, qtParam=None, scale=1.0, degree=0.0):
        
        self.scale  = scale
        self.degree = degree
        
        if qtParam:
            super(Star, self).__init__(qtParam)
        else:
            super(Star, self).__init__()
        self.recalc()

    def getScale(self):
        return self.__scale

    def setScale(self, value):
        self.__scale = float(value)
        
    def getDegree(self):
        return self.__degree

    def setDegree(self, value):
        self.__degree = float(value) + 0.375
    
    def recalc(self):
        startX = (0.5 + 0.5 * math.cos(0.8 * self.__degree * math.pi) * self.__scale)
        startY = (0.5 + 0.5 * math.sin(0.8 * self.__degree * math.pi) * self.__scale)
        self << QPointF(startX, startY)
        for i in range(5):
            self << QPointF((0.5 + 0.5 * 
                             math.cos(0.8 * (i+self.__degree) * math.pi) * self.__scale),
                            (0.5 + 0.5 * 
                             math.sin(0.8 * (i+self.__degree) * math.pi) *self.__scale))
            
    scale = property(getScale, setScale, None, "scale's docstring")
    degree = property(getDegree, setDegree, None, "degree's docstring")
    
#        self.diamondPolygon = QPolygonF()
#        self.diamondPolygon << QPointF(0.4, 0.5) \
#                            << QPointF(0.5, 0.4) \
#                            << QPointF(0.6, 0.5) \
#                            << QPointF(0.5, 0.6) \
#                            << QPointF(0.4, 0.5)
