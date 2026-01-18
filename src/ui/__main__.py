import sys
import math
import numpy as np
import logging
import os
import subprocess

sys.path.insert(0, '.')

from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QGroupBox, QFormLayout, QDoubleSpinBox,
    QTextEdit, QStatusBar, QStackedWidget, QProgressBar, QFileDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.data.mp import mpRetriever as mp
from src.data.oqmd import oqmdRetriever as oqmd
from src.data.mp import mpCleaner
from src.data.oqmd import oqmdCleaner
from src.indexCalc import subscores as ic
from utils.debug import logDebug
from src.data.matDataObj import matDataObj
from indexCalc.calculator import calculateQsi
from src.bulkTest import runBulkTest, ConfusionMatrixWindow

propertyDisplayNames = {
    "stability": "Stability",
    "bandGap": "Band Gap",
    "formationEnergy": "Formation Energy",
    "thickness": "Thickness",
    "symmetry": "Symmetry"
}

class QTextEditLogger(logging.Handler, QObject):
    appendText = pyqtSignal(str)
    messageLogged = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = parent
        self.appendText.connect(self.widget.append)
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.appendText.emit(msg)
        self.messageLogged.emit(msg)

class CalculationWorker(QObject):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, int, str)

    def __init__(self, formula, forceOqmd, weights):
        super().__init__()
        self.formula = formula
        self.forceOqmd = forceOqmd
        self.weights = weights

    def run(self):
        logDebug("Worker thread started.")
        result = calculateQsi(self.formula, self.forceOqmd, self.weights)
        logDebug("Index Calculated: " + str(result.get('index')))
        self.finished.emit(result)

class BulkCalculationWorker(QObject):
    finished = pyqtSignal(object)
    progress = pyqtSignal(int, int, str)

    def __init__(self, inputFile, outputDir):
        super().__init__()
        self.inputFile = inputFile
        self.outputDir = outputDir

    def run(self):
        logDebug("Bulk worker thread started.")
        results = runBulkTest(self.inputFile, self.outputDir, progressCallback=self.progress.emit)
        self.finished.emit(results)

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
        
        self.axes.tick_params(axis='x', colors='white', labelsize=10)
        self.axes.tick_params(axis='y', colors='white', labelsize=8)
        self.axes.yaxis.grid(color='white', linestyle='dashed', alpha=0.2)
        self.axes.xaxis.grid(color='white', linestyle='dashed', alpha=0.2)
        self.axes.spines['polar'].set_visible(False) 

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        dataWithLoop = data + data[:1]
        anglesWithLoop = angles + angles[:1]

        self.axes.plot(anglesWithLoop, dataWithLoop, 'o-', color='#00d1b2', linewidth=2, markersize=5)
        self.axes.fill(anglesWithLoop, dataWithLoop, color='#00d1b2', alpha=0.25)
        self.axes.set_thetagrids(np.degrees(angles), labels)
        self.axes.set_ylim(0, 1)
        
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

        if value < 0.33:
            color = '#ff3860' 
        elif value < 0.66:
            color = '#ffdd57' 
        else:
            color = '#23d160' 

        values = [value, 1 - value]
        colors = [color, '#2d2d2d'] 
        
        self.axes.pie(values, colors=colors, startangle=90, wedgeprops=dict(width=0.25, edgecolor='#1e1e1e'))

        centerCircle = plt.Circle((0,0), 0.75, fc='none')
        self.axes.add_artist(centerCircle)

        self.axes.text(0, 0, f'{value:.2f}', ha='center', va='center', fontsize=24, weight='bold', color='white', fontname='Arial')
        
        self.axes.axis('equal')
        self.figure.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantum Suitability Index (QSI) Calculator")
        self.setFixedSize(1200, 700)

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

        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QHBoxLayout(mainWidget)

        leftPanel = QWidget()
        leftLayout = QVBoxLayout(leftPanel)
        mainLayout.addWidget(leftPanel)

        formulaGroup = QGroupBox("Chemical Formula")
        formulaLayout = QVBoxLayout()
        self.formulaInput = QLineEdit()
        self.formulaInput.setPlaceholderText("e.g., MoS2")
        formulaLayout.addWidget(self.formulaInput)
        formulaGroup.setLayout(formulaLayout)
        leftLayout.addWidget(formulaGroup)

        weightsGroup = QGroupBox("Sub-index Weights")
        weightsLayout = QFormLayout()
        
        defaultWeights = {
            "stability": 0.35,
            "bandGap": 0.3,
            "formationEnergy": 0.15,
            "thickness": 0.1,
            "symmetry": 0.1
        }

        self.weightsInputs = {
            "stability": QDoubleSpinBox(),
            "bandGap": QDoubleSpinBox(),
            "formationEnergy": QDoubleSpinBox(),
            "thickness": QDoubleSpinBox(),
            "symmetry": QDoubleSpinBox()
        }
        for name, spinbox in self.weightsInputs.items():
            spinbox.setRange(0.0, 1.0)
            spinbox.setSingleStep(0.05)
            spinbox.setValue(defaultWeights.get(name, 0.0))
            weightsLayout.addRow(propertyDisplayNames.get(name, name), spinbox)
        weightsGroup.setLayout(weightsLayout)
        leftLayout.addWidget(weightsGroup)

        self.oqmdCheckbox = QCheckBox("Force OQMD Data")
        leftLayout.addWidget(self.oqmdCheckbox)

        self.calculateButton = QPushButton("Calculate QSI")
        self.calculateButton.clicked.connect(self.startCalculation)
        leftLayout.addWidget(self.calculateButton)

        self.bulkCalculateButton = QPushButton("Start Bulk Calculation")
        self.bulkCalculateButton.clicked.connect(self.startBulkCalculation)
        leftLayout.addWidget(self.bulkCalculateButton)

        logsGroup = QGroupBox("Logs")
        logsLayout = QVBoxLayout()
        self.logsOutput = QTextEdit()
        self.logsOutput.setReadOnly(True)
        logsLayout.addWidget(self.logsOutput)
        logsGroup.setLayout(logsLayout)
        leftLayout.addWidget(logsGroup)

        rightPanel = QWidget()
        right_layout = QVBoxLayout(rightPanel)
        mainLayout.addWidget(rightPanel, 1)

        self.stackedWidget = QStackedWidget()
        right_layout.addWidget(self.stackedWidget)

        self.chartsView = QWidget()
        chartsLayout = QHBoxLayout(self.chartsView)
        self.radarChart = RadarChart(self.chartsView)
        self.donutChart = DonutChart(self.chartsView)
        chartsLayout.addWidget(self.radarChart)
        chartsLayout.addWidget(self.donutChart)
        self.stackedWidget.addWidget(self.chartsView)

        self.loadingView = QWidget()
        loadingLayout = QVBoxLayout(self.loadingView)
        
        self.loadingText = QLabel("Calculating Quantum Suitability Index...")
        self.loadingText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loadingText.setStyleSheet("font-size: 20px; color: #007aff; font-weight: bold; margin-bottom: 20px;")
        
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0) 
        self.progressBar.setFixedHeight(6)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet("""
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

        self.progressLabel = QLabel("")
        self.progressLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressLabel.setStyleSheet("font-size: 12px; color: #aaaaaa; margin-top: 5px;")
        
        loadingLayout.addStretch()
        loadingLayout.addWidget(self.loadingText)
        loadingLayout.addWidget(self.progressBar)
        loadingLayout.addWidget(self.progressLabel)
        loadingLayout.addStretch()
        self.stackedWidget.addWidget(self.loadingView)

        initialLabels = [propertyDisplayNames.get(k, k) for k in self.weightsInputs.keys()]
        self.radarChart.plot([0, 0, 0, 0, 0], initialLabels)
        self.donutChart.plot(0)

        self.setStatusBar(QStatusBar(self))

        logHandler = QTextEditLogger(self.logsOutput)
        logHandler.messageLogged.connect(self.statusBar().showMessage)
        
        from utils import debug
        debugLogger = logging.getLogger('utils.debug')
        debugLogger.addHandler(logHandler)
        debugLogger.setLevel(logging.INFO)

    def startCalculation(self):
        self.logsOutput.clear()
        logDebug("Starting QSI calculation...")
        
        formula = self.formulaInput.text()
        if not formula:
            logDebug("Error: Please enter a chemical formula.")
            return

        forceOqmd = self.oqmdCheckbox.isChecked()
        weights = {name: spinbox.value() for name, spinbox in self.weightsInputs.items()}

        totalWeight = sum(weights.values())
        if not math.isclose(totalWeight, 1.0):
            logDebug(f"Error: Weights must sum to 1.0 (current sum: {totalWeight:.2f})")
            return
        
        self.loadingText.setText("Calculating Quantum Suitability Index...")
        self.progressLabel.setText("")
        self.progressBar.setRange(0, 0)
        self.calculateButton.setEnabled(False)
        self.bulkCalculateButton.setEnabled(False)
        self.stackedWidget.setCurrentIndex(1) 
        
        self.thread = QThread()
        self.worker = CalculationWorker(formula, forceOqmd, weights)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.onCalculationFinished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def onCalculationFinished(self, result):
        self.calculateButton.setEnabled(True)
        self.bulkCalculateButton.setEnabled(True)
        self.stackedWidget.setCurrentIndex(0)
        if result['error']:
            logDebug(result['error'])
            labels = [propertyDisplayNames.get(k, k) for k in self.weightsInputs.keys()]
            self.radarChart.plot([0, 0, 0, 0, 0], labels)
            self.donutChart.plot(0)
        else:
            labels = [propertyDisplayNames.get(k, k) for k in self.weightsInputs.keys()]
            self.radarChart.plot(result['subScores'], labels)
            self.donutChart.plot(result['index'])
        
        logDebug("QSI calculation finished.")

    def startBulkCalculation(self):
        logDebug("Opening file dialog for bulk test...")
        inputFileDialog = QFileDialog(self)
        inputFileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        inputFileDialog.setNameFilter("JSON files (*.json)")
        
        if inputFileDialog.exec():
            inputFilePath = inputFileDialog.selectedFiles()[0]
            logDebug(f"Starting bulk test with file: {inputFilePath}")

            outputDir = QFileDialog.getExistingDirectory(None, "Select Output Directory")

            if not outputDir:
                logDebug("No output directory selected. Exiting.")
                return

            self.loadingText.setText("Running Bulk Test...")
            self.progressLabel.setText("Initializing...")
            self.progressBar.setRange(0, 100)
            self.calculateButton.setEnabled(False)
            self.bulkCalculateButton.setEnabled(False)
            self.stackedWidget.setCurrentIndex(1)

            self.thread = QThread()
            self.worker = BulkCalculationWorker(inputFilePath, outputDir)
            self.worker.moveToThread(self.thread)

            self.worker.progress.connect(self.onBulkProgress)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.onBulkFinished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def onBulkProgress(self, processed, total, formula):
        progress = int((processed / total) * 100)
        self.progressBar.setValue(progress)
        self.progressLabel.setText(f"Processing {formula} ({processed}/{total})")

    def onBulkFinished(self, results):
        self.calculateButton.setEnabled(True)
        self.bulkCalculateButton.setEnabled(True)
        self.stackedWidget.setCurrentIndex(0)
        
        if results:
            logDebug("Showing confusion matrix")
            tp, tn, fp, fn, inconclusiveCount = results
            
            self.matrixWindow = ConfusionMatrixWindow(tp, tn, fp, fn, inconclusiveCount)
            self.matrixWindow.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.matrixWindow.show()
        else:
            logDebug("Bulk test failed or was cancelled.")
        
        logDebug("Bulk calculation finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())