from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt

class ConfusionMatrixWindow(QMainWindow):
    def __init__(self, tp, tn, fp, fn, inconclusive_count=0):
        super().__init__()
        self.setWindowTitle("Bulk Test Results - Confusion Matrix")
        self.setGeometry(100, 100, 400, 250)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        # Headers
        layout.addWidget(QLabel(""), 0, 0)
        
        predicted_true_label = QLabel("Predicted True")
        predicted_true_label.setObjectName("header")
        layout.addWidget(predicted_true_label, 0, 1, Qt.AlignmentFlag.AlignCenter)
        
        predicted_false_label = QLabel("Predicted False")
        predicted_false_label.setObjectName("header")
        layout.addWidget(predicted_false_label, 0, 2, Qt.AlignmentFlag.AlignCenter)
        
        actual_true_label = QLabel("Actual True")
        actual_true_label.setObjectName("header")
        layout.addWidget(actual_true_label, 1, 0, Qt.AlignmentFlag.AlignRight)

        actual_false_label = QLabel("Actual False")
        actual_false_label.setObjectName("header")
        layout.addWidget(actual_false_label, 2, 0, Qt.AlignmentFlag.AlignRight)

        # Matrix values
        tp_label = QLabel(str(tp))
        tp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tp_label.setObjectName("value")
        tp_label.setStyleSheet("background-color: #007aff;") # Blue for correct prediction

        fp_label = QLabel(str(fp))
        fp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fp_label.setObjectName("value")
        fp_label.setStyleSheet("background-color: #2d2d2d;") # Gray for false positive

        fn_label = QLabel(str(fn))
        fn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fn_label.setObjectName("value")
        fn_label.setStyleSheet("background-color: #2d2d2d;") # Gray for false negative

        tn_label = QLabel(str(tn))
        tn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tn_label.setObjectName("value")
        tn_label.setStyleSheet("background-color: #007aff;") # Blue for correct prediction


        layout.addWidget(tp_label, 1, 1)
        layout.addWidget(fp_label, 2, 1)
        layout.addWidget(fn_label, 1, 2)
        layout.addWidget(tn_label, 2, 2)

        # Inconclusive count
        inconclusive_label = QLabel(f"Inconclusive/Not Found: {inconclusive_count}")
        inconclusive_label.setObjectName("inconclusive")
        inconclusive_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(inconclusive_label, 3, 0, 1, 3)
        
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
