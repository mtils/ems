'''
Created on 03.11.2011

@author: michi
'''
import math, time, logging

from PyQt4.QtCore import QObject, QPointF, Qt, QRectF
from PyQt4.QtGui import QGraphicsScene, QGraphicsPolygonItem, \
    QGraphicsEllipseItem, QGraphicsPathItem, QPolygonF, QTransform, \
    QPainterPath
    
from ems.qt4.location.maps.geomapobject import GeoMapObject #@UnresolvedImport
from ems.qt4.location.geocoordinate import GeoCoordinate #@UnresolvedImport
from ems.qt4.location.projwrapper import \
ProjCoordinateSystem, ProjCoordinate, ProjPolygon #@UnresolvedImport
from geomaprouteobject import GeoMapRouteObject #@UnresolvedImport
from geomapgroupobject import GeoMapGroupObject #@UnresolvedImport
import logging

class GeoMapObjectEngine(QObject):
    '''
     A quick note about how the transforms are set up:

      Each QGeoMapObject has its own "local" coordinate system, whether this
      a pixel system or meters or whatever.
    
      For local systems that are not in pixels, we do a two-stage transform --
      first we transform the object to arc-seconds, then we transform from
      arc-seconds to pixels on the screen. This is necessary as QGeoMapData
      subclasses only provide a mapping from lat/lon coordinates to screen pixels
      and no other source.
    
      For local systems that are in pixels, we simply translate to the screen
      coordinates. However, we still generate a transform to arc-seconds for these
      objects, to speed up the drawing process.
    
      QGeoMapDataPrivate has two sets of 3 fields that are used here:
        - xxxTrans
        - xxxScene
        - xxxItems
      (where xxx = [latLon, pixel])
    
      xxxTrans = a multi-hash of transforms associated with each QGeoMapObject
                 (a given map object may appear at more than one coordinate if
                  it wraps over the dateline)
      xxxScene = a QGraphicsScene filled with bounding boxes for each object, one
                 for each entry in xxxTrans
      xxxItems = a hash taking the items in the xxxScene and giving back the original
                 QGeoMapObject they were created for
    
      the "latLon" entries describe the transformations from local coordinates to
      arc-seconds, and the "pixel" entries describe the transformations from local
      coordinates to pixels on screen.
    
      Items within latLonScene have their coordinates in arc-seconds, and items
      within pixelScene have theirs in pixels.
    '''
    
    def __init__(self, mapData, mapDataP=None):
        self.md = mapData
        self.mdp = mapData
        
        self.latLonExact = {}
        self.pixelExact = {}
        
        self.latLonTrans = {}
        self.latLonScene = QGraphicsScene()
        self.latLonScene.setItemIndexMethod(QGraphicsScene.BspTreeIndex)
        self.latLonItems = {}
        self.latLonItemsRev = {}
        
        self.pixelTrans = {}
        self.pixelScene = QGraphicsScene()
        self.pixelScene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.pixelItems = {}
        self.pixelItemsRev = {}
        
        self.objectsForPixelUpdate = set()
        self.objectsForLatLonUpdate = set()
        
        self.exactMappingTolerance = 1.0 
        QObject.__init__(self, None)
    
    def clearForDeletion(self):
        self.pixelScene.clear()
        self.latLonScene.clear()
        del self.pixelScene
        del self.latLonScene
        
        self.latLonExact.clear()
        self.pixelExact.clear()
        self.latLonTrans.clear()
        self.latLonItems.clear()
        self.latLonItemsRev.clear()
        self.pixelTrans.clear()
        self.pixelItems.clear()
        self.pixelItemsRev.clear()
        self.objectsForPixelUpdate.clear()
        self.objectsForLatLonUpdate.clear()
        #return
        for i in self.latLonExact:
            logging.getLogger(__name__).warning(unicode(self.latLonExact[i]))
        
        for i in self.pixelExact:
            logging.getLogger(__name__).warning(unicode(self.pixelExact[i]))
    '''
    ****************************************************************************
     Object management
    ****************************************************************************
    '''
    
    def addObject(self, obj):
        self.objectsForLatLonUpdate.add(obj)
        self.updateTransforms()
        self.rebuildScenes()
    
    def removeObject(self, obj):
        if obj.type_() == GeoMapObject.GroupType:
            for child in obj.childs:
                self.removeObject(child)
        else:
            rectsToUpdate = []
            try:
                for item in self.pixelItemsRev[obj]:
                    rectsToUpdate.append(item.boundingRect())
            except KeyError:
                pass
            try:
                for item in self.pixelItemsRev[obj]:
                    try:
                        del self.latLonItems[item]
                    except KeyError:
                        pass
                    #TODO The were errors that the scene differs
                    if item.scene() is self.latLonScene:
                        self.latLonScene.removeItem(item)
                    del item
            except KeyError:
                pass
            try:
                del self.latLonItemsRev[obj]
            except KeyError:
                pass 
            
            try:
                del self.pixelTrans[obj]
            except KeyError:
                pass
            try:
                for item in self.pixelItemsRev[obj]:
                    del self.pixelItems[item]
                    #TODO The were errors that the scene differs
                    if item.scene() is self.pixelScene:
                        self.pixelScene.removeItem(item)
                    del item
                del self.pixelItemsRev[obj]
            except KeyError:
                pass
            
            for rect in rectsToUpdate:
                self.mdp.triggerUpdateMapDisplay(rect)
    
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
        projStr = projStr.format(origin.lat, origin.lng)
        
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
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
            
            westPoly = wgs * west
            pi = self.polyCopy(elItem)
            pi.setPolygon(westPoly)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
    
            eastPoly = wgs * east
            
            pi = self.polyCopy(elItem)
            pi.setPolygon(eastPoly)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
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
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
            
            westPoly = wgs * west
            pi = self.polyCopy(polyItem)
            pi.setPolygon(westPoly)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
            
            eastPoly = wgs * east
            pi = self.polyCopy(polyItem)
            pi.setPolygon(eastPoly)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
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
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
            
            westPath = path * west;
            pi = self.pathCopy(pathItem);
            pi.setPath(westPath);
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
            
            eastPath = path * east
            pi = self.pathCopy(pathItem)
            pi.setPath(eastPath)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
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
            ox = origin.lng * 3600.0;
            oy = origin.lat * 3600.0;
            toAbs.translate(ox, oy)
        
        try:
            for i in self.latLonExact[obj]:
                del i
            del self.latLonExact[obj]
        except KeyError:
            pass
        
        if isinstance(item,QGraphicsPolygonItem):
            polyItem = item
            if polyItem.polygon().isEmpty() or polyItem.polygon().size() < 3:
                return False
            
            poly = polyItem.polygon() * polyItem.transform()
            poly = poly * toAbs
            
            pi = self.polyCopy(polyItem)
            pi.setPolygon(poly)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]
                
            polys.append(pi.boundingRect())
            
            westPoly = poly * west
            pi = self.polyCopy(polyItem)
            pi.setPolygon(westPoly)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(pi.boundingRect())
            
            eastPoly = poly * east
            pi = self.polyCopy(polyItem);
            pi.setPolygon(eastPoly);
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
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
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            originalBounds = pi.boundingRect()
            polys.append(QPolygonF(originalBounds))
            
            westPath = path * west
            pi = self.pathCopy(pathItem);
            pi.setPath(westPath)
            
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(QPolygonF(originalBounds) * west)
            
            eastPath = path * east
            pi = self.pathCopy(pathItem)
            pi.setPath(eastPath);
            try:
                self.latLonExact[obj].append(pi)
            except KeyError:
                self.latLonExact[obj] = [pi]

            polys.append(QPolygonF(originalBounds) * east)

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
        projStr = projStr.format(origin.lat, origin.lng)
        
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
    
        return flip * item.transform() * latLon
    
    def bilinearPixelsToSeconds(self, origin, item, local, latLon):
        pixelOrigin = self.mdp.coordinateToScreenPosition(origin)
        
        wgs = QPolygonF()
        for pt in local:
            coord = self.md.screenPositionToCoordinate(pt + pixelOrigin)
            
            lpt = QPointF(coord.lng * 3600.0, coord.lat * 3600.0)
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
#        for i in range(len(local)):
#            print local.at(i), wgs.at(i)
#        print self.md._worldReferenceViewportRect
        if not ok:
            raise TypeError("QGeoMapData: bilinear transform from meters to arc-seconds " +
                            "failed: could not obtain a transformation matrix");
    
        return item.transform() * latLon
    
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
            
            try:
                self.pixelTrans[obj].append(pixel)
            except KeyError:
                self.pixelTrans[obj] = [pixel]

            polys.append(pixelPoly)

    class PathStep(object):
        __slots__ = ['tooClose','pixel','e']

    def exactPixelMap(self, origin, obj, polys):
        '''
        @param origin: GeoCoordinate
        @type origin: GeoCoordinate
        @param obj: GeoMapObject
        @type obj: GeoMapObject
        @param polys: List of QPolygonF
        @type polys: list
        '''
        #print "exactPixelMap!!"
        latLonItems = self.latLonExact[obj]
        
        try:
            for i in self.pixelExact[obj]:
                del i
            del self.pixelExact[obj]
        except KeyError:
            pass
        
        tolerance = self.exactMappingTolerance
        
        if isinstance(obj, GeoMapRouteObject):
            tolerance = obj.detailLevel()
        # square it
        tolerance = tolerance * tolerance
        
        for latLonItem in latLonItems:
            if isinstance(latLonItem, QGraphicsPolygonItem):
                poly = latLonItem.polygon()
                pixelPoly = self.polyToScreen(poly)
    
                pi = self.polyCopy(latLonItem)
                pi.setPolygon(pixelPoly)
                
                try:
                    self.pixelExact[obj].append(pi)
                except KeyError:
                    self.pixelExact[obj] = [pi]

                polys.append(pi.boundingRect())
            
            if isinstance(latLonItem, QGraphicsPathItem):
                pathItem = latLonItem
                path = pathItem.path()
                pathSize = path.elementCount()
                mpath = QPainterPath()
    
                screen = self.latLonViewport().boundingRect()
    
                lastPixelAdded = QPointF()
                lastOutside = True
    
                steps = []
                
                for i in range(pathSize):
                    e = path.elementAt(i)
                    pathStep = GeoMapObjectEngine.PathStep()
                    pathStep.e = e
                    
                    x = e.x; x /= 3600.0
                    y = e.y; y /= 3600.0
                    
                    pixel = self.mdp.coordinateToScreenPosition(x, y)
                    deltaP = QPointF(pixel - lastPixelAdded)
                    delta = deltaP.x() * deltaP.x() + deltaP.y() * deltaP.y()
                    
                    pathStep.pixel = pixel
                    
                    if not lastPixelAdded.isNull() and delta < tolerance:
                        pathStep.tooClose = True
                    else:
                        pathStep.tooClose = False
                        lastPixelAdded = pixel
                    steps.append(pathStep)
                
                em = steps[0].e
                
                for i in range(pathSize):
                    e = steps[i].e
                    
                    if steps[i].tooClose:
                        continue
                    
                    # guilty until proven innocent
                    outside = True
                    if screen.contains(e.x, e.y):
                        outside = False
                    if lastOutside:
                        if (em.x < screen.left() and e.x > screen.right()):
                            outside = False;
                        if (em.x > screen.right() and e.x < screen.left()):
                            outside = False;
                        if (em.y < screen.bottom() and e.y > screen.top()):
                            outside = False;
                        if (em.y > screen.top() and e.y < screen.bottom()):
                            outside = False;
                    
                    # skip points not inside the screen rect
                    # or attached to points inside it
                    if (outside and lastOutside):
                        continue
                    
                    # entering the screen rect
                    if not outside and lastOutside and i > 0:
                        lastPixel = steps[i-1].pixel
                        mpath.moveTo(lastPixel)
                    lastOutside = outside;
    
                    pixel = steps[i].pixel
    
                    if e.isMoveTo():
                        mpath.moveTo(pixel)
                    else:
                        mpath.lineTo(pixel)
    
                    em = e
                    
                del steps
                
                pi = self.pathCopy(pathItem)
                pi.setPath(mpath)
                #self.pixelExact.insertMulti(obj, pi);
                try:
                    self.pixelExact[obj].append(pi)
                except KeyError:
                    self.pixelExact[obj] = [pi]

                polys.append(QPolygonF(pi.boundingRect()))
        
    def pixelShiftToScreen(self, origin, obj, polys):
        '''
        @param origin: GeoCoordinate
        @type origin: GeoCoordinate
        @param obj: GeoMapObject
        @type obj: GeoMapObject
        @param polys: A list to which the polys will be appended
        @type polys: list
        '''
        #print "pixelShiftToScreen", time.time()
        item = self.graphicsItemFromMapObject(obj)
        if not item:
            return
    
        localRect = item.boundingRect() | item.childrenBoundingRect()
        
        # compute the transform as an origin shift
        origins = []
        origins.append(QPointF(origin.lng, origin.lat))
        origins.append(QPointF(origin.lng + 360.0, origin.lat))
        origins.append(QPointF(origin.lng - 360.0, origin.lat))
        
        for o in origins:
            pixel = item.transform()
            pixelOrigin = self.mdp.coordinateToScreenPosition(o.x(), o.y())
            pixel.translate(pixelOrigin.x(), pixelOrigin.y())
            
            try:
                self.pixelTrans[obj].append(pixel)
            except KeyError:
                self.pixelTrans[obj] = [pixel]

            polys.append(pixel.map(QPolygonF(localRect)))
        
#        print "PixelShift2Screen"
#        for poly in polys:
#            print "Next Poly"
#        for p in polys[0]:
#            print p                
    
    '''
    ****************************************************************************
     Update utility functions
    ****************************************************************************
    '''
    
    @staticmethod
    def _zoomDepsRecurse(eng, group):
        '''
        @param eng: GeoObjectEngine
        @type eng: GeoObjectEngine
        @param group: GeoMapGroupObject
        @type group: GeoMapGroupObject
        '''

        for obj in group.childs:
            if isinstance(obj, GeoMapGroupObject):
                GeoMapObjectEngine._zoomDepsRecurse(eng, obj)
            else:
                if obj.units() == GeoMapObject.PixelUnit:
                    eng.objectsForLatLonUpdate.add(obj)
                    eng.objectsForPixelUpdate.add(obj)
    
    def invalidateZoomDependents(self):
        #print "invalidateZoomDependents"
        if self.mdp._containerObject:
            GeoMapObjectEngine._zoomDepsRecurse(self, self.mdp._containerObject)
    
    
    def invalidatePixelsForViewport(self, updateNow=True):

        #print "GeoMapObjectEngine.invalidatePixelsForViewport"

        view = self.latLonViewport()

        itemsInView = self.latLonScene.items(view, Qt.IntersectsItemShape,
                                             Qt.AscendingOrder)
        
        
        for latLonItem in itemsInView:
            for obj in self.latLonItems[latLonItem]:
                self.objectsForPixelUpdate.add(obj)
        
        if updateNow:
            self.mdp.updateMapDisplay.emit(QRectF())
    
    def trimPixelTransforms(self):
        #print "trimPixelTransforms"
#        self.mdp.updateMapDisplay.emit(QRectF())
#        return
        view = self.latLonViewport()
#        print 'viewport'
#        for pt in view:
#            print pt
        itemsInView = self.latLonScene.items(view, Qt.IntersectsItemShape,
                                             Qt.AscendingOrder)

        shouldBe = set()
        for latLonItem in itemsInView:
            for obj in self.latLonItems[latLonItem]:
            #obj = self.latLonItems[latLonItem]
                shouldBe.add(obj)
        
        itemsInPixels = self.pixelScene.items()

        currentlyAre = set()
        for pixelItem in itemsInPixels:
            obj = self.pixelItems[pixelItem]
            currentlyAre.add(obj)
        
        excess = currentlyAre.difference(shouldBe)
        
        for obj in excess:
            for item in self.pixelItemsRev[obj]:
                self.pixelScene.removeItem(item)
                del self.pixelItems[item]
                del item
            try:
                del self.pixelTrans[obj]
            except KeyError:
                pass
            try:
                del self.pixelItemsRev[obj]
            except KeyError:
                pass
        
        self.mdp.updateMapDisplay.emit(QRectF())
    
    def invalidateObject(self, obj):
        '''
        @param obj: The GeoMapObject
        @type obj: GeoMapObject
        '''
        #print "invalidateObject"
        self.updateLatLonTransform(obj)
        
        view = self.latLonViewport().boundingRect()
        
        
        needsPixelUpdate = False
        try:
            for item in self.latLonItemsRev[obj]:
                if item.boundingRect().intersects(view):
                    needsPixelUpdate = True
                    break
        except KeyError, e:
            logging.warn(str(e))
        
        if needsPixelUpdate:
            self.objectsForPixelUpdate.add(obj)
            self.mdp.triggerUpdateMapDisplay()
        
    def updateTransforms(self):
        '''
        update the transform tables as necessary
        '''
        #starttime = time.time()
        #print "updateTransforms"

        groupUpdated = False

        for obj in self.objectsForLatLonUpdate:
            #print "obj in objectsForLatLonUpdate", time.time()
            if obj.type_() == GeoMapObject.GroupType:
                self.updateLatLonsForGroup(obj)
                groupUpdated = True
            else:
                self.updateLatLonTransform(obj)

        #print "updateLatLonTransform end",time.time()

        self.objectsForLatLonUpdate = set()

        for obj in self.objectsForPixelUpdate:
            #print "obj in objectsForPixelUpdate", time.time()
            if obj.type_() == GeoMapObject.GroupType:
                self.updatePixelsForGroup(obj)
                groupUpdated = True
            else:
                self.updatePixelTransform(obj)

        #print "updatePixelTransform end",time.time()
        self.objectsForPixelUpdate = set()

        if groupUpdated:
            #rebuildScenesTime = time.time()
            self.rebuildScenes()
            #print "rebuildScenes end",time.time()-rebuildScenesTime

        #print "updateTransforms end",time.time() - starttime
    
    def updatePixelsForGroup(self, group):
        '''
        @param group: GeoMapGroupObject
        @type group: GeoMapGroupObject
        '''
        for obj in group.childs:
            if obj.type_() == GeoMapObject.GroupType:
                self.updatePixelsForGroup(obj)
            else:
                self.updatePixelTransform(obj)
    
    def updateLatLonsForGroup(self, group):
        '''
        @param group: GeoMapGroupObject
        @type group: GeoMapGroupObject
        '''
        for obj in group.childs:
            if obj.type_() == GeoMapGroupObject:
                self.updateLatLonsForGroup(obj)
            else:
                self.updateLatLonTransform(obj)
    
    @staticmethod
    def addGroupToScene(eng, group):
        '''
        @param eng: GeoMapObjectEngine
        @type eng: GeoMapObjectEngine
        @param group: GeoMapGroupObject
        @type group: GeoMapGroupObject
        '''
        for obj in group.childs:
            if obj.type_() == GeoMapObject.GroupType:
                GeoMapObjectEngine.addGroupToScene(eng, obj)
            else:
                try:
                    for i in eng.latLonItemsRev[obj]:
                        eng.latLonScene.addItem(i)
                except KeyError:
                    pass
                try:
                    for i in eng.pixelItemsRev[obj]:
                        eng.pixelScene.addItem(i)
                except KeyError:
                    pass
        
    def rebuildScenes(self):
        #return
        #starttime = time.time()
        #print "Start rebuildScenes"
        
        #clear is not working
        for i in self.latLonScene.items():
            self.latLonScene.removeItem(i)
        for i in self.pixelScene.items():
            self.pixelScene.removeItem(i)
    
        #del self.latLonScene
        #del self.pixelScene
    
        #self.latLonScene = QGraphicsScene()
        #self.pixelScene = QGraphicsScene()
        #self.pixelScene.setItemIndexMethod(QGraphicsScene.NoIndex)
    
        self.addGroupToScene(self, self.mdp._containerObject)
        #print "End rebuildScenes in {0}".format((time.time()-starttime))
    
    '''
    ****************************************************************************
     Actual update functions
    ****************************************************************************
    '''
    
    def updateLatLonTransform(self, obj):
        '''
        
        @param obj: The obj to update
        @type obj: GeoMapObject
        '''
        origin = obj.origin()
        
        item = self.graphicsItemFromMapObject(obj)
        
        if not item:
            return
        
        localRect = (item.boundingRect() | item.childrenBoundingRect())
        
        # skip any objects with invalid bounds
        if not localRect.isValid() or localRect.isEmpty() or localRect.isNull():
            return
        
        
        #local = QPolygonF(localRect) * item.transform()
        local = QPolygonF(localRect) * item.transform()
        #local = localRect * item.transform() 
        #local = QPolygonF(item.transform().mapRect(localRect))
        #local = item.transform().mapRect(localRect)
        #local = item.transform() * localRect
        
        #local = localRect * trans
#        for i in local:
#            print i
        polys = []
        
        try:
            del self.latLonTrans[obj]
        except KeyError:
            pass 
        
        if obj.transformType() == GeoMapObject.BilinearTransform or\
            obj.units() == GeoMapObject.PixelUnit:
            latLon = QTransform()
            
            if obj.units() == GeoMapObject.MeterUnit:
                latLon = self.bilinearMetersToSeconds(origin, item, local, latLon);
            elif obj.units() == GeoMapObject.RelativeArcSecondUnit:
                latLon.translate(origin.lng * 3600.0, origin.lat * 3600.0)
            elif obj.units() == GeoMapObject.PixelUnit:
                latLon = self.bilinearPixelsToSeconds(origin, item, local, latLon)
            
            polys.append(latLon.map(QPolygonF(localRect)))
            
            try:
                self.latLonTrans[obj].append(latLon)
            except KeyError:
                self.latLonTrans[obj] = [latLon]

            latLonWest = QTransform()
            latLonWest.translate(360.0 * 3600.0, 0.0)
            latLonWest = latLon * latLonWest
            
            polys.append(latLonWest.map(QPolygonF(localRect)))

            try:
                self.latLonTrans[obj].append(latLonWest)
            except KeyError:
                self.latLonTrans[obj] = [latLonWest]

            latLonEast = QTransform()
            latLonEast.translate(-360.0 * 3600.0, 0.0)
            latLonEast = latLon * latLonEast
            
            polys.append(latLonEast.map(QPolygonF(localRect)))
            
            try:
                self.latLonTrans[obj].append(latLonEast)
            except KeyError:
                self.latLonTrans[obj] = [latLonEast]
            
        elif obj.transformType() == GeoMapObject.ExactTransform:
            if obj.units() == GeoMapObject.MeterUnit:
                if not self.exactMetersToSeconds(origin, obj, item, polys):
                    return
            elif obj.units() == GeoMapObject.AbsoluteArcSecondUnit or\
                   obj.units() == GeoMapObject.RelativeArcSecondUnit:
                if not self.exactSecondsToSeconds(origin, obj, item, polys):
                    return
            else:
                return
#        for poly in polys:
#            print "Next Poly"
#            for p in poly:
#                print p
        try:
            items = self.latLonItemsRev[obj]
        except KeyError:
            items = []
        if len(items) != len(polys):
            for item in items:
                self.latLonScene.removeItem(item)
                del self.latLonItems[item]
                del item
            try:
                del self.latLonItemsRev[obj]
            except KeyError:
                pass
            
            for poly in polys:
                item = QGraphicsPolygonItem(poly)
                #item.setZValue(obj.zValue())
                item.setVisible(True)
                self.latLonItems[item] = [obj]
                try:
                    self.latLonItemsRev[obj].append(item)
                except KeyError:
                    self.latLonItemsRev[obj] = [item]

                self.latLonScene.addItem(item)
        else:
            i = 0
            for item in items:
                if not item:
                    continue
                
                item.setPolygon(polys[i])
                i += 1
                
    
    def updatePixelTransform(self, obj):
        origin = obj.origin()
        item = self.graphicsItemFromMapObject(obj)
        
        # skip any objects without graphicsitems
        if not item:
            return
        
        localRect = (item.boundingRect() | item.childrenBoundingRect())
        
        # skip any objects with invalid bounds
        if not localRect.isValid() or localRect.isEmpty() or localRect.isNull():
            return
        
        polys = []
        
        try:
            del self.pixelTrans[obj]
        except KeyError:
            pass
        
        if obj.transformType() == GeoMapObject.BilinearTransform:
            self.bilinearSecondsToScreen(origin, obj, polys)
        elif obj.transformType() == GeoMapObject.ExactTransform:
            if obj.units() == GeoMapObject.PixelUnit:
                self.pixelShiftToScreen(origin, obj, polys)
            else:
                self.exactPixelMap(origin, obj, polys)
        
        try:
            items = self.pixelItemsRev[obj]
        except KeyError:
            items = []
        
        if len(items) != len(polys):
            for item in items:
                del self.pixelItems[item]
                self.pixelScene.removeItem(item)
                del item
            
            try:
                del self.pixelItemsRev[obj]
            except KeyError:
                pass
            
            for poly in polys:
                item = QGraphicsPolygonItem(poly)
                
                item.setVisible(True)
                self.pixelItems[item] = obj
                #self.pixelItemsRev.insertMulti(obj, item);
                try:
                    self.pixelItemsRev[obj].append(item)
                except KeyError:
                    self.pixelItemsRev[obj] = [item]

                self.pixelScene.addItem(item)
        else:
            for i in range(len(polys)):
                item = items[i]
                
                if not item:
                    continue
                
                item.setPolygon(polys[i])
            
    
    def latLonViewport(self):
        '''
        @rtype: QPolygonF
        '''
        view = QPolygonF()
        viewport = self.md.viewport()
        offset = 0.0
        
        c = viewport.bottomLeft()
         
        #try:
        cLatitude = c.lat
        cLongitude = c.lng
        
        c2 = viewport.bottomRight()
        c2Latitude = c2.lat
        c2Longitude = c2.lng
        
        #print viewport
        #print c
        
        if isinstance(cLatitude, float):
            view << QPointF(cLongitude * 3600.0, cLatitude * 3600.0)
            
            if c2Longitude < cLongitude:
                offset = 360.0 * 3600.0
            view << QPointF(c2Longitude * 3600.0 + offset, c2Latitude * 3600.0)
            c3 = viewport.topRight();
            view << QPointF(c3.lng * 3600.0 + offset, c3.lat * 3600.0)
            c4 = viewport.topLeft();
            view << QPointF(c4.lng * 3600.0, c4.lat * 3600.0)
        #except TypeError:
        #   pass 
        
#        print "latLonViewport"
#        for i in view:
#            print i
        #print view
        return view
    
    def polyToScreen(self, poly):
        r = QPolygonF()
        for pt in poly:
            x = pt.x() / 3600.0
            y = pt.y() / 3600.0
            pixel = self.mdp.coordinateToScreenPosition(x, y)
            r.append(pixel)
        return r
    
    def graphicsItemFromMapObject(self, obj):
        try:
            return obj.info().graphicsItem
        except AttributeError:
            return None