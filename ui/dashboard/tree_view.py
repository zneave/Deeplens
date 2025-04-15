from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

class TreeView(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.item_cache = {}

    def populate(self, layers):
        self.clear()
        self.item_cache.clear()

        for layer in layers:
            self._add_layer_to_tree(layer["name"].split("."), layer)

    def _add_layer_to_tree(self, path_parts, layer, parent_key=""):
        current_key = f"{parent_key}.{path_parts[0]}" if parent_key else path_parts[0]

        if current_key in self.item_cache:
            item = self.item_cache[current_key]
        else:
            item = QTreeWidgetItem([path_parts[0]])
            if parent_key:
                parent_item = self.item_cache[parent_key]
                parent_item.addChild(item)
            else:
                self.addTopLevelItem(item)
            self.item_cache[current_key] = item

        if len(path_parts) > 1:
            self._add_layer_to_tree(path_parts[1:], layer, current_key)
        else:
            item.setData(0, Qt.UserRole, layer)
