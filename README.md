# mathinsociology

A minimal repository for quantitative sociology experiments. See `RESEARCH_PLAN.md` for a data-first blueprint on linking social
structure, crime, and deviance using only official statistics and transparent statistical models.

## Quickstart: run a real-data demo

**One-touch launcher (recommended for presentations)**

```bash
python scripts/run_demo.py --offline-only --open
```

This single command caches data (or uses bundled samples if you are offline), saves the merged
panel to `data/owid_crime_panel.csv`, prints the regression summary, and opens the static
presentation deck at `build/presentation.html`.

**Manual steps**

1. Install dependencies (requires internet access the first time):
   ```bash
   pip install -r requirements.txt
   ```
   If you are offline or behind a restrictive proxy, skip this step and rely on the bundled
   sample CSVs in `data/raw/` (the scripts will pick them up automatically if downloads fail).
2. Run the downloader/model script against publicly hosted datasets (or the bundled fallbacks):
   ```bash
   python scripts/pull_and_model.py --head --summary --save-data data/owid_crime_panel.csv --offline-only
   ```
   - Pulls homicide rates (IHME/GBD via Our World in Data), World Bank Gini inequality, population,
     youth unemployment, urbanization share, and GDP per capita (PPP).
   - Caches raw CSVs under `data/` (or writes the bundled fallbacks there) and saves a merged
     country-year panel with standardized predictors.
   - The model output tests whether inequality correlates with homicide rate changes while controlling
     for demography, urbanicity, income, and country/year effects.

See `data/SOURCES.md` for the exact URLs used. The script aligns with the hypotheses and models in `RESEARCH_PLAN.md` so you can
move from plan to executable analysis with real, well-documented data.

## Presentable UI-style HTML

Generate a static, presentation-ready page with plots, equations, and the regression headline:

```bash
python scripts/presentation_app.py --output build/presentation.html --open
```

The HTML uses Plotly (CDN) for interactive charts and MathJax for equations, so you can present from a browser without running
live notebooks.
