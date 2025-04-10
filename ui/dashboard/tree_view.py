from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

class TreeView(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)

    def populate(self, layers):
        self.clear()
        for layer in layers:
            name_parts = layer["name"].split(".")
            self._add_layer_to_tree(name_parts, layer)

    def _add_layer_to_tree(self, path_parts, layer, parent=None):
        if not path_parts:
            return

        existing = None
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.text(0) == path_parts[0]:
                existing = item
                break

        if parent:
            children = [parent.child(i).text(0) for i in range(parent.childCount())]
            if path_parts[0] in children:
                for i in range(parent.childCount()):
                    if parent.child(i).text(0) == path_parts[0]:
                        existing = parent.child(i)
                        break

        item = existing if existing else QTreeWidgetItem([path_parts[0]])

        if parent and not existing:
            parent.addChild(item)
        elif not parent and not existing:
            self.addTopLevelItem(item)

        if len(path_parts) > 1:
            self._add_layer_to_tree(path_parts[1:], layer, item)
