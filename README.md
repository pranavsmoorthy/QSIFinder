# Exploring Alternative Materials for Computer Processors

## Table of Contents
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Methodology](#methodology)
  - [Core Approach](#core-approach)
  - [Measured Properties](#measured-properties)
  - [Data Sources](#data-sources)
- [Bulk Testing And Analysis](#bulk-testing-and-analysis)
- [DISCLAIMER!!](#disclaimer)

## The Problem

As technology advances, traditional silicon-based processors are approaching their computational limits. This creates an urgent need to explore new materials. Promising candidates include *graphene* and *transition metal dichalcogenides (TMDs)*.

However, a significant gap exists: there is no unified, high-throughput computational pipeline to translate the microscopic properties of these materials into predictable, device-level performance metrics for quantum computing.

## The Solution

This project aims to answer the question:

> **How can open source material databases and programming be integrated to create a low-cost pipeline that can predict a material's performance for quantum computing?**

The goal is to create an open-source application that:
1.  Takes a material's name as input.
2.  Outputs a "Quantum Suitability Index" (QSI) to indicate its feasibility for quantum computing.
3.  Delivers accurate results in a time and cost-effective manner.

## Methodology

### Core Approach

The project will employ a computational and theoretical approach, relying on open-source materials databases.

This model will calculate the QSI, which will then be validated against existing experimental data for known materials to ensure accuracy.

### Measured Properties and Scoring

The QSI is calculated by evaluating five main properties of a material. Each property is assigned a subscore based on a custom formula, which is then used to calculate the final QSI.

1.  **Electronic Performance (Band Gap)**
    -   **Description:** A larger band gap leads to less current leakage. The model now differentiates between materials based on their potential application in visible or UV light spectrums. For typical applications, an ideal band gap is around 1.0eV. For materials suited as UV emitters (band gap > 2.0eV), an ideal gap of 2.5eV is targeted.
    -   **Ideal Value:** ~1.0eV (Visible) or ~2.5eV (UV)
    -   **Formula:** A Gaussian function is used to score materials, favoring those with a band gap close to the relevant ideal value.
        ```math
        \text{score} = e^{-\frac{(\text{bandGap} - \text{idealGap})^2}{2 \cdot \text{tolerance}^2}}
        ```
    -   **Default Parameters:** 
        -   For visible range: `idealGap = 1.0`, `tolerance = 0.5`
        -   For UV range (`bandGap > 2.0eV`): `idealGap = 2.5`, `tolerance = 1.0`

2.  **Stability (Hull Distance)**
    -   **Description:** This metric indicates the thermodynamic stability of a material. A lower hull distance is better.
    -   **Ideal Value:** 0 eV/atom
    -   **Formula:** An exponential decay function is used, where a stability of 0 yields a score of 1.
        ```math
        \text{score} = e^{-\frac{\text{stability}}{\text{decayConstant}}}
        ```
    -   **Default Parameters:** `decayConstant = 0.05`

3.  **Formation Energy**
    -   **Description:** This metric indicates if a compound is more stable than its constituent elements. More negative values imply higher chemical stability.
    -   **Ideal Value:** Negative
    -   **Formula:** A sigmoid function favors negative values.
        ```math
        \text{score} = \frac{1}{1 + e^{\text{steepness} \cdot (\text{formationEnergy} - \text{cutoff})}}
        ```
    -   **Default Parameters:** `cutoff = 0`, `steepness = 2`

4.  **Miniaturization Limits (Thickness)**
    -   **Description:** This represents the smallest repeating volume of the material's crystal structure, indicating how small the material can be made. Thinner materials are preferred.
    -   **Ideal Value:** ~0.6 nm (thickness of one atom)
    -   **Formula:** An inverse power function is used, where the score is higher for thicknesses closer to an ideal thickness (0.6 nm).
        ```math
        \text{score} = \frac{1}{1 + \text{sensitivity} \cdot (\text{thickness} - \text{idealThickness})^2}
        ```
    -   **Default Parameters:** `minThickness = 0.3`, `sensitivity = 0.5`

5.  **Structural Uniformity (Symmetry)**
    -   **Description:** This represents the degree of symmetry in the material's crystals. Higher symmetry (a higher space group number) is better for preserving quantum information. There are 230 space groups.
    -   **Ideal Value:** 230
    -   **Formula:** A power function with diminishing returns for higher symmetry.
        ```math
        \text{score} = \left(\frac{\text{symmetry}}{230}\right)^{\text{curvature}}
        ```
    -   **Default Parameters:** `curvature = 0.5`

### Quantum Suitability Index (QSI) Calculation

The individual subscores are combined into a single Quantum Suitability Index (QSI) using a weighted geometric mean. This allows for a balanced assessment where each property contributes to the final score based on its assigned importance.

**Formula:**
```math
\text{QSI} = \text{score}_{\text{bg}}^{w_{\text{bg}}} \cdot \text{score}_{\text{st}}^{w_{\text{st}}} \cdot \text{score}_{\text{fe}}^{w_{\text{fe}}} \cdot \text{score}_{\text{th}}^{w_{\text{th}}} \cdot \text{score}_{\text{sy}}^{w_{\text{sy}}}
```

**Default Weights:**
The default weights for each property are as follows:
-   `stability`: 0.35
-   `bandGap`: 0.3
-   `formationEnergy`: 0.15
-   `thickness`: 0.1
-   `symmetry`: 0.1


### Data Sources

To ensure data quality and mitigate biases from any single source, data will be pulled from two primary databases:

-   **The Materials Project:** This will be the primary source due to its curated and high-quality data.
-   **The Open Quantum Materials Database (OQMD):** This will be used as a secondary source, especially for materials not found in the Materials Project.

Furthermore, the equations as well as a rudimentary version of the model can be found at this link: https://www.desmos.com/calculator/n7tveikjv6

## Bulk Testing and Analysis

The project includes a powerful bulk testing utility that operates in two distinct modes: **Validation Mode** to test the QSI model's accuracy against known data, and **Prediction Mode** to efficiently calculate the QSI for a list of new materials.

### Running the Bulk Tester

Both modes are initiated through the main UI:

```bash
python -m src.ui
```

Clicking the "Start Bulk Calculation" button will open a file dialog. The format of the selected JSON file determines which mode the tester will run in.

### Validation Mode

This mode is for assessing the accuracy of the QSI model. It compares the model's predictions against a ground truth dataset.

**Input Format (JSON Object):**
The input file must be a JSON object where each key is a material's formula and the value is a boolean (`true` or `false`) indicating its known suitability.

*Example (`validation_set.json`):*
```json
{
  "Si": true,
  "NaCl": false,
  "Graphene": true
}
```

**Output:**
-   **Confusion Matrix UI:** After processing, a window appears displaying a confusion matrix with True Positives, True Negatives, False Positives, and False Negatives.
-   **JSON Files:** Detailed reports for each category (`truePositives.json`, `trueNegatives.json`, etc.), inconclusive materials (`inconclusive.json`), and a consolidated list of all calculated indices (`indices.json`) are saved to the chosen output directory.

### Prediction Mode

This mode is for efficiently calculating the QSI for a list of materials without a known suitability.

**Input Format (JSON Array):**
The input file must be a JSON array containing a list of material formula strings.

*Example (`prediction_set.json`):*
```json
[
  "MoS2",
  "WSe2",
  "BN"
]
```

**Output:**
-   **Confirmation Dialog:** After processing, a message box confirms the number of materials processed and the location of the output files. No confusion matrix is shown.
-   **JSON Files:** The results are saved to two files in the chosen output directory:
    -   `indices.json`: A dictionary mapping each successfully processed material to its calculated QSI value.
    -   `inconclusive.json`: A list of materials that could not be processed.


## Disclaimer
This was all cobbled together by a high school student for an AP Research project, so in the off chance this is used for actual research purposes, keep this in mind.