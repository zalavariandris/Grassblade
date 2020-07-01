from glumpy import app, gloo, gl, glm
import numpy as np
import cv2

# -----------------------------------------------------------------------------
# Copyright (c) 2009-2016 Nicolas P. Rougier. All rights reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
from glumpy import app
from glumpy.log import log
from glumpy.graphics.text import FontManager
from glumpy.graphics.collections import GlyphCollection, PointCollection
from glumpy.transforms import Position, OrthographicProjection, Viewport, PanZoom

from baseline import Image

class Window(app.Window):
	def __init__(self):
		super().__init__()

	def on_draw(self, dt):
		print("draw")

window = Window()#app.Window(width=1200, height=800, color=(1,1,1,1))

class Image:
	def __init__(self, transform=None, viewport=None):
		self.program = gloo.Program(
			vertex="""
			#version 120
			attribute vec2 position;
			attribute vec2 uv;
			varying vec2 vUv;
			void main(){
				vUv = vec2(uv.s, uv.t);
				gl_PointSize = 10.0;
				gl_Position = <transform(position)>;
				<viewport.transform>;
			}
			""",
			fragment="""
			#version 120
			varying vec2 vUv;
			uniform sampler2D texture;
			void main(){
				<viewport.clipping>;
				vec4 tex = texture2D(texture, vUv);
				gl_FragColor = vec4(tex.rgb, 1);
			}
			""")

		dtype = [("position", np.float32, 2),  # x,y
		 ("color",    np.float32, 3),  # r,g,b
		 ("uv",    	  np.float32, 2)]  # s,t

		V = np.zeros(4, dtype)
		V["position"] = [[ 10, 10], [100, 10], [ 10,100], [100,100]]
		V["uv"] = [[ 0, 0], [1, 0], [ 0,1], [1,1]]

		self.vertices = V.view(gloo.VertexBuffer)
		self.program.bind(self.vertices)

		if transform is not None:
			self.program["transform"] = transform

		if viewport is not None:
			self.program["viewport"] = viewport

	def draw(self):
		self.program.draw(gl.GL_POINTS)
		self.program.draw(gl.GL_TRIANGLE_STRIP)

	@property
	def image(self):
		return self.program['texture']

	@image.setter
	def image(self, img):
		self.program['texture'] = img
		self.program['position'] = [[ img.shape[1], img.shape[0]], [0, img.shape[0]], [ img.shape[1],0], [0,0]]


# create window projection
projection = PanZoom(OrthographicProjection(Position()))
viewport = Viewport()
window.attach(projection)
window.attach(viewport)

# create labels
labels = GlyphCollection('agg', transform=projection, viewport=viewport)
font = FontManager.get("OpenSans-Regular.ttf", size=10, mode='agg')
for x in range(0, 1050, 50):
	text = "{}".format(x)
	labels.append(text, font, origin = (x,0,0), anchor_x="left", anchor_y="bottom")

for y in range(0, 1050, 50):
	text = "{}".format(y)
	labels.append(text, font, origin = (0,y,0), anchor_x="left", anchor_y="bottom")

# create image
image = Image(transform=projection, viewport=viewport)
img = cv2.imread("stinkbug.png")
image.image = img

# create points
points = PointCollection("agg", color="local", size="local", transform=projection, viewport=viewport)
points.append(np.random.uniform(0.0,500,(100,3)),
		  color = np.random.uniform(0,1,(100,4)),
		  size  = np.random.uniform(1,24,(100)))

help(points)
@window.event
def on_draw(dt):
	window.clear()
	image.draw()
	points.draw()
	labels.draw()

app.run()