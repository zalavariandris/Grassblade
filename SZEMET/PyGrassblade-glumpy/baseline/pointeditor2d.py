from glumpy import app, gloo, gl, glm
import numpy as np
import cv2
import math

class PointEditor2D(app.Viewport):
	def __init__(self, initialPoints=np.random.uniform(-1,1, (10, 2) )):
		super().__init__()
		# create vertex buffer
		dtype = [("position", np.float32, 2),  # x,y
				 ("color",    np.float32, 3),  # r,g,b
				 ("uv",    	  np.float32, 2)]  # s,t

		n = initialPoints.shape[0]
		V = np.zeros(n, dtype)
		V["position"] = initialPoints
		V['position']*=0.9
		V["color"] = np.full(3, (0.0, 1.0, 0.5))
		# V["color"] = np.random.uniform(0,1, (4,3))
		# V["color"][0::2] = (0,1,0)
		# V["color"][1::2] = (1,0,1)
		V = V.view(gloo.VertexBuffer)
		self.vertices = V
		# self.indices = np.array([0,1,2, 0,2,3,  0,3,4, 0,4,5,  0,5,6, 0,6,1,
			  # 1,6,7, 1,7,2,  7,4,3, 7,3,2,  4,7,6, 4,6,5], dtype=np.uint32)
		vertex = """
		uniform mat4   model;         // Model matrix
		uniform mat4   view;          // View matrix
		uniform mat4   projection;    // Projection matrix
		attribute vec2 position;      // Vertex position
		attribute vec3 color;
		varying vec3 vColor;
		void main()
		{
			vColor = color;
			gl_PointSize = 10.0;
			gl_Position = projection * view * model * vec4(position, 0.0,1.0);
		} """

		fragment = """
		varying vec3 vColor;
		void main()
		{
			gl_FragColor = vec4(vColor.rgb, 1.0);
		}"""
		self.program = gloo.Program(vertex, fragment)
		self.program.bind(self.vertices)
		self.program['model'] = np.eye(4, dtype=np.float32)
		self.program['view'] = np.eye(4, dtype=np.float32)
		self.program['projection'] = np.eye(4, dtype=np.float32)
		self.hovered = -1
		self.selected = -1
		self.originalColors = np.copy(self.vertices['color'])
		self.modifiers = 0;

	def raycast(self, x, y):
		positions = self.vertices['position']
		# positions = data.dot(transform_matrix.T)

		mouse = x/self.size[0]*2-1, (1-y/self.size[1])*2-1, 1, 1
		transform_matrix = self.program['projection'].reshape(4,4)
		mouse = np.array([mouse[0], mouse[1], 0, 1]).dot( np.linalg.inv(transform_matrix))
		x,y = mouse[0], mouse[1]

		for i in range( len(positions)):
			pos = positions[i]
			v = np.subtract( pos, [x, y])
			distance = math.sqrt( np.dot(v, v) )
			if( distance < 5 ):
				return i

		return -1

	def on_mouse_motion(self, x, y, dx, dy):
		hitIndex = self.raycast(x, y)
		if hitIndex!=self.hovered:
			if self.hovered>=0:
				"""leave hovered"""
				self.vertices['color'][self.hovered] = self.originalColors[self.hovered]

			if hitIndex>=0:
				"""enter hit index"""
				self.vertices['color'][hitIndex] = 1,0.5,0

			self.hovered = hitIndex

	def on_mouse_press(self, x, y, buttons):
		if self.modifiers==0:
			if self.hovered>=0:
				self.selected = self.hovered
			else:
				self.selected = -1
				print(buttons)
		elif self.modifiers==4:
			if self.hovered>=0:
				print("remove")
			else:
				print("add")

	def on_mouse_drag(self, x, y, dx, dy, buttons):
		if self.selected>=0:
			self.vertices['position'][self.selected] += dx,dy

	def on_key_press(self, key, modifiers):
		self.modifiers = modifiers

	def on_key_release(self, key, modifiers):
		self.modifiers = modifiers

	def draw(self):
		self.program.draw(gl.GL_POINTS)

	def append(self, point):
		pass

	@property
	def points(self):
		return self.vertices['position']

	@points.setter
	def points(self, values):
		self.vertices['position'] = values