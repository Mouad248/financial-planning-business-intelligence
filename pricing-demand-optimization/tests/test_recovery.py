"""Independent numerical reference and solver failure checks."""
import numpy as np
import pandas as pd
import pytest
from scipy.stats import linregress

from elasticity import _fit_ols
from optimize_prices import solve


def test_ols_matches_independent_simple_regression():
    x = np.arange(25, dtype=float)
    y = 2 + 3*x + np.sin(x)
    result = _fit_ols(y, {"x": x})
    reference = linregress(x, y)
    assert result.params["x"] == pytest.approx(reference.slope)
    assert result.bse["x"] == pytest.approx(reference.stderr)


def test_binary_solver_selects_known_optimum():
    candidates = pd.DataFrame([
        {"market": "A", "change": 0., "units": 100., "revenue": 100.},
        {"market": "A", "change": -.15, "units": 150., "revenue": 120.},
        {"market": "B", "change": 0., "units": 100., "revenue": 100.},
        {"market": "B", "change": -.15, "units": 140., "revenue": 140.},
    ])
    result = solve(candidates, max_big_moves=1)
    assert result["revenue"] == pytest.approx(240.)
    assert result["plan"].set_index("market").loc["B", "change"] == -.15
    with pytest.raises(RuntimeError, match="No optimal price plan"):
        solve(candidates, volume_floor_ratio=10)
