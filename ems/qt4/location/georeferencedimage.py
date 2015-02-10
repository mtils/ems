'''
Created on 17.12.2011

@author: michi
'''
from __future__ import print_function
from pprint import pprint as pp
import struct
import numpy
import sys
import tempfile
import os

from PyQt4.QtCore import Qt, QSize, QSizeF, QPoint, QRect, QRectF, QPointF
from PyQt4.QtGui import QApplication, QImage, QImageReader, QPainter

import gdal, osr
from gdalconst import *

from ems.qt4.location.geocoordinate import GeoCoordinate
from application.locationplugins.geoboundingbox_utm import GeoBoundingBoxUtm,\
    GeoBoundingBox


class GeoReferencedImage(QImage):
    def __init__(self, fileName=None, geoBoundingBox=None, imageSize=None,
                 projection='utm'):
        
        self._onePixelSize = QSizeF(0.0, 0.0)
        self._geoBoundingBox = GeoBoundingBoxUtm()
        self._sourceSize = QSize()
        self.painter = None
        
        
        if (fileName) and (geoBoundingBox is None):
            
            '''----------------------------------------------------------------
             First open the file with gdal to retrieve geospacial metadata
            ----------------------------------------------------------------'''
            if not os.path.exists(fileName):
                raise IOError("File {0} not found.".format(fileName))
            dataset = gdal.Open(fileName, GA_ReadOnly)
            if dataset is None:
                raise IOError("File {0} not found.".format(fileName))
            
            self.gdalDriver = dataset.GetDriver()
            self._sourceSize = QSize(dataset.RasterXSize, dataset.RasterYSize)
            
            
            geotransform = dataset.GetGeoTransform()

            if geotransform is None:
                raise TypeError("Geotransform could not be received")
            
            self._onePixelSize = QSizeF(geotransform[1], geotransform[5])
            
            
            topLeftCoord = GeoCoordinate()
            topLeftCoord.lat =geotransform[0]
            topLeftCoord.lng = geotransform[3]
            topLeftCoord.projection=projection
            
            bottomRightCoord = self.calcBottomRightCoordinate(topLeftCoord,
                                                               self._onePixelSize,
                                                               self._sourceSize,
                                                               projection)
            print("GeoReferencedImage.__init__.topLeftCoord, bottomRightCoord",topLeftCoord, bottomRightCoord)
            self._geoBoundingBox = GeoBoundingBoxUtm(topLeftCoord,
                                                     bottomRightCoord)
            
            '''----------------------------------------------------------------
             Copy the file with gdal to bmp format because qt crashes here
             after gdal import.
             A memory copy was even slower than the tempfile method (???)
            ----------------------------------------------------------------'''
            dstFormat = "BMP"
            
            targetDriver = gdal.GetDriverByName(dstFormat)
            
            dstFileName = os.path.join(tempfile.gettempdir(), tempfile.mktemp('.BMP',
                                                                              'gdal2qimage-'))
            
            
            target = targetDriver.CreateCopy(dstFileName, dataset, 0)
            
            
            dataset = None
            target = None
            
            QImage.__init__(self, dstFileName)
            
            os.remove(dstFileName)
            if os.path.exists(dstFileName + '.aux.xml'):
                os.remove(dstFileName + '.aux.xml')
            
        elif (geoBoundingBox is not None):
            
            
            self._geoBoundingBox = geoBoundingBox
            
            if not fileName:
                if imageSize is None:
                    raise TypeError("If you construct a new GeoReferencedImage" +
                                    "give a imageSize")
                
                self._sourceSize = imageSize
                
                QImage.__init__(self, imageSize, QImage.Format_RGB32)
            else:
                QImage.__init__(self, fileName)
                
        print('GeoReferencedImage.__init__.fileName',fileName)
        
        
    def origin(self):
        return self._topLeftCoordinate
    
    def onePixelSize(self):
        if self._onePixelSize.isNull():
            geoSize = self.geoSize()
            x = geoSize.width() / self.size().width()
            y = geoSize.height() / self.size().height()
            self._onePixelSize = QSizeF(x, y)
        return self._onePixelSize
    
    def geoBoundingBox(self, rect=None):
        print("GeoReferencedImage.geoBoundingBox.rect", rect)
        if not self._geoBoundingBox.isValid():
            pass
        if rect is None:
            return self._geoBoundingBox
        topLeft = self.pixelPosition2GeoCoordinate(rect.topLeft())
        bottomRight = self.pixelPosition2GeoCoordinate(rect.bottomRight())
        print("GeoReferencedImage.geoBoundingBox.topLeft", topLeft)
        print("GeoReferencedImage.geoBoundingBox.bottomRight", bottomRight)
        return GeoBoundingBoxUtm(topLeft, bottomRight)
    
    def geoSize(self):
        return QSizeF(self._geoBoundingBox.width(), 0 - self._geoBoundingBox.height())
    
    def coordinate2PixelPosition(self, coordinate):
        if not self._geoBoundingBox.contains(coordinate):
            return QPointF()
        topLeftLat = self._geoBoundingBox.topLeft().lat
        bottomRightLon = self._geoBoundingBox.bottomRight().lng
        
        
        
#        print(coordinate.latitude() - topLeftLat)
#        print(coordinate.longitude() - bottomRightLon)
        
        x = (coordinate.lat - topLeftLat) / self.onePixelSize().width()
        y = (coordinate.lng - bottomRightLon) / self.onePixelSize().height()
        #print(x,y)
        result = QPointF(x, float(self.size().height()) + y)
        
        return result
    
    def pixelPosition2GeoCoordinate(self, pixelPos):
        if not self.rectF().contains(QPointF(pixelPos)):
            return GeoCoordinate()
        
        lat = (pixelPos.x() * self.onePixelSize().width()) + \
               self._geoBoundingBox.topLeft().lat
        lon = ((self.size().height() - pixelPos.y()) * abs(self.onePixelSize().height())) + \
               self._geoBoundingBox.bottomRight().lng
        
        coord = GeoCoordinate()
        coord.lat = lat
        coord.lng = lon
        coord.projection="utm"
        return coord
    
    @staticmethod
    def calcBottomRightCoordinate(topLeftCoordinate, pixelSize, sourceSize,
                                  projection='utm'):
        coord = GeoCoordinate()
        coord.lat = topLeftCoordinate.lat +  (pixelSize.width()*sourceSize.width())
        coord.lng = topLeftCoordinate.lng - (abs(pixelSize.height())*sourceSize.height())
        coord.projection=projection
        return coord
    
    def rectF(self, geoBoundingBox=None):
        '''
        Returns the QRect. Reimplemented QImage.rect().
        With no param it just returns super().rect().
        Pass a GeoBoundingBox and it will return the
        intersected rect of this GeoBoundingBox.
        This means that if you pass a GeoBoundingBox which is not within the
        boundries of that Image, you will get a invalid QRect.
        If you pass a GeoBoundingBox which intersects the GeoBoundingBox of
        this image, it will return the intercection.
        
        @param geoBoundingBox: A GeoBoundingBox if a particular rect is requested (Optional)
        @type geoBoundingBox: GeoBoundingBox
        @return: A QRect of the whole image if no GeoBoundingBox passed, else intersection
        @rtype: QRectF
        '''
        if geoBoundingBox is None:
            return QRectF(QImage.rect(self))
        #print('GeoReferencedImage.rectF', geoBoundingBox)
        intersected = self._geoBoundingBox.intersected(geoBoundingBox)
        #intersected = geoBoundingBox.intersected(self._geoBoundingBox)
#        print("source: {0}".format(geoBoundingBox))
#        print("target: {0}".format(self._geoBoundingBox))
#        print("intersected: {0}".format(intersected))
        if intersected.isValid():
            return QRectF(self.coordinate2PixelPosition(intersected.topLeft()),
                         self.coordinate2PixelPosition(intersected.bottomRight()))
        
        return QRectF()
    
    def fillImage(self, color=None):
        if color is None:
            color = Qt.black
        painter = QPainter(self)
        painter.fillRect(self.rect(), color)
        painter.end()
    
    def paste(self, otherImage):
        sourceRect = otherImage.rectF(self._geoBoundingBox)
#        intersectedImage = otherImage.copy(QRect(int(round(sourceRect.x())),
#                                                 int(round(sourceRect.y())),
#                                                 int(round(sourceRect.width())),
#                                                 int(round(sourceRect.height())))
#                                           )
        sourceBoundingBox = otherImage.geoBoundingBox(sourceRect)
        print("GeoReferencedImage.paste.sourceRect: {0}".format(sourceRect))
        print("GeoReferencedImage.paste.sourceBoundingBox: {0}".format(sourceBoundingBox))
        targetRect = self.rectF(sourceBoundingBox)
#        print("targetRect: {0}".format(targetRect))
        #if self.painter is None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        
        #painter.setPen(Qt.lightGray)
        
#        if not self.imageLoaded:
#        if prefill is not None:
#            painter.fillRect(self.rect(), prefill)
#        painter.drawImage(targetRect, intersectedImage,
#                          QRectF(intersectedImage.rect()),
#                          Qt.AutoColor)
        painter.drawImage(targetRect, otherImage, sourceRect)
        #painter = None
#        dstFileName = os.path.join(tempfile.gettempdir(), tempfile.mktemp('.BMP',
#                                                                              'testimage-'))
#        testImage = self.copy(targetRect.toRect())
#        
#        testImage.save(dstFileName)
        
        #painter.end()
        
                
        
        
        

if __name__ == '__main__':

    try:
        fileSpec = sys.argv[1]
        if os.path.isdir(fileSpec):
            allFiles = [os.path.join(fileSpec,f) for f in os.listdir(fileSpec)]
            files = []
            for single_file in allFiles:
                if single_file.lower().endswith('.tif') or single_file.lower().endswith('.tiff'):
                    files.append(single_file)

        elif os.path.isfile(fileSpec):
            files = [fileSpec]
    except IndexError:
        print('Please provide an input directory or file')
        sys.exit()

    for fileName in files:

        app = QApplication([])

    #    tileLeftTop = GeoCoordinate(470007.8125, 5382398.4375, projection="utm")
    #    tileBottomRight = GeoCoordinate(470011.710938, 5382394.53906, projection="utm")

        #Oben bei zoom 10
        #tileLeftTop = GeoCoordinate(470000.0, 5383000.0, projection="utm")
        #tileBottomRight = GeoCoordinate(470999.992188, 5382000.00781, projection="utm")
        
        #Unten bei Zoom 10
        tileLeftTop = GeoCoordinate(470000.0, 5382000.0, projection="utm")
        tileBottomRight = GeoCoordinate(470999.992188, 5381000.00781, projection="utm")
        
        tileBounds = GeoBoundingBoxUtm(tileLeftTop, tileBottomRight)
        
        sourceImage = GeoReferencedImage(fileName)
        print("----------SourceImage {0} -------------".format(os.path.basename(fileName)))
        print("GeoBoundingBox: {0}".format(sourceImage.geoBoundingBox()))
        print("SourceSize: {0}".format(sourceImage.size()))
        print("OnePixelSize: {0}".format(sourceImage.onePixelSize()))
        print("GeoSize: {0}".format(sourceImage.geoSize()))
        #print(tileBounds)
        
        targetImage = GeoReferencedImage(geoBoundingBox=tileBounds, imageSize=QSize(500, 500))
        print("----------TargetImage-------------")
        print("GeoBoundingBox: {0}".format(targetImage.geoBoundingBox()))
    #    print("SourceSize: {0}".format(targetImage.size()))
    #    print("OnePixelSize: {0}".format(targetImage.onePixelSize()))
    #    print("GeoSize: {0}".format(targetImage.geoSize()))
    #    print("GeoCoord: {0} = Pos {1} Null: {2}".format(tileLeftTop,
    #                                           targetImage.coordinate2PixelPosition(tileLeftTop),
    #                                           targetImage.coordinate2PixelPosition(tileLeftTop).isNull()))
    #    
    #    print("GeoCoord: {0} = Pos {1}".format(tileBottomRight,
    #                                           targetImage.coordinate2PixelPosition(tileBottomRight)))
    #    
    #    center = GeoCoordinate(tileLeftTop.latitude() + tileBounds.width()/2,
    #                           tileLeftTop.longitude() - tileBounds.height()/2,
    #                           projection="utm")
    #    
    #    print("GeCoord {0} = Pos {1}".format(center,
    #                                         targetImage.coordinate2PixelPosition(center)))
    #    
    #    print("Pos {0} = Coord {1}".format(QPoint(0,0),
    #                                       targetImage.pixelPosition2GeoCoordinate(QPoint(0,0))))
    #    
    #    print("Pos {0} = Coord {1}".format(QPoint(250,250),
    #                                       targetImage.pixelPosition2GeoCoordinate(QPoint(250,250))))
    #    
    #    
    #    print("Pos {0} = Coord {1}".format(QPoint(499,499),
    #                                       targetImage.pixelPosition2GeoCoordinate(QPoint(499,499))))
    #    
        
        print("intersected: {0}".format(targetImage.geoBoundingBox().intersected(sourceImage.geoBoundingBox())))
        
        print("rect: {0}".format(sourceImage.rectF(targetImage.geoBoundingBox())))
        
        #targetImage.paste(sourceImage)
        #result = sourceImage.save("/tmp/gdal-out-qt.png", "PNG")
        #print("Result: {0} isNull:{1}".format(result, sourceImage.isNull()))
        #targetImage.save("/tmp/qt-result-2.png")
    print("Fertig")
        #sys.exit(app.exec_())

