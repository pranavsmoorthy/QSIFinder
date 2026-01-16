import sys
import math
import numpy as np
import logging

# Add the project root to the python path
sys.path.insert(0, '.')

from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QGroupBox, QFormLayout, QDoubleSpinBox,
    QTextEdit, QStatusBar, QStackedWidget, QProgressBar
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Backend imports
from src.data.mp import mpRetriever as mp
from src.data.oqmd import oqmdRetriever as oqmd
from src.data.mp import mpCleaner
from src.data.oqmd import oqmdCleaner
from src.indexCalc import subscores as ic
from utils.debug import log_debug
from src.data.matDataObj import matDataObj

PROPERTY_DISPLAY_NAMES = {
    "stability": "Stability",
    "bandGap": "Band Gap",
    "formationEnergy": "Formation Energy",
    "thickness": "Thickness",
    "symmetry": "Symmetry"
}

class QTextEditLogger(logging.Handler, QObject):
    append_text = pyqtSignal(str)
    message_logged = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = parent
        self.append_text.connect(self.widget.append)
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.append_text.emit(msg)
        self.message_logged.emit(msg)

class CalculationWorker(QObject):
    finished = pyqtSignal(dict)

    def __init__(self, formula, force_oqmd, weights):
        super().__init__()
        self.formula = formula
        self.force_oqmd = force_oqmd
        self.weights = weights

    def run(self):
        log_debug("Worker thread started.")
        dataMP = mp.retrieveMPData(self.formula) if not self.force_oqmd else [{"dataFound": False}]
        finalCandidate = None

        if dataMP[0].get("dataFound") and not self.force_oqmd:
            finalCandidate = mpCleaner.filter(dataMP)
        else:
            dataOQMD = oqmd.retrieveOQMDData(self.formula)
            finalCandidate = oqmdCleaner.filter(dataOQMD)
        
        log_debug("Final Candidate: " + str(finalCandidate))

        if finalCandidate.formula is None:
            self.finished.emit({'error': "No valid material candidate found in MP or OQMD databases."})
            return

        log_debug("Calculating Index...")
        
        bg_subscore = ic.getBandGapSubscore(finalCandidate.bandGap)
        st_subscore = ic.getStabilitySubscore(finalCandidate.hullDistance)
        fe_subscore = ic.getFormationEnergySubscore(finalCandidate.formationEnergy)
        th_subscore = ic.getThicknessSubscore(finalCandidate.thickness)
        sy_subscore = ic.getSymmetrySubscore(finalCandidate.symmetry)
        
        sub_scores = [st_subscore, bg_subscore, fe_subscore, th_subscore, sy_subscore]
        
        index = ic.getTotalIndex(finalCandidate, self.weights)
        log_debug("Index Calculated: " + str(index))
        
        self.finished.emit({'sub_scores': sub_scores, 'index': index, 'error': None})

class RadarChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_alpha(0)
        self.axes = fig.add_subplot(111, polar=True)
        self.axes.patch.set_alpha(0)
        super(RadarChart, self).__init__(fig)
        self.setParent(parent)
        self.setStyleSheet("background-color:transparent;")

    def plot(self, data, labels):
        self.axes.clear()
        self.axes.patch.set_alpha(0)
        
        # Professional Styling
        self.axes.tick_params(axis='x', colors='white', labelsize=10)
        self.axes.tick_params(axis='y', colors='white', labelsize=8)
        self.axes.yaxis.grid(color='white', linestyle='dashed', alpha=0.2)
        self.axes.xaxis.grid(color='white', linestyle='dashed', alpha=0.2)
        self.axes.spines['polar'].set_visible(False) # Remove outer circle for cleaner look

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        data_with_loop = data + data[:1]
        angles_with_loop = angles + angles[:1]

        self.axes.plot(angles_with_loop, data_with_loop, 'o-', color='#00d1b2', linewidth=2, markersize=5)
        self.axes.fill(angles_with_loop, data_with_loop, color='#00d1b2', alpha=0.25)
        self.axes.set_thetagrids(np.degrees(angles), labels)
        self.axes.set_ylim(0, 1)
        
        # Ensure grid lines are drawn below the plot
        self.axes.set_axisbelow(True)
        
        self.figure.canvas.draw()

class DonutChart(FigureCanvas):
    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_alpha(0)
        self.axes = fig.add_subplot(111)
        self.axes.patch.set_alpha(0)
        super(DonutChart, self).__init__(fig)
        self.setParent(parent)
        self.setStyleSheet("background-color:transparent;")

    def plot(self, value):
        self.axes.clear()
        self.axes.axis('off')
        
        value = max(0, min(1, value))

        # Professional Color Palette
        if value < 0.33:
            color = '#ff3860' # Red
        elif value < 0.66:
            color = '#ffdd57' # Yellow/Orange
        else:
            color = '#23d160' # Green

        values = [value, 1 - value]
        colors = [color, '#2d2d2d'] # Dark grey for the remaining part
        
        # Use a slightly thinner ring for a modern look
        self.axes.pie(values, colors=colors, startangle=90, wedgeprops=dict(width=0.25, edgecolor='#1e1e1e'))

        center_circle = plt.Circle((0,0), 0.75, fc='none')
        self.axes.add_artist(center_circle)

        self.axes.text(0, 0, f'{value:.2f}', ha='center', va='center', fontsize=24, weight='bold', color='white', fontname='Arial')
        
        self.axes.axis('equal')
        self.figure.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantum Suitability Index (QSI) Calculator")
        self.setFixedSize(1200, 600)

        # Apply Dark Theme
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
            QGroupBox {
                border: 1px solid #3e3e3e;
                border-radius: 6px;
                margin-top: 20px;
                padding-top: 10px;
                font-weight: bold;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #1e1e1e;
            }
            QLineEdit, QDoubleSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 5px;
                color: #ffffff;
                selection-background-color: #007aff;
            }
            QPushButton {
                background-color: #007aff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0062cc;
            }
            QPushButton:pressed {
                background-color: #0051a8;
            }
            QPushButton:disabled {
                background-color: #3e3e3e;
                color: #888888;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                color: #e0e0e0;
                font-family: "Menlo", "Consolas", monospace;
                font-size: 12px;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #888888;
            }
            QCheckBox {
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel)

        formula_group = QGroupBox("Chemical Formula")
        formula_layout = QVBoxLayout()
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("e.g., MoS2")
        formula_layout.addWidget(self.formula_input)
        formula_group.setLayout(formula_layout)
        left_layout.addWidget(formula_group)

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
            weights_layout.addRow(PROPERTY_DISPLAY_NAMES.get(name, name), spinbox)
        weights_group.setLayout(weights_layout)
        left_layout.addWidget(weights_group)

        self.oqmd_checkbox = QCheckBox("Force OQMD Data")
        left_layout.addWidget(self.oqmd_checkbox)

        self.calculate_button = QPushButton("Calculate QSI")
        self.calculate_button.clicked.connect(self.start_calculation)
        left_layout.addWidget(self.calculate_button)

        logs_group = QGroupBox("Logs")
        logs_layout = QVBoxLayout()
        self.logs_output = QTextEdit()
        self.logs_output.setReadOnly(True)
        logs_layout.addWidget(self.logs_output)
        logs_group.setLayout(logs_layout)
        left_layout.addWidget(logs_group)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, 1)

        self.stacked_widget = QStackedWidget()
        right_layout.addWidget(self.stacked_widget)

        # Charts View (Index 0)
        self.charts_view = QWidget()
        charts_layout = QHBoxLayout(self.charts_view)
        self.radar_chart = RadarChart(self.charts_view)
        self.donut_chart = DonutChart(self.charts_view)
        charts_layout.addWidget(self.radar_chart)
        charts_layout.addWidget(self.donut_chart)
        self.stacked_widget.addWidget(self.charts_view)

        # Loading View (Index 1)
        self.loading_view = QWidget()
        loading_layout = QVBoxLayout(self.loading_view)
        
        loading_text = QLabel("Calculating Quantum Suitability Index...")
        loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_text.setStyleSheet("font-size: 20px; color: #007aff; font-weight: bold; margin-bottom: 20px;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate mode
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #007aff;
                border-radius: 3px;
            }
        """)
        
        loading_layout.addStretch()
        loading_layout.addWidget(loading_text)
        loading_layout.addWidget(self.progress_bar)
        loading_layout.addStretch()
        self.stacked_widget.addWidget(self.loading_view)

        initial_labels = [PROPERTY_DISPLAY_NAMES.get(k, k) for k in self.weights_inputs.keys()]
        self.radar_chart.plot([0, 0, 0, 0, 0], initial_labels)
        self.donut_chart.plot(0)

        self.setStatusBar(QStatusBar(self))

        log_handler = QTextEditLogger(self.logs_output)
        log_handler.message_logged.connect(self.statusBar().showMessage)
        
        from utils import debug
        debug_logger = logging.getLogger('utils.debug')
        debug_logger.addHandler(log_handler)
        debug_logger.setLevel(logging.INFO)

    def start_calculation(self):
        self.logs_output.clear()
        log_debug("Starting QSI calculation...")
        
        formula = self.formula_input.text()
        if not formula:
            log_debug("Error: Please enter a chemical formula.")
            return

        force_oqmd = self.oqmd_checkbox.isChecked()
        weights = {name: spinbox.value() for name, spinbox in self.weights_inputs.items()}

        total_weight = sum(weights.values())
        if not math.isclose(total_weight, 1.0):
            log_debug(f"Error: Weights must sum to 1.0 (current sum: {total_weight:.2f})")
            return

        self.calculate_button.setEnabled(False)
        self.stacked_widget.setCurrentIndex(1) # Show loading screen
        self.thread = QThread()
        self.worker = CalculationWorker(formula, force_oqmd, weights)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_calculation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_calculation_finished(self, result):
        self.calculate_button.setEnabled(True)
        self.stacked_widget.setCurrentIndex(0) # Show charts
        if result['error']:
            log_debug(result['error'])
            labels = [PROPERTY_DISPLAY_NAMES.get(k, k) for k in self.weights_inputs.keys()]
            self.radar_chart.plot([0, 0, 0, 0, 0], labels)
            self.donut_chart.plot(0)
        else:
            labels = [PROPERTY_DISPLAY_NAMES.get(k, k) for k in self.weights_inputs.keys()]
            self.radar_chart.plot(result['sub_scores'], labels)
            self.donut_chart.plot(result['index'])
        
        log_debug("QSI calculation finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())