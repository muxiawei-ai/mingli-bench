# Changelog

All notable changes to MingLi-Bench will be documented in this file.

The format is inspired by Keep a Changelog, and this project uses semantic versioning once public releases begin.

## [Unreleased]

### Added

- GitHub Actions CI for Python 3.9-3.12.
- `mingli_bench.solar_terms` approximate 24 solar-term calculation based on apparent solar longitude.
- `mingli_bench.locations` timezone normalization for benchmark birth-place strings.
- `mingli_bench.lunar` Chinese lunar-date parser and fixture-backed lunar/solar lookup.
- `mingli_bench.chart_api` stable `ChartInput -> BaziChart` API for application and agent integrations.
- `mingli_bench.agent` lightweight local agent layer with optional LLM interpretation.
- `mingli_bench.report` deterministic local report layer for chart summaries, five-element profiles, caveats, and follow-up questions.
- `mingli_bench.api` lightweight local HTTP API with `/health`, `/chart`, and `/agent`.
- Local web UI served at `/` by `mingli-bench serve`.
- Agent run trace metadata for input, chart, report, prompt, and LLM stages.
- `mingli_bench.interpretation` structured `mingli_interpretation.v1` contract for local and LLM interpretations.
- `mingli_bench.intent` rule-based user-question routing for Agent domain hints.
- `mingli_bench.agent_eval` and `eval-agent` CLI for pipeline-level Agent evaluation.
- Intent/category alignment diagnostics in Agent evaluation summaries.
- Benchmark-option-aware intent routing with expanded Chinese domain keywords.
- Generic `LLM_API_KEY`, `LLM_MODEL`, and `LLM_BASE_URL` env var compatibility for local Agent setups.
- `requirements-openrouter.txt` and optional OpenRouter dependency extra for lighter LLM eval installs.
- Answer-choice extraction, parse-rate, and accuracy metrics for benchmark-backed Agent evaluations.
- Option-score interpretation contract fields and option-by-option prompt guidance for A-D benchmark questions.
- More robust OpenAI-compatible response text extraction, including empty-content diagnostics and optional OpenRouter reasoning controls.
- `mingli_bench.bazi` Bazi derivation:
  - Gregorian date/time to year pillar with calculated Li Chun boundary,
  - Gregorian date/time to month pillar with major solar-term boundaries,
  - Gregorian date to day pillar,
  - late Zi-hour rollover at 23:00,
  - day stem + time to hour pillar,
  - `bazi_from_birth_info()` helper for benchmark records,
  - `bazi_from_gregorian()` JSON-friendly helper.
- CLI flags:
  - `--bazi-date`,
  - `--bazi-time`,
  - `--bazi-location`,
  - `--bazi-country`,
  - `--bazi-case`,
  - `--lunar-date`,
  - `--lunar-from-solar`,
  - `--solar-from-lunar`,
  - `--chart-input-json`,
  - `--agent-input-json`,
  - `--agent-question`,
  - `--agent-model`,
  - interactive `agent` command with `--no-llm`, `--json`, and `--show-prompt`.
  - `serve` command with `--host`, `--port`, and `--api-model`.
- Fixture regression tests for Bazi month/day/hour pillars, location normalization, lunar-date lookup, the stable chart API, and the local agent layer.

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
