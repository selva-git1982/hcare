import json
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from hcare.scoring import DIMENSIONS, PROFILES, assess, weighted_metrics
from hcare.collector import load_evidence
from hcare.storage import save_assessment, list_assessments
from hcare.reporting import pdf_report

st.set_page_config(page_title="H-CARE OCMS", page_icon="🛡️", layout="wide")
st.title("H-CARE | Operational Compliance Monitoring System")
st.caption("Research prototype • Synthetic example data • Not a compliance certification")

with st.sidebar:
    st.header("Assessment")
    assessment_name = st.text_input("Assessment name", "Synthetic Healthcare Platform B3")
    profile = st.selectbox("Risk-weight profile", list(PROFILES))
    custom = st.checkbox("Customize dimension weights")
    weights = PROFILES[profile].copy()
    if custom:
        raw = [st.number_input(f"D{i+1} weight", 0.0, 1.0, float(w), 0.05) for i, w in enumerate(weights)]
        if sum(raw) <= 0:
            st.error("At least one weight must be positive")
            st.stop()
        weights = [w / sum(raw) for w in raw]
        st.caption("Custom weights are normalized to sum to 1.")

st.subheader("0. Import synthetic monitoring evidence")
imported = None
uploaded = st.file_uploader("Optional synthetic metrics JSON", type=["json"])
if uploaded is not None:
    try:
        imported = load_evidence(uploaded.getvalue().decode("utf-8"))
        st.success("Synthetic metrics validated. Dimension scores calculated from imported measurements.")
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
        st.error(f"Evidence import failed: {exc}")
        st.stop()

st.subheader("1. Dimension scoring and evidence confidence")
st.info("Example values reproduce the illustrative matrix in the H-CARE paper. Replace them with verified assessment data.")
example_scores = [0.90, 1.00, 0.90, 0.90, 1.00]
example_confidence = [1.00, 0.90, 0.85, 0.90, 1.00]
scores, confidence = [], []
for i, name in enumerate(DIMENSIONS):
    with st.expander(f"D{i+1} · {name}", expanded=(i == 0)):
        mode = st.radio("Scoring method", ["Direct dimension score", "Measured metrics"], horizontal=True, key=f"mode{i}")
        if mode == "Direct dimension score":
            score = st.slider("Normalized score", 0.0, 1.0, example_scores[i], 0.01, key=f"score{i}")
        else:
            template = [{"name": "Example metric", "value": 90.0, "target": 100.0, "direction": "higher", "weight": 1.0}]
            table = st.data_editor(pd.DataFrame(template), num_rows="dynamic", key=f"metrics{i}")
            try:
                score = weighted_metrics(table.to_dict("records"))
                st.write(f"Computed dimension score: **{score:.3f}**")
            except (ValueError, TypeError, KeyError) as exc:
                st.error(f"Invalid metric configuration: {exc}")
                st.stop()
        conf = st.slider("Evidence confidence (retrievable support)", 0.0, 1.0, example_confidence[i], 0.01, key=f"conf{i}")
        st.text_input("Evidence reference / artifact ID (do not enter PHI)", key=f"evidence{i}")
        if imported is not None:
            score = imported[0][i]
            st.caption(f"Imported calculated score: {score:.3f} (overrides manual score)")
        scores.append(score)
        confidence.append(conf)

st.subheader("2. Critical-control gates")
st.caption("These are example risk-based gates; determine mandatory gates for your own assessment profile.")
gates = {}
for name in ["Effective access control", "Required audit capability", "Validated critical-workload recovery", "Required data-integrity evidence"]:
    gates[name] = st.checkbox(name, value=True, key=f"gate_{name}")

result = assess(scores, confidence, weights, gates)
st.subheader("3. Assessment results")
a, b, c = st.columns(3)
a.metric("Base H-CARE index", f"{result['base_index']:.2f} / 100")
b.metric("Evidence-adjusted index", f"{result['evidence_adjusted_index']:.2f} / 100")
c.metric("Evidence gap", f"{result['evidence_gap']:.2f} points")
if result["eligible"]:
    st.success(result["status"])
else:
    st.error(result["status"] + " — Failed gates: " + ", ".join(result["failed_gates"]))

chart = pd.DataFrame({"Dimension": [f"D{i+1}" for i in range(5)], "Score": [v * 100 for v in scores], "Evidence-adjusted": [s*c*100 for s,c in zip(scores,confidence)]}).set_index("Dimension")
st.bar_chart(chart)
st.subheader("4. Weight sensitivity")
sensitivity = []
for name, w in PROFILES.items():
    r = assess(scores, confidence, w, gates)
    sensitivity.append({"Profile": name, "Base H": r["base_index"], "Evidence-adjusted H_E": r["evidence_adjusted_index"]})
st.dataframe(pd.DataFrame(sensitivity), hide_index=True, use_container_width=True)

report = {"assessment": assessment_name, "generated_at_utc": datetime.now(timezone.utc).isoformat(), "profile": profile if not custom else "Custom", "result": result, "evidence_references": {DIMENSIONS[i]: (imported[1][DIMENSIONS[i]] if imported is not None else st.session_state.get(f"evidence{i}", "")) for i in range(5)}, "sensitivity": sensitivity, "disclaimer": "Research assessment prototype, not legal or regulatory certification. Inputs are assessor-provided, not independently verified."}
st.download_button("Download assessment JSON", json.dumps(report, indent=2), file_name="hcare_assessment.json", mime="application/json")
st.download_button("Download dimension scores CSV", pd.DataFrame({"dimension": DIMENSIONS, "score": scores, "confidence": confidence, "weight": weights}).to_csv(index=False), file_name="hcare_dimensions.csv", mime="text/csv")

st.subheader("5. Save and export")
if st.button("Save assessment to local history"):
    save_assessment(report)
    st.success("Saved to local SQLite assessment history")
st.download_button("Download assessment PDF", pdf_report(report), file_name="hcare_report.pdf", mime="application/pdf")
history = list_assessments()
if history:
    st.subheader("6. Assessment history")
    st.dataframe(pd.DataFrame(history), hide_index=True, use_container_width=True)
    st.line_chart(pd.DataFrame(list(reversed(history))).set_index("created_at")[["base", "adjusted"]])
