from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QProgressBar, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer

class BulkTestRunnerWindow(QMainWindow):
    def __init__(self, input_file):
        super().__init__()
        self.setWindowTitle("Bulk Test Runner")
        self.setGeometry(100, 100, 400, 100)
        
        self.input_file = input_file
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Starting bulk test...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QProgressBar {
                background-color: #2d2d2d;
                border: none;
                border-radius: 3px;
                height: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007aff;
                border-radius: 3px;
            }
        """)

    def start_bulk_test(self, run_bulk_test_func):
        # This function will be called to start the test
        # We use a QTimer to allow the UI to render before the test starts
        QTimer.singleShot(100, lambda: run_bulk_test_func(self.input_file, self.progress_callback))

    def progress_callback(self, processed_count, total_materials, formula):
        progress = int((processed_count / total_materials) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"Processing {formula} ({processed_count}/{total_materials})")
        QApplication.processEvents() # Allow UI to update
