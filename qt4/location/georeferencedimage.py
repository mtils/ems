'''
Created on 17.12.2011

@author: michi
'''
from __future__ import print_function
import struct
import numpy
import sys
import tempfile
import os

from PyQt4.QtCore import Qt, QSize, QSizeF, QPoint
from PyQt4.QtGui import QApplication, QImage, QImageReader

import gdal, osr
from gdalconst import *

from ems.qt4.location.geocoordinate import GeoCoordinate
from application.locationplugins.geoboundingbox_utm import GeoBoundingBoxUtm,\
    GeoBoundingBox

class GeoReferencedImage(QImage):
    def __init__(self, fileNameOrBoundingBox=None, imageSize=None,
                 projection='utm'):
        
        self._onePixelSize = QSizeF()
        self._geoBoundingBox = GeoBoundingBoxUtm()
        self._sourceSize = QSize()
        
        if isinstance(fileNameOrBoundingBox, basestring):
            
            '''----------------------------------------------------------------
             First open the file with gdal to retrieve geospacial metadata
            ----------------------------------------------------------------'''
            
            dataset = gdal.Open(fileNameOrBoundingBox, GA_ReadOnly)
            if dataset is None:
                raise IOError("File {0} not found.".format(fileNameOrBoundingBox))
            
            self.gdalDriver = dataset.GetDriver()
            self._sourceSize = QSize(dataset.RasterXSize, dataset.RasterYSize)
            
            
            geotransform = dataset.GetGeoTransform()
            if geotransform is None:
                raise TypeError("Geotransform could not be received")
            
            self._onePixelSize = QSizeF(geotransform[1], geotransform[5])
            
            
            topLeftCoord = GeoCoordinate(geotransform[0], geotransform[3],
                                         projection=projection)
            
            bottomRightCoord = self._calcBottomRightCoordinate(topLeftCoord,
                                                               self._onePixelSize,
                                                               self._sourceSize,
                                                               projection)
            
            self._geoBoundingBox = GeoBoundingBoxUtm(topLeftCoord,
                                                     bottomRightCoord)
            
            '''----------------------------------------------------------------
             Copy the file with gdal to png format because qt crashes here
             after gdal import.
             A memory copy was even slower than the tempfile method (???)
            ----------------------------------------------------------------'''
            dstFormat = "PNG"
            
            targetDriver = gdal.GetDriverByName(dstFormat)
            
            dstFileName = os.path.join(tempfile.gettempdir(), tempfile.mktemp('.png',
                                                                              'gdal2qimage-'))
            
            
            target = targetDriver.CreateCopy(dstFileName, dataset, 0)
            
            
            dataset = None
            target = None
            
            QImage.__init__(self, dstFileName)
            os.remove(dstFileName)
            if os.path.exists(dstFileName + '.aux.xml'):
                os.remove(dstFileName + '.aux.xml')
            
        elif isinstance(fileNameOrBoundingBox, GeoBoundingBox):
            
            self._geoBoundingBox = fileNameOrBoundingBox
            
            if imageSize is None:
                raise TypeError("If you construct a new GeoReferencedImage" +
                                "give a imageSize")
            
            self._sourceSize = imageSize
            QImage.__init__(self, imageSize, QImage.Format_RGB32)
        
        
        
    def origin(self):
        return self._topLeftCoordinate
    
    def onePixelSize(self):
        if not self._onePixelSize.isValid():
            geoSize = self.geoSize()
            x = geoSize.width() / self.size().width()
            y = geoSize.height() / self.size().height()
            self._onePixelSize = QSizeF(x, y)
        return self._onePixelSize
    
    def geoBoundingBox(self):
        if not self._geoBoundingBox.isValid():
            pass
        return self._geoBoundingBox
    
    def geoSize(self):
        return QSizeF(self._geoBoundingBox.width(), 0 - self._geoBoundingBox.height())
    
    def coordinate2PixelPosition(self, coordinate):
        if not self._geoBoundingBox.contains(coordinate):
            return QPoint()
        topLeftLat = self._geoBoundingBox.topLeft().latitude()
        bottomRightLon = self._geoBoundingBox.bottomRight().longitude()
        
        
        
#        print(coordinate.latitude() - topLeftLat)
#        print(coordinate.longitude() - bottomRightLon)
        
        x = (coordinate.latitude() - topLeftLat) / self.onePixelSize().width()
        y = (coordinate.longitude() - bottomRightLon) / self.onePixelSize().height()
        #print(x,y)
        result = QPoint(int(round(x)), int(round(self.size().height() + y)))
        
        #Return 499,499 on highest val because there is no 500,500
        if result.x() == self.size().width():
            result.setX(self.size().width()-1)
        if result.y() == self.size().height():
            result.setY(self.size().height()-1)
        
        return result
    
    def pixelPosition2GeoCoordinate(self, pixelPos):
        if not self.rect().contains(pixelPos):
            return GeoCoordinate()
        
        lat = (pixelPos.x() * self.onePixelSize().width()) + \
               self._geoBoundingBox.topLeft().latitude()
        lon = ((self.size().height() - pixelPos.y()) * abs(self.onePixelSize().height())) + \
               self._geoBoundingBox.bottomRight().longitude()
        
        return GeoCoordinate(lat, lon, projection="utm")
    
    @staticmethod
    def _calcBottomRightCoordinate(topLeftCoordinate, pixelSize, sourceSize,
                                  projection='utm'):
        
        return GeoCoordinate(topLeftCoordinate.latitude() + \
                                 (pixelSize.width()*sourceSize.width()),
                             topLeftCoordinate.longitude() - \
                                 (abs(pixelSize.height())*sourceSize.height()),
                             projection=projection)
    
    def rect(self, geoBoundingBox=None):
        if geoBoundingBox is None:
            return QImage.rect(self)
        
        
        
        
        

if __name__ == '__main__':
    fileName = '/home/michi/Dokumente/IT/Kontakte/SmartGeomatics/Projekte/Datenlieferungen/2011-11-30 Pfalzgrafenweiler Orthofotos UTM32N/34705383/34705383.tif'
    #fileName = '/home/michi/Dokumente/IT/Kontakte/SmartGeomatics/Projekte/Datenlieferungen/2011-06-01 Pfalzgrafenweiler Orthos nativ/Orthofotos rgb/34625377.tif'

    
    
    app = QApplication([])
    
    
    tileLeftTop = GeoCoordinate(470007.8125, 5382398.4375, projection="utm")
    tileBottomRight = GeoCoordinate(470011.710938, 5382394.53906, projection="utm")
    tileBounds = GeoBoundingBoxUtm(tileLeftTop, tileBottomRight)
    
    
    sourceImage = GeoReferencedImage(fileName)
    print("----------SourceImage-------------")
    print("GeoBoundingBox: {0}".format(sourceImage.geoBoundingBox()))
    print("SourceSize: {0}".format(sourceImage.size()))
    print("OnePixelSize: {0}".format(sourceImage.onePixelSize()))
    print("GeoSize: {0}".format(sourceImage.geoSize()))
    #print(tileBounds)
    
    targetImage = GeoReferencedImage(tileBounds, QSize(500, 500))
    print("----------TargetImage-------------")
    print("GeoBoundingBox: {0}".format(targetImage.geoBoundingBox()))
    print("SourceSize: {0}".format(targetImage.size()))
    print("OnePixelSize: {0}".format(targetImage.onePixelSize()))
    print("GeoSize: {0}".format(targetImage.geoSize()))
    print("GeoCoord: {0} = Pos {1} Null: {2}".format(tileLeftTop,
                                           targetImage.coordinate2PixelPosition(tileLeftTop),
                                           targetImage.coordinate2PixelPosition(tileLeftTop).isNull()))
    print("GeoCoord: {0} = Pos {1}".format(tileBottomRight,
                                           targetImage.coordinate2PixelPosition(tileBottomRight)))
    
    center = GeoCoordinate(tileLeftTop.latitude() + tileBounds.width()/2,
                           tileLeftTop.longitude() - tileBounds.height()/2,
                           projection="utm")
    
    print("GeCoord {0} = Pos {1}".format(center,
                                         targetImage.coordinate2PixelPosition(center)))
    
    print("Pos {0} = Coord {1}".format(QPoint(0,0),
                                       targetImage.pixelPosition2GeoCoordinate(QPoint(0,0))))
    
    print("Pos {0} = Coord {1}".format(QPoint(250,250),
                                       targetImage.pixelPosition2GeoCoordinate(QPoint(250,250))))
    
    
    print("Pos {0} = Coord {1}".format(QPoint(499,499),
                                       targetImage.pixelPosition2GeoCoordinate(QPoint(499,499))))
    
    print("intersected: {0}".format(targetImage.geoBoundingBox().intersected(sourceImage.geoBoundingBox())))
    
    
    #result = sourceImage.save("/tmp/gdal-out-qt.png", "PNG")
    #print("Result: {0} isNull:{1}".format(result, sourceImage.isNull()))
    print("Fertig")
    #sys.exit(app.exec_())
    
    
    
    
