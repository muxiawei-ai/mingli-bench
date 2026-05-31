# Changelog

All notable changes to MingLi-Bench will be documented in this file.

The format is inspired by Keep a Changelog, and this project uses semantic versioning once public releases begin.

## [Unreleased]

### Added

- GitHub Actions CI for Python 3.9-3.12.
- `mingli_bench.bazi` partial Bazi derivation:
  - Gregorian date to year pillar with documented approximate Li Chun boundary,
  - Gregorian date to day pillar,
  - late Zi-hour rollover at 23:00,
  - day stem + time to hour pillar,
  - `bazi_from_gregorian()` JSON-friendly helper.
- CLI flags:
  - `--bazi-date`,
  - `--bazi-time`.
- Fixture regression tests for Bazi day/hour pillars.

## [0.1.0] - 2026-05-31

### Added

- Initial open-source packaging direction for MingLi-Bench as a benchmark and reusable Chinese metaphysics data toolkit.
- Python package metadata via `pyproject.toml`.
- `mingli_bench.calendar` pure helpers:
  - sexagenary cycle names and indexes,
  - earthly branch lookup for Chinese double-hours,
  - Bazi four-pillar parsing,
  - five-element counting.
- `mingli_bench.charts` utilities for extracting Bazi and Ziwei summaries from pre-computed chart fixtures.
- CLI utilities:
  - `--hour-branch`,
  - `--analyze-pillars`,
  - `--show-chart`.
- Unit tests for calendar helpers and chart fixture extraction.
- Contributor guide and GitHub issue / PR templates.

### Changed

- README repositioned toward engineering reuse: calendar helpers, chart fixtures, CLI/API usage, benchmark reproducibility, and roadmap.

### Notes

- Full lunar / solar conversion and solar-term calculation are roadmap items, not yet implemented in this release.
