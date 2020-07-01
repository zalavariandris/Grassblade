import sys
from PySide2.QtWidgets import QApplication, QLabel, QOpenGLWidget



class Window(QOpenGLWidget):
	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.mouseTracking = True

	def paintEvent(self, paintEvent):
		painter = QPainter(self)
		
	def mouseMoveEvent(self, event):
		print(event)

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec_()



# class App:
# 	def __init__(self):
# 		self.qapp = QApplication(sys.argv)
# 		label = QLabel("Hello World!")
# 		label.show()

# 	def run(self):
# 		self.qapp.exec_()





# app = App()
# app.run()