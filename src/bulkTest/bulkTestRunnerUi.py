from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QProgressBar, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer

class BulkTestRunnerWindow(QMainWindow):
    def __init__(self, inputFile):
        super().__init__()
        self.setWindowTitle("Bulk Test Runner")
        self.setGeometry(100, 100, 400, 100)
        
        self.inputFile = inputFile
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        layout = QVBoxLayout(centralWidget)
        
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        layout.addWidget(self.progressBar)
        
        self.statusLabel = QLabel("Starting bulk test...")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.statusLabel)
        
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

    def startBulkTest(self, runBulkTestFunc):
        # This function will be called to start the test
        # We use a QTimer to allow the UI to render before the test starts
        QTimer.singleShot(100, lambda: runBulkTestFunc(self.inputFile, self.progressCallback))

    def progressCallback(self, processedCount, totalMaterials, formula):
        progress = int((processedCount / totalMaterials) * 100)
        self.progressBar.setValue(progress)
        self.statusLabel.setText(f"Processing {formula} ({processedCount}/{totalMaterials})")
        QApplication.processEvents() # Allow UI to update
