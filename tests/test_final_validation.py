"""Final reproducible functional checks for the H-CARE research prototype."""
from hcare.scoring import PROFILES, assess

SCORES = [0.90, 1.00, 0.90, 0.90, 1.00]
CONFIDENCE = [1.00, 0.90, 0.85, 0.90, 1.00]


def test_paper_example():
    result = assess(SCORES, CONFIDENCE, PROFILES['Default'], {'audit': True, 'recovery': True})
    assert result['base_index'] == 93.50
    assert result['evidence_adjusted_index'] == 86.33
    assert result['evidence_gap'] == 7.17
    assert result['eligible'] is True


def test_mandatory_gate_failure_cannot_be_offset_by_score():
    result = assess(SCORES, CONFIDENCE, PROFILES['Default'], {'audit': False, 'recovery': True})
    assert result['base_index'] == 93.50
    assert result['evidence_adjusted_index'] == 86.33
    assert result['eligible'] is False
    assert 'audit' in result['failed_gates']
    assert result['status'] == 'Not eligible under current assessment profile'


def test_evidence_confidence_reduces_adjusted_index():
    complete = assess(SCORES, [1.0]*5, PROFILES['Default'], {'audit': True})
    partial = assess(SCORES, CONFIDENCE, PROFILES['Default'], {'audit': True})
    assert complete['evidence_adjusted_index'] == complete['base_index']
    assert partial['evidence_adjusted_index'] < complete['evidence_adjusted_index']
