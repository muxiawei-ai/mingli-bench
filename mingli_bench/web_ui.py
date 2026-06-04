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

    [hidden] {
      display: none !important;
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

    .tag-strong {
      background: #e5f3ef;
      color: #0f5148;
      border: 1px solid #b8d8d0;
    }

    .tag-missing {
      background: #fff0df;
      color: #7a4308;
      border: 1px solid #edc08c;
    }

    .tag-intent {
      background: #eef0ff;
      color: #333d7c;
      border: 1px solid #c9cef7;
    }

    .tag-source {
      background: #eeeeea;
      color: var(--muted);
      border: 1px solid var(--line);
    }

    .interpretation {
      display: grid;
      gap: 16px;
    }

    .interpretation-head {
      display: grid;
      gap: 10px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--line);
    }

    .overview {
      margin: 0;
      font-size: 17px;
      line-height: 1.75;
    }

    .answer-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .section-list {
      display: grid;
      gap: 16px;
    }

    .reading-section {
      display: grid;
      gap: 10px;
      padding-bottom: 15px;
      border-bottom: 1px solid var(--line);
    }

    .reading-section:last-child {
      padding-bottom: 0;
      border-bottom: 0;
    }

    .reading-section h3 {
      margin: 0;
      font-size: 16px;
      line-height: 1.35;
      letter-spacing: 0;
    }

    .reading-section p {
      margin: 0;
      line-height: 1.85;
      white-space: pre-wrap;
    }

    .detail-group {
      display: grid;
      gap: 6px;
      margin-top: 2px;
      padding-left: 12px;
      border-left: 3px solid var(--line);
      color: var(--muted);
      font-size: 13px;
    }

    .detail-group strong {
      font-size: 12px;
      color: var(--muted);
    }

    .detail-group ul {
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 4px;
    }

    .detail-group li {
      line-height: 1.55;
    }

    .option-score-list {
      display: grid;
      gap: 8px;
    }

    .option-score {
      display: grid;
      grid-template-columns: 52px 1fr;
      gap: 10px;
      align-items: start;
      padding: 10px 0;
      border-top: 1px solid var(--line);
    }

    .option-score:first-child {
      border-top: 0;
    }

    .option-score strong {
      color: var(--accent);
    }

    .option-score p {
      margin: 0;
      line-height: 1.7;
    }

    .boundary-note {
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 1px solid rgba(138, 90, 0, 0.25);
      border-radius: var(--radius);
      background: #fff8e8;
      color: #4f3909;
      line-height: 1.7;
    }

    .boundary-note strong {
      font-size: 13px;
    }

    .follow-up-form {
      display: grid;
      gap: 12px;
    }

    .follow-up-form textarea {
      min-height: 74px;
    }

    .history-list {
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }

    .history-item {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #fffdf8;
      overflow: hidden;
    }

    .history-item summary {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px;
      cursor: pointer;
      list-style: none;
    }

    .history-item summary::-webkit-details-marker {
      display: none;
    }

    .history-title {
      display: grid;
      gap: 4px;
      min-width: 0;
    }

    .history-title strong {
      font-size: 13px;
      color: var(--muted);
    }

    .history-title span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 700;
    }

    .history-toggle {
      color: var(--accent);
      font-size: 13px;
      font-weight: 750;
    }

    .history-body {
      display: grid;
      gap: 12px;
      padding: 0 12px 12px;
      border-top: 1px solid var(--line);
    }

    .history-body .interpretation-head {
      padding-top: 12px;
    }

    .history-body .overview {
      font-size: 15px;
    }

    .history-item p {
      margin: 0;
      line-height: 1.7;
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
            <div class="metric"><span>问题方向</span><strong id="intentDomain">-</strong></div>
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

          <section class="panel" id="followUpPanel" hidden>
            <h2>继续追问</h2>
            <div class="panel-body">
              <form id="followUpForm" class="follow-up-form">
                <label>
                  基于当前命盘继续问
                  <textarea id="followUpQuestion" placeholder="例如：事业上更适合稳定路线还是自主发展？"></textarea>
                </label>
                <div class="actions">
                  <button type="submit" id="followUpButton">继续咨询</button>
                  <button type="button" id="clearFollowUpButton">清空</button>
                </div>
                <div id="followUpError" class="error" role="alert"></div>
              </form>
              <div id="historyList" class="history-list"></div>
            </div>
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
    const followUpPanel = document.getElementById("followUpPanel");
    const followUpForm = document.getElementById("followUpForm");
    const followUpQuestion = document.getElementById("followUpQuestion");
    const followUpButton = document.getElementById("followUpButton");
    const followUpError = document.getElementById("followUpError");
    const clearFollowUpButton = document.getElementById("clearFollowUpButton");
    const historyList = document.getElementById("historyList");

    let currentChartInput = null;
    let currentQuestion = "";
    let currentOverview = "";
    let conversationTurns = [];

    calendarType.addEventListener("change", () => {
      const isLunar = calendarType.value === "lunar";
      lunarDateWrap.hidden = !isLunar;
      ymdWrap.hidden = isLunar;
    });

    resetButton.addEventListener("click", () => {
      form.reset();
      calendarType.dispatchEvent(new Event("change"));
      formError.textContent = "";
      followUpError.textContent = "";
      followUpQuestion.value = "";
      followUpPanel.hidden = true;
      historyList.replaceChildren();
      currentChartInput = null;
      currentQuestion = "";
      currentOverview = "";
      conversationTurns = [];
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
        data.interpretation = normalizeInterpretation(data.interpretation);
        currentChartInput = payload.chart_input;
        currentQuestion = payload.question;
        currentOverview = data.interpretation?.overview || "";
        conversationTurns = [{
          question: payload.question,
          overview: currentOverview,
          interpretation: data.interpretation
        }];
        renderResult(data);
        renderHistory();
      } catch (error) {
        formError.textContent = error.message;
      } finally {
        submitButton.disabled = false;
        submitButton.textContent = "生成报告";
      }
    });

    followUpForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      followUpError.textContent = "";
      const nextQuestion = followUpQuestion.value.trim();
      if (!currentChartInput) {
        followUpError.textContent = "请先生成一次命盘报告";
        return;
      }
      if (!nextQuestion) {
        followUpError.textContent = "请输入追问内容";
        return;
      }
      followUpButton.disabled = true;
      followUpButton.textContent = "追问中";
      try {
        const payload = {
          chart_input: currentChartInput,
          question: buildFollowUpQuestion(nextQuestion)
        };
        const response = await fetch("/agent", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error?.message || "请求失败");
        }
        data.interpretation = normalizeInterpretation(data.interpretation);
        currentQuestion = nextQuestion;
        currentOverview = data.interpretation?.overview || "";
        conversationTurns.push({
          question: nextQuestion,
          overview: currentOverview,
          interpretation: data.interpretation
        });
        renderResult(data);
        renderHistory();
        followUpQuestion.value = "";
      } catch (error) {
        followUpError.textContent = error.message;
      } finally {
        followUpButton.disabled = false;
        followUpButton.textContent = "继续咨询";
      }
    });

    clearFollowUpButton.addEventListener("click", () => {
      followUpQuestion.value = "";
      followUpError.textContent = "";
      followUpQuestion.focus();
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

    function buildFollowUpQuestion(nextQuestion) {
      const previous = conversationTurns[conversationTurns.length - 1] || {};
      return [
        "这是基于同一命盘的继续追问。",
        `上一轮问题：${previous.question || currentQuestion || "无"}`,
        `上一轮概览：${previous.overview || currentOverview || "无"}`,
        `当前追问：${nextQuestion}`,
        "请直接回答当前追问，并保持结构化、审慎、可读。"
      ].join("\\n");
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
      data.interpretation = normalizeInterpretation(data.interpretation);
      document.getElementById("emptyState").hidden = true;
      document.getElementById("result").hidden = false;

      const report = data.report;
      const summary = report.summary;
      const inputQuality = report.input_quality;
      const intent = data.intent || {};
      document.getElementById("pillarsText").textContent = summary.pillars_text || "-";
      document.getElementById("dayMaster").textContent = `${summary.day_master || "-"} (${summary.day_master_element || "未知"})`;
      document.getElementById("hourBranch").textContent = summary.hour_branch || "未知";
      document.getElementById("intentDomain").textContent = intent.primary_domain || "-";

      renderElements(report.element_profile || []);
      renderSignalTags(report, intent, inputQuality);
      renderTags("caveats", [
        ...(report.caveats || []),
        ...(report.follow_up_questions || []).map((item) => `追问：${item}`)
      ]);

      const llmPanel = document.getElementById("llmPanel");
      if (data.response) {
        llmPanel.hidden = false;
        renderInterpretation(data.interpretation);
        followUpPanel.hidden = false;
      } else {
        llmPanel.hidden = true;
        followUpPanel.hidden = true;
      }
      document.getElementById("rawJson").textContent = JSON.stringify(data, null, 2);
    }

    function normalizeInterpretation(interpretation) {
      if (!interpretation || typeof interpretation !== "object") {
        return interpretation;
      }
      const embedded = parseEmbeddedJsonObject(interpretation.overview);
      if (!embedded || !embedded.sections) {
        return interpretation;
      }
      return {
        ...interpretation,
        ...embedded,
        mode: embedded.mode || "llm_json",
        parsed_from_response: true,
        raw_response: interpretation.raw_response || interpretation.overview
      };
    }

    function parseEmbeddedJsonObject(value) {
      if (typeof value !== "string") {
        return null;
      }
      const trimmed = value.trim();
      const start = trimmed.indexOf("{");
      const end = trimmed.lastIndexOf("}");
      const candidates = [trimmed];
      if (start >= 0 && end > start) {
        candidates.push(trimmed.slice(start, end + 1));
      }
      for (const candidate of candidates) {
        const parsed = parseJsonCandidate(candidate);
        if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
          return parsed;
        }
      }
      return null;
    }

    function parseJsonCandidate(candidate) {
      let current = candidate;
      for (let index = 0; index < 3; index += 1) {
        if (current && typeof current === "object" && !Array.isArray(current)) {
          return current;
        }
        if (typeof current !== "string") {
          return null;
        }
        try {
          current = JSON.parse(current.trim());
        } catch (_error) {
          return null;
        }
      }
      return current && typeof current === "object" && !Array.isArray(current) ? current : null;
    }

    function renderInterpretation(interpretation) {
      const container = document.getElementById("llmResponse");
      container.replaceChildren();
      container.className = "interpretation";
      appendInterpretationContent(container, interpretation, {includeBoundary: true});
    }

    function appendInterpretationContent(container, interpretation, options = {}) {
      if (!interpretation) {
        container.textContent = "";
        return;
      }

      const head = document.createElement("div");
      head.className = "interpretation-head";
      if (interpretation.overview) {
        const overview = document.createElement("p");
        overview.className = "overview";
        overview.textContent = interpretation.overview;
        head.appendChild(overview);
      }
      const answerRow = document.createElement("div");
      answerRow.className = "answer-row";
      if (interpretation.answer_choice) {
        answerRow.appendChild(makeTag(`结论选项：${interpretation.answer_choice}`));
      }
      if (interpretation.answer_confidence !== null && interpretation.answer_confidence !== undefined) {
        answerRow.appendChild(makeTag(`审慎置信度：${formatPercent(interpretation.answer_confidence)}`));
      }
      if (interpretation.mode) {
        answerRow.appendChild(makeTag(`模式：${interpretation.mode}`));
      }
      if (answerRow.children.length) {
        head.appendChild(answerRow);
      }
      if (options.includeBoundary) {
        head.appendChild(makeBoundaryNote());
      }
      container.appendChild(head);

      if (interpretation.option_scores && Object.keys(interpretation.option_scores).length) {
        const optionSection = document.createElement("div");
        optionSection.className = "reading-section";
        const title = document.createElement("h3");
        title.textContent = "选项比较";
        optionSection.appendChild(title);
        const list = document.createElement("div");
        list.className = "option-score-list";
        Object.entries(interpretation.option_scores).forEach(([letter, value]) => {
          const row = document.createElement("div");
          row.className = "option-score";
          const score = document.createElement("strong");
          score.textContent = `${letter} · ${formatScore(value?.score)}`;
          const rationale = document.createElement("p");
          rationale.textContent = value?.rationale || "暂无理由";
          row.append(score, rationale);
          list.appendChild(row);
        });
        optionSection.appendChild(list);
        container.appendChild(optionSection);
      }

      const sectionList = document.createElement("div");
      sectionList.className = "section-list";
      (interpretation.sections || []).forEach((section) => {
        sectionList.appendChild(renderReadingSection(section));
      });
      if (sectionList.children.length) {
        container.appendChild(sectionList);
      }

      if (interpretation.follow_up_questions?.length) {
        container.appendChild(renderDetailBlock("建议追问", interpretation.follow_up_questions));
      }
      if (interpretation.caveats?.length) {
        container.appendChild(renderDetailBlock("整体边界", interpretation.caveats));
      }
    }

    function renderReadingSection(section) {
      const block = document.createElement("article");
      block.className = "reading-section";
      const title = document.createElement("h3");
      title.textContent = section.title || "未命名段落";
      const summary = document.createElement("p");
      summary.textContent = section.summary || "";
      block.append(title, summary);
      if (section.evidence?.length) {
        block.appendChild(renderDetailBlock("依据", section.evidence));
      }
      if (section.caveats?.length) {
        block.appendChild(renderDetailBlock("限制", section.caveats));
      }
      return block;
    }

    function renderDetailBlock(title, items) {
      const block = document.createElement("div");
      block.className = "detail-group";
      const heading = document.createElement("strong");
      heading.textContent = title;
      const list = document.createElement("ul");
      (items || []).filter(Boolean).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
      });
      block.append(heading, list);
      return block;
    }

    function makeBoundaryNote() {
      const note = document.createElement("div");
      note.className = "boundary-note";
      const title = document.createElement("strong");
      title.textContent = "解读边界";
      const text = document.createElement("div");
      text.textContent = "以下内容是传统命理视角下的结构化参考，不等同于确定事实或人生决策依据；涉及健康、财务、法律等现实问题时，仍应以专业意见和现实证据为准。";
      note.append(title, text);
      return note;
    }

    function makeTag(text, extraClass = "") {
      const tag = document.createElement("span");
      tag.className = extraClass ? `tag ${extraClass}` : "tag";
      tag.textContent = text;
      return tag;
    }

    function formatPercent(value) {
      const number = Number(value);
      return Number.isFinite(number) ? `${Math.round(number * 100)}%` : "-";
    }

    function formatScore(value) {
      const number = Number(value);
      return Number.isFinite(number) ? number.toFixed(2) : "-";
    }

    function renderHistory() {
      historyList.replaceChildren();
      conversationTurns.slice(-6).forEach((turn, index) => {
        const absoluteIndex = conversationTurns.length - Math.min(conversationTurns.length, 6) + index;
        const item = document.createElement("details");
        item.className = "history-item";
        const summary = document.createElement("summary");
        const title = document.createElement("span");
        title.className = "history-title";
        const label = document.createElement("strong");
        label.textContent = absoluteIndex === 0 ? "初始问题" : `追问 ${absoluteIndex}`;
        const question = document.createElement("span");
        question.textContent = turn.question;
        title.append(label, question);
        const toggle = document.createElement("span");
        toggle.className = "history-toggle";
        toggle.textContent = "展开";
        summary.append(title, toggle);
        item.addEventListener("toggle", () => {
          toggle.textContent = item.open ? "收起" : "展开";
        });

        const body = document.createElement("div");
        body.className = "history-body";
        appendInterpretationContent(body, turn.interpretation, {includeBoundary: false});
        item.append(summary, body);
        historyList.appendChild(item);
      });
    }

    function renderSignalTags(report, intent, inputQuality) {
      const container = document.getElementById("signalTags");
      container.replaceChildren();
      (report.strongest_elements || []).forEach((item) => {
        container.appendChild(makeTag(`相对较多：${item}`, "tag-strong"));
      });
      (report.missing_elements || []).forEach((item) => {
        container.appendChild(makeTag(`未见：${item}`, "tag-missing"));
      });
      container.appendChild(makeTag(`问题方向：${intent.primary_domain || "-"}`, "tag-intent"));
      if (intent.confidence !== null && intent.confidence !== undefined) {
        container.appendChild(makeTag(`意图识别：${formatPercent(intent.confidence)}`, "tag-intent"));
      }
      container.appendChild(makeTag(`历法来源：${inputQuality.calendar_source || "-"}`, "tag-source"));
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
        container.appendChild(makeTag(value));
      });
    }
  </script>
</body>
</html>
"""


__all__ = ["render_index_html"]
