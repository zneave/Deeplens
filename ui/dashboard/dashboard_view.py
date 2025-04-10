from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, QFileDialog, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from .tree_view import LayerTree
from .graph_view import GraphView
from .details_panel import DetailsPanel
from core.model_loader import load_pytorch_model, ModelInfo, get_module_info
import torchvision.models as models
import torch.nn as nn

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # 🔘 Control Bar
        control_bar = QHBoxLayout()
        self.load_btn = QPushButton("Load Model")
        self.load_btn.clicked.connect(self.load_model_from_file)

        self.demo_selector = QComboBox()
        self.demo_selector.addItem("Choose Demo Model")
        self.demo_selector.addItems(["ResNet18", "VGG16", "AlexNet"])
        self.demo_selector.currentIndexChanged.connect(self.load_demo_model)

        control_bar.addWidget(self.load_btn)
        control_bar.addWidget(self.demo_selector)
        control_bar.addStretch()

        # 🧩 Core UI Panels
        self.tree = LayerTree()
        self.graph = GraphView()
        self.details = DetailsPanel()
        self.graph.set_details_panel(self.details)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.graph)
        splitter.addWidget(self.details)
        splitter.setSizes([300, 600, 300])

        layout.addLayout(control_bar)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def load_model_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Model", "", "Model Files (*.pt *.pth)"
        )
        if file_path:
            try:
                model_info = load_pytorch_model(file_path)
                self.tree.populate(model_info.layers)
                self.graph.render_layers(model_info.layers)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))

    def load_demo_model(self, index):
        if index == 0:
            return  # Default: no selection

        demo_models = {
            1: models.resnet18,
            2: models.vgg16,
            3: models.alexnet
        }

        model_fn = demo_models.get(index)
        if model_fn:
            model: nn.Module = model_fn(weights=None)
            layers = []
            for name, module in model.named_modules():
                if name == "":
                    continue
                layers.append(get_module_info(name, module))
            model_info = ModelInfo(model.__class__.__name__, layers)
            self.tree.populate(model_info.layers)
            self.graph.render_layers(model_info.layers)

