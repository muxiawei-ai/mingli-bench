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
  - stable `ChartInput -> BaziChart` API for app and agent integrations,
  - lightweight local `MingLiAgent` service layer with optional LLM calls,
  - sexagenary cycle names and indexes,
  - earthly branch mapping for Chinese double-hours,
  - Bazi year/month/day/hour derivation from Gregorian date/time,
  - approximate 24 solar-term calculation for month boundaries,
  - benchmark birth-place normalization to timezone offsets,
  - Chinese lunar-date parsing and fixture-backed lunar/solar lookup,
  - Bazi four-pillar parsing,
  - five-element counting,
  - compact chart summary extraction.
- CLI utilities that do not require an LLM key:
  - dataset statistics,
  - hour branch lookup,
  - Bazi pillar analysis,
  - Gregorian date/time to Bazi chart output,
  - `ChartInput` JSON to stable `BaziChart` JSON output,
  - local agent prompt generation and optional LLM interpretation,
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
python -m mingli_bench.cli --lunar-date "一九八四年闰十月十七"
python -m mingli_bench.cli --lunar-from-solar 1978-04-05
python -m mingli_bench.cli --solar-from-lunar "一九七八年二月廿八"
python -m mingli_bench.cli --chart-input-json '{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾","country":"中国"}'
python -m mingli_bench.cli --agent-input-json '{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾"}' --agent-question "分析事业和性格"
python -m mingli_bench.cli agent --no-llm
mingli-bench agent --model google/gemini-2.5-pro
mingli-bench eval-agent --sample 10
mingli-bench eval-agent --model google/gemini-2.5-pro --sample 10
mingli-bench serve --port 8765
python -m mingli_bench.cli --show-chart case_1
```

`--agent-input-json` runs locally by default and returns the chart, a deterministic local report, and the LLM prompt. Add `--agent-model google/gemini-2.5-pro` or another supported model to call an actual LLM using your `.env` credentials.
Agent JSON results include a `trace` field for auditing input, chart building, local reporting, prompt construction, and LLM call/skip stages.
They also include an `interpretation` field using the `mingli_interpretation.v1` structured contract; local mode returns a deterministic scaffold, while LLM mode attempts to parse model JSON output into the same schema.
They also include an `intent` field that routes the user question into coarse domains such as career, wealth, relationship, health, personality, study, family, timing, or general analysis.

`mingli-bench agent` starts an interactive local agent. Use `--no-llm` to keep it fully local with a structured chart report, `--model` to call an LLM, and `--json` for machine-readable output.
Add `--show-prompt` when you want to inspect the full prompt sent to the model.

## Agent Evaluation

`eval-agent` runs benchmark cases through the local agent pipeline. By default it does not call an LLM, making it useful for checking chart generation, intent routing, intent/category alignment, trace completeness, and interpretation schema compliance:

```bash
mingli-bench eval-agent --sample 10
```

To evaluate real model output parsing:

```bash
mingli-bench eval-agent --model google/gemini-2.5-pro --sample 10
```

By default it saves:

- `summary.json`: aggregate metrics, distributions, and error samples.
- `records.jsonl`: one full agent result per benchmark case.

Use `--no-save` to print only the terminal summary.

## Local HTTP API

Start the local API server:

```bash
mingli-bench serve --port 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

By default, `/agent` stays fully local and does not call an LLM. To enable LLM interpretation, start the server with a model:

```bash
mingli-bench serve --model google/gemini-2.5-pro
```

Example requests:

```bash
curl http://127.0.0.1:8765/health

curl -X POST http://127.0.0.1:8765/agent \
  -H 'Content-Type: application/json' \
  -d '{"chart_input":{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾"},"question":"分析事业和性格"}'
```

Endpoints:

- `GET /`: local web UI.
- `GET /health`: service health check.
- `POST /chart`: accepts `ChartInput` and returns stable `BaziChart` JSON.
- `POST /agent`: accepts `chart_input` and optional `question`, then returns the chart, deterministic report, prompt, and optional LLM response.

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
from mingli_bench.agent import MingLiAgent
from mingli_bench.bazi import bazi_from_birth_info, bazi_from_gregorian
from mingli_bench.calendar import hour_branch, parse_bazi_pillars
from mingli_bench.chart_api import build_bazi_chart
from mingli_bench.charts import get_chart_summary
from mingli_bench.lunar import lunar_from_solar_date, parse_chinese_lunar_date

print(hour_branch(23))  # 子

chart = build_bazi_chart({
    "calendar_type": "solar",
    "year": 1978,
    "month": 4,
    "day": 5,
    "hour": 18,
    "minute": 0,
    "country": "中国",
    "location": "台湾",
})
print(chart.as_dict()["pillars_text"])  # 戊午 丙辰 丁酉 己酉
print(chart.day_master)                 # 丁

agent_result = MingLiAgent().run(
    {
        "calendar_type": "solar",
        "year": 1978,
        "month": 4,
        "day": 5,
        "hour": 18,
        "location": "台湾",
    },
    question="分析事业和性格",
)
print(agent_result.prompt)  # Local prompt, no LLM call unless a model client is provided.
print(agent_result.report.to_markdown())  # Deterministic local chart report.

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

lunar = parse_chinese_lunar_date("一九八四年闰十月十七")
print(lunar.as_dict())
print(lunar_from_solar_date("1978-04-05")["lunar_date"])  # 一九七八年二月廿八

bazi = parse_bazi_pillars("甲寅 戊辰 己亥 壬申")
print(bazi["day_master"])  # 己
print(bazi["five_elements_summary"])

summary = get_chart_summary("case_1")
print(summary["bazi"]["chinese_date"])
print(summary["ziwei"]["palaces"][0])
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

`mingli_bench.solar_terms` provides deterministic approximate solar-term datetimes by searching apparent solar longitude. It is suitable for developer tooling and regression tests, but it is not a high-precision ephemeris. Historical timezone/DST handling and full standalone lunar/solar conversion remain future work.

The Bazi year pillar follows the Li Chun convention. Around January/February, this can differ from chart sources that label the year by Lunar New Year.

`mingli_bench.chart_api` is the recommended application-facing API. It accepts solar or fixture-backed lunar `ChartInput` data and returns a stable `BaziChart` object with pillars, day master, five-element summary, timezone metadata, lunar metadata, source, and warnings.

`mingli_bench.agent` is the recommended first integration point for an actual fortune-telling agent. It keeps deterministic chart calculation local, then optionally calls an LLM for interpretation when a model client is configured.

`mingli_bench.locations` currently uses a small auditable alias table rather than a full geocoder. Ambiguous inputs such as `usa` fall back to UTC+8 and return warnings so callers can ask for a state/city or pass an explicit offset in future integrations.

`mingli_bench.lunar` currently parses Chinese lunar-date strings and provides fixture-backed lookup against `data/fortune_api_results.json`. It is not yet a full standalone lunar calendar conversion engine.

## Attribution

This project is derived from and references upstream open-source and data resources, including `DestinyLinker/MingLi-Bench`, `iztro`, and raw competition materials. See [ATTRIBUTION.md](./ATTRIBUTION.md) for details.

## Testing

```bash
python -m unittest discover -s tests
```

The test suite covers pure calendar helpers and chart fixture extraction. LLM API tests are intentionally not part of the default suite because they require credentials and can incur cost.

## Roadmap

- Keep hardening the stable `ChartInput -> BaziChart` API contract.
- Add higher-level agent conversation memory and follow-up question handling.
- Add a full standalone lunar / solar conversion engine.
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
