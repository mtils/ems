'''
Created on 03.11.2011

@author: michi
'''
import math

from PyQt4.QtCore import QObject, QPointF
from PyQt4.QtGui import QGraphicsScene, QGraphicsPolygonItem, \
    QGraphicsEllipseItem, QGraphicsPathItem, QPolygonF, QTransform
    
from lib.ems.qt4.location.maps.geomapobject import GeoMapObject
from lib.ems.qt4.location.geocoordinate import GeoCoordinate
from lib.ems.qt4.location.projwrapper import ProjCoordinateSystem,\
    ProjCoordinate, ProjPolygon

class GeoMapObjectEngine(QObject):
    def __init__(self, mapData, mapDataP=None):
        self.md = mapData
        self.mdp = mapData
        
        self.latLonExact = {}
        self.pixelExact = {}
        
        self.latLonTrans = {}
        self.latLonScene = QGraphicsScene()
        self.latLonItems = {}
        self.latLonItemsRev = {}
        
        self.pixelTrans = {}
        self.pixelScene = QGraphicsScene()
        self.pixelScene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.pixelItems = {}
        self.pixelItemsRev = {}
        
        self.objectsForPixelUpdate = []
        self.objectsForLatLonUpdate = []
        
        self.exactMappingTolerance = 1.0 
        QObject.__init__(self, None)
    
    def __del__(self):
        
        del self.pixelScene
        del self.latLonScene
        
        for i in self.latLonExact:
            del self.latLonExact[i]
        
        for i in self.pixelExact:
            del self.pixelExact[i]
    '''
    ****************************************************************************
     Object management
    ****************************************************************************
    '''
    
    def addObject(self, obj):
        self.objectsForLatLonUpdate.append(obj)
        self.objectsForPixelUpdate.append(obj)
        self.updateTransforms()
        self.rebuildScenes()
    
    def removeObject(self, obj):
        if obj.type_() == GeoMapObject.GroupType:
            for child in obj.childObjects():
                self.removeObject(child)
        else:
            rectsToUpdate = []
            for item in self.pixelItemsRev[obj]:
                rectsToUpdate.append(item.boundingRect())
                
            for item in self.pixelItemsRev[obj]:
                del self.latLonItems[item]
                self.latLonScene.removeItem(item)
                del item
            del self.latLonItemsRev[obj]
            
            del self.pixelTrans[obj]
            for item in self.pixelItemsRev[obj]:
                del self.pixelItems[item]
                self.pixelScene.removeItem(item)
                del item
            del self.pixelItemsRev[obj]
            
            for rect in rectsToUpdate:
                self.mdp.emitUpdateMapDisplay(rect)
    
    '''
    ****************************************************************************
     Transform support functions
    ****************************************************************************
    '''
    
    @staticmethod
    def polyCopy(item):
        '''
        @param polyItem: The polygonitem to copy
        @type polyItem: QGraphicsPolygonItem | QGraphicsEllipseItem | QGraphicsPathItem
        @rtype: QGraphicsPolygonItem
        '''
        if not isinstance(item, QGraphicsPathItem):
            pi = QGraphicsPolygonItem()
        else:
            pi = QGraphicsPathItem()
            
        pi.setBrush(item.brush())
        pi.setPen(item.pen())
        pi.setVisible(item.isVisible())
        if isinstance(item, QGraphicsPolygonItem):
            pi.setFillRule(item.fillRule())
        pi.setOpacity(item.opacity())
        pi.setGraphicsEffect(item.graphicsEffect())
        
        return pi
    
    @staticmethod
    def pathCopy(path):
        return GeoMapObjectEngine.polyCopy(path)
    
    @staticmethod
    def approximateCircle(elItem, obj, center, projCenter):
        '''
        Seems to try to calculate a circle
        
        @param elItem: QGraphicsEllipseItem
        @type elItem: QGraphicsEllipseItem
        @param obj: GeoMapObject
        @type obj: GeoMapObject
        @param center: The center
        @type center: GeoCoordinate
        @param projCenter: ProjCoordinate
        @type projCenter: ProjCoordinate
        @rtype: QPolygonF
        '''
        rect = elItem.rect()
        
        a = rect.height() / 2.0;
        b = rect.width() / 2.0;
    
        asq = a*a
        bsq = b*b
        
        secPoly = QPolygonF()
        detail = 150
        
        if obj.type_() == GeoMapObject.CircleType:
            detail = obj.pointCount()
        
        Pi = math.pi
        twopi = 6.283185307179
        
        dth = twopi/detail
        
        startAngle = elItem.startAngle()
        startAngle /= 16.0
        startAngle *= twopi
        startAngle /= 360.0
    
        stopAngle = elItem.startAngle() + elItem.spanAngle()
        stopAngle /= 16.0
        stopAngle *= twopi
        stopAngle /= 360.0
    
        drawToCenter = (elItem.spanAngle() != 360 * 16)
        
        theta = startAngle
        while theta < stopAngle:
            top = b*math.sin(theta);
            bottom = a*math.cos(theta);
    
            phi = math.atan(top / bottom);
            if bottom < 0:
                phi = phi + Pi
            
            phiDeg = (360.0 * phi) / twopi;

            costh = math.cos(theta);
            sinth = math.sin(theta);
    
            r = math.sqrt(asq*costh*costh + bsq*sinth*sinth);
            
            y, x = GeoCoordinate.atDistanceAndAzimuthStatic(center, r,
                                                                phiDeg)
            
            y *= 3600.0
            x *= 3600.0
            
            secPoly << QPointF(x, y)
            
            theta += dth
        
        if drawToCenter:
            secPoly << QPointF(projCenter.x() * 3600.0, projCenter.y() * 3600.0)
        
        return secPoly
    
    def exactMetersToSeconds(self, origin, obj, item, polys):
        '''
        
        @param origin: GeoCoordinate
        @type origin: GeoCoordinate
        @param obj: GeoMapObject
        @type obj: GeoMapObject
        @param item: QGraphicsItem
        @type item: QGraphicsItem
        @param polys: List of polygons (which will be altered)
        @type polys: list
        '''
        projStr = "+proj=tmerc +lat_0={0:.12f} +lon_0={1.12f} +k=1.0 +x_0=0 +y_0=0 +ellps=WGS84"
        projStr = projStr.format(origin.latitude(), origin.longitude())
        
        localSys = ProjCoordinateSystem(projStr, False)
        wgs84 = ProjCoordinateSystem("+proj=latlon +ellps=WGS84")
        
        west = QTransform()
        west.translate(360.0 * 3600.0, 0.0)
        
        east = QTransform()
        east.translate(-360.0 * 3600.0, 0.0)
        
        for i in self.latLonExact[obj]:
            del i
        del self.latLonExact[obj]
        
        if isinstance(item, QGraphicsEllipseItem):
            elItem = item
            rect = elItem.rect()
            
            cen = rect.center()
            c = ProjCoordinate(cen.x(), -1*cen.y(), 0.0, localSys)
            c.convert(wgs84);
            center = c.toGeoCoordinate()
            
            wgs = self.approximateCircle(elItem, obj, center, c)

            pi = self.polyCopy(elItem);
            pi.setPolygon(wgs)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi,]
                
            polys.append(pi.boundingRect())
            
            westPoly = wgs * west
            pi = self.polyCopy(elItem)
            pi.setPolygon(westPoly)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            
            polys.append(pi.boundingRect())
    
            eastPoly = wgs * east
            
            pi = self.polyCopy(elItem)
            pi.setPolygon(eastPoly)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
                
            polys.append(pi.boundingRect())
            
            return True
        
        elif isinstance(item, QGraphicsPolygonItem):
            polyItem = item
            poly = polyItem.polygon() * polyItem.transform()
            
            p = ProjPolygon(poly, localSys)
            p.scalarMultiply(1, -1, 1)
            p.convert(wgs84)
            wgs = p.toPolygonF(3600.0)
            
            pi = self.polyCopy(polyItem);
            pi.setPolygon(wgs)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
                
            polys.append(pi.boundingRect())
            
            westPoly = wgs * west
            pi = self.polyCopy(polyItem)
            pi.setPolygon(westPoly)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            
            polys.append(pi.boundingRect())
            
            eastPoly = wgs * east
            pi = self.polyCopy(polyItem)
            pi.setPolygon(eastPoly)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            
            polys.append(pi.boundingRect())
            
            return True
        
        elif isinstance(item, QGraphicsPathItem):
            pathItem = item
            path = pathItem.path() * pathItem.transform()
            
            for i in range(path.elementCount()):
                e = path.elementAt(i)
                
                c = ProjCoordinate(e.x, -1*e.y, 0.0, localSys)
                c.convert(wgs84)
                path.setElementPositionAt(i, c.x() * 3600.0, c.y() * 3600.0)
            
            pi = self.pathCopy(pathItem)
            pi.setPath(path)
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            
            polys.append(pi.boundingRect())
            
            westPath = path * west;
            pi = self.pathCopy(pathItem);
            pi.setPath(westPath);
            
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
                
            polys.append(pi.boundingRect())
            
            eastPath = path * east
            pi = self.pathCopy(pathItem)
            pi.setPath(eastPath)
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            
            polys.append(pi.boundingRect())
    
            return True
        
        return False
    
    def exactSecondsToSeconds(self, origin, obj, item, polys):
        '''
        @param origin: GeoCoordinate
        @type origin: GeoCoordinate
        @param obj: obj
        @type obj: GeoMapObject
        @param item: QGraphicsItem
        @type item: QGraphicsItem
        @param polys: A list of polys which will be filled
        @type polys: list
        @rtype: bool
        '''
        
        west = QTransform()
        west.translate(360.0 * 3600.0, 0.0)
    
        east = QTransform()
        east.translate(-360.0 * 3600.0, 0.0);
            
        toAbs = QTransform()
        if obj.units() == GeoMapObject.RelativeArcSecondUnit:
            ox = origin.longitude() * 3600.0;
            oy = origin.latitude() * 3600.0;
            toAbs.translate(ox, oy)
        
        for i in self.latLonExact[obj]:
            del i
        del self.latLonExact[obj]
        
        if isinstance(item,QGraphicsPolygonItem):
            polyItem = item
            if polyItem.polygon().isEmpty() or polyItem.polygon().size() < 3:
                return False
            
            poly = polyItem.polygon() * polyItem.transform()
            poly = poly * toAbs
            
            pi = self.polyCopy(polyItem)
            pi.setPolygon(poly)
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
                
            polys.append(pi.boundingRect())
            
            westPoly = poly * west
            pi = self.polyCopy(polyItem)
            pi.setPolygon(westPoly)
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
                
            polys.append(pi.boundingRect())
            
            eastPoly = poly * east
            pi = self.polyCopy(polyItem);
            pi.setPolygon(eastPoly);
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            polys.append(pi.boundingRect())
            
            return True
        elif isinstance(item, QGraphicsPathItem):
            pathItem = item
            
            if pathItem.path().isEmpty() or pathItem.path().elementCount() < 2:
                return False
            
            path = pathItem.path() * pathItem.transform()
            path = path * toAbs
            
            pi = self.pathCopy(pathItem)
            pi.setPath(path)
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            originalBounds = pi.boundingRect()
            polys.append(originalBounds)
            
            westPath = path * west
            pi = self.pathCopy(pathItem);
            pi.setPath(westPath)
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            polys.append(originalBounds * west)
            
            eastPath = path * east
            pi = self.pathCopy(pathItem)
            pi.setPath(eastPath);
            if self.latLonExact.has_key(obj):
                self.latLonExact[obj].append(pi)
            else:
                self.latLonExact[obj] = [pi]
            polys.append(originalBounds * east)
            
            return True
        return False
    
    def bilinearMetersToSeconds(self, origin, item, local, latLon):
        '''
        @param origin: GeoCoordinate
        @type origin: GeoCoordinate
        @param item: QGraphicsItem
        @type item: QGraphicsItem
        @param local: QPolygonF
        @type local: QPolygonF
        @param latLon: QTransform
        @type latLon: QTransform
        '''
        projStr = "+proj=tmerc +lat_0={0} +lon_0={1} +k=1.0 +x_0=0 +y_0=0 +ellps=WGS84"
        projStr = projStr.format(origin.latitude(), origin.longitude())
        
        localSys = ProjCoordinateSystem(projStr, False)
        wgs84 = ProjCoordinateSystem("+proj=latlon +ellps=WGS84")
        
        p = ProjPolygon(local, localSys)
        
        if not p.convert(wgs84):
            raise TypeError("QGeoMapData: bilinear transform from meters to arc-seconds " +
                     "failed: projection is singular")
        
        wgs = p.toPolygonF(3600.0);

        # QTransform expects the last vertex (closing vertex) to be dropped
        local.remove(4)
        wgs.remove(4)
        
        # perform wrapping
        if wgs.at(2).x() < wgs.at(3).x():
            topRight = wgs.at(1)
            topRight.setX(topRight.x() + 360.0 * 3600.0)
            wgs.replace(1, topRight)
    
            bottomRight = wgs.at(2)
            bottomRight.setX(bottomRight.x() + 360.0 * 3600.0)
            wgs.replace(2, bottomRight)
        
        ok = QTransform.quadToQuad(local, wgs, latLon)
        if not ok:
            TypeError("QGeoMapData: bilinear transform from meters to arc-seconds " +
                     "failed: could not obtain a transformation matrix")
        
        flip = QTransform()
        flip.scale(1, -1)
    
        latLon = flip * item.transform() * latLon
    
    def bilinearPixelsToSeconds(self, origin, item, local, latLon):
        pixelOrigin = self.mdp.coordinateToScreenPosition(origin.longitude(),
                                                          origin.latitude())
        
        wgs = QPolygonF()
        for pt in local:
            coord = self.md.screenPositionToCoordinate(pt + pixelOrigin)
            
            lpt = QPointF(coord.longitude() * 3600.0, coord.latitude() * 3600.0)
            wgs.append(lpt)
        
        # QTransform expects the last vertex (closing vertex) to be dropped
        local.remove(4)
        wgs.remove(4)
        
        # perform wrapping
        if wgs.at(2).x() < wgs.at(3).x():
            topRight = wgs.at(1)
            topRight.setX(topRight.x() + 360.0 * 3600.0)
            wgs.replace(1, topRight)
    
            bottomRight = wgs.at(2)
            bottomRight.setX(bottomRight.x() + 360.0 * 3600.0)
            wgs.replace(2, bottomRight)
        
        ok = QTransform.quadToQuad(local, wgs, latLon)
        if not ok:
            raise TypeError("QGeoMapData: bilinear transform from meters to arc-seconds " +
                            "failed: could not obtain a transformation matrix");
    
        latLon = item.transform() * latLon
    
    def bilinearSecondsToScreen(self, origin, obj, polys):
        
        latLons = self.latLonTrans[obj]
        item = self.graphicsItemFromMapObject(obj)
        if not item:
            return
        
        for latLon in latLons:
            pixel = QTransform()
            local = (item.boundingRect() | item.childrenBoundingRect())
            latLonPoly = latLon.map(local)
            
            pixelPoly = self.polyToScreen(latLonPoly)

            #QTransform expects the last vertex (closing vertex) to be dropped
            local.remove(4);
            pixelPoly.remove(4);
    
            ok = QTransform.quadToQuad(local, pixelPoly, pixel)
            if not ok:
                raise TypeError("QGeoMapData: bilinear transform to screen from arc-seconds "
                                "failed: could not compute transformation matrix")
            
            if self.pixelTrans.has_key(obj):
                self.pixelTrans[obj].append(pixel)
            else:
                self.pixelTrans[obj] = [pixel]
            
            polys.append(pixelPoly)
    
    
            