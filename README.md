# Exploring Alternative Materials for Computer Processors

## Table of Contents
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Methodology](#methodology)
  - [Core Approach](#core-approach)
  - [Measured Properties](#measured-properties)
  - [Data Sources](#data-sources)

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

### Measured Properties

The QSI is calculated by evaluating four main properties of a material. The raw data for these properties will be collected and used to develop the algorithm.

1.  **Electronic Performance**
    -   **Metric:** Band Gap
    -   **Description:** A larger band gap leads to less current leakage.
    -   **Ideal Value:** ~1.5eV

2.  **Manufacturing Feasibility**
    -   **Metrics:**
        -   Hull Distance / Stability
        -   Formation Energy
    -   **Description:** These metrics measure the material's stability.
        -   *Hull Distance* indicates if the material is the most thermodynamically stable version of itself.
        -   *Formation Energy* indicates if the compound is more stable than its constituent elements.
    -   **Ideal Values:**
        -   Hull Distance / Stability: 0
        -   Formation Energy: Negative value

3.  **Miniaturization Limits**
    -   **Metric:** Unit Cell Dimensions
    -   **Description:** This represents the smallest repeating volume of the material's crystal structure, indicating how small the material can be made.
    -   **Ideal Value:** 0.6 to 0.7 nanometers thick (the minimum for semiconducting behavior).

4.  **Structural Uniformity**
    -   **Metric:** Space Group
    -   **Description:** This represents the degree of symmetry in the material's crystals. Higher symmetry helps preserve information longer in a quantum computer. There are 230 space groups, with the 230th being the most symmetrical.

### Data Sources

To ensure data quality and mitigate biases from any single source, data will be pulled from two primary databases:

-   **The Materials Project:** This will be the primary source due to its curated and high-quality data.
-   **The Open Quantum Materials Database (OQMD):** This will be used as a secondary source, especially for materials not found in the Materials Project.