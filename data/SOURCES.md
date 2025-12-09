# Data sources

The repository does not vend full raw data. The script `scripts/pull_and_model.py` downloads
public, well-documented datasets directly from their maintainers:

- **Homicide rates (per 100k)**: Our World in Data grapher endpoint based on IHME/GBD 2019 estimates.
  URL: https://ourworldindata.org/grapher/homicide-rate.csv
- **Income inequality (Gini, World Bank)**: Our World in Data grapher endpoint for the World Bank Gini series.
  URL: https://ourworldindata.org/grapher/gini-index.csv

When offline or if endpoints move, the repository includes small, documented fallback
samples in `data/raw/` to keep the demo workflow functional. Downloaded (or fallback)
files are cached locally under `data/` when you run the script.
