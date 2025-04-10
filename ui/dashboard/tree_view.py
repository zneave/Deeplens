from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

class LayerTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Model Layers")

    def populate(self, layers):
        self.clear()
        root = QTreeWidgetItem(self, ["Root"])
        for layer in layers:
            name = f"{layer['name']} ({layer['type']})"
            item = QTreeWidgetItem(root, [name])
            shape = str(layer['shape']) if layer['shape'] else "N/A"
            item.setToolTip(0, f"Shape: {shape} | Params: {layer['params']}")
        self.expandAll()
