from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt

class ConfusionMatrixWindow(QMainWindow):
    def __init__(self, tp, tn, fp, fn, inconclusiveCount=0):
        super().__init__()
        self.setWindowTitle("Bulk Test Results - Confusion Matrix")
        self.setGeometry(100, 100, 400, 250)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QGridLayout(centralWidget)

        # Headers
        layout.addWidget(QLabel(""), 0, 0)
        
        predictedTrueLabel = QLabel("Predicted True")
        predictedTrueLabel.setObjectName("header")
        layout.addWidget(predictedTrueLabel, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        predictedFalseLabel = QLabel("Predicted False")
        predictedFalseLabel.setObjectName("header")
        layout.addWidget(predictedFalseLabel, 0, 2, Qt.AlignmentFlag.AlignCenter)
        
        actualTrueLabel = QLabel("Actual True")
        actualTrueLabel.setObjectName("header")
        layout.addWidget(actualTrueLabel, 1, 0, Qt.AlignmentFlag.AlignRight)

        actualFalseLabel = QLabel("Actual False")
        actualFalseLabel.setObjectName("header")
        layout.addWidget(actualFalseLabel, 2, 0, Qt.AlignmentFlag.AlignRight)

        # Matrix values
        tpLabel = QLabel(str(tp))
        tpLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tpLabel.setObjectName("value")
        tpLabel.setStyleSheet("background-color: #007aff;") # Blue for correct prediction

        fpLabel = QLabel(str(fp))
        fpLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fpLabel.setObjectName("value")
        fpLabel.setStyleSheet("background-color: #2d2d2d;") # Gray for false positive

        fnLabel = QLabel(str(fn))
        fnLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fnLabel.setObjectName("value")
        fnLabel.setStyleSheet("background-color: #2d2d2d;") # Gray for false negative

        tnLabel = QLabel(str(tn))
        tnLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tnLabel.setObjectName("value")
        tnLabel.setStyleSheet("background-color: #007aff;") # Blue for correct prediction


        layout.addWidget(tpLabel, 1, 1)
        layout.addWidget(fpLabel, 2, 1)
        layout.addWidget(fnLabel, 1, 2)
        layout.addWidget(tnLabel, 2, 2)

        # Inconclusive count
        inconclusiveLabel = QLabel(f"Inconclusive/Not Found: {inconclusiveCount}")
        inconclusiveLabel.setObjectName("inconclusive")
        inconclusiveLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(inconclusiveLabel, 3, 0, 1, 3)
        
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
            QLabel#header {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            QLabel#value {
                font-size: 16px;
                padding: 10px;
                border: 1px solid #3e3e3e;
            }
            QLabel#inconclusive {
                font-size: 14px;
                padding: 10px;
                color: #888888;
            }
        """)
