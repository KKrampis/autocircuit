import importlib.util
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).parents[1] / "detect_numeric_phase_boundaries.py"
SPEC = importlib.util.spec_from_file_location("phase_detection", MODULE_PATH)
PHASES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PHASES)


def test_exact_segmentation_recovers_known_three_phase_signal():
    signal = np.vstack(
        [
            np.zeros((5, 2)),
            np.full((6, 2), 5.0),
            np.full((7, 2), -3.0),
        ]
    )

    boundaries, cost = PHASES.exact_segmentation(
        signal,
        n_boundaries=2,
        min_segment_size=3,
    )

    assert boundaries == [5, 11]
    assert abs(cost) < 1e-10


def test_zero_boundary_model_returns_single_segment():
    signal = np.arange(20, dtype=float).reshape(10, 2)

    boundaries, cost = PHASES.exact_segmentation(
        signal,
        n_boundaries=0,
        min_segment_size=3,
    )

    assert boundaries == []
    assert cost > 0
