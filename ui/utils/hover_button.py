from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPropertyAnimation, QSize, QEasingCurve

class HoverButton(QPushButton):
    def __init__(self, label="", parent=None):
        super().__init__(label, parent)
        self._animation = QPropertyAnimation(self, b"size")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)

    def enterEvent(self, event):
        self._animate_resize(1.06)  # Grow a bit
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_resize(1.00)  # Return to original size
        super().leaveEvent(event)

    def _animate_resize(self, scale_factor):
        current_size = self.size()
        target_size = QSize(int(current_size.width() * scale_factor),
                            int(current_size.height() * scale_factor))
        self._animation.stop()
        self._animation.setStartValue(current_size)
        self._animation.setEndValue(target_size)
        self._animation.start()
