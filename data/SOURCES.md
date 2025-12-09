# Data sources

The repository does not vend full raw data. The script `scripts/pull_and_model.py` downloads
public, well-documented datasets directly from their maintainers:

- **Homicide rates (per 100k)**: Our World in Data grapher endpoint based on IHME/GBD 2019 estimates.
  URL: https://ourworldindata.org/grapher/homicide-rate.csv
- **Income inequality (Gini, World Bank)**: Our World in Data grapher endpoint for the World Bank Gini series.
  URL: https://ourworldindata.org/grapher/gini-index.csv
- **Population**: Our World in Data population series (UN/World Bank harmonized).
  URL: https://ourworldindata.org/grapher/population.csv
- **Youth unemployment**: ILO modeled estimate via OWID.
  URL: https://ourworldindata.org/grapher/youth-unemployment-rate.csv
- **Urban population share**: World Bank urbanization share via OWID.
  URL: https://ourworldindata.org/grapher/urban-population-share.csv
- **GDP per capita (PPP)**: Maddison Project 2020 series via OWID.
  URL: https://ourworldindata.org/grapher/gdp-per-capita-maddison-2020.csv

When offline or if endpoints move, the repository includes small, documented fallback
samples in `data/raw/` to keep the demo workflow functional. Downloaded (or fallback)
files are cached locally under `data/` when you run the script.
