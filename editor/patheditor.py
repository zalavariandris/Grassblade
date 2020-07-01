from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class CtrlPoint(QGraphicsEllipseItem):
    def __init__(self, x,y, onChange=None):
        radius = 30
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.onChange = onChange
        self.setPos(x, y)
        self.setBrush(QColor("darkorange"))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges , True)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        
        self.setAcceptHoverEvents(True)

    def itemChange(self, change, value):
        if self.onChange is not None and change is QGraphicsItem.ItemPositionHasChanged:
            self.onChange(self)

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        if option.state & QStyle.State_Selected:
            painter.setBrush(Qt.yellow)
        elif option.state & QStyle.State_MouseOver:
            painter.setBrush(Qt.yellow)
        else:
            painter.setBrush(Qt.black)

        painter.drawEllipse(-5,-5, 10, 10)

class PathEditorItem(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        print("init bezier editor")
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.ctrlPoints = []
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def onCtrlPointChanged(self, ctrlPoint):
        p = self.path()
        p.setElementPositionAt(ctrlPoint.idx, ctrlPoint.pos().x(), ctrlPoint.pos().y())
        self.setPath(p)

    def updateControlPoints(self):
        updateRange = range(min(self.path().elementCount(), len(self.ctrlPoints)))
        addRange = range(len(self.ctrlPoints), self.path().elementCount())
        removeRange = range(self.path().elementCount(), len(self.ctrlPoints))

        for i in updateRange:
            """update ctrl points"""

        for i in removeRange:
            """remove ctrl points"""

        for i in addRange:
            """add ctrl points"""
            element = self.path().elementAt(i)

            # print("add ctrl point", i, element.x, element.y)
            ctrlPoint = CtrlPoint(element.x, element.y, self.onCtrlPointChanged)
            # ctrlPoint = CtrlPoint(element.x, element.y)
            ctrlPoint.idx = i
            ctrlPoint.setParentItem(self)
            self.ctrlPoints.append(ctrlPoint)

            # ctrlPoint.installSceneEventFilter(self)

    def sceneEventFilter(self, watched, event):
        # if event.type()
        if event.type() == QEvent.GraphicsSceneMouseMove:
            print("move")
        return super().sceneEventFilter(watched, event)

    def setPath(self, path):
        super().setPath(path)
        

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSceneHasChanged:
            self.updateControlPoints()

        return super().itemChange(change, value)
        
    # def hoverMoveEvent(self, event):
    #     hitIndex = self.raycast(event.pos().x(), event.pos().y())

    #     # update hovred points
    #     if hitIndex!=self.hovered:
    #         if self.hovered>=0:
    #             pass #leave

    #         if hitIndex>=0:
    #             pass #enter

    #         self.hovered=hitIndex
    #         self.update()

    # def raycast(self, x, y):
    #     # x,y and points are in the same space.
    #     for i in range( self.path().elementCount() ):
    #         element = self.path().elementAt(i)
    #         v = np.array([element.x, element.y]) - np.array([x,y])
    #         distanceSq = np.dot(v,v)
    #         if distanceSq<10*10:
    #             return i
    #     return -1

    # def hoverLeaveEvent(self, event):
    #     print("hover leave event")

    # def paint(self, painter, option, widget):
    #     super().paint(painter, option, widget)
    #     # help(self.path())
    #     radius = 5
    #     for i in range( self.path().elementCount() ):
    #         element = self.path().elementAt(i)
    #         if i is self.hovered:
    #             painter.setBrush(Qt.green)
    #         else:
    #             painter.setBrush(Qt.white)
    #         painter.drawEllipse(element.x-radius, element.y-radius, radius*2, radius*2)
            # painter.drawPoint(element.x, element.y)

        # self.path().setElementPositionAt()

    # def mouseMoveEvent(self, event):
    #     print("mouse move event")