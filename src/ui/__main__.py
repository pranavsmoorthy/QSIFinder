import sys
import math
import numpy as np
import logging

# Add the project root to the python path
sys.path.insert(0, '.')

from PyQt6.QtCore import pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QGroupBox, QFormLayout, QDoubleSpinBox,
    QTextEdit, QStatusBar
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
        self.axes = fig.add_subplot(111, polar=True)
        super(RadarChart, self).__init__(fig)
        self.setParent(parent)

    def plot(self, data, labels):
        self.axes.clear()
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        data_with_loop = data + data[:1]
        angles_with_loop = angles + angles[:1]

        self.axes.plot(angles_with_loop, data_with_loop, 'o-')
        self.axes.fill(angles_with_loop, data_with_loop, alpha=0.25)
        self.axes.set_thetagrids(np.degrees(angles), labels)
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
        
        value = max(0, min(1, value))

        if value < 0.33:
            color = 'red'
        elif value < 0.66:
            color = 'orange'
        else:
            color = 'green'

        values = [value, 1 - value]
        colors = [color, 'lightgrey']
        
        self.axes.pie(values, colors=colors, startangle=90, wedgeprops=dict(width=0.3))

        center_circle = plt.Circle((0,0), 0.70, fc='white')
        self.axes.add_artist(center_circle)

        self.axes.text(0, 0, f'{value:.2f}', ha='center', va='center', fontsize=20, weight='bold')
        
        self.axes.axis('equal')
        self.figure.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantum Suitability Index (QSI) Calculator")
        self.setFixedSize(1200, 600)

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
            weights_layout.addRow(name, spinbox)
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

        self.radar_chart = RadarChart(right_panel)
        self.donut_chart = DonutChart(right_panel)
        
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.radar_chart)
        charts_layout.addWidget(self.donut_chart)
        right_layout.addLayout(charts_layout)

        self.radar_chart.plot([0, 0, 0, 0, 0], list(self.weights_inputs.keys()))
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
        if result['error']:
            log_debug(result['error'])
            self.radar_chart.plot([0, 0, 0, 0, 0], list(self.weights_inputs.keys()))
            self.donut_chart.plot(0)
        else:
            labels = list(self.weights_inputs.keys())
            self.radar_chart.plot(result['sub_scores'], labels)
            self.donut_chart.plot(result['index'])
        
        log_debug("QSI calculation finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())