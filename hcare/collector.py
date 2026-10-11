"""Import structured synthetic metrics. No live system or PHI access."""
import json
from hcare.scoring import DIMENSIONS, weighted_metrics

def load_evidence(raw):
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("dataset_type") != "synthetic":
        raise ValueError("Only explicitly labeled synthetic datasets are accepted")
    metrics = data.get("dimensions")
    if not isinstance(metrics, dict) or set(metrics) != set(DIMENSIONS):
        raise ValueError("Supply metrics for exactly the five H-CARE dimensions")
    scores = []
    refs = {}
    for name in DIMENSIONS:
        entry = metrics[name]
        scores.append(weighted_metrics(entry["metrics"]))
        refs[name] = str(entry.get("evidence_reference", ""))
    return scores, refs
