from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import numpy as np
from OpenGL.GL import *

import cv2
from viewer2D import Viewer2D
from patheditor import PathEditorItem
from inspector import InspectorView, HasTraitsInspectorView
from outliner import OutlinerView

from traitlets import HasTraits, Int, Float, Bool, Unicode
from traittypes import Array

from scene import Scene
class BezierNode(HasTraits):
    points = Array()
    inTangents = Array()
    outTangents = Array()


class BezierNodeEditorItem(QGraphicsPathItem):
    def __init__(self, target):
        super().__init__()
        self.target = None
        self.setTarget(target)
        self._ctrlPoints = []
        pen = self.pen()
        pen.setWidth(3)
        pen.setColor(Qt.cyan)
        self.setPen(pen)

    def setTarget(self, target):
        if self.target is not None:
            self.target.unobserve(self.handleChange, ["points", "inTangents", "outTangents"])
        if target is not None:
            target.observe(self.handleChange, ["points", "inTangents", "outTangents"])

        # create path from points
        print("points:", target.points)
        print("shape:", target.points.shape)

        path = self.pathFromPoints(target.points, target.inTangents, target.outTangents)
        self.setPath(path)
        self.target = target

    @staticmethod
    def pathFromPoints(points, inTangents, outTangents):
        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for i in range(points.shape[0]-1):
            outTangent = outTangents[i]
            inTangent = inTangents[i+1]
            endPoint = points[i+1]
            path.cubicTo(outTangent[0], outTangent[1], inTangent[0], inTangent[1], endPoint[0], endPoint[1])

        return path

    def handleChange(self, change):
        # update path
        path = self.pathFromPoints(self.target.points, self.target.inTangents, self.target.outTangents)
        self.setPath(path)

        # patch control points
        print("handle change")
        for i, ctrlPoint in enumerate(self._ctrlPoints):
            element = self.path().elementAt(i)
            ctrlPoint.setPos(element.x, element.y)
            # print(i, ctrlPoint)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if self.isSelected():
                for i in range(self.path().elementCount()):
                    element = self.path().elementAt(i)
                    print("element:", end=" ")
                    if element.isMoveTo():
                        print("moveTo")
                    elif element.isLineTo():
                        print("lineTo")
                    elif element.isCurveTo():
                        print("curveTo")
                    elif element.type is QPainterPath.ElementType.CurveToDataElement:
                        print("CurveToDataElement")
                    else:
                        print(element.type)

                    print("create ctrlPoint")
                    ctrlPoint = QGraphicsRectItem(-5,-5,10,10)
                    ctrlPoint.setParentItem(self)
                    ctrlPoint.setPos(element.x, element.y)
                    ctrlPoint.installSceneEventFilter(self)
                    
                    self._ctrlPoints.append(ctrlPoint)

        return super().itemChange(change, value)

    def sceneEventFilter(self, watched, event):
        if event.type() == QEvent.GraphicsSceneMouseMove:
            print("Move!!!!!!!!!!!!!!!")
            watched.setPos(event.scenePos())
        return True
            

class RectNode(HasTraits):
    x = Float(25)
    y = Float(25)
    w = Float(50)
    h = Float(50)


class RectNodeEditorItem(QGraphicsRectItem):
    def __init__(self, target):
        super().__init__(0,0,99,99)
        self.target = target

        def on_change(change):
            print("change", change)
            self.setRect(self.target.x, self.target.y, self.target.w, self.target.h)
        self.setRect(self.target.x, self.target.y, self.target.w, self.target.h)
        self.target.observe(on_change)


class ReadNode(HasTraits):
    file = Unicode()
    frame = Int()
    play = Bool()
    

class ReadNodeEditorItem(QGraphicsPixmapItem):
    def __init__(self, target):
        super().__init__()
        self.target=target
        self.setFlags(QGraphicsItem.ItemIsSelectable)

        # capture video
        self.cap = cv2.VideoCapture("./footage/IMG_9148.MOV")

        def on_frame_changed(change):
            self.showFrame(change['new'])

        self.target.observe(on_frame_changed, ['frame'])
        self.showFrame(target.frame)

    def getCurrentFrame(self):
        # from opencv documentation: 
        # 0-based index of the frame to be decoded/captured next.
        # so it get the current frame, need to subtract 1
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1

    def getImageAtFrame(self, frame):
        if frame == self.getCurrentFrame()+1:
            ret, img = self.cap.read()
            return img
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            ret, img = self.cap.read()
            return img

    def showFrame(self, frame):
        print("show frame", frame)
        if self.getCurrentFrame() == frame:
            return

        else:
            img = self.getImageAtFrame(frame)
            height, width, channels = img.shape
            qImg = QImage(img.data, width, height, 3*width, QImage.Format_RGB888).rgbSwapped()
            pix = QPixmap.fromImage(qImg)
            self.setPixmap(pix)



import time
class Editor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Editor")
        # Create the Outliner
        self.outliner = QListWidget()
        leftDock = QDockWidget("outliner")
        leftDock.setWidget(self.outliner)
        self.addDockWidget(Qt.LeftDockWidgetArea, leftDock)

        # Create the inspector
        self.inspector = QWidget()
        self.inspector.setLayout(QVBoxLayout())
        self.inspector.layout().setAlignment(Qt.AlignTop)
        rightDock = QDockWidget('inspector')
        rightDock.setWidget(self.inspector)
        self.addDockWidget(Qt.RightDockWidgetArea, rightDock)

        # Create the Viewer
        self.viewer = Viewer2D()
        self.setCentralWidget(self.viewer)

        """
        Create and bind model
        """
        self.scene = Scene()
        
        self.outlinerEditors = dict()
        self.viewerEditors = dict()
        self.inspectorEditors = dict()

        def on_items_changed():
            new_items = set( self.scene.items() )

            # update outliner items
            outliner_items = set( self.outlinerEditors.keys() )
            outliner_added = new_items-outliner_items
            outliner_removed = outliner_items-new_items

            for item in outliner_added:
                editorItem = self.createOutlinerEditor(item)
                editorItem.userData = item
                self.outliner.addItem(editorItem)
                self.outlinerEditors[item] = editorItem
            
            for item in outliner_removed:
                editorItem = self.outlinerEditors.pop(item)
                row = self.outliner.row(editorItem)
                self.outliner.takeItem(row)

            # update viewer items
            viewer_items = set( self.viewerEditors.keys() )
            viewer_add = new_items-viewer_items
            viewer_remove = viewer_items-new_items

            for item in viewer_add:
                editorItem = self.createViewerEditor(item)
                self.viewer.scene.addItem(editorItem)
                self.viewerEditors[item] = editorItem

            for item in viewer_remove:
                editorItem = self.viewerEditors.pop(item)
                self.viewer.scene.removeItem(editorItem)

        self.scene.itemsChanged.connect(on_items_changed)
        
        def on_selection_changed():
            """
            sync widgets selection
            """
            
            """update outliner selection"""
            outliner_selection = self.outliner.selectedItems()
            new_selection = [self.outlinerEditors[item] for item in self.scene.selection()]

            self.outliner.blockSignals(True)
            for sel in outliner_selection:
                self.outliner.setItemSelected(sel, False)

            for sel in new_selection:
                self.outliner.setItemSelected(sel, True)
            self.outliner.blockSignals(False)
            
            """update viewer selection"""
            viewer_selection = self.viewer.scene.selectedItems()
            new_selection = [self.viewerEditors[item] for item in self.scene.selection()]
            
            self.viewer.scene.blockSignals(True)
            for sel in viewer_selection:
                sel.setSelected(False)

            for sel in new_selection:
                sel.setSelected(True)
            self.viewer.scene.blockSignals(False)

            """update inspector based on selection"""
            # clear inspector
            while self.inspector.layout().count()>0:
                child = self.inspector.layout().takeAt(0)
                child.widget().setTarget(None)
                child.widget().deleteLater()

            selection = self.scene.selection()
            if len(selection)>0:
                editorWidget = self.createInspectorEditor(selection[0])
                editorWidget.setTarget(selection[0])
                self.inspector.layout().addWidget(editorWidget)

        self.scene.selectionChanged.connect(on_selection_changed)

        def on_outliner_selection_changed():
            selection = [item.userData for item in self.outliner.selectedItems()]
            self.scene.setSelection(selection)
        self.outliner.itemSelectionChanged.connect(on_outliner_selection_changed)

        def on_viewer_selection_changed():
            selection = [item.userData for item in self.viewer.scene.selectedItems()]
            self.scene.setSelection(selection)
        self.viewer.scene.selectionChanged.connect(on_viewer_selection_changed)

    def setTargets(self, targets):
        self.scene.setItems(targets)

    def targets(self):
        return self.scene.items()

    def setSelection(self, selection):
        self.scene.setSelection(selection)

    def selection(self):
        return self.scene.selection()

    def createOutlinerEditor(self, target):
        text = target.__class__.__name__
        return QListWidgetItem(text)

    def createViewerEditor(self, target):
        if isinstance(target, RectNode):
            editorItem = RectNodeEditorItem(target)
        elif isinstance(target, ReadNode):
            editorItem = ReadNodeEditorItem(target)

        elif isinstance(target, BezierNode):
            editorItem = BezierNodeEditorItem(target)

        editorItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
        editorItem.userData = target
        return editorItem

    def createInspectorEditor(self, target):
        if isinstance(target, HasTraits):
            itemInspector = HasTraitsInspectorView()
            return itemInspector
        else:
            raise NotImplementedError

class EditorDelegate():
    def createEditor(self, target):
        pass


if __name__=="__main__":
    # create View
    app = QApplication.instance() or QApplication()
    editor = Editor()
    readNode = ReadNode()
    rectNode = RectNode()
    bezierNode = BezierNode()
    bezierNode.points = np.array([
        (1000, 0), 
        (1000, 1000)])
    bezierNode.inTangents = np.random.uniform(0,500, (2,2))
    bezierNode.outTangents = np.random.uniform(0,500, (2,2))
    editor.setTargets([rectNode, bezierNode])
    editor.show()
    timer = QTimer()
    def animate():
        print("animate")
        bezierNode.points = np.random.uniform(0, 1000, (2,2))
    timer.timeout.connect(animate)
    timer.start(1000/1)
    app.exec_()