from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QComboBox, QFileDialog
from ui.dashboard.tree_view import TreeView
from ui.dashboard.graph_view import GraphView
from ui.dashboard.details_panel import DetailsPanel
from core.model_loader import load_pytorch_model

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        center_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.tree = TreeView()
        left_layout.addWidget(QLabel("📁 Model Layers"))
        left_layout.addWidget(self.tree)

        self.graph = GraphView()
        center_layout.addWidget(QLabel("📊 Architecture Flow"))
        center_layout.addWidget(self.graph)

        self.details = DetailsPanel()
        right_layout.addWidget(QLabel("🧠 Layer Details"))
        right_layout.addWidget(self.details)

        self.model_summary_label = QLabel("Model Summary: Loading...")
        right_layout.addWidget(self.model_summary_label)

        self.graph.set_details_panel(self.details)

        self.model_selector = QComboBox()
        self.model_selector.addItem("Select example model...")
        self.model_selector.addItem("ResNet18")
        self.model_selector.addItem("VGG16")
        self.model_selector.currentIndexChanged.connect(self.handle_model_selection)

        self.upload_btn = QPushButton("Upload Custom Model (.pt)")
        self.upload_btn.clicked.connect(self.upload_model)

        center_layout.addWidget(self.model_selector)
        center_layout.addWidget(self.upload_btn)

        layout.addLayout(left_layout, 1)
        layout.addLayout(center_layout, 3)
        layout.addLayout(right_layout, 1)

        self.setLayout(layout)

    def update_model_summary(self, model_info):
        total_params = sum(layer['params'] for layer in model_info.layers)
        num_layers = len(model_info.layers)
        self.model_summary_label.setText(f"Total Layers: {num_layers}\nTotal Params: {total_params:,}\n")

    def handle_model_selection(self, index):
        if index == 1:  # ResNet18
            from torchvision.models import resnet18
            model = resnet18(weights=None)
            model_info = load_pytorch_model(model)
            self.tree.populate(model_info.layers)
            self.graph.render_layers(model_info.layers, expanded_groups=self.graph.expanded_groups)
            self.update_model_summary(model_info)

        elif index == 2:  # VGG16
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
