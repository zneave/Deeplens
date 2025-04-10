import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

# Auto-generate project diagram
from project_flow.generate_flowchart import generate_project_diagram


def main():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    generate_project_diagram(current_dir, output_filename="docs/images/project_structure")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
