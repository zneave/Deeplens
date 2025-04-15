from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QLabel, QComboBox, QFileDialog
from ui.dashboard.tree_view import TreeView
from ui.dashboard.graph_view import GraphView
from ui.dashboard.details_panel import DetailsPanel
from core.model_loader import load_pytorch_model
from PyQt5.QtCore import QSize

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()

        self.tree = TreeView()
        layout.addWidget(QLabel("Model Layers"), 0, 0)
        layout.addWidget(self.tree, 1, 0)

        self.graph = GraphView()
        layout.addWidget(QLabel("Architecture Flow"), 0, 1)
        layout.addWidget(self.graph, 1, 1, 4, 1)

        self.details = DetailsPanel()
        layout.addWidget(QLabel("Layer Details"), 0, 2)
        layout.addWidget(self.details, 1, 2)

        self.model_summary_label = QLabel("Model Summary: Loading...")
        layout.addWidget(self.model_summary_label, 2, 2)

        self.model_selector = QComboBox()
        self.model_selector.addItem("Select example model...")
        self.model_selector.addItem("ResNet18")
        self.model_selector.addItem("VGG16")
        self.model_selector.currentIndexChanged.connect(self.handle_model_selection)

        self.upload_btn = QPushButton("Upload Custom Model (.pt)")
        self.upload_btn.clicked.connect(self.upload_model)

        layout.addWidget(self.model_selector, 3, 2)
        layout.addWidget(self.upload_btn, 4, 2)

        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 2)

        layout.setColumnStretch(2, 1)

        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(15)

        self.setLayout(layout)

    def update_model_summary(self, model_info):
        total_params = sum(layer['params'] for layer in model_info.layers)
        num_layers = len(model_info.layers)
        self.model_summary_label.setText(f"Total Layers: {num_layers}\nTotal Params: {total_params:,}\n")

    def handle_model_selection(self, index):
        if index == 1:
            from torchvision.models import resnet18
            model = resnet18(weights=None)
            model_info = load_pytorch_model(model)
            self.tree.populate(model_info.layers)
            self.graph.render_layers(model_info.layers, expanded_groups=self.graph.expanded_groups)
            self.update_model_summary(model_info)

        elif index == 2:
            from torchvision.models import vgg16
            model = vgg16(weights=None)
            model_info = load_pytorch_model(model)
            self.tree.populate(model_info.layers)
            self.graph.render_layers(model_info.layers, expanded_groups=self.graph.expanded_groups)
            self.update_model_summary(model_info)

    def upload_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select .pt model", "", "PyTorch Model (*.pt)")
        if path:
            model_info = load_pytorch_model(path)
            self.tree.populate(model_info.layers)
            self.graph.render_layers(model_info.layers, expanded_groups=self.graph.expanded_groups)
