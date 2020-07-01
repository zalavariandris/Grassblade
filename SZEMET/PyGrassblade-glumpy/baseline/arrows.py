from glumpy import app, gloo, gl, glm
import numpy as np
class Arrows():
	def __init__(self):
		initialPoints = np.random.uniform(-1,1, (10, 2))
		# create vertex buffer
		dtype = [("position", np.float32, 2),  # x,y
				 ("color",    np.float32, 3),  # r,g,b
				 ("uv",    	  np.float32, 2)]  # s,t

		n = initialPoints.shape[0]
		V = np.zeros(n, dtype)
		V["position"] = initialPoints
		V['position']*=0.9
		V["color"] = np.zeros( (n,3) )
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
			gl_Position = projection * view * model * vec4(position, 0.0, 1.0);
		} """

		fragment = """
		varying vec3 vColor;
		void main()
		{
			gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0);
		}"""
		self.program = gloo.Program(vertex, fragment)
		self.program.bind(self.vertices)
		self.program['model'] = np.eye(4, dtype=np.float32)
		self.program['view'] = np.eye(4, dtype=np.float32)
		self.program['projection'] = np.eye(4, dtype=np.float32)

	def draw(self):
		self.program.draw(gl.GL_LINES)
