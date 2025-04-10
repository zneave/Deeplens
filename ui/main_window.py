from PyQt5.QtWidgets import QMainWindow, QWidget, QStackedLayout, QStatusBar, QAction, QFileDialog
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
from .landing.landing_page import LandingPage
from .dashboard.dashboard_view import DashboardView
from core.model_loader import load_pytorch_model

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neural Network Visualizer")
        self.resize(1200, 800)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.init_ui()
        self.create_menu()

    def init_ui(self):
        # Set up the central stacked layout
        self.central = QWidget()
        self.layout = QStackedLayout()
        self.central.setLayout(self.layout)

        # Pages
        self.landing = LandingPage()
        self.dashboard = DashboardView()

        self.layout.addWidget(self.landing)
        self.layout.addWidget(self.dashboard)
        self.setCentralWidget(self.central)

        # Connect landing button
        self.landing.continue_clicked.connect(self.show_dashboard)

    def show_dashboard(self):
        # Smooth transition animation
        old_geometry = self.central.geometry()

        self.dashboard.setGeometry(
            old_geometry.x() + old_geometry.width(), old_geometry.y(),
            old_geometry.width(), old_geometry.height()
        )
        self.layout.setCurrentWidget(self.dashboard)

        self.animation = QPropertyAnimation(self.dashboard, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.dashboard.geometry())
        self.animation.setEndValue(old_geometry)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        load_action = QAction("Load Model", self)
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def load_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Model", "", "Model Files (*.pt *.pth *.h5 *.onnx)"
        )
        if path:
            try:
                if path.endswith((".pt", ".pth")):
                    model_info = load_pytorch_model(path)
                    self.dashboard.tree.populate(model_info.layers)
                    self.status_bar.showMessage(f"Loaded {model_info.name} with {len(model_info.layers)} layers")
                else:
                    self.status_bar.showMessage("Only PyTorch supported right now")
            except Exception as e:
                self.status_bar.showMessage(str(e))

