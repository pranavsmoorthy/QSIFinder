import json
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication, QFileDialog

from src.bulkTest.calculator import calculate_qsi
from src.bulkTest.confusion_matrix_ui import ConfusionMatrixWindow
from src.bulkTest.bulk_test_runner_ui import BulkTestRunnerWindow
from utils.debug import log_debug

def run_bulk_test(input_file_path, output_dir, threshold=0.7, progress_callback=None):
    log_debug(f"Starting bulk test with input file: {input_file_path}")
    try:
        with open(input_file_path, 'r') as f:
            materials = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_debug(f"Error reading input file: {e}")
        return None

    chunk_size = 45
    material_items = list(materials.items())
    total_materials = len(material_items)
    
    true_positives = {}
    true_negatives = {}
    false_positives = {}
    false_negatives = {}
    inconclusive_materials = []



    for i in range(0, total_materials, chunk_size):
        chunk = material_items[i:i+chunk_size]
        
        for processed_count, (formula, is_truly_suitable) in enumerate(chunk, start=i):
            log_debug(f"Processing {formula} ({processed_count + 1}/{total_materials})")
            
            if progress_callback:
                progress_callback(processed_count + 1, total_materials, formula)

            result = calculate_qsi(formula)
            
            if result.get('error'):
                log_debug(f"Could not process {formula}: {result['error']}")
                if formula not in inconclusive_materials: inconclusive_materials.append(formula)
                continue

            qsi = result['index']
            if qsi is None:
                if formula not in inconclusive_materials: inconclusive_materials.append(formula)
                continue

            is_predicted_suitable = qsi >= threshold

            if is_truly_suitable and is_predicted_suitable:
                true_positives[formula] = qsi
            elif not is_truly_suitable and not is_predicted_suitable:
                true_negatives[formula] = qsi
            elif not is_truly_suitable and is_predicted_suitable:
                false_positives[formula] = qsi
            elif is_truly_suitable and not is_predicted_suitable:
                false_negatives[formula] = qsi
        
        # Write chunk results
        write_chunk_results(output_dir, true_positives, true_negatives, false_positives, false_negatives, inconclusive_materials)

    log_debug(f"Bulk test finished. Results saved in '{output_dir}' directory.")
    
    return (len(true_positives), len(true_negatives), len(false_positives), len(false_negatives), len(inconclusive_materials))

def write_chunk_results(output_dir, tp, tn, fp, fn, inconclusive):
    with open(os.path.join(output_dir, 'true_positives.json'), 'w') as f:
        json.dump(tp, f, indent=4)
    with open(os.path.join(output_dir, 'true_negatives.json'), 'w') as f:
        json.dump(tn, f, indent=4)
    with open(os.path.join(output_dir, 'false_positives.json'), 'w') as f:
        json.dump(fp, f, indent=4)
    with open(os.path.join(output_dir, 'false_negatives.json'), 'w') as f:
        json.dump(fn, f, indent=4)
    with open(os.path.join(output_dir, 'inconclusive.json'), 'w') as f:
        json.dump(inconclusive, f, indent=4)

def main():
    if len(sys.argv) < 2:
        print("Usage: python bulk_tester.py <path_to_input.json>")
        sys.exit(1)
        
    input_file = sys.argv[1]

    app = QApplication(sys.argv)
    
    output_dir = QFileDialog.getExistingDirectory(None, "Select Output Directory")

    if not output_dir:
        log_debug("No output directory selected. Exiting.")
        sys.exit(0)

    runner_window = BulkTestRunnerWindow(input_file)
    runner_window.show()

    def start_test(input_file, progress_callback):
        results = run_bulk_test(input_file, output_dir, progress_callback=progress_callback)
        if results:
            tp, tn, fp, fn, inconclusive_count = results
            runner_window.matrix_window = ConfusionMatrixWindow(tp, tn, fp, fn, inconclusive_count)
            runner_window.matrix_window.show()
            runner_window.close()
        else:
            runner_window.close()

    runner_window.start_bulk_test(start_test)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
