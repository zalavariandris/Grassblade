from glumpy import app, gloo, gl, glm
import numpy as np
import cv2
	
import baseline as bl

# load image
img = cv2.imread("stinkbug.png")

window = app.Window(width=1200, height=950, color=(1,1,1,1))

@window.event
def on_resize(width, height):
	def orthographic(left, right, bottom, top):
		w = right-left
		h = top-bottom

		return np.linalg.inv(np.array([
			[w/2,0,0,0],
			[0,-h/2,0,0],
			[0,0,1,0],
			[w/2+bottom,h/2+left,0,1]
		]))

	margin = 100
	projection = orthographic(-margin,width-margin, -margin, height-margin)
	
	image.program['projection'] = projection
	pointsEditor.program['projection'] = projection


""" axis """
from glumpy.graphics.text import FontManager
from glumpy.graphics.collections import GlyphCollection
text = "The quick brown fox jumps over the lazy dog"
labels = GlyphCollection('agg')
x,y,z = 2,window.height,0
for i in range(6,54,2):
    font = FontManager.get("OpenSans-Regular.ttf", size=i, mode='agg')
    y -= i*1.1
    labels.append(text, font, origin = (x,y,z), anchor_x="left")

image = bl.Image()

pointsEditor = bl.PointEditor2D()
pointsEditor.points = np.array([
	(0.1,0.1),(0.11,0.11),
	(0.1,0.9),(0.11,0.91),
	(0.9,0.9),(0.91,0.91),
	(0.9,0.1),(0.91,0.11),
	(0.5,0.5),(0.51,0.1)
])*(img.shape[1], img.shape[0])
window.attach(pointsEditor)

arrows = bl.Arrows()
warper = bl.Warper()

@window.event
def on_draw(dt):
	""" Warp image """
	# prepare warp points
	sourcePoints = pointsEditor.points[0::2].copy()
	targetPoints = pointsEditor.points[1::2].copy()
	out_img = warper.warp(sourcePoints, targetPoints, img)

	""" display image """
	image.image = out_img

	""" draw stuff """
	window.clear( (0.95, 0.95, 0.95, 1) )
	image.draw()
	arrows.vertices['position'] = pointsEditor.points
	arrows.draw()
	pointsEditor.draw()
	labels.draw()
	

@window.event
def on_init():
	pass
	# gl.glEnable(gl.GL_DEPTH_TEST)

app.run()