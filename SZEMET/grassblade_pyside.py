from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import numpy as np
import math
app = QApplication.instance() or QApplication()


import cv2
import numpy as np
class Warper:
    def __init__(self):
        self.tps=cv2.createThinPlateSplineShapeTransformer()

    def __call__(self, sourcePoints, targetPoints, img):
        print("warp")
        """ reference: https://qiita.com/SousukeShimoyama/items/2bf8defb2d057bb8b742"""
        """ warp image """
        # prepare source and target points
        sshape = sourcePoints.reshape (1, -1, 2)
        tshape = targetPoints.reshape (1, -1, 2)
        matches = []
        for i in range(sshape.shape[1]):
            matches.append (cv2.DMatch (i, i, 0))

        self.tps.estimateTransformation(tshape.copy(), sshape.copy(), matches)


        return self.tps.warpImage(img)


class PointEditor2D(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMouseTracking(True)
        nrOfPoints = 100
        self.points = np.zeros((0,2))#np.random.uniform(0,(self.width(), self.height()), (nrOfPoints,2))
        
        # interactivity
        self.hovered=-1
        self.selection = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen);
        for i in range(len(self.points)):
            point = self.points[i]
            if self.hovered==i or i in self.selection:
                painter.setBrush(Qt.green)
            else:
                painter.setBrush(Qt.black)
            painter.drawEllipse(point[0]-5,point[1]-5, 10, 10)
        
    def mouseMoveEvent(self, event):
        print("mousemove", event.pos(), end="\r")
        x1 = event.x() # map mouse coords to paint coords if necessary
        y1 = event.y()
        
        if event.buttons() & Qt.LeftButton:
            # drag selected points
            delta = event.pos() - self.lastPoint
            delta = np.array([delta.x(), delta.y()])
            for i in self.selection:
                self.points[i]+=delta
            self.update()

        else:
            # update hovered points
            hitIndex = self.raycast(x1, y1)
            if hitIndex!=self.hovered:
                if self.hovered>=0:
                    pass #leave

                if hitIndex>=0:
                    pass #enter

                self.hovered=hitIndex

                self.update()
                                    
        # keep last mouse pos to calculate mouse movement
        self.lastPoint = event.pos()
    
    def raycast(self, x, y):
        # x,y and points are in the same space.
        for i in range(len(self.points)):
            point = self.points[i]
            v = self.points[i] - np.array([x,y])
            distance = math.sqrt(np.dot(v,v))
            if distance<10:
                return i
        return -1
    
    def mousePressEvent(self, event):
        x1 = event.x() # map mouse coords to paint coords if necessary
        y1 = event.y()
        hitIndex = self.raycast(x1, y1)
        
        if event.modifiers() == Qt.NoModifier:
            # update selection on mouse press
            if hitIndex>=0:
                self.selection = [hitIndex]
            else:
                self.selection = []
                
        if event.modifiers() == Qt.ControlModifier:
            # add or delete point on mousepress
            if hitIndex>=0:
                # delete point
                self.points = np.delete(self.points, hitIndex, axis=0)
            else:
                # add new point
                newPoint = np.array([x1, y1])
                self.points = np.append(self.points, [newPoint], axis=0)
                self.selection = [self.points.shape[0]-1]
        self.update()
        self.lastPoint = event.pos()
        
    def sizeHint(self):
        return QSize(500, 500)
    
class Arrows(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawLine(0,0,100,100)
        
    def sizeHint(self):
        return QSize(500, 500)

def run():
    window = QWidget()
    window.resize(500, 500)
    pointeditor = PointEditor2D(parent=window)
    try:
        pointeditor.points = np.load('points.npy') # load
    except FileNotFoundError:
        pass

    # window.show()
    window.show()
    app.exec_()
    np.save('points.npy', pointeditor.points) # save