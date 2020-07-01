from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import numpy as np
import cv2
import math

from thinplatespline import ThinPlateSpline
from griddatawarp import GriddataWarp
from rbfwarp import RbfWarp

class Editor(QtWidgets.QOpenGLWidget):
	def __init__(self, image, points, parent=None):
		super().__init__(parent=parent)
		self.setMouseTracking(True)
		# nrOfPoints = 100
		# self.points = np.zeros((0,2))#np.random.uniform(0,(self.width(), self.height()), (nrOfPoints,2))
		
		# interactivity
		self.hovered=-1
		self.selection = []

		self.tps = ThinPlateSpline()
		self.griddata = GriddataWarp()
		self.rbf = RbfWarp()
		self.points = points
		self.image = image

	def paintGL(self):
		painter = QtGui.QPainter(self)
		self.painter = painter

		sourcePoints = self.points[0::2]
		targetPoints = self.points[1::2]
		# out_img = self.tps(self.image, sourcePoints, targetPoints)
		# out_img = self.griddata(self.image, sourcePoints[:targetPoints.shape[0]], targetPoints)
		out_img = self.rbf(self.image, sourcePoints[:targetPoints.shape[0]], targetPoints)
		# draw image
		self.drawImage(0,0, out_img)

		# draw points
		selectionMask = np.full(self.points.shape[0], False, dtype=bool)
		selectionMask[self.selection]=True
		if self.hovered>=0:
			selectionMask[self.hovered]=True
		painter.setPen(QtGui.QPen(QtGui.Qt.black, 2))
		painter.setBrush(QtGui.Qt.green)
		self.drawPoints(self.points[selectionMask==False])
		painter.setBrush(QtGui.Qt.white)
		self.drawPoints(self.points[selectionMask==True])
		# self.drawPoints(self.points[self.selection])

		# # draw points
		# painter.setPen(QtGui.QPen(QtGui.Qt.black, 2))
		# for i in range(len(self.points)):
		# 	point = self.points[i]
		# 	if self.hovered==i or i in self.selection:
		# 		painter.setBrush(QtGui.Qt.green)
		# 	else:
		# 		painter.setBrush(QtGui.Qt.white)
		# 	painter.drawEllipse(point[0]-5,point[1]-5, 10, 10)

		# draw arrows
		painter.setPen(QtGui.QPen(QtGui.Qt.white, 2))
		for src, dst in zip(self.points[0::2], self.points[1::2]):
			self.drawArrow(painter, src[0],src[1], dst[0],dst[1])
		self.painter = None

	def drawPoints(self, points):
		painter = self.painter
	
		for pos in points:
			painter.drawEllipse(pos[0]-5,pos[1]-5, 10, 10)

	def drawImage(self, x, y, image):
		# painter = self.painter
		painter = self.painter
		height, width, channels = image.shape
		qimg = QtGui.QImage(image.data, width, height, width * channels, QtGui.QImage.Format_RGB888)
		painter.drawImage(0,0,qimg)


	def drawArrow(self, painter, x, y, x1, y1, width=10):
		"""prepare"""
		position = (x, y)
		vector = (x1-x, y1-y)
		vectors = np.array([vector])  # All x's, then all y's
		norms = vectors/np.sqrt((vectors ** 2).sum(-1))[..., np.newaxis]
		normal = norms[0]
		tangent = (-normal[1], normal[0])

		"""draw"""
		# draw arrow body
		painter.drawLine(x,y,x1,y1)

		#draw arrow head
		painter.drawLine(
			x1, y1, 
			x1-normal[0]*width-tangent[0]*width, 
			y1-normal[1]*width-tangent[1]*width
		) #left side
		painter.drawLine(
			x1, y1, 
			x1-normal[0]*width+tangent[0]*width, 
			y1-normal[1]*width+tangent[1]*width
		) # right side


	def mouseMoveEvent(self, event):
		x1 = event.x() # map mouse coords to paint coords if necessary
		y1 = event.y()
		
		if event.buttons() & QtGui.Qt.LeftButton:
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
			v = point - np.array([x,y])
			distance = math.sqrt(np.dot(v,v))
			if distance<10:
				return i
		return -1
	
	def mousePressEvent(self, event):
		x1 = event.x() # map mouse coords to paint coords if necessary
		y1 = event.y()
		hitIndex = self.raycast(x1, y1)
		
		if event.modifiers() == QtGui.Qt.NoModifier:
			# update selection on mouse press
			if hitIndex>=0:
				self.selection = [hitIndex]
			else:
				self.selection = []
				
		if event.modifiers() == QtGui.Qt.ControlModifier:
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
		return QtCore.QSize(500, 500)

def run():
	import numpy as np
	try:
		points = np.load('points.npy') # load
	except FileNotFoundError:
		points = np.random.uniform(0, 256, (6, 2))
	img = cv2.imread("stinkbug_small.png")
	app = QtWidgets.QApplication.instance() or QtWidgets.QApplication()
	editor=Editor(image = img, points=points)
	editor.resize(1000, 800)
	editor.show()
	app.exec_()
	np.save('points.npy', editor.points) #save

if __name__ == "__main__":
	run()
	