# MingLi-Bench

面向八字、紫微斗数与中文命理评测的可复用数据工具库和 LLM benchmark 工具。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![CI](https://github.com/muxiawei-ai/mingli-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/muxiawei-ai/mingli-bench/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Questions](https://img.shields.io/badge/Questions-160-green.svg)](./data/data.json)
[![Years](https://img.shields.io/badge/Years-2022--2025-orange.svg)](./data)

[English](./README.md)

## 一句话介绍

MingLi-Bench 是一个工程化的中文命理数据与评测工具库，提供干支/时辰/八字基础函数、预排八字与紫微命盘数据、命理选择题 benchmark，以及可复现实验 CLI。

## 为什么有开源价值

中文历法和命理计算经常散落在私有应用、临时脚本或纯 prompt demo 里，难以测试、复用和比较。MingLi-Bench 的价值在于把这些能力拆成可审计的工程资产：

- 标准化题目数据：出生信息、问题、选项、答案、事件类别。
- 预排命盘数据：把“排盘是否准确”和“推理是否准确”解耦。
- 可测试纯函数：干支、时辰地支、四柱解析、五行统计。
- CLI 工具：无需模型 key 也能查数据、看命盘、解析四柱。
- LLM 评测框架：用于比较模型、prompt、命盘注入、选项打乱等实验设置。

这个项目不是消费级“算命娱乐应用”，而是面向开发者、研究者和开源贡献者的中文历法 / 命理数据工具与评测基准。

## 功能列表

- 160 道 2022-2025 年命理选择题。
- 十二类事件标签：事业、健康、婚姻、家庭、财运、性格等。
- `data/fortune_api_results.json` 中的预排八字和紫微斗数命盘。
- 核心工具函数：
  - 面向应用和 Agent 集成的稳定 `ChartInput -> BaziChart` API，
  - 本地轻量 `MingLiAgent` 服务层，并支持可选 LLM 调用，
  - 六十甲子名称与索引，
  - 24 小时制到十二时辰地支，
  - 从公历日期/时间推导八字年/月/日/时柱，
  - 用近似二十四节气计算月令边界，
  - benchmark 出生地到时区偏移的标准化，
  - 中文农历日期解析和基于 fixture 的农历/公历互查，
  - 八字四柱解析，
  - 五行数量统计，
  - 按 `case_id` 提取命盘摘要。
- CLI：
  - 数据集统计，
  - 时辰地支查询，
  - 四柱解析，
  - 公历日期/时间转八字输出，
  - `ChartInput` JSON 转稳定 `BaziChart` JSON 输出，
  - 本地 Agent prompt 生成和可选 LLM 解读，
  - case 命盘摘要，
  - 多模型 LLM benchmark。
- 支持 OpenRouter、OpenAI、Anthropic、Google、DeepSeek、豆包等模型接口。

## 安装

```bash
git clone https://github.com/muxiawei-ai/mingli-bench.git
cd mingli-bench
python -m pip install -e .
```

如果只想从源码目录运行：

```bash
python -m pip install -r requirements.txt
```

## CLI 使用

无需 API key：

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
mingli-bench serve --port 8765
python -m mingli_bench.cli --show-chart case_1
```

`--agent-input-json` 默认只在本地运行，返回命盘、本地结构化 report 和准备给 LLM 的 prompt。加上 `--agent-model google/gemini-2.5-pro` 或其他支持模型后，才会读取 `.env` 并调用真实 LLM。

`mingli-bench agent` 会启动交互式本地 Agent。使用 `--no-llm` 可以保持完全本地运行并输出结构化命盘报告，使用 `--model` 可以调用 LLM，使用 `--json` 可以输出机器可读 JSON。
需要查看发给模型的完整 prompt 时，可以加 `--show-prompt`。

## 本地 HTTP API

启动本地服务：

```bash
mingli-bench serve --port 8765
```

然后打开：

```text
http://127.0.0.1:8765/
```

默认不会调用 LLM。需要让 `/agent` 调用模型时，启动时指定模型：

```bash
mingli-bench serve --model google/gemini-2.5-pro
```

调用示例：

```bash
curl http://127.0.0.1:8765/health

curl -X POST http://127.0.0.1:8765/agent \
  -H 'Content-Type: application/json' \
  -d '{"chart_input":{"calendar_type":"solar","year":1978,"month":4,"day":5,"hour":18,"location":"台湾"},"question":"分析事业和性格"}'
```

可用端点：

- `GET /`：本地网页界面。
- `GET /health`：服务健康检查。
- `POST /chart`：输入 `ChartInput`，返回稳定 `BaziChart` JSON。
- `POST /agent`：输入 `chart_input` 和可选 `question`，返回命盘、结构化 report、prompt 和可选 LLM 解读。

安装后也可以使用命令：

```bash
mingli-bench --stats
mingli-bench --show-chart case_1
```

LLM 评测示例：

```bash
cp .env.example .env
# 填入你要调用的模型服务商 key

python -m mingli_bench.cli \
  --model google/gemini-2.5-pro \
  --year 2025 \
  --cot \
  --astro \
  --sample 10
```

当模型名包含 `/`，例如 `openai/gpt-4o`、`anthropic/claude-sonnet-4-6`、`google/gemini-2.5-pro`，CLI 会自动按 OpenRouter 模型 ID 处理。

## Python API 示例

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
print(agent_result.prompt)  # 本地生成 prompt；除非提供 model client，否则不会调用 LLM。
print(agent_result.report.to_markdown())  # 本地结构化命盘报告。

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

## 数据说明

| 文件 | 说明 |
|---|---|
| `data/data.json` | 标准化题目、选项、答案、类别和出生信息。 |
| `data/fortune_api_results.json` | 以 `case_id` 关联的预排八字 / 紫微命盘数据。 |
| `data/raw/` | 原始年度文本。 |

当前仓库把命盘作为数据 fixture 使用，并提供提取和标准化工具。核心库已经可以在固定东八区语境下，从公历出生日期/时间推导八字四柱。

### 当前八字计算范围

`mingli_bench.bazi` 当前实现：

- 用公历日期/时间和计算得到的立春边界推导年柱；
- 用 12 个节令边界推导月柱；
- 用连续六十甲子日循环推导日柱；
- 支持 23:00 后晚子时按次日计算日柱；
- 根据日干和时辰推导时柱。
- 对 benchmark fixture 中出现的出生地做时区标准化。

`mingli_bench.solar_terms` 通过太阳视黄经搜索来给出确定性的近似节气时间，适合开发者工具和回归测试，但不是高精度星历。历史时区/DST 处理、完整独立农历/公历转换仍属于后续工作。

八字年柱采用立春换年约定。因此在每年 1-2 月附近，结果可能和按农历新年标记年份的外部命盘来源不同。

`mingli_bench.chart_api` 是推荐给应用层使用的稳定 API。它接受公历或 fixture-backed 农历 `ChartInput`，返回结构化 `BaziChart`，包含四柱、日主、五行统计、时区信息、农历信息、来源和 warnings。

`mingli_bench.agent` 是后续搭建真正算命 Agent 的推荐入口。它把确定性的排盘计算保留在本地，只在配置模型客户端时才调用 LLM 做解释。

`mingli_bench.locations` 当前使用一张小而可审计的地点别名表，而不是完整地理编码服务。像 `usa` 这种不够精确的输入会回退到 UTC+8，并返回 warning，方便上层应用继续追问州/城市，或在后续集成中传入明确时区。

`mingli_bench.lunar` 当前支持中文农历日期解析，并基于 `data/fortune_api_results.json` 做 fixture-backed 的农历/公历互查。它还不是完整独立的农历转换引擎。

## 来源与致谢

本项目基于并引用了上游开源项目和数据资源，包括 `DestinyLinker/MingLi-Bench`、`iztro` 以及赛事原始资料。详细说明见 [ATTRIBUTION.md](./ATTRIBUTION.md)。

## 测试

```bash
python -m unittest discover -s tests
```

默认测试覆盖纯函数和命盘数据提取。LLM API 测试不放在默认测试里，因为需要密钥且会产生费用。

## Roadmap

- 持续打磨稳定的 `ChartInput -> BaziChart` API 契约。
- 增加更高层的 Agent 对话记忆和追问处理。
- 增加完整独立的农历 / 公历转换引擎。
- 扩展节气验证样例和边界场景测试。
- 扩展出生地标准化范围，不只覆盖当前 fixture 中出现的地点。
- 增加显式时区偏移覆盖和历史 DST 策略钩子。
- 增加更完整的紫微斗数命盘标准化 API。
- 增加模型响应缓存和可复现实验 manifest。
- API 稳定后发布 PyPI 包。

## 贡献方式

欢迎贡献。适合优先参与的方向：

- 增加历法、干支、节气测试样例。
- 改进命盘标准化。
- 补充文档和 API 示例。
- 增加模型评测适配器。
- 校验数据记录和原始数据来源。

提交 PR 前请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 许可证

本项目基于 [MIT License](./LICENSE) 开源。
