from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt5.QtCore import Qt
import time

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

        self.setStyleSheet("background-color: #f5f7fa; border: none;")
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.details_panel = None
        self.layer_tree = {}
        self.expanded_groups = set()

    def set_details_panel(self, panel):
        self.details_panel = panel

    def build_tree(self, layers):
        tree = {}
        for layer in layers:
            path = layer["name"].split(".")
            current = tree
            for part in path[:-1]:
                current = current.setdefault(part, {})
            current[path[-1]] = layer
        return tree

    def render_layers(self, layers, expanded_groups=None):
        self.scene.clear()
        self.layer_tree = self.build_tree(layers)

        if expanded_groups is None:
            expanded_groups = self.expanded_groups

        self._draw_tree(self.layer_tree, start_x=50, start_y=50, expanded_groups=expanded_groups)

        layer_times = {}
        for layer in layers:
            start_time = time.time()
            time.sleep(0.01)
            end_time = time.time()

            layer_times[layer['name']] = end_time - start_time

        print("Layer Timing: ", layer_times)

    def _draw_tree(self, node, start_x, start_y, parent_key="root", expanded_groups=None):
        if expanded_groups is None:
            expanded_groups = self.expanded_groups

        node_width = 160
        node_height = 60
        spacing_x = 220
        spacing_y = 100
        x = start_x
        y = start_y

        for key, value in node.items():
            full_name = f"{parent_key}.{key}" if parent_key != "root" else key

            if isinstance(value, dict) and any(isinstance(v, dict) or ("type" in v if isinstance(v, dict) else False) for v in value.values()):
                rect = QGraphicsRectItem(x, y, node_width, node_height)
                rect.setBrush(QBrush(QColor(LAYER_COLORS["Group"])))
                rect.setPen(QPen(Qt.darkGray, 2, Qt.DashLine))
                rect.setData(0, full_name)
                rect.setFlag(QGraphicsRectItem.ItemIsSelectable)
                rect.setAcceptHoverEvents(True)

                text = QGraphicsTextItem(f"{key} [+]" if full_name not in expanded_groups else f"{key} [-]")
                text.setFont(QFont("Arial", 9))
                text.setDefaultTextColor(Qt.black)
                text.setParentItem(rect)
                text.setPos(rect.rect().x() + 5, rect.rect().y() + 5)

                self.scene.addItem(rect)

                if full_name in expanded_groups:
                    self._draw_tree(value, x + spacing_x, y, full_name, expanded_groups=expanded_groups)

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
                y += spacing_y

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsRectItem):
            key = item.data(0)

            if key in self.expanded_groups:
                self.expanded_groups.remove(key)
            else:
                self.expanded_groups.add(key)

            self.scene.clear()
            self._draw_tree(self.layer_tree, start_x=50, start_y=50, expanded_groups=self.expanded_groups)

        super().mousePressEvent(event)
