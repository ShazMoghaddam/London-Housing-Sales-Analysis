# Changelog

All notable changes to this project are listed here. Versions are dated by month, like `v2026.11`.

## v2026.11 · November 2026

A full rebuild, from a single notebook into a tested, reproducible analysis.

### Fixed

- The "total sales across London" added up all 47 rows of the file, including the regions, England and Wales, so it
  was 24 times too big. Totals now use the London row, and tests check the boroughs add up to it
- The "highest growth borough" came out as England, and the README's answer was left as a placeholder
- Claims about Camden and Barnet are replaced with figures calculated from every borough

### Added

- A findings report with seven findings, written from the data by `findings/build.py`
- Six charts and two headline tiles, all drawn with [bezel-charts](https://pypi.org/project/bezel-charts/)
- Comparisons of the crash and recovery across every borough, Inner and Outer London, and the regions of England and Wales
- Tests, an automatic check on every pull request, Dependabot and a security policy
- Social preview image in `assets/social-preview.png`

### Changed

- New folder structure: `data/`, `findings/`, `notebooks/`, `charts/` and `tests/`
- README rewritten around the findings
- Notebook rewritten and moved to `notebooks/london_housing_analysis.ipynb`
- Data moved to `data/housing_sales_borough.csv`, unchanged

## June 2025

- First version: one notebook and a README
