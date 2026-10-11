# H-CARE OCMS — Functional Validation

## Scope
This is a **functional validation of the scoring implementation**, not empirical validation of real healthcare platform performance, HIPAA compliance, or 21 CFR Part 11 compliance.

## Reproduce
From the root of your existing `hcare-ocms` repository, copy `tests/test_final_validation.py` into `tests/` and run:

```bash
source .venv/bin/activate
python3 -m pip install pytest
python3 -m pytest -v
```

The three new tests check:

1. **Illustrative paper example:** base index 93.50, evidence-adjusted index 86.33, gap 7.17.
2. **Mandatory gate override:** failing the `audit` gate changes eligibility to false **without changing the numerical scores**.
3. **Evidence confidence:** incomplete confidence lowers the adjusted index while leaving the base index unchanged.

## Manual dashboard check

1. Launch `python3 -m streamlit run app.py`.
2. Keep the paper's default dimension scores, confidence factors, and weights. Confirm 93.50 / 86.33.
3. Uncheck a mandatory audit or recovery gate. Confirm **Not eligible** while both numerical scores remain unchanged.
4. Re-enable the gate. Confirm eligibility is restored.
5. Save a synthetic assessment and restart the application. Confirm it remains in assessment history.
6. Export a PDF and check its scores, gate status, and synthetic-evidence disclaimer.

## Recording results
Document the test date, Python version, pytest result, and any manual checks. Do not claim that these synthetic tests establish regulatory compliance or real-world platform performance.
