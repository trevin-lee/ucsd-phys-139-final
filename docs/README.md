# TESS Anomaly Detection - Physics 139 Final Project

## Project Overview
This project focuses on analyzing anomalies in TESS (Transiting Exoplanet Survey Satellite) data using machine learning techniques. TESS monitors the brightness of stars to detect exoplanet transits and stellar variability, producing a rich dataset for anomaly detection.

## Repository Structure
```
.
├── docs/               # LaTeX documents
│   ├── proposal.tex   # Project proposal
│   └── final_paper.tex # Final paper
├── notebooks/          # Jupyter notebooks for analysis
├── data/              # TESS datasets (not tracked in git)
└── README.md          # This file
```

## Setup
1. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

## Data Sources
- TESS data archive: [MAST](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html)
- TESS Science Support Center: [TESS Science](https://tess.mit.edu/)

## Project Goals
- Identify and classify anomalies in TESS light curves
- Apply machine learning techniques for automated anomaly detection
- Analyze the characteristics of detected anomalies

