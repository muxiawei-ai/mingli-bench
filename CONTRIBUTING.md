# Contributing to MingLi-Bench

Thank you for helping improve MingLi-Bench. This project is intended to be a reusable engineering toolkit for Chinese metaphysics data, calendar helpers, chart fixtures, and LLM evaluation.

## Good First Contributions

- Add tests for Ganzhi, five elements, hour branches, lunar dates, or solar terms.
- Improve Bazi / Ziwei chart normalization.
- Add examples for CLI and Python API usage.
- Improve data validation and raw-data documentation.
- Add model provider adapters or benchmark result parsers.

## Development Setup

```bash
git clone https://github.com/DestinyLinker/MingLi-Bench.git
cd MingLi-Bench
python -m pip install -e .
python -m unittest discover -s tests
```

LLM evaluation commands require API keys and may incur cost. Please keep those tests out of the default unit test suite.

## Pull Request Checklist

- Keep changes focused and easy to review.
- Add or update tests for behavior changes.
- Update README or docs when adding public CLI/API features.
- Do not commit `.env`, API keys, model responses with private data, or generated benchmark logs unless they are explicitly intended as public fixtures.
- For data changes, explain source, format, and validation steps in the PR description.

## Project Scope

Accepted scope:

- Chinese calendar, Ganzhi, Bazi, Ziwei, and related reusable computation helpers.
- Dataset normalization and validation.
- LLM benchmark harnesses and model adapters.
- Reproducibility tooling for benchmark runs.

Out of scope:

- Consumer fortune-telling product UI.
- Paid prediction services.
- Claims of deterministic real-world predictive accuracy.

## Code Style

- Prefer pure functions for reusable calculation logic.
- Keep API boundaries small and documented.
- Avoid adding heavyweight dependencies unless they clearly improve correctness or maintainability.
- Keep generated artifacts out of source control by default.
