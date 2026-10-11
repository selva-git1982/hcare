# H-CARE OCMS

**Operational Compliance Monitoring System** — an open-source research prototype implementing the H-CARE assessment methodology described in *H-CARE: A Compliance-Aware Evaluation Framework for Healthcare Data Platforms* by Selvamurugan Ramamoorthy.

## Features
- Five dimensions (D1–D5) with configurable normalized scores or metric measurements
- Risk-weighted base index: `H = 100 × Σ(wᵢ × Sᵢ)`
- Evidence-adjusted index: `H_E = 100 × Σ(wᵢ × Sᵢ × Cᵢ)`
- Non-compensatory critical-control gates
- Default, transaction-focused, and records-focused sensitivity profiles
- Interactive Streamlit dashboard, JSON/CSV exports, unit tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit displays (usually http://localhost:8501).

## Tests

```bash
python -m pytest -q
```

## Publish to GitHub

```bash
git init
git add .
git commit -m "Initial H-CARE OCMS prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hcare-ocms.git
git push -u origin main
```

Create an empty GitHub repository named `hcare-ocms` first. Replace `YOUR_USERNAME`.

## Limitations and safeguards

- The starting values are **illustrative**, not collected from a production system.
- The application does **not** automatically inspect SQL Server, collect evidence, authenticate users, or monitor infrastructure continuously.
- The software does **not** determine HIPAA, Part 11, or GxP compliance or replace validation, security, privacy, or legal review.
- Do not enter PHI, credentials, or confidential evidence into this prototype. It has no authentication or protected evidence storage.
- Gate selections and evidence confidence are assessor-supplied and must be supported by a documented risk assessment.
- Version your regulatory mappings and retain independently verified supporting artifacts in an approved secure system.

## Reference

Selvamurugan Ramamoorthy, *H-CARE: A Compliance-Aware Evaluation Framework for Healthcare Data Platforms*, IEEE-format manuscript, 2026.
