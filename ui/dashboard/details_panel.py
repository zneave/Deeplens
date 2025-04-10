from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

class DetailsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.type_label = QLabel("Type: ")
        self.shape_label = QLabel("Shape: ")
        self.activation_label = QLabel("Activation: ")
        self.param_label = QLabel("Params: ")

        group = QGroupBox("Layer Details")
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.type_label)
        group_layout.addWidget(self.shape_label)
        group_layout.addWidget(self.activation_label)
        group_layout.addWidget(self.param_label)
        group.setLayout(group_layout)

        layout.addWidget(group)
        layout.addStretch()
        self.setLayout(layout)

    def update_details(self, layer):
        self.type_label.setText(f"Type: {layer['type']}")
        self.shape_label.setText(f"Shape: {layer.get('shape', 'N/A')}")
        self.activation_label.setText("Activation: (TBD)")  # Could be enhanced
        self.param_label.setText(f"Params: {layer['params']}")
