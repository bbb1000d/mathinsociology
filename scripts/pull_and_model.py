"""Download public crime and inequality data and run a minimal regression demo.

The script intentionally stays close to the models described in RESEARCH_PLAN.md:
- Pull homicide-rate data (per 100k people) from Our World in Data (OWID).
- Pull Gini inequality series from OWID / World Bank.
- Construct a country-year panel and standardize the inequality predictor.
- Run a simple log-rate OLS with country and year fixed effects to test whether
  inequality is associated with homicide changes.

Usage examples (after installing dependencies from requirements.txt):
    python scripts/pull_and_model.py --summary --offline-only
    python scripts/pull_and_model.py --save-data data/owid_crime_panel.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HOMICIDE_URL = "https://ourworldindata.org/grapher/homicide-rate.csv"
GINI_URL = "https://ourworldindata.org/grapher/gini-index.csv"
# Extra socio-economic controls so the panel is richer and still fully public.
POPULATION_URL = "https://ourworldindata.org/grapher/population.csv"
YOUTH_UNEMP_URL = "https://ourworldindata.org/grapher/youth-unemployment-rate.csv"
URBAN_SHARE_URL = "https://ourworldindata.org/grapher/urban-population-share.csv"
GDP_PC_URL = "https://ourworldindata.org/grapher/gdp-per-capita-maddison-2020.csv"

# Bundled samples keep the workflow functional when internet access is blocked or
# OWID endpoint names change. They mirror the column names of the live series.
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
HOMICIDE_FALLBACK = SAMPLE_DIR / "owid_homicide_rate_sample.csv"
GINI_FALLBACK = SAMPLE_DIR / "owid_gini_worldbank_sample.csv"
POPULATION_FALLBACK = SAMPLE_DIR / "owid_population_sample.csv"
YOUTH_UNEMP_FALLBACK = SAMPLE_DIR / "owid_youth_unemployment_sample.csv"
URBAN_SHARE_FALLBACK = SAMPLE_DIR / "owid_urban_share_sample.csv"
GDP_PC_FALLBACK = SAMPLE_DIR / "owid_gdp_per_capita_sample.csv"


def _cache_csv(url: str, path: Path, fallback: Path, offline_only: bool = False) -> Path:
    """Download a CSV if not cached; fall back to bundled sample when offline."""
    if path.exists():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    if not offline_only:
        try:
            df = pd.read_csv(url)
            df.to_csv(path, index=False)
            return path
        except Exception as exc:  # pragma: no cover - defensive path
            print(
                f"Could not download {url}: {exc}\nUsing bundled fallback at {fallback} instead."
            )

    if not fallback.exists():
        raise FileNotFoundError(f"Fallback file {fallback} is missing. Please provide data manually.")
    fallback_df = pd.read_csv(fallback)
    fallback_df.to_csv(path, index=False)
    return path


def load_raw(cache_dir: Path, offline_only: bool = False) -> Dict[str, pd.DataFrame]:
    """Load raw series with caching; stays functional when offline."""

    paths = {
        "homicide": _cache_csv(HOMICIDE_URL, cache_dir / "owid_homicide_rate.csv", HOMICIDE_FALLBACK, offline_only),
        "gini": _cache_csv(GINI_URL, cache_dir / "owid_gini.csv", GINI_FALLBACK, offline_only),
        "population": _cache_csv(POPULATION_URL, cache_dir / "population.csv", POPULATION_FALLBACK, offline_only),
        "youth_unemp": _cache_csv(
            YOUTH_UNEMP_URL, cache_dir / "youth_unemployment.csv", YOUTH_UNEMP_FALLBACK, offline_only
        ),
        "urban_share": _cache_csv(
            URBAN_SHARE_URL, cache_dir / "urban_population_share.csv", URBAN_SHARE_FALLBACK, offline_only
        ),
        "gdp_pc": _cache_csv(GDP_PC_URL, cache_dir / "gdp_per_capita.csv", GDP_PC_FALLBACK, offline_only),
    }

    return {name: pd.read_csv(path) for name, path in paths.items()}


def tidy_panel(raw: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Standardize column names, merge, and engineer analysis-ready variables."""
    homicide = raw["homicide"]
    gini = raw["gini"]
    population = raw["population"]
    youth_unemp = raw["youth_unemp"]
    urban_share = raw["urban_share"]
    gdp_pc = raw["gdp_pc"]
    homicide_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        # OWID homicide headers vary across downloads; we coalesce below.
        "Homicide rate (IHME, GBD 2019)": "homicide_rate_per_100k",
        "Homicide rate (IHME, GBD 2019) - Sex: Both - Age: Age-standardized": "homicide_rate_per_100k",
    }
    gini_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        "Gini coefficient (World Bank estimate)": "gini_worldbank",
    }
    population_cols = {"Entity": "country", "Code": "iso_code", "Year": "year", "Population": "population"}
    youth_unemp_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        "Youth unemployment rate (modeled ILO estimate)": "youth_unemployment_rate",
    }
    urban_share_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        "Urban population (% of total population)": "urban_population_share",
    }
    gdp_pc_cols = {
        "Entity": "country",
        "Code": "iso_code",
        "Year": "year",
        "GDP per capita, PPP (Maddison Project Database 2020)": "gdp_per_capita_ppp",
    }

    # Some CSV variants split the homicide column at the comma when not quoted or
    # append age/sex qualifiers. Coalesce those into a single column before
    # renaming so both the online and bundled offline samples work uniformly.
    if "Homicide rate (IHME, GBD 2019)" not in homicide.columns:
        candidates = [
            c
            for c in homicide.columns
            if "homicide" in c.lower() and "rate" in c.lower()
        ]
        if candidates:
            homicide = homicide.rename(columns={candidates[0]: "Homicide rate (IHME, GBD 2019)"})
        else:  # pragma: no cover - defensive guard for malformed CSVs
            raise KeyError(
                "Could not find a homicide rate column. Inspect the CSV headers and update tidy_panel coalescing logic."
            )

    homicide = homicide.rename(columns=homicide_cols)
    gini = gini.rename(columns=gini_cols)
    population = population.rename(columns=population_cols)
    youth_unemp = youth_unemp.rename(columns=youth_unemp_cols)
    urban_share = urban_share.rename(columns=urban_share_cols)
    gdp_pc = gdp_pc.rename(columns=gdp_pc_cols)

    homicide = homicide[["country", "iso_code", "year", "homicide_rate_per_100k"]]
    gini = gini[["country", "iso_code", "year", "gini_worldbank"]]
    population = population[["country", "iso_code", "year", "population"]]
    youth_unemp = youth_unemp[["country", "iso_code", "year", "youth_unemployment_rate"]]
    urban_share = urban_share[["country", "iso_code", "year", "urban_population_share"]]
    gdp_pc = gdp_pc[["country", "iso_code", "year", "gdp_per_capita_ppp"]]

    merged = homicide.merge(gini, on=["country", "iso_code", "year"], how="inner")
    for df in (population, youth_unemp, urban_share, gdp_pc):
        merged = merged.merge(df, on=["country", "iso_code", "year"], how="left")

    merged = merged.dropna(subset=["homicide_rate_per_100k", "gini_worldbank"])

    merged["homicide_per_person"] = merged["homicide_rate_per_100k"] / 100_000.0
    merged["homicide_count"] = merged["homicide_per_person"] * merged["population"].fillna(0)

    merged["log_homicide_rate"] = np.log(merged["homicide_rate_per_100k"].clip(lower=1e-6))
    merged["gini_std"] = (merged["gini_worldbank"] - merged["gini_worldbank"].mean()) / merged[
        "gini_worldbank"
    ].std(ddof=0)
    merged["youth_unemployment_rate"] = merged["youth_unemployment_rate"].astype(float)
    merged["urban_population_share"] = merged["urban_population_share"].astype(float)
    merged["gdp_per_capita_ppp"] = merged["gdp_per_capita_ppp"].astype(float)

    # Standardized covariates for comparability
    for col in ["youth_unemployment_rate", "urban_population_share", "gdp_per_capita_ppp"]:
        if merged[col].notna().any():
            merged[f"{col}_std"] = (merged[col] - merged[col].mean()) / merged[col].std(ddof=0)

    return merged


def run_model(panel: pd.DataFrame):
    """Fit a log-rate OLS with fixed effects and extra controls."""
    formula = "log_homicide_rate ~ gini_std + youth_unemployment_rate_std + urban_population_share_std + gdp_per_capita_ppp_std + C(country) + C(year)"
    model = smf.ols(formula, data=panel).fit(cov_type="HC3")
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("data"), help="Where to cache downloaded CSVs.")
    parser.add_argument("--offline-only", action="store_true", help="Skip downloads and rely solely on bundled samples.")
    parser.add_argument(
        "--save-data", type=Path, default=None, help="Optional path to save the merged, analysis-ready panel dataset."
    )
    parser.add_argument("--summary", action="store_true", help="Print model summary after fitting.")
    parser.add_argument("--head", action="store_true", help="Show the first few merged rows for inspection.")
    args = parser.parse_args()

    raw = load_raw(args.cache_dir, offline_only=args.offline_only)
    panel = tidy_panel(raw)

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
