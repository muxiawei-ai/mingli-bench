# Open Source Release Plan

## Recommended Repository Name

Recommended: `mingli-bench`

Alternative names:

- `mingli-toolkit`
- `bazi-ziwei-bench`
- `chinese-metaphysics-bench`

`mingli-bench` is the best fit for the current codebase because the repository already combines benchmark data, chart fixtures, CLI tooling, and reusable helper APIs.

## GitHub Repository Description

Chinese metaphysics benchmark and reusable Bazi/Ziwei chart utilities for LLM evaluation, Ganzhi helpers, and developer tooling.

## Attribution Positioning

This project should explicitly disclose that it is derived from `DestinyLinker/MingLi-Bench` and references `iztro` for pre-computed chart fixtures. The recommended wording is:

```text
This repository is derived from DestinyLinker/MingLi-Bench and extends the project toward reusable Chinese metaphysics data utilities, CLI/API tooling, and reproducible LLM evaluation. Pre-computed chart fixtures reference iztro-generated Bazi/Ziwei data. See ATTRIBUTION.md for details.
```

## GitHub Topics

```text
bazi
ziwei-doushu
chinese-calendar
ganzhi
four-pillars
llm-evaluation
benchmark
openrouter
python
cli
dataset
traditional-chinese
metaphysics
developer-tools
ai-evaluation
```

## Release v0.1.0 Draft

Title:

```text
v0.1.0 - Initial open-source toolkit release
```

Body:

```markdown
## Highlights

This is the first engineering-oriented open-source release of MingLi-Bench.

MingLi-Bench provides reusable Chinese metaphysics data utilities and LLM benchmark tooling for Bazi (八字), Ziwei Doushu (紫微斗数), and structured fortune-telling evaluation.

## Added

- 160 normalized benchmark questions from 2022-2025.
- Pre-computed Bazi and Ziwei chart fixtures keyed by `case_id`.
- `mingli_bench.calendar` pure helpers:
  - sexagenary cycle names and indexes,
  - Chinese double-hour earthly branch lookup,
  - Bazi four-pillar parsing,
  - five-element counting.
- `mingli_bench.charts` utilities for chart fixture extraction and normalization.
- CLI utilities:
  - `--stats`,
  - `--hour-branch`,
  - `--analyze-pillars`,
  - `--show-chart`.
- LLM benchmark runner with provider routing.
- Unit tests for calendar helpers and chart utilities.
- MIT license, contributing guide, changelog, issue templates, and PR template.
- Attribution notes for the upstream MingLi-Bench repository, iztro chart fixtures, and source question materials.

## Notes

Full lunar / solar date conversion, 24 solar-term calculation, and direct Bazi pillar derivation from Gregorian birth data are roadmap items. The current release focuses on benchmark reproducibility, chart fixture extraction, and small reusable primitives.

## Quick Start

```bash
python -m pip install -e .
python -m unittest discover -s tests
python -m mingli_bench.cli --show-chart case_1
```
```

## OpenAI Codex for Open Source Application Copy

```text
项目名称：MingLi-Bench

项目地址：https://github.com/muxiawei-ai/mingli-bench

项目简介：
MingLi-Bench 是一个面向中文命理、八字、紫微斗数与大模型评测的开源工程项目。它不是消费级算命应用，而是一个开发者工具库和 benchmark：提供标准化命理题目数据、预排八字/紫微命盘 fixture、干支/时辰/四柱解析等可测试纯函数、CLI 工具，以及用于比较 LLM 在中文命理推理任务上表现的评测框架。

开源价值：
中文历法、干支、八字和紫微斗数相关工具长期分散在私有应用、临时脚本或不可复现实验中。MingLi-Bench 希望把这些能力拆成可审计、可测试、可复用的工程模块：一方面服务中文文化与传统知识计算的开源生态，另一方面为 LLM 在非英语、专业规则密集型任务上的评测提供可复现基准。

当前已完成：
- 160 道 2022-2025 年标准化命理选择题；
- 预排八字和紫微斗数命盘数据；
- Python CLI，用于数据统计、命盘查看、时辰地支查询和四柱解析；
- 可测试的干支、时辰、八字四柱、五行统计纯函数；
- 多模型 LLM benchmark runner；
- MIT License、README、CONTRIBUTING、CHANGELOG、issue/PR templates 和基础单元测试。

未来计划：
- 实现农历/公历转换；
- 实现二十四节气计算；
- 从公历出生时间直接推导年柱、月柱、日柱、时柱；
- 增加时区和出生地标准化；
- 增强紫微斗数命盘标准化 API；
- 建立公开的模型评测结果和可复现实验配置。

希望 Codex 支持的原因：
这个项目非常适合 Codex for Open Source：它需要持续做工程化重构、测试补齐、算法模块抽取、文档维护、CLI/API 设计和 benchmark reproducibility。Codex 可以帮助把现有数据和脚本逐步整理成真正稳定、可维护、对开发者有价值的开源工具库。
```
