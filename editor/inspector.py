from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from traitlets import HasTraits, Int, Float, Bool, Unicode

class InspectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setLayout(QFormLayout())


class InspectorView(InspectorWidget):
    def __init__(self, target, parent=None):
        super().__init__(parent=parent)
        self.target = target

    def createEditorWidget(self, target):
        if isinstance(target, HasTraits):
            return HasTraitsInspectorView(target)
        raise NotImplementedError

    def setTarget(self, target):
        self.target = target
        self.layout().addWidget(self.createEditorWidget(target))

import math
class HasTraitsInspectorView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._handlers = dict()
        self.target=None

    def setTarget(self, target):
        assert target is None or isinstance(target, HasTraits)

        if self.target is not None:
            for name, handler in self._handlers.items():
                self.target.unobserve(handler, [name])

        if target is not None:
            self.setLayout(QFormLayout())
        
            for name, traitType in target.traits().items():
                if type(traitType)==Float:
                    spinbox = QDoubleSpinBox()
                    spinbox.setRange(-99999, 99999)
                    spinbox.setValue(getattr(target, name))
                    self.layout().addRow(name, spinbox)

                    def syncmodel(value, spinbox=spinbox, name=name):
                        print("syncmodel")
                        if getattr(target, name) != value:
                            setattr(target, name, value)
                    
                    spinbox.valueChanged.connect(syncmodel)
                    

                    # Sync view to model
                    def syncview(change, spinbox=spinbox):
                        if spinbox.value() != change['new']:
                            spinbox.setValue ( change['new'] )
                    self._handlers[name] = syncview
                    target.observe(syncview, [name])

                elif type(traitType)==Int:
                    spinbox = QSpinBox()
                    spinbox.setRange(-99999, 99999)
                    spinbox.setValue(getattr(target, name))
                    self.layout().addRow(name, spinbox)

                    def syncmodel(value, spinbox=spinbox, name=name):
                        if getattr(target, name) != value:
                            setattr(target, name, value)
                    spinbox.valueChanged.connect(syncmodel)

                    # Sync view to model
                    def syncview(change, spinbox=spinbox):
                        if spinbox.value() != change['new']:
                            spinbox.setValue ( change['new'] )
                    self._handlers[name] = syncview
                    target.observe(syncview, [name])

                elif type(traitType) == Bool:
                    checkbox = QCheckBox()
                    checkbox.setChecked(getattr(target, name))
                    self.layout().addRow(name, checkbox)

                    def syncmodel(value, checkbox=checkbox, name=name):
                        if getattr(target, name) != value:
                            setattr(target, name, checkbox.isChecked())
                    checkbox.stateChanged.connect(syncmodel)

                    def syncview(change, checkbox=checkbox):
                        checkbox.setChecked(change['new'])
                    self._handlers[name] = syncview
                    target.observe(syncview, [name])

        self.target=target

    def __del__(self):
        self.setTarget(None)