# Pricing and demand simulation

A small, anonymous study of **how changing prices could affect demand and revenue across five markets**. All data is generated locally; there are no client records or measured business outcomes.

## How it works

1. **Generate demand** (`src/generate_data.py`): 182 weeks for five markets, with known price sensitivities, seasonal patterns, trends and weather shocks.
2. **Estimate sensitivity** (`src/elasticity.py`): compare a naive log-log regression with a regression including seasonal/trend/weather controls. NumPy computes OLS coefficients and classical standard errors; this is the same regression specification as the archived statsmodels version.
3. **Choose prices** (`src/optimize_prices.py`): a binary integer program selects one candidate price per market. It maximizes modeled revenue while limiting changes to 15%, allowing at most two changes larger than 10%, and retaining at least 97% of baseline volume. SciPy's bundled HiGHS solver runs the program; no separate PuLP/CBC installation is needed.
4. **Demonstrate experiment analysis** (`src/experiment.py`): a separate synthetic A/B example illustrates sample sizing, mean comparisons and CUPED variance reduction.

Elasticity describes demand sensitivity. With elasticity -2, a 5% price cut predicts demand multiplied by `0.95**-2`, approximately 1.108, and revenue multiplied by `0.95**-1`, approximately 1.053. That is the intuition behind a price cut increasing revenue when demand is sufficiently elastic.

## Run the core

On this machine, Python 3.13 already has the numerical dependencies:

```powershell
py -3.13 src/generate_data.py
py -3.13 src/elasticity.py
py -3.13 src/optimize_prices.py
py -3.13 src/experiment.py
```

For a fresh environment, install `requirements-core.txt`. From this project folder, the shared local test runner can be used without downloading packages again:

```powershell
$env:PYTHONPATH = (Resolve-Path '..\..\_workspace\runtime\python314\core').Path
py -3.13 -m pytest -q
```

The shared directory supplies pure-Python pytest; numerical calculations use Python 3.13's existing NumPy, pandas and SciPy. It is not a portable bundled environment.

## Checked results

**11 tests passed**, including an independent SciPy regression reference and a known-optimum/infeasible-solver check. The 910-row simulation reproduces **+12.22% modeled revenue** and **+31.07% modeled volume**. Numerical results and dependency versions are in [reports/verification.json](reports/verification.json).

These are scenario projections relative to a baseline built from the last 13 weeks' mean price and mean units. Costs, capacity, competing markets and estimation uncertainty are not optimized. Some elasticity intervals cross the threshold at which the preferred price direction changes. One simulation's recovery of known elasticities does not establish real-world causal identification or repeated-sample interval coverage.

## Optional forecasting

`src/forecast.py` and `src/figures.py` retain the XGBoost/MLflow/SHAP workflow. Install `requirements.txt` for those optional tools. Their training, tracking, explanations and historical PNG figures were **not rerun or validated** during this recovery.

The implemented evaluation is conditional rolling **one-week prediction within 13-week blocks**, using observed earlier demand inside each block. Current price/weather inputs are assumed available. It is not a fixed-origin forecast of the next quarter.

The A/B generator independently injects a user-revenue uplift; it does not simulate the optimizer's price intervention. Its different effect cannot validate or contradict the elasticity-based price plan. Large-sample intervals are approximate; an A/A test may reject by chance.

Original files are preserved under ignored `.private/backups/`. Markets are neutral labels; mandatory MIT attribution is retained in `LICENSE`. No CV or interview material is included.
