from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class Scene(QObject):
    itemsChanged = Signal()
    selectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._items = []
        self._selection = []

    def items(self):
        return self._items

    def setItems(self, items):
        self._items = items
        self.itemsChanged.emit()

    def addItem(self, item):
        self._items.append(item)
        self.itemsChanged.emit()

    def removeItem(self, item):
        self._items.remove(item)
        self.itemsChanged.emit()

    def selection(self):
        return self._selection

    def setSelection(self, selection):
        if set(selection) !=set(self._selection):
            self._selection = selection
            self.selectionChanged.emit()
        
