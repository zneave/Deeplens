from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QMenu, QAction
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt

LAYER_COLORS = {
    "Conv2d": "#2d8cf0",
    "ReLU": "#00a896",
    "BatchNorm2d": "#f4a261",
    "MaxPool2d": "#e76f51",
    "Linear": "#9b5de5",
    "Flatten": "#f15bb5",
    "Dropout": "#ff6b6b",
    "Group": "#dcdcdc",
    "Default": "#999999"
}


class GraphView(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setRenderHint(QPainter.Antialiasing)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.details_panel = None

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setStyleSheet("background-color: #f5f7fa; border: none;")

        self.nodes = []
        self.layer_tree = {}
        self.expanded_groups = set()

    def set_details_panel(self, panel):
        self.details_panel = panel

    def wheelEvent(self, event):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(zoom_factor, zoom_factor)

    def clear(self):
        self.scene.clear()
        self.nodes = []

    def build_tree(self, layers):
        tree = {}
        for layer in layers:
            path = layer["name"].split(".")
            current = tree
            for part in path[:-1]:
                current = current.setdefault(part, {})
            current[path[-1]] = layer
        return tree

    def render_layers(self, layers):
        self.clear()
        self.layer_tree = self.build_tree(layers)
        self._draw_tree(self.layer_tree, start_x=50, start_y=50)

    def _draw_tree(self, node, start_x, start_y, parent_key="root", depth=0):
        node_width = 160
        node_height = 60
        spacing_x = 220
        spacing_y = 100
        x = start_x
        y = start_y

        for key, value in node.items():
            full_name = f"{parent_key}.{key}" if parent_key != "root" else key

            if isinstance(value, dict) and any(isinstance(v, dict) or (isinstance(v, dict) and "type" in v) for v in value.values()):
                # Draw group block
                rect = QGraphicsRectItem(x, y, node_width, node_height)
                rect.setBrush(QBrush(QColor(LAYER_COLORS["Group"])))
                rect.setPen(QPen(Qt.darkGray, 2, Qt.DashLine))
                rect.setData(0, full_name)
                rect.setFlag(QGraphicsRectItem.ItemIsSelectable)
                rect.setAcceptHoverEvents(True)

                text = QGraphicsTextItem(f"{key} [+]" if full_name not in self.expanded_groups else f"{key} [-]")
                text.setFont(QFont("Arial", 9))
                text.setDefaultTextColor(Qt.black)
                text.setParentItem(rect)
                text.setPos(rect.rect().x() + 5, rect.rect().y() + 5)

                self.scene.addItem(rect)
                self.nodes.append(rect)

                if full_name in self.expanded_groups:
                    self._draw_tree(value, x + spacing_x, y, full_name, depth + 1)

                y += spacing_y

            elif isinstance(value, dict) and "type" in value:
                layer = value
                color = LAYER_COLORS.get(layer["type"], LAYER_COLORS["Default"])
                rect = QGraphicsRectItem(x, y, node_width, node_height)
                rect.setBrush(QBrush(QColor(color)))
                rect.setPen(QPen(Qt.black, 1))
                rect.setData(0, full_name)
                rect.setToolTip(f"{layer['name']}\nShape: {layer.get('shape', 'N/A')}\nParams: {layer['params']}")

                text = QGraphicsTextItem(f"{layer['name'].split('.')[-1]}\n{layer['type']}")
                text.setFont(QFont("Arial", 9))
                text.setDefaultTextColor(Qt.white)
                text.setParentItem(rect)
                text.setPos(rect.rect().x() + 5, rect.rect().y() + 5)

                rect.setFlag(QGraphicsRectItem.ItemIsSelectable)
                rect.setAcceptHoverEvents(True)

                self.scene.addItem(rect)
                self.nodes.append(rect)

                y += spacing_y

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsRectItem):
            key = item.data(0)

            if key in self.expanded_groups:
                self.expanded_groups.remove(key)
            elif key and self._is_group(key):
                self.expanded_groups.add(key)
            else:
                layer = self._find_layer_by_name(self.layer_tree, key)
                if layer and self.details_panel:
                    self.details_panel.update_details(layer)

            self.clear()
            self._draw_tree(self.layer_tree, start_x=50, start_y=50)

        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsRectItem):
            key = item.data(0)
            if not key:
                return

            menu = QMenu(self)
            if self._is_group(key):
                if key in self.expanded_groups:
                    action = QAction("Collapse Group", self)
                    action.triggered.connect(lambda: self._collapse_and_refresh(key))
                else:
                    action = QAction("Expand Group", self)
                    action.triggered.connect(lambda: self._expand_and_refresh(key))
                menu.addAction(action)
            menu.exec_(event.globalPos())

    def _expand_and_refresh(self, key):
        self.expanded_groups.add(key)
        self.clear()
        self._draw_tree(self.layer_tree, start_x=50, start_y=50)

    def _collapse_and_refresh(self, key):
        self.expanded_groups.discard(key)
        self.clear()
        self._draw_tree(self.layer_tree, start_x=50, start_y=50)

    def _is_group(self, name):
        def find(node, parts):
            if not parts:
                return isinstance(node, dict)
            return find(node.get(parts[0], {}), parts[1:])
        return find(self.layer_tree, name.split("."))

    def _find_layer_by_name(self, node, target):
        for key, value in node.items():
            full_key = f"{key}"
            if isinstance(value, dict):
                result = self._find_layer_by_name(value, target)
                if result:
                    return result
            elif isinstance(value, dict) and value.get("name") == target:
                return value
        return None
