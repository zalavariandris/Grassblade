from glumpy import app, gloo, gl, glm
import numpy as np
import cv2

class Image:
	def __init__(self):
		# create vertex buffer
		dtype = [("position", np.float32, 2),  # x,y
				 ("color",    np.float32, 3),  # r,g,b
				 ("uv",    	  np.float32, 2)]  # s,t

		V = np.zeros(4, dtype)
		V["position"] = [[ 1, 1], [-1, 1], [ 1,-1], [-1,-1]]
		V['position']*=0.9
		V["uv"] = [[ 1, 1], [0, 1], [ 1,0], [0,0]]
		V["color"] = np.ones( (4,3) )
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
		attribute vec2 uv;
		attribute vec3 color;
		varying vec3 vColor;
		varying vec2 vUv;
		void main()
		{
			vUv = vec2(uv.s, uv.t);
			vColor = color;
			gl_PointSize = 10.0;
			gl_Position = projection * view * model * vec4(position, 0.0,1.0);
		} """

		fragment = """
		varying vec3 vColor;
		varying vec2 vUv;
		uniform sampler2D texture;
		void main()
		{
			vec4 tex = texture2D(texture, vUv);
			gl_FragColor = vec4(vColor.rgb*tex.rgb, 1.0);
		} """
		self.program = gloo.Program(vertex, fragment)
		self.program.bind(self.vertices)
		self.program['model'] = np.eye(4, dtype=np.float32)
		self.program['view'] = np.eye(4, dtype=np.float32)
		# self.program['projection'] = np.eye(4, dtype=np.float32)

		# self.model = np.eye(4, dtype=np.float32)

	def draw(self):
		self.program.draw(gl.GL_TRIANGLE_STRIP)
		# self.program.draw(gl.GL_POINTS)

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, img):
		self.program['texture'] = img
		self.program['position'] = [[ img.shape[1], img.shape[0]], [0, img.shape[0]], [ img.shape[1],0], [0,0]]
	

