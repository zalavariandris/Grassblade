from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class OutlinerWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class OutlinerView(OutlinerWidget):
    def __init__(self, target, selection=[], parent=None):
        super().__init__(parent = parent)
        self.setTarget(target)

    def setTarget(self, target):
        assert isinstance(target, list) or target is None
        self.target = target

        if self.target is None:
            # clear all items
            while self.topLevelItemCount()>0:
                self.takeTopLevelItem(0)
        
        else:
            # populate outliner
            for node in target:
                treeItem = QTreeWidgetItem([node.__class__.__name__])
                treeItem.userData = node
                self.addTopLevelItem(treeItem)
