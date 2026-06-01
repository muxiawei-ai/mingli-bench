"""Static local web UI served by the MingLi API."""

from __future__ import annotations

from typing import Optional


def render_index_html(model_name: Optional[str] = None) -> str:
    """Return the local single-page UI HTML."""

    model_label = model_name or "Local report only"
    return INDEX_HTML.replace("__MODEL_LABEL__", _escape_html(model_label))


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MingLi Agent</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f6f1;
      --surface: #ffffff;
      --surface-soft: #f1efe7;
      --ink: #24221f;
      --muted: #6c675f;
      --line: #ded9cd;
      --accent: #16675a;
      --accent-ink: #ffffff;
      --warn: #8a5a00;
      --danger: #a13d36;
      --focus: #c88a25;
      --radius: 8px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 15px;
      line-height: 1.5;
    }

    button,
    input,
    select,
    textarea {
      font: inherit;
    }

    .shell {
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 22px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .mark {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border-radius: var(--radius);
      background: var(--ink);
      color: var(--accent-ink);
      font-weight: 750;
      flex: 0 0 auto;
    }

    h1 {
      margin: 0;
      font-size: 18px;
      line-height: 1.2;
      letter-spacing: 0;
    }

    .status {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--accent);
    }

    main {
      display: grid;
      grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
      gap: 0;
      min-height: 0;
    }

    .input-pane {
      padding: 22px;
      border-right: 1px solid var(--line);
      background: var(--surface);
      overflow: auto;
    }

    .result-pane {
      padding: 22px;
      overflow: auto;
    }

    form {
      display: grid;
      gap: 18px;
    }

    fieldset {
      margin: 0;
      padding: 0;
      border: 0;
      display: grid;
      gap: 12px;
    }

    legend {
      padding: 0;
      margin: 0 0 2px;
      font-size: 13px;
      font-weight: 750;
      color: var(--muted);
      text-transform: uppercase;
    }

    label {
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
    }

    input,
    select,
    textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #fffdf8;
      color: var(--ink);
      padding: 10px 11px;
      outline: none;
      min-height: 42px;
    }

    textarea {
      min-height: 86px;
      resize: vertical;
    }

    input:focus,
    select:focus,
    textarea:focus {
      border-color: var(--focus);
      box-shadow: 0 0 0 3px rgba(200, 138, 37, 0.16);
    }

    .grid-two {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }

    .grid-three {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .actions {
      display: flex;
      align-items: center;
      gap: 10px;
      padding-top: 4px;
    }

    button {
      min-height: 42px;
      border: 1px solid transparent;
      border-radius: var(--radius);
      padding: 0 14px;
      cursor: pointer;
      font-weight: 750;
    }

    button[type="submit"] {
      background: var(--accent);
      color: var(--accent-ink);
    }

    button[type="button"] {
      background: var(--surface-soft);
      color: var(--ink);
      border-color: var(--line);
    }

    button:disabled {
      cursor: progress;
      opacity: 0.72;
    }

    .summary-bar {
      display: grid;
      grid-template-columns: repeat(4, minmax(130px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }

    .metric,
    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
    }

    .metric {
      padding: 13px;
      min-height: 82px;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 5px;
    }

    .metric strong {
      display: block;
      font-size: 18px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .panel {
      margin-bottom: 16px;
      overflow: hidden;
    }

    .panel h2 {
      margin: 0;
      padding: 13px 15px;
      font-size: 15px;
      border-bottom: 1px solid var(--line);
      background: var(--surface-soft);
      letter-spacing: 0;
    }

    .panel-body {
      padding: 15px;
    }

    .element-list {
      display: grid;
      gap: 9px;
    }

    .element-row {
      display: grid;
      grid-template-columns: 44px 1fr 96px;
      align-items: center;
      gap: 10px;
    }

    .bar {
      height: 10px;
      border-radius: 999px;
      background: var(--surface-soft);
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      width: 0;
      background: var(--accent);
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 0 10px;
      border-radius: var(--radius);
      background: var(--surface-soft);
      color: var(--ink);
      font-size: 13px;
    }

    .muted {
      color: var(--muted);
    }

    .warning {
      color: var(--warn);
    }

    .error {
      color: var(--danger);
      font-weight: 700;
    }

    pre {
      margin: 0;
      max-height: 420px;
      overflow: auto;
      padding: 14px;
      border-radius: var(--radius);
      background: #211f1b;
      color: #f9f4e8;
      font-size: 12px;
      line-height: 1.55;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .empty {
      min-height: 340px;
      display: grid;
      place-items: center;
      border: 1px dashed var(--line);
      border-radius: var(--radius);
      color: var(--muted);
      background: rgba(255, 255, 255, 0.52);
      text-align: center;
      padding: 24px;
    }

    @media (max-width: 920px) {
      header {
        align-items: flex-start;
        flex-direction: column;
      }

      main {
        grid-template-columns: 1fr;
      }

      .input-pane {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .summary-bar {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 560px) {
      header,
      .input-pane,
      .result-pane {
        padding: 16px;
      }

      .grid-two,
      .grid-three,
      .summary-bar {
        grid-template-columns: 1fr;
      }

      .element-row {
        grid-template-columns: 38px 1fr;
      }

      .element-row .muted {
        grid-column: 1 / -1;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="brand">
        <div class="mark">命</div>
        <div>
          <h1>MingLi Agent</h1>
          <div class="muted">本地排盘与结构化报告</div>
        </div>
      </div>
      <div class="status"><span class="dot"></span><span id="serviceStatus">__MODEL_LABEL__</span></div>
    </header>

    <main>
      <section class="input-pane">
        <form id="agentForm">
          <fieldset>
            <legend>出生信息</legend>
            <label>
              日期类型
              <select id="calendarType" name="calendar_type">
                <option value="solar">公历</option>
                <option value="lunar">农历</option>
              </select>
            </label>
            <label id="lunarDateWrap" hidden>
              农历日期
              <input id="lunarDate" name="lunar_date" placeholder="一九七八年二月廿八">
            </label>
            <div class="grid-three" id="ymdWrap">
              <label>年<input id="year" name="year" inputmode="numeric" value="1978"></label>
              <label>月<input id="month" name="month" inputmode="numeric" value="4"></label>
              <label>日<input id="day" name="day" inputmode="numeric" value="5"></label>
            </div>
            <div class="grid-two">
              <label>时间<input id="time" name="time" placeholder="18:00" value="18:00"></label>
              <label>性别<input id="gender" name="gender" placeholder="女"></label>
            </div>
            <div class="grid-two">
              <label>国家/地区<input id="country" name="country" placeholder="中国"></label>
              <label>出生地<input id="location" name="location" placeholder="台湾" value="台湾"></label>
            </div>
          </fieldset>

          <fieldset>
            <legend>问题</legend>
            <label>
              咨询方向
              <textarea id="question" name="question">分析事业和性格</textarea>
            </label>
          </fieldset>

          <div class="actions">
            <button type="submit" id="submitButton">生成报告</button>
            <button type="button" id="resetButton">重置</button>
          </div>
          <div id="formError" class="error" role="alert"></div>
        </form>
      </section>

      <section class="result-pane">
        <div id="emptyState" class="empty">填写信息后生成本地命盘报告</div>
        <div id="result" hidden>
          <div class="summary-bar">
            <div class="metric"><span>四柱</span><strong id="pillarsText">-</strong></div>
            <div class="metric"><span>日主</span><strong id="dayMaster">-</strong></div>
            <div class="metric"><span>时辰</span><strong id="hourBranch">-</strong></div>
            <div class="metric"><span>时区</span><strong id="timezone">-</strong></div>
          </div>

          <section class="panel">
            <h2>五行分布</h2>
            <div class="panel-body">
              <div id="elementList" class="element-list"></div>
            </div>
          </section>

          <section class="panel">
            <h2>结构提示</h2>
            <div class="panel-body">
              <div class="tag-list" id="signalTags"></div>
            </div>
          </section>

          <section class="panel">
            <h2>输入与限制</h2>
            <div class="panel-body">
              <div id="caveats" class="tag-list"></div>
            </div>
          </section>

          <section class="panel" id="llmPanel" hidden>
            <h2>LLM 解读</h2>
            <div class="panel-body" id="llmResponse"></div>
          </section>

          <section class="panel">
            <h2>原始 JSON</h2>
            <div class="panel-body"><pre id="rawJson"></pre></div>
          </section>
        </div>
      </section>
    </main>
  </div>

  <script>
    const form = document.getElementById("agentForm");
    const calendarType = document.getElementById("calendarType");
    const lunarDateWrap = document.getElementById("lunarDateWrap");
    const ymdWrap = document.getElementById("ymdWrap");
    const submitButton = document.getElementById("submitButton");
    const resetButton = document.getElementById("resetButton");
    const formError = document.getElementById("formError");

    calendarType.addEventListener("change", () => {
      const isLunar = calendarType.value === "lunar";
      lunarDateWrap.hidden = !isLunar;
      ymdWrap.hidden = isLunar;
    });

    resetButton.addEventListener("click", () => {
      form.reset();
      calendarType.dispatchEvent(new Event("change"));
      formError.textContent = "";
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      formError.textContent = "";
      submitButton.disabled = true;
      submitButton.textContent = "生成中";
      try {
        const payload = buildPayload();
        const response = await fetch("/agent", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error?.message || "请求失败");
        }
        renderResult(data);
      } catch (error) {
        formError.textContent = error.message;
      } finally {
        submitButton.disabled = false;
        submitButton.textContent = "生成报告";
      }
    });

    function buildPayload() {
      const chartInput = {
        calendar_type: calendarType.value,
        hour: null,
        minute: 0
      };
      if (calendarType.value === "lunar") {
        const lunarDate = valueOf("lunarDate");
        if (!lunarDate) {
          throw new Error("请输入农历日期");
        }
        chartInput.lunar_date = lunarDate;
      } else {
        chartInput.year = numberOf("year", "年");
        chartInput.month = numberOf("month", "月");
        chartInput.day = numberOf("day", "日");
      }

      const parsedTime = parseTime(valueOf("time"));
      chartInput.hour = parsedTime.hour;
      chartInput.minute = parsedTime.minute;
      copyOptional(chartInput, "gender");
      copyOptional(chartInput, "country");
      copyOptional(chartInput, "location");

      return {
        chart_input: chartInput,
        question: valueOf("question") || "请基于这个八字命盘，给出结构化、审慎的中文命理分析。"
      };
    }

    function valueOf(id) {
      return document.getElementById(id).value.trim();
    }

    function numberOf(id, label) {
      const value = Number.parseInt(valueOf(id), 10);
      if (!Number.isFinite(value)) {
        throw new Error(`${label} 必须是数字`);
      }
      return value;
    }

    function copyOptional(target, id) {
      const value = valueOf(id);
      if (value) {
        target[id] = value;
      }
    }

    function parseTime(value) {
      if (!value) {
        return {hour: null, minute: 0};
      }
      const parts = value.split(":");
      const hour = Number.parseInt(parts[0], 10);
      const minute = parts.length > 1 ? Number.parseInt(parts[1], 10) : 0;
      if (!Number.isFinite(hour) || hour < 0 || hour > 23) {
        throw new Error("小时必须在 0 到 23 之间");
      }
      if (!Number.isFinite(minute) || minute < 0 || minute > 59) {
        throw new Error("分钟必须在 0 到 59 之间");
      }
      return {hour, minute};
    }

    function renderResult(data) {
      document.getElementById("emptyState").hidden = true;
      document.getElementById("result").hidden = false;

      const report = data.report;
      const summary = report.summary;
      const inputQuality = report.input_quality;
      document.getElementById("pillarsText").textContent = summary.pillars_text || "-";
      document.getElementById("dayMaster").textContent = `${summary.day_master || "-"} (${summary.day_master_element || "未知"})`;
      document.getElementById("hourBranch").textContent = summary.hour_branch || "未知";
      document.getElementById("timezone").textContent = inputQuality.timezone || "-";

      renderElements(report.element_profile || []);
      renderTags("signalTags", [
        ...(report.strongest_elements || []).map((item) => `相对较多：${item}`),
        ...(report.missing_elements || []).map((item) => `未见：${item}`),
        `历法来源：${inputQuality.calendar_source || "-"}`
      ]);
      renderTags("caveats", [
        ...(report.caveats || []),
        ...(report.follow_up_questions || []).map((item) => `追问：${item}`)
      ]);

      const llmPanel = document.getElementById("llmPanel");
      if (data.response) {
        llmPanel.hidden = false;
        document.getElementById("llmResponse").textContent = formatInterpretation(data.interpretation);
      } else {
        llmPanel.hidden = true;
      }
      document.getElementById("rawJson").textContent = JSON.stringify(data, null, 2);
    }

    function formatInterpretation(interpretation) {
      if (!interpretation) {
        return "";
      }
      const lines = [
        `概览：${interpretation.overview || ""}`,
        `模式：${interpretation.mode || ""}`
      ];
      (interpretation.sections || []).forEach((section) => {
        lines.push("", `【${section.title || "未命名段落"}】`, section.summary || "");
        if (section.evidence?.length) {
          lines.push(`依据：${section.evidence.join("；")}`);
        }
        if (section.caveats?.length) {
          lines.push(`限制：${section.caveats.join("；")}`);
        }
      });
      if (interpretation.follow_up_questions?.length) {
        lines.push("", "建议追问：");
        interpretation.follow_up_questions.forEach((item) => lines.push(`- ${item}`));
      }
      if (interpretation.caveats?.length) {
        lines.push("", "整体限制：");
        interpretation.caveats.forEach((item) => lines.push(`- ${item}`));
      }
      return lines.join("\\n");
    }

    function renderElements(profile) {
      const list = document.getElementById("elementList");
      list.replaceChildren();
      profile.forEach((signal) => {
        const row = document.createElement("div");
        row.className = "element-row";
        const name = document.createElement("strong");
        name.textContent = signal.element;
        const bar = document.createElement("div");
        bar.className = "bar";
        const fill = document.createElement("div");
        fill.className = "bar-fill";
        fill.style.width = `${Math.min(signal.count * 12.5, 100)}%`;
        bar.appendChild(fill);
        const meta = document.createElement("span");
        meta.className = "muted";
        meta.textContent = `${signal.count} · ${signal.level}`;
        row.append(name, bar, meta);
        list.appendChild(row);
      });
    }

    function renderTags(id, values) {
      const container = document.getElementById(id);
      container.replaceChildren();
      values.filter(Boolean).forEach((value) => {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = value;
        container.appendChild(tag);
      });
    }
  </script>
</body>
</html>
"""


__all__ = ["render_index_html"]
