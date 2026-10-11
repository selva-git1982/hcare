import pytest
from hcare.scoring import PROFILES, assess, normalize, weighted_metrics

def test_illustrative_default():
    result = assess([.9, 1, .9, .9, 1], [1, .9, .85, .9, 1], PROFILES["Default"], {"audit": True})
    assert result["base_index"] == 93.5
    assert result["evidence_adjusted_index"] == 86.33
    assert result["eligible"]

def test_failed_gate_overrides_high_score():
    result = assess([1]*5, [1]*5, PROFILES["Default"], {"audit": False})
    assert result["base_index"] == 100
    assert not result["eligible"]

def test_normalization():
    assert normalize(200, 100) == 1
    assert normalize(200, 100, "lower") == .5
    assert weighted_metrics([{"value": 90, "target": 100}]) == .9

def test_invalid_weights():
    with pytest.raises(ValueError):
        assess([1]*5, [1]*5, [.1]*5, {})
