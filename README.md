# MingLi-Bench

Reusable Chinese metaphysics data utilities and LLM benchmark tooling for Bazi (八字), Ziwei Doushu (紫微斗数), and structured fortune-telling evaluation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![CI](https://github.com/muxiawei-ai/mingli-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/muxiawei-ai/mingli-bench/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Questions](https://img.shields.io/badge/Questions-160-green.svg)](./data/data.json)
[![Years](https://img.shields.io/badge/Years-2022--2025-orange.svg)](./data)

[中文](./README_zh.md)

## Why This Project Is Useful

Chinese calendar and metaphysics systems are often locked inside private apps, ad hoc scripts, or prompt-only demos. MingLi-Bench makes the computational pieces easier to inspect, test, and reuse:

- Normalized benchmark questions with birth metadata, event categories, options, and answers.
- Pre-computed Bazi and Ziwei chart fixtures that separate chart derivation from model reasoning.
- Small, testable Ganzhi and Bazi helper functions for developer workflows.
- A CLI for dataset inspection, chart lookup, pillar analysis, and LLM benchmark runs.
- A reproducible evaluation harness for comparing models, prompts, chart injection, and option shuffling.

The project is not positioned as a fortune-telling consumer app. It is a developer-facing toolkit and benchmark for Chinese calendar / metaphysics data workflows.

## Features

- 160 normalized multiple-choice benchmark questions from 2022-2025.
- Twelve event categories: career, health, marriage, family, wealth, personality, and more.
- Pre-computed Bazi and Ziwei chart data in `data/fortune_api_results.json`.
- Pure utility functions for:
  - sexagenary cycle names and indexes,
  - earthly branch mapping for Chinese double-hours,
  - Bazi year/month/day/hour derivation from Gregorian date/time,
  - approximate 24 solar-term calculation for month boundaries,
  - benchmark birth-place normalization to timezone offsets,
  - Bazi four-pillar parsing,
  - five-element counting,
  - compact chart summary extraction.
- CLI utilities that do not require an LLM key:
  - dataset statistics,
  - hour branch lookup,
  - Bazi pillar analysis,
  - Gregorian date/time to Bazi chart output,
  - chart summary lookup by `case_id`.
- LLM evaluation CLI with OpenRouter, OpenAI, Anthropic, Google, DeepSeek, and Doubao support.

## Installation

```bash
git clone https://github.com/muxiawei-ai/mingli-bench.git
cd mingli-bench
python -m pip install -e .
```

If you only want to run from source without installing the package:

```bash
python -m pip install -r requirements.txt
```

## CLI Usage

No API key required:

```bash
python -m mingli_bench.cli --stats
python -m mingli_bench.cli --hour-branch 23
python -m mingli_bench.cli --analyze-pillars "甲寅 戊辰 己亥 壬申"
python -m mingli_bench.cli --bazi-date 1974-04-28 --bazi-time 16:40
python -m mingli_bench.cli --bazi-date 1978-04-05 --bazi-time 18:00 --bazi-location 台湾
python -m mingli_bench.cli --bazi-case case_13
python -m mingli_bench.cli --show-chart case_1
```

Installed command form:

```bash
mingli-bench --stats
mingli-bench --show-chart case_1
```

LLM benchmark run:

```bash
cp .env.example .env
# Fill the provider key you plan to use.

python -m mingli_bench.cli \
  --model google/gemini-2.5-pro \
  --year 2025 \
  --cot \
  --astro \
  --sample 10
```

OpenRouter model ids such as `openai/gpt-4o`, `anthropic/claude-sonnet-4-6`, and `google/gemini-2.5-pro` are routed through OpenRouter automatically when the model name contains `/`.

## Python API Examples

```python
from mingli_bench.bazi import bazi_from_birth_info, bazi_from_gregorian
from mingli_bench.calendar import hour_branch, parse_bazi_pillars
from mingli_bench.charts import get_chart_summary

print(hour_branch(23))  # 子

bazi_chart = bazi_from_gregorian("1974-04-28", hour=16, minute=40)
print(bazi_chart["year_pillar"])   # 甲寅
print(bazi_chart["month_pillar"])  # 戊辰
print(bazi_chart["day_pillar"])    # 己亥
print(bazi_chart["hour_pillar"])   # 壬申

birth_info_chart = bazi_from_birth_info({
    "year": 1978,
    "month": 4,
    "day": 5,
    "hour": 18,
    "minute": 0,
    "country": "中国",
    "location": "台湾",
    "calendar_type": "solar",
})
print(birth_info_chart["timezone"]["timezone"])  # Asia/Taipei

bazi = parse_bazi_pillars("甲寅 戊辰 己亥 壬申")
print(bazi["day_master"])  # 己
print(bazi["five_elements_summary"])

chart = get_chart_summary("case_1")
print(chart["bazi"]["chinese_date"])
print(chart["ziwei"]["palaces"][0])
```

## Dataset

| File | Description |
|---|---|
| `data/data.json` | Normalized benchmark questions, options, answers, categories, and birth metadata. |
| `data/fortune_api_results.json` | Pre-computed Bazi and Ziwei chart fixtures keyed by `case_id`. |
| `data/raw/` | Raw yearly source text files. |

The chart fixtures are generated externally and are treated as data fixtures in this repository. The current Python utilities extract and normalize them, and the core library can derive Bazi pillars from Gregorian birth data in a fixed UTC+8 calendar context.

### Current Bazi Calculation Scope

`mingli_bench.bazi` currently implements:

- year pillar from Gregorian date/time using the calculated Li Chun boundary,
- month pillar from the 12 major solar-term boundaries,
- day pillar with fixture-validated continuous sexagenary day cycle,
- late Zi-hour day rollover at 23:00,
- hour pillar from day stem and time.
- birth-place normalization for the locations present in the benchmark fixtures.

`mingli_bench.solar_terms` provides deterministic approximate solar-term datetimes by searching apparent solar longitude. It is suitable for developer tooling and regression tests, but it is not a high-precision ephemeris. Historical timezone/DST handling and lunar/solar date conversion remain future work.

The Bazi year pillar follows the Li Chun convention. Around January/February, this can differ from chart sources that label the year by Lunar New Year.

`mingli_bench.locations` currently uses a small auditable alias table rather than a full geocoder. Ambiguous inputs such as `usa` fall back to UTC+8 and return warnings so callers can ask for a state/city or pass an explicit offset in future integrations.

## Attribution

This project is derived from and references upstream open-source and data resources, including `DestinyLinker/MingLi-Bench`, `iztro`, and raw competition materials. See [ATTRIBUTION.md](./ATTRIBUTION.md) for details.

## Testing

```bash
python -m unittest discover -s tests
```

The test suite covers pure calendar helpers and chart fixture extraction. LLM API tests are intentionally not part of the default suite because they require credentials and can incur cost.

## Roadmap

- Add pure lunar / solar date conversion utilities.
- Expand solar-term validation fixtures and boundary-case coverage.
- Expand birthplace normalization beyond bundled fixture locations.
- Add explicit timezone-offset override and historical DST policy hooks.
- Add richer Ziwei chart normalization APIs.
- Add model-response caching and deterministic benchmark run manifests.
- Publish package builds to PyPI once the API stabilizes.

## Contributing

Contributions are welcome. Good first contributions include:

- adding calendar and Ganzhi test fixtures,
- improving chart normalization,
- adding documentation examples,
- adding model evaluation adapters,
- validating data records and raw-data provenance.

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull request.

## License

MIT License. See [LICENSE](./LICENSE).
