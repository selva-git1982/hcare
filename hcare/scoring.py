"""H-CARE scoring engine, based on the published framework."""
from dataclasses import dataclass
from typing import Any

DIMENSIONS = ["Performance & Scalability", "Availability & Resilience", "Security & Compliance", "Data Integrity & Quality", "Governance & Auditability"]
PROFILES = {
    "Default": [0.20, 0.20, 0.25, 0.20, 0.15],
    "Transaction-focused": [0.30, 0.30, 0.20, 0.10, 0.10],
    "Records-focused": [0.10, 0.15, 0.35, 0.25, 0.15],
}

def normalize(value: float, target: float, direction: str = "higher") -> float:
    """Normalize a nonnegative measurement to [0, 1]."""
    if value < 0 or target <= 0:
        raise ValueError("Value must be nonnegative and target positive")
    if direction == "higher":
        return min(value / target, 1.0)
    if direction == "lower":
        return min(target / value, 1.0) if value else 1.0
    raise ValueError("direction must be 'higher' or 'lower'")

def weighted_metrics(metrics: list[dict[str, Any]]) -> float:
    if not metrics:
        raise ValueError("At least one metric is required")
    total = sum(float(m.get("weight", 1)) for m in metrics)
    if total <= 0 or any(float(m.get("weight", 1)) < 0 for m in metrics):
        raise ValueError("Metric weights must be nonnegative and sum positive")
    scores = []
    for m in metrics:
        score = normalize(float(m["value"]), float(m["target"]), m.get("direction", "higher"))
        scores.append(score * float(m.get("weight", 1)))
    return sum(scores) / total

def assess(scores: list[float], confidence: list[float], weights: list[float], gates: dict[str, bool]) -> dict[str, Any]:
    if not (len(scores) == len(confidence) == len(weights) == 5):
        raise ValueError("Exactly five dimension values required")
    if any(not 0 <= v <= 1 for v in scores + confidence + weights):
        raise ValueError("Scores, confidence and weights must be between 0 and 1")
    if abs(sum(weights) - 1.0) > 1e-8:
        raise ValueError("Weights must sum to 1")
    base = 100 * sum(w * s for w, s in zip(weights, scores))
    adjusted = 100 * sum(w * s * c for w, s, c in zip(weights, scores, confidence))
    failed = [name for name, passed in gates.items() if not passed]
    return {
        "base_index": round(base, 2),
        "evidence_adjusted_index": round(adjusted, 2),
        "evidence_gap": round(base - adjusted, 2),
        "eligible": not failed,
        "status": "Eligible under current assessment profile" if not failed else "Not eligible under current assessment profile",
        "failed_gates": failed,
        "dimension_scores": dict(zip(DIMENSIONS, scores)),
        "dimension_confidence": dict(zip(DIMENSIONS, confidence)),
        "weights": dict(zip(DIMENSIONS, weights)),
    }
