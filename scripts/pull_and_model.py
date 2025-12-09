"""Download public crime and inequality data and run a minimal regression demo.

The script intentionally stays close to the models described in RESEARCH_PLAN.md:
- Pull homicide-rate data (per 100k people) from Our World in Data (OWID).
- Pull Gini inequality series from OWID / World Bank.
- Construct a country-year panel and standardize the inequality predictor.
- Run a simple log-rate OLS with country and year fixed effects to test whether
  inequality is associated with homicide changes.

Usage examples (after installing dependencies from requirements.txt):
    python scripts/pull_and_model.py --summary
    python scripts/pull_and_model.py --save-data data/owid_crime_panel.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HOMICIDE_URL = (
    "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/"
    "Homicide%20Rate%20-%20Our%20World%20in%20Data/Homicide%20Rate%20-%20Our%20World%20in%20Data.csv"
)
GINI_URL = (
    "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/"
    "Gini%20coefficient%20(World%20Bank%20estimate)%20-%20World%20Bank/Gini%20coefficient%20(World%20Bank%20estimate)%20-%20World%20Bank.csv"
)


def _cache_csv(url: str, path: Path) -> Path:
    """Download a CSV if it is not already cached locally."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.read_csv(url)
        df.to_csv(path, index=False)
    return path


def load_raw(cache_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load homicide and inequality series, caching raw CSVs locally."""
    homicide_path = _cache_csv(HOMICIDE_URL, cache_dir / "owid_homicide_rate.csv")
    gini_path = _cache_csv(GINI_URL, cache_dir / "owid_gini.csv")

    homicide = pd.read_csv(homicide_path)
    gini = pd.read_csv(gini_path)
    return homicide, gini


def tidy_panel(homicide: pd.DataFrame, gini: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names, merge, and engineer analysis-ready variables."""
    homicide_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        "Homicide rate (IHME, GBD 2019)": "homicide_rate_per_100k",
    }
    gini_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        "Gini coefficient (World Bank estimate)": "gini_worldbank",
    }

    homicide = homicide.rename(columns=homicide_cols)
    gini = gini.rename(columns=gini_cols)

    # Keep only the columns we need
    homicide = homicide[["country", "iso_code", "year", "homicide_rate_per_100k"]]
    gini = gini[["country", "iso_code", "year", "gini_worldbank"]]

    merged = homicide.merge(gini, on=["country", "iso_code", "year"], how="inner")
    merged = merged.dropna(subset=["homicide_rate_per_100k", "gini_worldbank"])

    merged["log_homicide_rate"] = np.log(merged["homicide_rate_per_100k"].clip(lower=1e-6))
    merged["gini_std"] = (merged["gini_worldbank"] - merged["gini_worldbank"].mean()) / merged[
        "gini_worldbank"
    ].std(ddof=0)

    return merged


def run_model(panel: pd.DataFrame):
    """Fit a log-rate OLS with country and year fixed effects."""
    formula = "log_homicide_rate ~ gini_std + C(country) + C(year)"
    model = smf.ols(formula, data=panel).fit(cov_type="HC3")
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("data"), help="Where to cache downloaded CSVs.")
    parser.add_argument(
        "--save-data", type=Path, default=None, help="Optional path to save the merged, analysis-ready panel dataset."
    )
    parser.add_argument("--summary", action="store_true", help="Print model summary after fitting.")
    parser.add_argument("--head", action="store_true", help="Show the first few merged rows for inspection.")
    args = parser.parse_args()

    homicide, gini = load_raw(args.cache_dir)
    panel = tidy_panel(homicide, gini)

    if args.save_data:
        args.save_data.parent.mkdir(parents=True, exist_ok=True)
        panel.to_csv(args.save_data, index=False)

    if args.head:
        print(panel.head())

    if args.summary:
        model = run_model(panel)
        print(model.summary())


if __name__ == "__main__":
    main()
