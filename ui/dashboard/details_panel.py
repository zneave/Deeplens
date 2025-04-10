from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class DetailsPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.type_label = QLabel("Type: ")
        self.shape_label = QLabel("Shape: ")
        self.activation_label = QLabel("Activation: ")
        self.param_label = QLabel("Params: ")
        self.weight_stats_label = QLabel("Weight Stats: ")

        group = QGroupBox("Layer Details")
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.type_label)
        group_layout.addWidget(self.shape_label)
        group_layout.addWidget(self.activation_label)
        group_layout.addWidget(self.param_label)
        group_layout.addWidget(self.weight_stats_label)
        group.setLayout(group_layout)

        layout.addWidget(group)
        layout.addStretch()
        self.setLayout(layout)

    def update_details(self, layer):
        self.type_label.setText(f"Type: {layer.get('type', 'N/A')}")
        self.shape_label.setText(f"Shape: {layer.get('shape', 'N/A')}")
        self.activation_label.setText(f"Activation: {layer.get('activation', 'N/A')}")
        self.param_label.setText(f"Params: {layer.get('params', 'N/A')}")

        weight_stats = layer.get("weight_stats")
        if weight_stats:
            self.weight_stats_label.setText(
                f"Mean: {weight_stats['mean']:.2f}, Std: {weight_stats['std']:.2f}, Min: {weight_stats['min']:.2f}, Max: {weight_stats['max']:.2f}"
            )
        else:
            self.weight_stats_label.setText("Weight Stats: N/A")
