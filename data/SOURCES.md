# Data sources

The repository does not vend raw data. The script `scripts/pull_and_model.py` downloads
public, well-documented datasets directly from their maintainers:

- **Homicide rates (per 100k)**: Our World in Data dataset based on IHME/GBD 2019 estimates.
  URL: https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Homicide%20Rate%20-%20Our%20World%20in%20Data/Homicide%20Rate%20-%20Our%20World%20in%20Data.csv
- **Income inequality (Gini, World Bank)**: Our World in Data dataset sourced from the World Bank.
  URL: https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Gini%20coefficient%20(World%20Bank%20estimate)%20-%20World%20Bank/Gini%20coefficient%20(World%20Bank%20estimate)%20-%20World%20Bank.csv

To keep the repository lean, downloaded files are cached locally under `data/` when you run the script.
