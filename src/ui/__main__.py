import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QGroupBox, QFormLayout, QDoubleSpinBox,
    QTextEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class RadarChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, polar=True)
        super(RadarChart, self).__init__(fig)
        self.setParent(parent)

    def plot(self, data, labels):
        self.axes.clear()
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        data += data[:1]
        angles += angles[:1]

        self.axes.plot(angles, data, 'o-')
        self.axes.fill(angles, data, alpha=0.25)
        self.axes.set_thetagrids(np.degrees(angles[:-1]), labels)
        self.axes.set_ylim(0, 1)
        self.figure.canvas.draw()

class DonutChart(FigureCanvas):
    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(DonutChart, self).__init__(fig)
        self.setParent(parent)

    def plot(self, value):
        self.axes.clear()
        
        # Ensure the value is within the [0, 1] range
        value = max(0, min(1, value))

        # Define colors
        if value < 0.33:
            color = 'red'
        elif value < 0.66:
            color = 'orange'
        else:
            color = 'green'

        # Data for the donut chart
        values = [value, 1 - value]
        colors = [color, 'lightgrey']
        
        # Plotting the donut chart
        self.axes.pie(values, colors=colors, startangle=90, wedgeprops=dict(width=0.3))

        # Adding a circle in the center to make it a donut
        center_circle = plt.Circle((0,0), 0.70, fc='white')
        self.axes.add_artist(center_circle)

        # Adding the text in the center
        self.axes.text(0, 0, f'{value:.2f}', ha='center', va='center', fontsize=20, weight='bold')
        
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        self.figure.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantum Suitability Index (QSI) Calculator")
        self.setFixedSize(1200, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left panel for inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel)

        # Formula input
        formula_group = QGroupBox("Chemical Formula")
        formula_layout = QVBoxLayout()
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("e.g., MoS2")
        formula_layout.addWidget(self.formula_input)
        formula_group.setLayout(formula_layout)
        left_layout.addWidget(formula_group)

        # Weights customization
        weights_group = QGroupBox("Sub-index Weights")
        weights_layout = QFormLayout()
        
        default_weights = {
            "stability": 0.35,
            "bandGap": 0.3,
            "formationEnergy": 0.15,
            "thickness": 0.1,
            "symmetry": 0.1
        }

        self.weights_inputs = {
            "stability": QDoubleSpinBox(),
            "bandGap": QDoubleSpinBox(),
            "formationEnergy": QDoubleSpinBox(),
            "thickness": QDoubleSpinBox(),
            "symmetry": QDoubleSpinBox()
        }
        for name, spinbox in self.weights_inputs.items():
            spinbox.setRange(0.0, 1.0)
            spinbox.setSingleStep(0.05)
            spinbox.setValue(default_weights.get(name, 0.0))
            weights_layout.addRow(name, spinbox)
        weights_group.setLayout(weights_layout)
        left_layout.addWidget(weights_group)

        # OQMD option
        self.oqmd_checkbox = QCheckBox("Force OQMD Data")
        left_layout.addWidget(self.oqmd_checkbox)

        # Calculate button
        self.calculate_button = QPushButton("Calculate QSI")
        self.calculate_button.clicked.connect(self.calculate_qsi)
        left_layout.addWidget(self.calculate_button)

        # Logs
        logs_group = QGroupBox("Logs")
        logs_layout = QVBoxLayout()
        self.logs_output = QTextEdit()
        self.logs_output.setReadOnly(True)
        logs_layout.addWidget(self.logs_output)
        logs_group.setLayout(logs_layout)
        left_layout.addWidget(logs_group)


        # Right panel for charts
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, 1) # Give more space to the right panel

        # Charts
        self.radar_chart = RadarChart(right_panel)
        self.donut_chart = DonutChart(right_panel)
        
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.radar_chart)
        charts_layout.addWidget(self.donut_chart)
        right_layout.addLayout(charts_layout)

        # Initial plot
        self.radar_chart.plot([0, 0, 0, 0, 0], list(self.weights_inputs.keys()))
        self.donut_chart.plot(0)


    def calculate_qsi(self):
        self.logs_output.clear()
        self.logs_output.append("Starting QSI calculation...")
        formula = self.formula_input.text()
        use_oqmd = self.oqmd_checkbox.isChecked()
        weights = {name: spinbox.value() for name, spinbox in self.weights_inputs.items()}

        # Validate weights
        total_weight = sum(weights.values())
        if not math.isclose(total_weight, 1.0):
            self.logs_output.append(f"Error: Weights must sum to 1.0 (current sum: {total_weight:.2f})")
            return

        #
        # TODO: Here you would call your backend functions to get the actual data
        # based on the formula, oqmd flag, and weights.
        #
        
        # For now, let's use some dummy data to show the charts
        sub_indexes = [np.random.rand() for _ in self.weights_inputs.keys()]
        final_index = np.random.rand()

        # Update charts
        labels = list(self.weights_inputs.keys())
        self.radar_chart.plot(sub_indexes, labels)
        self.donut_chart.plot(final_index)
        self.logs_output.append("QSI calculation finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())