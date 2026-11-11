"""
Estimacion de elasticidad-precio de la demanda, por mercado.

Tres estimadores, en orden creciente de cuidado:

1. log-log ingenuo         log(q) ~ log(p)
2. log-log con controles   log(q) ~ log(p) + estacionalidad + tendencia + choques
3. efectos fijos           log(q) ~ log(p) + dummies de mercado, sobre el panel

El punto del modulo no es correr una regresion. Es mostrar por que el
estimador ingenuo se equivoca de forma sistematica: el precio no se mueve al
azar, se mueve con la temporada, y si no se controla la estacionalidad el
coeficiente de precio absorbe parte de ella. El sesgo tiene direccion
predecible y aqui se mide contra la elasticidad verdadera del simulador.

Esa es la parte que le importa a un area de Revenue Management: no el numero,
sino cuanto confiar en el numero.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class OLSResult:
    """Ordinary least squares coefficients and classical standard errors."""
    params: pd.Series
    bse: pd.Series


def _fit_ols(y, features) -> OLSResult:
    features = pd.DataFrame(features).astype(float)
    design = np.column_stack([np.ones(len(features)), features.to_numpy()])
    y = np.asarray(y, dtype=float)
    beta, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank != design.shape[1] or len(y) <= rank:
        raise ValueError("OLS needs a full-rank design and positive residual degrees of freedom")
    residual = y - design @ beta
    inverse = np.linalg.pinv(design)
    covariance = (residual @ residual / (len(y)-rank)) * (inverse @ inverse.T)
    names = ["const", *features.columns]
    return OLSResult(pd.Series(beta, index=names), pd.Series(np.sqrt(np.maximum(np.diag(covariance), 0)), index=names))

from generate_data import generate_panel, true_elasticities


def naive_loglog(df: pd.DataFrame) -> float:
    """Elasticidad sin controles. Sesgada cuando el precio covaria con la demanda."""
    model = _fit_ols(np.log(df["units"].to_numpy()), {"log_price": np.log(df["price"].to_numpy())})
    return float(model.params["log_price"])


def controlled_loglog(df: pd.DataFrame) -> tuple[float, float, OLSResult]:
    """Elasticidad controlando estacionalidad, tendencia y choques exogenos.

    La estacionalidad entra como armonicos de Fourier en lugar de 52 dummies
    semanales: mismo poder explicativo con dos ordenes de magnitud menos de
    parametros, que es lo que permite estimar por mercado sin quedarse sin
    grados de libertad.
    """
    d = df.copy().reset_index(drop=True)
    woy = d["week_of_year"].to_numpy()

    features = {
        "log_price": np.log(d["price"].to_numpy()),
        "trend": np.arange(len(d)) / len(d),
        "weather_shock": d["weather_shock"].to_numpy(),
    }
    for k in (1, 2):
        features[f"sin{k}"] = np.sin(2 * np.pi * k * woy / 52.0)
        features[f"cos{k}"] = np.cos(2 * np.pi * k * woy / 52.0)

    model = _fit_ols(np.log(d["units"].to_numpy()), features)
    beta = float(model.params["log_price"])
    stderr = float(model.bse["log_price"])
    return beta, stderr, model


def fixed_effects_panel(panel: pd.DataFrame) -> float:
    """Elasticidad promedio del panel con efectos fijos de mercado."""
    d = panel.copy()
    woy = d["week_of_year"].to_numpy()
    X = pd.DataFrame(
        {
            "log_price": np.log(d["price"].to_numpy()),
            "weather_shock": d["weather_shock"].to_numpy(),
            "sin1": np.sin(2 * np.pi * woy / 52.0),
            "cos1": np.cos(2 * np.pi * woy / 52.0),
        }
    )
    X = pd.concat([X, pd.get_dummies(d["market"], prefix="mkt", drop_first=True).astype(float).reset_index(drop=True)], axis=1)
    model = _fit_ols(np.log(d["units"].to_numpy()), X)
    return float(model.params["log_price"])


def estimate_all(panel: pd.DataFrame) -> pd.DataFrame:
    truth = true_elasticities()
    out = []
    for market, g in panel.groupby("market"):
        naive = naive_loglog(g)
        controlled, stderr, _ = controlled_loglog(g)
        lo, hi = controlled - 1.96 * stderr, controlled + 1.96 * stderr
        out.append(
            {
                "market": market,
                "true": truth[market],
                "naive": round(naive, 3),
                "controlled": round(controlled, 3),
                "ci_low": round(lo, 3),
                "ci_high": round(hi, 3),
                "truth_in_ci": bool(lo <= truth[market] <= hi),
                "naive_bias": round(naive - truth[market], 3),
                "controlled_bias": round(controlled - truth[market], 3),
            }
        )
    return pd.DataFrame(out)


if __name__ == "__main__":
    panel = generate_panel()
    results = estimate_all(panel)

    print("\nElasticidad-precio por mercado (verdad conocida por simulacion)\n")
    print(results.to_string(index=False))

    print(f"\nSesgo absoluto medio, estimador ingenuo:    {results['naive_bias'].abs().mean():.3f}")
    print(f"Sesgo absoluto medio, estimador controlado: {results['controlled_bias'].abs().mean():.3f}")
    print(f"Cobertura del IC al 95%: {results['truth_in_ci'].sum()}/{len(results)} mercados")
    print(f"\nElasticidad de panel con efectos fijos: {fixed_effects_panel(panel):.3f}")
    print(f"Promedio simple de las elasticidades verdaderas: {results['true'].mean():.3f}")
