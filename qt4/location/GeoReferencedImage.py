'''
Created on 17.12.2011

@author: michi
'''
from __future__ import print_function
import struct
import numpy
import sys

from PyQt4.QtCore import Qt, QSize, QSizeF
from PyQt4.QtGui import QApplication, QImage, QImageReader

import gdal, osr
from gdalconst import *

from ems.qt4.location.geocoordinate import GeoCoordinate
from application.locationplugins.geoboundingbox_utm import GeoBoundingBoxUtm

class GeoReferencedImage(QImage):
    def __init__(self, fileNameOrSize=None):
        if isinstance(fileNameOrSize, basestring):
            dataset = gdal.Open(fileName, GA_ReadOnly)
            if dataset is None:
                raise IOError("File {0} not found.".format(fileName))
            
            self.gdalDriver = dataset.GetDriver()
            self._sourceSize = QSize(dataset.RasterXSize, dataset.RasterYSize)
            
            
            geotransform = dataset.GetGeoTransform()
            if geotransform is None:
                raise TypeError("Geotransform could not be received")
            
            self._pixelSize = QSizeF(geotransform[1], geotransform[5])
            
            self._topLeftCoordinate(GeoCoordinate(geotransform[0], geotransform[3],
                                                  projection="utm"))
            
            self._bottomRightCoordinate = None
            dataset = None
        
        
    def origin(self):
        return self._topLeftCoordinate
    
    def topLeftCoordinate(self):
        return self._topLeftCoordinate
    
    def bottomRightCoordinate(self):
        if self._bottomRightCoordinate is None:
            br = GeoCoordinate(self._topLeftCoordinate.latitude() + \
                               (self._pixelSize.width()*self._sourceSize.width()),
                               self._topLeftCoordinate.longitude() + \
                               (self._pixelSize.height()*self._sourceSize.height()),
                               projection="utm")
            
            self._bottomRightCoordinate = br
        return self._bottomRightCoordinate
        
        
        
        


fileName = '/home/michi/Dokumente/IT/Kontakte/SmartGeomatics/Projekte/Datenlieferungen/2011-11-30 Pfalzgrafenweiler Orthofotos UTM32N/34705383/34705383.tif'
#fileName = '/home/michi/Dokumente/IT/Kontakte/SmartGeomatics/Projekte/Datenlieferungen/2011-06-01 Pfalzgrafenweiler Orthos nativ/Orthofotos rgb/34625377.tif'

dataset = gdal.Open(fileName, GA_ReadOnly)
if dataset is None:
    raise IOError("File {0} not found.".format(fileName))

print("Size is {0}x{1}x{2}".format(dataset.RasterXSize, dataset.RasterYSize,
                                   dataset.RasterCount))

print("Projection is {0}".format(dataset.GetProjection()))

geotransform = dataset.GetGeoTransform()
if geotransform is None:
    raise TypeError("Geotransform could not be received")

print("Origin = ({0},{1})".format(geotransform[0], geotransform[3]))
print("Pixel Size = ({0},{1})".format(geotransform[1], geotransform[5]))




sourceSizeX = dataset.RasterXSize
sourceSizeY = dataset.RasterYSize

pixelSizeX = geotransform[1]
pixelSizeY = geotransform[5]

imageLeftTop = GeoCoordinate(geotransform[0], geotransform[3], projection='utm')

sourceBottomRight = GeoCoordinate(imageLeftTop.latitude() + (pixelSizeX*sourceSizeX),
                                  imageLeftTop.longitude() + (pixelSizeY*sourceSizeY),
                                  projection="utm")

sourceBounds = GeoBoundingBoxUtm(imageLeftTop, sourceBottomRight)

tileLeftTop = GeoCoordinate(469993.896484, 5382398.31543, projection="utm")
tileBottomRight = GeoCoordinate(470020.44014, 5382371.77177, projection="utm")
tileBounds = GeoBoundingBoxUtm(tileLeftTop, tileBottomRight)

print(sourceBounds)
print(tileBounds)

intersection = tileBounds.intersected(sourceBounds)
print("tileBounds.intersects(sourceBounds): {0}".format(tileBounds.intersects(sourceBounds)))
print("tileBounds.intersected(sourceBounds): {0}".format(intersection))

print("Rotation = ({0},{1}) (0 is north-up)".format(geotransform[2], geotransform[4]))


#dataset = None


band = dataset.GetRasterBand(1)
#
#print("Band Type = {0}".format(gdal.GetDataTypeName(band.DataType)))
#
min = band.GetMinimum()
max = band.GetMaximum()
#
if min is None or max is None:
    (min, max) = band.ComputeRasterMinMax(1)
#
print('Min={0:.3f}, Max={1:.3f}'.format(min, max))
#
if band.GetOverviewCount() > 0:
    print('Band has a color table with {0} entries'.format(band.GetOverviewCount()))
#
if not band.GetRasterColorTable() is None:
    print("Band has a color table with {0} entries".
          format(band.GetRasterColorTable().GetCount()))

#scanline = band.ReadRaster(0, 0, band.XSize, 1, band.XSize, 1, GDT_Float32, 0, 0)
#tupleOfFloats = struct.unpack('f' * band.XSize, scanline)

#for fmt in QImageReader.supportedImageFormats():
#    print(fmt)

formats = {'BMP':'bmp','PNG':'png','GTiff':'tif'}

dstFormat = "PNG"

targetSize = (sourceSizeX, sourceSizeY)


targetDriver = gdal.GetDriverByName(dstFormat)

dstFileName = "/tmp/gdal-out.png"
target = targetDriver.CreateCopy(dstFileName, dataset, 0)

#raster = numpy.zeros(targetSize, dtype=numpy.uint8)

#target.GetRasterBand(1).WriteArray(raster)

target = None
dataset = None


app = QApplication([])
sourceImage = QImage(dstFileName)
#result = sourceImage.save("/tmp/gdal-out-qt.png", "PNG")
#print("Result: {0} isNull:{1}".format(result, sourceImage.isNull()))
print("Fertig")





