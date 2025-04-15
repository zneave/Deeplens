from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QEasingCurve, Qt
from ui.utils.hover_button import HoverButton

class LandingPage(QWidget):
    continue_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel#Title {
                font-size: 32px;
                font-weight: bold;
                color: #222;
            }

            QLabel#Subtitle {
                font-size: 16px;
                color: #666;
            }

            QWidget#Card {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 16px;
                padding: 40px;
                max-width: 500px;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QWidget(objectName="Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(24)
        card_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Welcome to Deeplens", objectName="Title")
        subtitle = QLabel("Clarity in Complexity", objectName="Subtitle")

        self.start_button = HoverButton("Continue to Dashboard")
        self.start_button.setFixedWidth(250)
        self.start_button.setMinimumHeight(45)
        self.start_button.clicked.connect(self.continue_clicked.emit)
        self.start_button.setStyleSheet("""
            HoverButton {
                background-color: #2d8cf0;
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }

            HoverButton:hover {
                background-color: #1e6fb8;
            }

            HoverButton:pressed {
                background-color: #155a96;
            }
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.start_button)
        card_layout.addSpacing(10)

        outer_layout.addStretch()
        outer_layout.addWidget(card, alignment=Qt.AlignCenter)
        outer_layout.addStretch()

        self._fade_in()

    def _fade_in(self):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(1000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()
