"""One-touch launcher that builds the dataset, fits models, and renders the deck.

This is the quickest way to show the pipeline working with real data. It
orchestrates the following steps:

1) Pull + cache public data (or use bundled samples with --offline-only).
2) Save the merged panel to data/owid_crime_panel.csv
3) Fit the regression and print a compact summary.
4) Generate build/presentation.html and optionally open it.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pull_and_model import load_raw, run_model, tidy_panel
from presentation_app import build_presentation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path("data"), help="Cache folder for CSVs.")
    parser.add_argument("--offline-only", action="store_true", help="Use bundled samples only; skip downloads.")
    parser.add_argument("--open", action="store_true", help="Open the generated presentation in a browser.")
    args = parser.parse_args()

    raw = load_raw(args.cache_dir, offline_only=args.offline_only)
    panel = tidy_panel(raw)
    panel_path = args.cache_dir / "owid_crime_panel.csv"
    panel.to_csv(panel_path, index=False)
    print(f"Saved merged panel to {panel_path}")

    model = run_model(panel)
    print(model.summary())

    output = Path("build/presentation.html")
    build_presentation(args.cache_dir, output, open_file=args.open, offline_only=args.offline_only)
    print(f"Presentation written to {output}")
    if args.open:
        print("Opening presentation... (make sure a browser is available)")

if __name__ == "__main__":
    main()
