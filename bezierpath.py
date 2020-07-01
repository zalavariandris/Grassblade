
import math
import numpy as np
from numba import jitclass, float32

spec = [      
    ('x0', float32),
    ('y0', float32),      
    ('cx', float32),
    ('bx', float32),
    ('ax', float32),
    ('cy', float32),
    ('by', float32),
    ('ay', float32)
]

def bezierCoefficents(A, B, C, D):
    cx = 3 * (B[0] - A[0])
    bx = 3 * (C[0] - B[0]) - cx
    ax = D[0] - A[0] - cx - bx
    cy = 3 * (B[1] - A[1])
    by = 3 * (C[1] - B[1]) - cy
    ay = D[1] - A[1] - cy - by

    return [ax, ay, bx, by, cx, cy]


@jitclass(spec)
class Curve:
    def __init__(self, A, B, C, D):
        self.x0 = A[0]
        self.y0 = A[1]
        x1 = B[0]
        y1 = B[1]
        x2 = C[0]
        y2 = C[1]
        x3 = D[0]
        y3 = D[1]

        # Calculate the polynomial coefficients.
        self.cx = 3 * (x1 - self.x0)
        self.bx = 3 * (x2 - x1) - self.cx
        self.ax = x3 - self.x0 - self.cx - self.bx
        self.cy = 3 * (y1 - self.y0)
        self.by = 3 * (y2 - y1) - self.cy
        self.ay = y3 - self.y0 - self.cy - self.by

    def getPoint(self, t):
        # points
        x = ((self.ax * t + self.bx) * t + self.cx) * t + self.x0
        y = ((self.ay * t + self.by) * t + self.cy) * t + self.y0

        return (x, y)

    def getTangent(self, t):
        # tangent
        tx = (3 * self.ax * t + 2 * self.bx) * t + self.cx
        ty = (3 * self.ay * t + 2 * self.by) * t + self.cy

        return (tx, ty)

    def getNearestTime(self, point):
        # rewritten from paper.js
        count = 8
        minDist = math.inf
        minT = 0

        def refine(t, debug=False):
            nonlocal minDist
            nonlocal minT

            if t>=0.0 and t<1.0:
                P = self.getPoint(t)
                vector = np.array([point[0] - P[0], point[1] - P[1]])
                dist = np.dot(vector, vector)
                
                if dist<minDist:
                    minDist = dist
                    minT = t
                    
                    return True
                return False
            return False

        for i in range(count):
            refine(i/count)

        step = 1.0/count/2
        while step>1e-18:
            if (not refine(minT-step, True)) and (not refine(minT+step)):
                step/=2.0

        return minT

    def getuv(self, x, y):
        t = self.getNearestTime( (x,y) )
        point = self.getPoint(t)
        tangent = self.getTangent(t)

        normal = np.array( [tangent[1], -tangent[0]] )
        vector = np.array([point[0]-x, point[1]-y])
        side = 1 if np.dot(normal, vector)>0 else -1
        dist = math.sqrt( np.dot(vector,vector) )

        # derive uv, from dist and t
        u = t/2
        if side==1:
            u = t/2
        else:
            u = (1-t)/2+0.5

        v=dist

        return u, v

    def getxy(self, u, v):
        if u<0.5:
            t = u*2
        else:
            t = 1-(u-0.5)*2

        dist = v

        point = self.getPoint(t)
        
        tangent = self.getTangent(t)
        
        length = math.sqrt(tangent[0]**2 + tangent[1]**2)
        normal = np.array([tangent[1], -tangent[0]]) / length

        if u<0.5:
            normal*=-1

        x, y = normal*dist+np.array(point)

        return x, y

class Path:
    def __init__(self, vertices, inTangents, outTangents, ax=None):
        segmentsCount = len(vertices)-1
        self.curves = []
        for i in range(segmentsCount):
            curve = Curve(
                vertices[i],
                vertices[i]+outTangents[i],
                vertices[i+1]-inTangents[i+1],
                vertices[i+1]
            )
            self.curves.append(curve)
        
        self.ax=ax

    def extend(self, length):
        # prepend start curveSegment
        tangent = self.curves[0].getTangent(1e-8)
        tangent/= np.linalg.norm(tangent)
        firstPoint = self.curves[0].getPoint(1e-8)

        startSegmentCtrlPoints = []
        for d in np.linspace(length, 0, 4)[:-1]:
            newPoint = firstPoint-tangent*d
            startSegmentCtrlPoints.append(newPoint)

        startSegmentCtrlPoints.append(firstPoint)
        segmentBefore = Curve(*startSegmentCtrlPoints)
        self.curves.insert(0, segmentBefore)

        # append end segment
        tangent = self.curves[-1].getTangent(1.0-1e-8)
        tangent/= np.linalg.norm(tangent)
        lastPoint = self.curves[-1].getPoint(1.0-1e-8)

        endSegmentCtrlPoints = [lastPoint]
        for d in np.linspace(0, length, 4)[1:]:
            newPoint = lastPoint+tangent*d
            endSegmentCtrlPoints.append(newPoint)

        segmentAfter = Curve(*endSegmentCtrlPoints)
        self.curves.append(segmentAfter)

    def _getCurveAtTime(self, t):
        if t==0:
            return 0,0
        if t==1:
            return len(self.curves)-1, 1

        # get curve for t
        count = len(self.curves)
        curve_idx = math.floor(t*count)
        curve = self.curves[curve_idx]
        curve_t = (t-curve_idx/count)*count

        return curve_idx, curve_t

    def getPoint(self, t):
        c, t = self._getCurveAtTime(t)
        # calc *t* for curve segment
        return self.curves[c].getPoint( t )

    def getTangent(self, t):
        if t==0:
            t = 1e-8
        if t==1.0:
            t = 1.0-1e-8
        c, t = self._getCurveAtTime(t)
        return self.curves[c].getTangent(t)

    def getNearestTime(self, point):
        count = len(self.curves)
        minCurve = None
        minCurveT = -1
        minDist = math.inf

        for c in range(count):
            curve = self.curves[c]
            t = curve.getNearestTime(point)
            P = curve.getPoint(t)
            vector = np.array([point[0] - P[0], point[1] - P[1]])
            dist = np.dot(vector, vector)
            if dist<minDist:
                minDist = dist
                minC = c
                minT = t
        
        t = minC/count+minT/count

        return t

    
    def getuv(self, x, y):
        t = self.getNearestTime( (x,y) )
        point = self.getPoint(t)
        tangent = self.getTangent(t)

        normal = np.array( [tangent[1], -tangent[0]] )
        vector = np.array([point[0]-x, point[1]-y])
        side = 1 if np.dot(normal, vector)>0 else -1
        dist = math.sqrt( np.dot(vector,vector) )

        # derive uv, from dist and t
        u = t/2
        if side==1:
            u = t/2
        else:
            u = (1-t)/2+0.5

        v=dist

        return u, v

    def getxy(self, u, v):
        if u<0.5:
            t = u*2
        else:
            t = 1-(u-0.5)*2

        dist = v

        point = self.getPoint(t)
        
        tangent = self.getTangent(t)
        
        length = math.sqrt(tangent[0]**2 + tangent[1]**2)
        normal = np.array([tangent[1], -tangent[0]]) / length

        if u<0.5:
            normal*=-1

        x, y = normal*dist+np.array(point)

        return x, y

    def plot(self, ax=None):
        points = np.array( [self.getPoint(t) for t in np.linspace(0,1,64)] )
        ax.plot(points[:,0], points[:,1])


import cv2
def pathWarp(src, sourcePath, targetPath):
    """warp image from source to target with path coordinates"""
    # create maps
    height, width, channels = src.shape
    mapx = np.zeros( (height, width), dtype=np.float32 )
    mapy = np.zeros( (height, width), dtype=np.float32 )

    # fill stmap
    for i in range(height*width):
        x = i%width
        y = i//width

        u, v = targetPath.getuv(x, y)
        x1, y1 = sourcePath.getxy(u, v)

        mapx[y,x] = x1
        mapy[y,x] = y1

    # remap src image
    return cv2.remap(src, mapx.astype(np.float32), mapy.astype(np.float32), cv2.INTER_LINEAR)
