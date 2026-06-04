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

    .button-primary {
      background: var(--accent);
      color: var(--accent-ink);
    }

    button[type="button"] {
      background: var(--surface-soft);
      color: var(--ink);
      border-color: var(--line);
    }

    button[type="button"].button-primary {
      background: var(--accent);
      color: var(--accent-ink);
      border-color: transparent;
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

    .result-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 16px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
    }

    .result-toolbar-title {
      display: grid;
      gap: 2px;
      min-width: 0;
    }

    .result-toolbar-title strong {
      font-size: 14px;
      line-height: 1.3;
    }

    .result-toolbar-title span {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
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

    .debug-panel summary {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 13px 15px;
      cursor: pointer;
      list-style: none;
      border-bottom: 1px solid var(--line);
      background: var(--surface-soft);
      font-weight: 750;
      font-size: 15px;
    }

    .debug-panel summary::-webkit-details-marker {
      display: none;
    }

    .debug-panel:not([open]) summary {
      border-bottom: 0;
    }

    .debug-toggle {
      color: var(--accent);
      font-size: 13px;
      font-weight: 750;
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

    .hexagram-panel {
      display: grid;
      gap: 16px;
    }

    .divination-basis {
      display: grid;
      gap: 6px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #f5f2ea;
      color: var(--ink);
      font-size: 14px;
      line-height: 1.75;
    }

    .divination-basis strong,
    .moving-line-card strong,
    .line-detail-table strong {
      color: var(--muted);
      font-size: 13px;
    }

    .hexagram-pair {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
      gap: 14px;
      align-items: center;
    }

    .hex-card {
      min-height: 240px;
      display: grid;
      justify-items: center;
      align-content: center;
      gap: 10px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #fffdf8;
    }

    .hex-card-label {
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }

    .hex-lines {
      display: grid;
      gap: 6px;
      width: 108px;
      margin: 2px auto 4px;
    }

    .hex-row {
      min-height: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      position: relative;
    }

    .hex-line {
      height: 7px;
      border-radius: 999px;
      background: var(--ink);
    }

    .hex-line.yang {
      width: 78px;
    }

    .hex-line.yin {
      width: 34px;
    }

    .hex-row.moving .hex-line {
      background: #6b5812;
    }

    .hex-row.moving::after {
      content: "";
      width: 11px;
      height: 11px;
      border: 2px solid #6b5812;
      border-radius: 999px;
      position: absolute;
      right: -12px;
      top: 50%;
      transform: translateY(-50%);
      background: #fffdf8;
    }

    .hex-card-name {
      font-size: 24px;
      font-weight: 850;
      line-height: 1.25;
    }

    .hex-card-meta {
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-align: center;
    }

    .hex-arrow {
      color: var(--muted);
      font-size: 28px;
      font-weight: 700;
    }

    .moving-line-card {
      padding: 14px 16px;
      border-left: 4px solid #8a6810;
      border-radius: var(--radius);
      background: #fff5e3;
      line-height: 1.8;
    }

    .moving-line-card blockquote {
      margin: 5px 0 6px;
      font-size: 18px;
      font-weight: 850;
    }

    .hexagram-panel .detail {
      padding: 10px 12px;
      border-left: 3px solid var(--line);
      background: #fbfaf5;
      color: var(--muted);
      font-size: 13px;
    }

    .line-detail-table {
      display: grid;
      gap: 0;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #fffdf8;
    }

    .line-detail-row {
      display: grid;
      grid-template-columns: 48px 88px minmax(0, 1fr);
      gap: 12px;
      align-items: start;
      padding: 10px 12px;
      border-top: 1px solid var(--line);
    }

    .line-detail-row:first-child {
      border-top: 0;
    }

    .line-detail-heading {
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      background: #f5f2ea;
    }

    .line-detail-heading + .line-detail-row {
      border-top: 0;
    }

    .line-detail-row.is-moving {
      background: #fff5e3;
    }

    .line-mini {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 6px;
      min-height: 20px;
      padding-top: 5px;
    }

    .line-mini .hex-line {
      height: 5px;
    }

    .line-mini .yang {
      width: 54px;
    }

    .line-mini .yin {
      width: 24px;
    }

    .export-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
    }

    .export-status {
      min-height: 22px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
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

      .result-toolbar {
        align-items: stretch;
        flex-direction: column;
      }

      .hexagram-pair {
        grid-template-columns: 1fr;
      }

      .hex-arrow {
        transform: rotate(90deg);
        justify-self: center;
      }

      .export-row {
        justify-content: flex-start;
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

      .line-detail-row {
        grid-template-columns: 36px minmax(0, 1fr);
      }

      .line-detail-row > div:last-child {
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
            <button type="button" id="demoButton">加载示例</button>
            <button type="button" id="resetButton">重置</button>
          </div>
          <div id="formError" class="error" role="alert"></div>
        </form>
      </section>

      <section class="result-pane">
        <div id="emptyState" class="empty">填写信息后生成本地命盘报告</div>
        <div id="result" hidden>
          <section class="result-toolbar" id="exportPanel" aria-label="报告导出">
            <div class="result-toolbar-title">
              <strong>本次报告</strong>
              <span>可复制 Markdown，或下载独立 HTML 打印版。</span>
            </div>
            <div class="export-row">
              <button type="button" id="copyMarkdownButton" class="button-primary">复制 Markdown</button>
              <button type="button" id="downloadMarkdownButton">下载 .md</button>
              <button type="button" id="downloadHtmlButton">下载 HTML</button>
              <span id="exportStatus" class="export-status" role="status"></span>
            </div>
          </section>

          <div class="summary-bar">
            <div class="metric"><span>四柱</span><strong id="pillarsText">-</strong></div>
            <div class="metric"><span>日主</span><strong id="dayMaster">-</strong></div>
            <div class="metric"><span>时辰</span><strong id="hourBranch">-</strong></div>
            <div class="metric"><span>问题方向</span><strong id="intentDomain">-</strong></div>
          </div>

          <section class="panel" id="hexagramPanel" hidden>
            <h2>卦象参考</h2>
            <div class="panel-body" id="hexagramContent"></div>
          </section>

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
            <h2>当前解读</h2>
            <div class="panel-body" id="llmResponse"></div>
          </section>

          <section class="panel" id="followUpPanel" hidden>
            <h2>追问与历史</h2>
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

          <details class="panel debug-panel" id="debugPanel">
            <summary><span>调试信息（原始 JSON）</span><span class="debug-toggle" id="debugToggle">展开</span></summary>
            <div class="panel-body"><pre id="rawJson"></pre></div>
          </details>
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
    const demoButton = document.getElementById("demoButton");
    const resetButton = document.getElementById("resetButton");
    const formError = document.getElementById("formError");
    const followUpPanel = document.getElementById("followUpPanel");
    const followUpForm = document.getElementById("followUpForm");
    const followUpQuestion = document.getElementById("followUpQuestion");
    const followUpButton = document.getElementById("followUpButton");
    const followUpError = document.getElementById("followUpError");
    const clearFollowUpButton = document.getElementById("clearFollowUpButton");
    const historyList = document.getElementById("historyList");
    const copyMarkdownButton = document.getElementById("copyMarkdownButton");
    const downloadMarkdownButton = document.getElementById("downloadMarkdownButton");
    const downloadHtmlButton = document.getElementById("downloadHtmlButton");
    const exportStatus = document.getElementById("exportStatus");
    const serviceStatus = document.getElementById("serviceStatus");
    const debugPanel = document.getElementById("debugPanel");
    const debugToggle = document.getElementById("debugToggle");

    let currentChartInput = null;
    let currentQuestion = "";
    let currentOverview = "";
    let latestResultData = null;
    let reportGeneratedAt = null;
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
      latestResultData = null;
      reportGeneratedAt = null;
      conversationTurns = [];
      debugPanel.open = false;
      updateDebugToggle();
      setExportStatus("");
    });

    demoButton.addEventListener("click", () => {
      const demo = buildDemoReportData();
      applyFormValues(demo.chartInput, demo.question);
      currentChartInput = demo.chartInput;
      currentQuestion = demo.question;
      latestResultData = demo.data;
      reportGeneratedAt = demo.generatedAt;
      debugPanel.open = false;
      updateDebugToggle();
      conversationTurns = demo.turns.map((turn) => ({
        ...turn,
        overview: turn.interpretation?.overview || "",
        interpretation: normalizeInterpretation(turn.interpretation)
      }));
      currentOverview = conversationTurns[conversationTurns.length - 1]?.overview || "";
      renderResult(demo.data);
      renderHistory();
      followUpQuestion.value = "";
      formError.textContent = "";
      followUpError.textContent = "";
      setExportStatus("已加载示例，未调用 API");
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
        latestResultData = data;
        reportGeneratedAt = new Date();
        debugPanel.open = false;
        updateDebugToggle();
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
        latestResultData = data;
        debugPanel.open = false;
        updateDebugToggle();
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

    debugPanel.addEventListener("toggle", updateDebugToggle);

    copyMarkdownButton.addEventListener("click", async () => {
      const markdown = buildMarkdownReport();
      if (!markdown) {
        setExportStatus("暂无可导出的报告");
        return;
      }
      try {
        await copyText(markdown);
        setExportStatus("已复制");
      } catch (_error) {
        setExportStatus("复制失败");
      }
    });

    downloadMarkdownButton.addEventListener("click", () => {
      const markdown = buildMarkdownReport();
      if (!markdown) {
        setExportStatus("暂无可导出的报告");
        return;
      }
      const blob = new Blob([markdown], {type: "text/markdown;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `mingli-report-${dateSlug(new Date())}.md`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setExportStatus("已下载");
    });

    downloadHtmlButton.addEventListener("click", () => {
      const html = buildPrintableHtmlReport();
      if (!html) {
        setExportStatus("暂无可导出的报告");
        return;
      }
      const blob = new Blob([html], {type: "text/html;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `mingli-report-${dateSlug(new Date())}.html`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setExportStatus("HTML 已下载");
    });

    function buildDemoReportData() {
      const chartInput = {
        calendar_type: "solar",
        year: 1990,
        month: 8,
        day: 16,
        hour: 9,
        minute: 30,
        gender: "女",
        country: "中国",
        location: "上海"
      };
      const question = "分析事业和性格";
      const report = {
        question,
        summary: {
          pillars_text: "庚午 甲申 癸丑 丁巳",
          day_master: "癸",
          day_master_element: "水",
          hour_branch: "巳"
        },
        input_quality: {
          calendar_source: "demo_fixture",
          timezone: "Asia/Shanghai",
          has_birth_time: true
        },
        element_profile: [
          {element: "木", count: 1, level: "low"},
          {element: "火", count: 3, level: "high"},
          {element: "土", count: 2, level: "medium"},
          {element: "金", count: 2, level: "medium"},
          {element: "水", count: 1, level: "low"}
        ],
        hexagram: {
          method: "梅花易数时间法示例",
          basis: [
            "年数(10)+月数(6)+日数(30)=46 -> 余6 -> 上卦：坎",
            "加时数(7，午时)=53 -> 余5 -> 下卦：巽 · 动爻：第五爻"
          ],
          primary: {
            role: "本卦",
            name: "井卦",
            symbol: "䷯",
            number: 48,
            upper: "坎",
            lower: "巽",
            lines: ["yin", "yang", "yang", "yin", "yang", "yin"],
            description: "坎上巽下 · 水风井"
          },
          changed: {
            role: "变卦",
            name: "升卦",
            symbol: "䷭",
            number: 46,
            upper: "坤",
            lower: "巽",
            lines: ["yin", "yang", "yang", "yin", "yin", "yin"],
            description: "坤上巽下 · 地风升"
          },
          moving_line: 5,
          moving_line_name: "九五",
          moving_line_text: "井洌，寒泉食。",
          interpretation: "井水洁净，甘泉可饮。象征长期积蓄的实力与资源，此刻可以被汲取运用；对事业主题而言，重点是把已有积累转成可见成果，而不是重新从零开始。",
          caveats: [
            "这是前端卦象展示示例，用于验证盘面模块与导出版式。",
            "真实起卦需要后续接入确定性的卦象计算引擎，不应由 LLM 直接编造。"
          ],
          line_details: [
            {index: 1, name: "初六 · 阴", text: "井泥不食，旧井无禽。", note: "底层资源尚未清理，旧方法需要重整。"},
            {index: 2, name: "九二 · 阳", text: "井谷射鲋，瓮敝漏。", note: "已有资源但承接容器不足，提醒补足执行与表达的漏洞。"},
            {index: 3, name: "九三 · 阳", text: "井渫不食，为我心恻。", note: "能力已经清澈，但仍需主动展示，等待本身不够。"},
            {index: 4, name: "六四 · 阴", text: "井甃，无咎。", note: "打好基础、修复结构，低调扎实即可。"},
            {index: 5, name: "九五 · 阳 · 动爻", text: "井洌，寒泉食。", note: "核心动爻，代表资源终于可用，适合进入成果转化。"},
            {index: 6, name: "上六 · 阴", text: "井收勿幕，有孚元吉。", note: "开放资源、形成信任，避免封闭与独占。"}
          ]
        },
        strongest_elements: ["火", "金"],
        missing_elements: [],
        caveats: [
          "这是前端示例数据，仅用于查看排版和导出效果。",
          "示例未调用 API，也不代表真实排盘或命理判断。"
        ],
        follow_up_questions: [
          "如果关注 2026 年事业节奏，可以继续追问具体月份。",
          "如果关注转型窗口，可以补充行业和当前岗位。"
        ]
      };
      const turns = [
        {
          question,
          interpretation: {
            schema_version: "mingli_interpretation.v1",
            mode: "local",
            overview: "示例报告：整体呈现执行力较强、行动节奏偏快的结构，适合用来检查页面层级、依据展示和导出样式。",
            sections: [
              {
                title: "排盘摘要",
                summary: "四柱示例为庚午、甲申、癸丑、丁巳。日主癸水，局中火金较显，水木相对不强，报告展示时会突出结构提示和五行分布。",
                evidence: ["pillars_text: 庚午 甲申 癸丑 丁巳", "day_master: 癸（水）", "demo_fixture: true"],
                caveats: ["该段为假数据，不用于实际分析。"]
              },
              {
                title: "性格观察",
                summary: "示例文本用于测试长段落阅读效果：火势较明时，表达、行动和推进感较强；金气参与时，规则意识、判断标准和执行边界也会被强调。水木偏弱的设定用于测试报告中关于弹性、复盘和长期规划的提醒是否醒目但不过度抢眼。",
                evidence: ["strongest_elements: 火, 金", "element_profile: 木1 火3 土2 金2 水1"],
                caveats: ["性格表述仅为版式示例，不代表确定事实。"]
              },
              {
                title: "事业倾向",
                summary: "示例结论强调稳健推进、项目制输出和阶段性复盘。适合检查小标题、正文、依据与限制之间的视觉层级。",
                evidence: ["intent.primary_domain: 事业", "question: 分析事业和性格"],
                caveats: ["真实职业判断需要结合行业、经验、环境与选择。"]
              }
            ],
            follow_up_questions: ["2026 年事业节奏如何？", "如果考虑转型，适合先做哪些准备？"],
            caveats: ["示例报告未调用模型。"],
            parsed_from_response: false,
            raw_response: null
          }
        },
        {
          question: "2026年事业节奏如何？",
          interpretation: {
            schema_version: "mingli_interpretation.v1",
            mode: "local",
            overview: "示例追问 1：2026 年可展示为先整理资源、再推进项目、最后复盘收束的节奏。",
            sections: [
              {
                title: "年度节奏",
                summary: "上半年适合梳理方向、明确边界和选择重点项目；年中之后更适合推进交付、合作沟通和成果展示。该段用于测试追问历史中的结构化段落排版。",
                evidence: ["demo_event_year: 2026", "question_domain: 事业"],
                caveats: ["这是示例节奏，不对应真实流年计算。"]
              },
              {
                title: "行动提示",
                summary: "建议把目标拆成可观察的里程碑，避免同时打开过多战线。适合测试建议型内容在页面和导出 HTML 中的可读性。",
                evidence: ["report.follow_up_questions includes career timing"],
                caveats: ["行动建议是测试文本，不构成现实职业建议。"]
              }
            ],
            follow_up_questions: ["如果想转型，适合什么时候开始准备？"],
            caveats: ["示例追问未调用 API。"],
            parsed_from_response: false,
            raw_response: null
          }
        },
        {
          question: "如果想转型，适合什么时候开始准备？",
          interpretation: {
            schema_version: "mingli_interpretation.v1",
            mode: "local",
            overview: "示例追问 2：转型更适合先小步试水，再评估资源与风险，避免直接大幅切换。",
            sections: [
              {
                title: "准备窗口",
                summary: "示例建议把准备期放在正式行动之前：先整理作品、验证方向、访谈目标行业，再决定是否投入更多资源。这里主要用来检查多轮追问后的历史折叠和导出完整性。",
                evidence: ["turn_index: 2", "demo_topic: transition"],
                caveats: ["真实转型判断需要补充行业、财务缓冲和个人约束。"]
              },
              {
                title: "风险边界",
                summary: "如果当前资源不足，适合先做低成本试验；如果已有明确机会，则可以把风险拆分为时间、现金流、人际支持和技能缺口四类。",
                evidence: ["demo_risk_categories: time, cashflow, support, skill_gap"],
                caveats: ["该段为版式和导出测试内容。"]
              }
            ],
            follow_up_questions: ["是否要把 HTML 打印版进一步做成正式报告版式？"],
            caveats: ["示例追问未调用 API。"],
            parsed_from_response: false,
            raw_response: null
          }
        }
      ];
      return {
        chartInput,
        question,
        generatedAt: new Date(),
        turns,
        data: {
          demo: true,
          response: "demo_response_no_api_call",
          chart: {
            pillars_text: report.summary.pillars_text
          },
          report,
          intent: {
            primary_domain: "事业",
            confidence: 0.92
          },
          interpretation: turns[turns.length - 1].interpretation,
          warnings: ["demo_data_no_api_call"],
          trace: [
            {
              name: "demo",
              status: "completed",
              summary: "Loaded front-end fixture data without API call."
            }
          ]
        }
      };
    }

    function applyFormValues(chartInput, question) {
      calendarType.value = chartInput.calendar_type || "solar";
      calendarType.dispatchEvent(new Event("change"));
      document.getElementById("year").value = chartInput.year || "";
      document.getElementById("month").value = chartInput.month || "";
      document.getElementById("day").value = chartInput.day || "";
      document.getElementById("time").value =
        chartInput.hour === null || chartInput.hour === undefined
          ? ""
          : `${pad2(chartInput.hour)}:${pad2(chartInput.minute || 0)}`;
      document.getElementById("gender").value = chartInput.gender || "";
      document.getElementById("country").value = chartInput.country || "";
      document.getElementById("location").value = chartInput.location || "";
      document.getElementById("question").value = question || "";
    }

    function buildMarkdownReport() {
      if (!latestResultData || !conversationTurns.length) {
        return "";
      }

      const data = latestResultData;
      const report = data.report || {};
      const summary = report.summary || {};
      const inputQuality = report.input_quality || {};
      const chartInput = currentChartInput || {};
      const lines = [];

      lines.push("# MingLi Agent 本地命盘报告", "");
      lines.push(`生成时间：${formatDateTime(reportGeneratedAt || new Date())}`);
      lines.push(`导出时间：${formatDateTime(new Date())}`);
      lines.push(`模型：${mdText(reportModelLabel(data))}`, "");

      lines.push("## 出生信息");
      appendKeyValue(lines, "日期类型", chartInput.calendar_type === "lunar" ? "农历" : "公历");
      appendKeyValue(lines, "出生日期", formatBirthDate(chartInput));
      appendKeyValue(lines, "出生时间", formatBirthTime(chartInput));
      appendKeyValue(lines, "性别", chartInput.gender);
      appendKeyValue(lines, "国家/地区", chartInput.country);
      appendKeyValue(lines, "出生地", chartInput.location);
      appendKeyValue(lines, "时区", inputQuality.timezone);
      lines.push("");

      lines.push("## 命盘摘要");
      appendKeyValue(lines, "四柱", summary.pillars_text);
      appendKeyValue(lines, "日主", `${summary.day_master || "-"}（${summary.day_master_element || "未知"}）`);
      appendKeyValue(lines, "时辰", summary.hour_branch || "未知");
      appendKeyValue(lines, "问题方向", data.intent?.primary_domain);
      appendList(lines, "相对较多", report.strongest_elements);
      appendList(lines, "未见五行", report.missing_elements);
      lines.push("");

      if (Array.isArray(report.element_profile) && report.element_profile.length) {
        lines.push("## 五行分布");
        report.element_profile.forEach((item) => {
          lines.push(`- ${mdText(item.element)}：${item.count}（${mdText(item.level)}）`);
        });
        lines.push("");
      }

      appendHexagramMarkdown(lines, report.hexagram);

      conversationTurns.forEach((turn, index) => {
        const interpretation = normalizeInterpretation(turn.interpretation);
        lines.push(index === 0 ? "## 初始问题" : `## 追问 ${index}`);
        lines.push(`**问题：** ${mdText(turn.question)}`, "");
        appendInterpretationMarkdown(lines, interpretation);
        lines.push("");
      });

      if (Array.isArray(report.caveats) && report.caveats.length) {
        appendDetailList(lines, "## 输入与限制", report.caveats);
      }

      lines.push("## 解读边界");
      lines.push("本报告是传统命理视角下的结构化参考，不等同于确定事实或人生决策依据；涉及健康、财务、法律等现实问题时，仍应以专业意见和现实证据为准。");

      return lines.join("\\n").replace(/\\n{3,}/g, "\\n\\n").trim() + "\\n";
    }

    function appendHexagramMarkdown(lines, hexagram) {
      if (!hexagram) {
        return;
      }
      const primary = hexagram.primary || {};
      const changed = hexagram.changed || {};
      lines.push("## 卦象参考");
      if (hexagram.method) {
        lines.push(`- 起卦方法：${mdText(hexagram.method)}`);
      }
      cleanTextList(hexagram.basis).forEach((item) => {
        lines.push(`- ${mdText(item)}`);
      });
      lines.push("");
      lines.push(`### 本卦：${mdText(primary.name || "-")} ${mdText(primary.symbol || "")}`);
      appendKeyValue(lines, "卦序", primary.number);
      appendKeyValue(lines, "上下卦", `${primary.upper || "-"}上${primary.lower || "-"}下`);
      appendKeyValue(lines, "说明", primary.description);
      lines.push("");
      lines.push(`### 变卦：${mdText(changed.name || "-")} ${mdText(changed.symbol || "")}`);
      appendKeyValue(lines, "卦序", changed.number);
      appendKeyValue(lines, "上下卦", `${changed.upper || "-"}上${changed.lower || "-"}下`);
      appendKeyValue(lines, "说明", changed.description);
      lines.push("");
      if (hexagram.moving_line_name || hexagram.moving_line_text || hexagram.interpretation) {
        lines.push(`### ${mdText(hexagram.moving_line_name || "动爻")}爻辞`);
        if (hexagram.moving_line_text) {
          lines.push(`> ${mdText(hexagram.moving_line_text)}`);
        }
        if (hexagram.interpretation) {
          lines.push(mdText(hexagram.interpretation));
        }
        lines.push("");
      }
      appendDetailList(lines, "卦象边界", hexagram.caveats);
    }

    function appendInterpretationMarkdown(lines, interpretation) {
      if (!interpretation) {
        return;
      }
      if (interpretation.overview) {
        lines.push(mdText(interpretation.overview), "");
      }
      const meta = [];
      if (interpretation.answer_choice) {
        meta.push(`结论选项：${interpretation.answer_choice}`);
      }
      if (interpretation.answer_confidence !== null && interpretation.answer_confidence !== undefined) {
        meta.push(`审慎置信度：${formatPercent(interpretation.answer_confidence)}`);
      }
      if (interpretation.mode) {
        meta.push(`生成方式：${formatModeLabel(interpretation.mode)}`);
      }
      if (meta.length) {
        lines.push(meta.map((item) => `\`${mdText(item)}\``).join(" "), "");
      }

      if (interpretation.option_scores && Object.keys(interpretation.option_scores).length) {
        lines.push("### 选项比较");
        Object.entries(interpretation.option_scores).forEach(([letter, value]) => {
          lines.push(`- ${letter}：${formatScore(value?.score)} - ${mdText(value?.rationale || "暂无理由")}`);
        });
        lines.push("");
      }

      (interpretation.sections || []).forEach((section) => {
        lines.push(`### ${mdText(section.title || "未命名段落")}`);
        if (section.summary) {
          lines.push(mdText(section.summary));
        }
        appendDetailList(lines, "依据", section.evidence);
        appendDetailList(lines, "限制", section.caveats);
        lines.push("");
      });
      appendDetailList(lines, "建议追问", interpretation.follow_up_questions);
      appendDetailList(lines, "整体边界", interpretation.caveats);
    }

    function buildPrintableHtmlReport() {
      const context = buildReportContext();
      if (!context) {
        return "";
      }
      const {data, report, summary, inputQuality, chartInput, generatedAt, exportedAt} = context;
      const turns = conversationTurns.map((turn, index) => ({
        label: index === 0 ? "初始问题" : `追问 ${index}`,
        question: mdText(turn.question),
        interpretation: normalizeInterpretation(turn.interpretation)
      }));

      return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MingLi Agent 本地命盘报告</title>
  <style>
    :root {
      --paper: #fffdf8;
      --ink: #24221f;
      --muted: #6c675f;
      --line: #ded9cd;
      --soft: #f3f0e7;
      --accent: #16675a;
      --accent-soft: #e5f3ef;
      --warn-soft: #fff8e8;
      --paper-shadow: rgba(36, 34, 31, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #efede6;
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 15px;
      line-height: 1.75;
    }
    .page {
      max-width: 920px;
      margin: 32px auto;
      padding: 42px;
      background: var(--paper);
      border: 1px solid var(--line);
      box-shadow: 0 18px 48px var(--paper-shadow);
    }
    header {
      display: grid;
      gap: 18px;
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #ffffff;
    }
    h1, h2, h3 { margin: 0; line-height: 1.35; letter-spacing: 0; }
    h1 { font-size: 30px; }
    h2 {
      margin-top: 30px;
      display: flex;
      align-items: center;
      gap: 9px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--line);
      font-size: 22px;
    }
    h2::before {
      content: "";
      width: 6px;
      height: 24px;
      border-radius: 999px;
      background: var(--accent);
      flex: 0 0 auto;
    }
    h3 { margin-top: 18px; font-size: 16px; }
    p { margin: 8px 0 0; white-space: pre-wrap; }
    ul { margin: 8px 0 0; padding-left: 20px; }
    li { margin: 3px 0; }
    .eyebrow {
      color: var(--accent);
      font-size: 12px;
      font-weight: 800;
    }
    .subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }
    .meta, .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 18px;
    }
    .meta div, .field {
      display: grid;
      gap: 2px;
      padding: 9px 0;
      border-bottom: 1px solid rgba(222, 217, 205, 0.75);
    }
    .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }
    .value { font-weight: 700; }
    .summary-cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }
    .summary-card {
      min-height: 86px;
      padding: 16px;
      border: 1px solid rgba(22, 103, 90, 0.22);
      border-top: 4px solid var(--accent);
      border-radius: 10px;
      background: linear-gradient(180deg, #ffffff 0%, #fbfdfb 100%);
      box-shadow: 0 8px 22px rgba(36, 34, 31, 0.05);
    }
    .summary-card .label { display: block; margin-bottom: 6px; }
    .summary-card .value {
      display: block;
      font-size: 20px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .chip {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 9px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--soft);
      font-size: 13px;
      font-weight: 650;
    }
    .chip.accent {
      background: var(--accent-soft);
      color: #0f5148;
      border-color: #b8d8d0;
    }
    .hexagram-panel {
      display: grid;
      gap: 18px;
      margin-top: 14px;
    }
    .divination-basis {
      display: grid;
      gap: 6px;
      padding: 16px 18px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--soft);
      font-size: 14px;
      line-height: 1.8;
    }
    .divination-basis strong,
    .moving-line-card strong,
    .line-detail-table strong {
      color: var(--muted);
      font-size: 13px;
    }
    .hexagram-pair {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
      gap: 18px;
      align-items: center;
    }
    .hex-card {
      min-height: 250px;
      display: grid;
      justify-items: center;
      align-content: center;
      gap: 11px;
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fbfaf5;
      break-inside: avoid;
    }
    .hex-card-label {
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }
    .hex-lines {
      display: grid;
      gap: 6px;
      width: 112px;
      margin: 3px auto 5px;
    }
    .hex-row {
      min-height: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      position: relative;
    }
    .hex-line {
      height: 7px;
      border-radius: 999px;
      background: var(--ink);
    }
    .hex-line.yang { width: 80px; }
    .hex-line.yin { width: 35px; }
    .hex-row.moving .hex-line { background: #6b5812; }
    .hex-row.moving::after {
      content: "";
      width: 11px;
      height: 11px;
      border: 2px solid #6b5812;
      border-radius: 999px;
      position: absolute;
      right: -12px;
      top: 50%;
      transform: translateY(-50%);
      background: #fbfaf5;
    }
    .hex-card-name {
      font-size: 26px;
      font-weight: 850;
      line-height: 1.2;
    }
    .hex-card-meta {
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-align: center;
    }
    .hex-arrow {
      color: var(--muted);
      font-size: 30px;
      font-weight: 700;
    }
    .moving-line-card {
      padding: 16px 18px;
      border-left: 4px solid #8a6810;
      border-radius: 10px;
      background: #fff3dc;
      line-height: 1.85;
      break-inside: avoid;
    }
    .moving-line-card blockquote {
      margin: 5px 0 6px;
      font-size: 20px;
      font-weight: 850;
    }
    .line-detail-table {
      display: grid;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fbfaf5;
      break-inside: avoid;
    }
    .line-detail-row {
      display: grid;
      grid-template-columns: 52px 92px minmax(0, 1fr);
      gap: 12px;
      align-items: start;
      padding: 11px 14px;
      border-top: 1px solid var(--line);
    }
    .line-detail-row:first-child { border-top: 0; }
    .line-detail-heading {
      padding: 11px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--soft);
    }
    .line-detail-heading + .line-detail-row { border-top: 0; }
    .line-detail-row.is-moving { background: #fff3dc; }
    .line-mini {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 6px;
      min-height: 20px;
      padding-top: 5px;
    }
    .line-mini .hex-line { height: 5px; }
    .line-mini .yang { width: 54px; }
    .line-mini .yin { width: 24px; }
    .print-tip {
      margin-top: 18px;
      padding: 12px 14px;
      border: 1px solid rgba(22, 103, 90, 0.22);
      border-radius: 10px;
      background: var(--accent-soft);
      color: #0f5148;
      font-size: 13px;
      font-weight: 650;
    }
    .turn {
      margin-top: 18px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      break-inside: avoid;
      background: #ffffff;
    }
    .turn-head {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 10px;
      align-items: start;
    }
    .turn-head h3 { margin-top: 0; }
    .turn-number {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: var(--ink);
      color: #ffffff;
      font-size: 13px;
      font-weight: 800;
      line-height: 1;
      font-variant-numeric: tabular-nums;
      padding-bottom: 1px;
    }
    .question {
      margin-top: 6px;
      color: var(--accent);
      font-weight: 800;
    }
    .section {
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
      break-inside: avoid;
    }
    .detail {
      margin-top: 10px;
      padding: 10px 12px;
      border-left: 3px solid var(--line);
      background: #fbfaf5;
      color: var(--muted);
      font-size: 13px;
    }
    .detail strong {
      color: var(--muted);
      font-size: 12px;
    }
    .boundary {
      margin-top: 28px;
      padding: 14px;
      border: 1px solid rgba(138, 90, 0, 0.25);
      border-radius: 8px;
      background: var(--warn-soft);
    }
    .footer {
      margin-top: 34px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
    }
    @media print {
      body { background: white; }
      .page { margin: 0; padding: 0; border: 0; max-width: none; box-shadow: none; }
      h2 { break-after: avoid; }
      .turn, .section, .boundary { break-inside: avoid; }
    }
    @media (max-width: 720px) {
      .page { margin: 0; padding: 24px; border: 0; }
      header { padding: 20px; }
      .meta, .grid, .summary-cards { grid-template-columns: 1fr; }
      .hexagram-pair { grid-template-columns: 1fr; }
      .hex-arrow { transform: rotate(90deg); justify-self: center; }
      .line-detail-row { grid-template-columns: 40px minmax(0, 1fr); }
      .line-detail-row > div:last-child { grid-column: 1 / -1; }
    }
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div class="eyebrow">STRUCTURED MINGLI REPORT</div>
      <h1>MingLi Agent 本地命盘报告</h1>
      <p class="subtitle">面向归档与打印的独立 HTML 报告，内容来自当前本地结构化会话。</p>
      <div class="meta">
        ${htmlField("生成时间", formatDateTime(generatedAt))}
        ${htmlField("导出时间", formatDateTime(exportedAt))}
        ${htmlField("模型", reportModelLabel(data))}
        ${htmlField("问题方向", data.intent?.primary_domain || "-")}
      </div>
      <div class="print-tip">打印提示：打开此 HTML 后，可使用浏览器“打印”或“另存为 PDF”保存正式版报告。</div>
    </header>

    <section>
      <h2>出生信息</h2>
      <div class="grid">
        ${htmlField("日期类型", chartInput.calendar_type === "lunar" ? "农历" : "公历")}
        ${htmlField("出生日期", formatBirthDate(chartInput))}
        ${htmlField("出生时间", formatBirthTime(chartInput))}
        ${htmlField("性别", chartInput.gender || "未提供")}
        ${htmlField("国家/地区", chartInput.country || "未提供")}
        ${htmlField("出生地", chartInput.location || "未提供")}
        ${htmlField("时区", inputQuality.timezone || "未提供")}
      </div>
    </section>

    <section>
      <h2>命盘摘要</h2>
      <div class="summary-cards">
        ${htmlSummaryCard("四柱", summary.pillars_text || "-")}
        ${htmlSummaryCard("日主", `${summary.day_master || "-"}（${summary.day_master_element || "未知"}）`)}
        ${htmlSummaryCard("时辰", summary.hour_branch || "未知")}
        ${htmlSummaryCard("历法来源", inputQuality.calendar_source || "-")}
      </div>
      ${htmlChips("结构提示", [
        ...(report.strongest_elements || []).map((item) => `相对较多：${item}`),
        ...(report.missing_elements || []).map((item) => `未见：${item}`)
      ], "accent")}
      ${htmlElementProfile(report.element_profile)}
    </section>

    ${renderHtmlHexagramSection(report.hexagram)}

    <section>
      <h2>咨询记录</h2>
      ${turns.map((turn, index) => renderHtmlTurn(turn, index)).join("")}
    </section>

    ${htmlListSection("输入与限制", report.caveats)}

    <section class="boundary">
      <h2>解读边界</h2>
      <p>本报告是传统命理视角下的结构化参考，不等同于确定事实或人生决策依据；涉及健康、财务、法律等现实问题时，仍应以专业意见和现实证据为准。</p>
    </section>

    <div class="footer">由 MingLi Agent 本地网页导出。导出文件不依赖本地服务，可直接打开或打印为 PDF。</div>
  </main>
</body>
</html>`;
    }

    function buildReportContext() {
      if (!latestResultData || !conversationTurns.length) {
        return null;
      }
      const data = latestResultData;
      const report = data.report || {};
      return {
        data,
        report,
        summary: report.summary || {},
        inputQuality: report.input_quality || {},
        chartInput: currentChartInput || {},
        generatedAt: reportGeneratedAt || new Date(),
        exportedAt: new Date()
      };
    }

    function renderHtmlTurn(turn, index) {
      return `<article class="turn">
        <div class="turn-head">
          <span class="turn-number">${index + 1}</span>
          <div>
            <h3>${escapeHtml(turn.label)}</h3>
            <div class="question">${escapeHtml(turn.question)}</div>
          </div>
        </div>
        ${renderHtmlInterpretation(turn.interpretation)}
      </article>`;
    }

    function renderHtmlInterpretation(interpretation) {
      if (!interpretation) {
        return "";
      }
      const meta = [];
      if (interpretation.answer_choice) {
        meta.push(`结论选项：${interpretation.answer_choice}`);
      }
      if (interpretation.answer_confidence !== null && interpretation.answer_confidence !== undefined) {
        meta.push(`审慎置信度：${formatPercent(interpretation.answer_confidence)}`);
      }
      if (interpretation.mode) {
        meta.push(`生成方式：${formatModeLabel(interpretation.mode)}`);
      }
      return [
        interpretation.overview ? `<p>${escapeHtml(interpretation.overview)}</p>` : "",
        htmlChips("", meta),
        htmlOptionScores(interpretation.option_scores),
        ...(interpretation.sections || []).map(renderHtmlSection),
        htmlListBlock("建议追问", interpretation.follow_up_questions),
        htmlListBlock("整体边界", interpretation.caveats)
      ].filter(Boolean).join("");
    }

    function renderHtmlSection(section) {
      return `<section class="section">
        <h3>${escapeHtml(section.title || "未命名段落")}</h3>
        ${section.summary ? `<p>${escapeHtml(section.summary)}</p>` : ""}
        ${htmlListBlock("依据", section.evidence, "detail")}
        ${htmlListBlock("限制", section.caveats, "detail")}
      </section>`;
    }

    function htmlOptionScores(scores) {
      if (!scores || !Object.keys(scores).length) {
        return "";
      }
      const items = Object.entries(scores).map(([letter, value]) => (
        `<li><strong>${escapeHtml(letter)}：${escapeHtml(formatScore(value?.score))}</strong> - ${escapeHtml(value?.rationale || "暂无理由")}</li>`
      )).join("");
      return `<div class="detail"><strong>选项比较</strong><ul>${items}</ul></div>`;
    }

    function htmlElementProfile(profile) {
      if (!Array.isArray(profile) || !profile.length) {
        return "";
      }
      const items = profile.map((item) => (
        `<span class="chip">${escapeHtml(item.element)}：${escapeHtml(String(item.count))}（${escapeHtml(item.level)}）</span>`
      ));
      return `<div class="chips">${items.join("")}</div>`;
    }

    function renderHtmlHexagramSection(hexagram) {
      const module = renderHexagramModule(hexagram);
      return module ? `<section><h2>卦象参考</h2>${module}</section>` : "";
    }

    function renderHexagramPanel(hexagram) {
      const panel = document.getElementById("hexagramPanel");
      const content = document.getElementById("hexagramContent");
      const module = renderHexagramModule(hexagram);
      if (!module) {
        panel.hidden = true;
        content.replaceChildren();
        return;
      }
      content.innerHTML = module;
      panel.hidden = false;
    }

    function renderHexagramModule(hexagram) {
      if (!hexagram || typeof hexagram !== "object") {
        return "";
      }
      const primary = hexagram.primary || {};
      const changed = hexagram.changed || {};
      if (!primary.name && !changed.name) {
        return "";
      }
      const basis = cleanTextList(hexagram.basis);
      const caveats = cleanTextList(hexagram.caveats);
      return `<div class="hexagram-panel">
        ${basis.length ? `<div class="divination-basis">
          <strong>起卦依据${hexagram.method ? `（${escapeHtml(hexagram.method)}）` : ""}</strong>
          ${basis.map((item) => `<div>${escapeHtml(item)}</div>`).join("")}
        </div>` : ""}
        <div class="hexagram-pair">
          ${renderHexCard(primary, hexagram.moving_line)}
          <div class="hex-arrow">-></div>
          ${renderHexCard(changed, hexagram.moving_line)}
        </div>
        ${renderMovingLineCard(hexagram)}
        ${renderLineDetailTable(hexagram)}
        ${caveats.length ? `<div class="detail"><strong>卦象边界</strong><ul>${caveats.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
      </div>`;
    }

    function renderHexCard(card, movingLine) {
      if (!card || typeof card !== "object") {
        return "";
      }
      const title = [card.name, card.symbol].filter(Boolean).join(" ");
      const meta = [
        card.number ? `第${card.number}卦` : "",
        card.upper && card.lower ? `${card.upper}上${card.lower}下` : "",
        card.description || ""
      ].filter(Boolean).join(" · ");
      return `<article class="hex-card">
        <div class="hex-card-label">${escapeHtml(card.role || "卦象")}</div>
        ${renderHexLines(card.lines, movingLine)}
        <div class="hex-card-name">${escapeHtml(title || "-")}</div>
        <div class="hex-card-meta">${escapeHtml(meta || "-")}</div>
      </article>`;
    }

    function renderHexLines(lines, movingLine) {
      if (!Array.isArray(lines) || !lines.length) {
        return "";
      }
      const rows = lines
        .map((line, index) => ({line, index: index + 1}))
        .reverse()
        .map(({line, index}) => {
          const movingClass = Number(movingLine) === index ? " moving" : "";
          return `<div class="hex-row${movingClass}">${renderLineGlyph(line)}</div>`;
        });
      return `<div class="hex-lines" aria-label="六爻卦象">${rows.join("")}</div>`;
    }

    function renderLineGlyph(line) {
      const type = isYangLine(line) ? "yang" : "yin";
      if (type === "yang") {
        return `<span class="hex-line yang"></span>`;
      }
      return `<span class="hex-line yin"></span><span class="hex-line yin"></span>`;
    }

    function isYangLine(line) {
      return line === "yang" || line === "y" || line === true || line === 1;
    }

    function renderMovingLineCard(hexagram) {
      if (!hexagram.moving_line_name && !hexagram.moving_line_text && !hexagram.interpretation) {
        return "";
      }
      return `<section class="moving-line-card">
        <strong>${escapeHtml(hexagram.moving_line_name || "动爻")}爻辞</strong>
        ${hexagram.moving_line_text ? `<blockquote>${escapeHtml(hexagram.moving_line_text)}</blockquote>` : ""}
        ${hexagram.interpretation ? `<p>${escapeHtml(hexagram.interpretation)}</p>` : ""}
      </section>`;
    }

    function renderLineDetailTable(hexagram) {
      const rows = Array.isArray(hexagram.line_details) ? hexagram.line_details : [];
      if (!rows.length) {
        return "";
      }
      const primaryLines = hexagram.primary?.lines || [];
      const movingLine = Number(hexagram.moving_line);
      const content = rows.map((row) => {
        const index = Number(row.index);
        const line = primaryLines[index - 1];
        const movingClass = movingLine === index ? " is-moving" : "";
        return `<div class="line-detail-row${movingClass}">
          <strong>${escapeHtml(lineIndexLabel(index))}</strong>
          <div class="line-mini">${renderLineGlyph(line)}</div>
          <div>
            <strong>${escapeHtml(row.name || "")}</strong>
            ${row.text ? `<p>${escapeHtml(row.text)}</p>` : ""}
            ${row.note ? `<p class="muted">${escapeHtml(row.note)}</p>` : ""}
          </div>
        </div>`;
      }).join("");
      return `<section class="line-detail-table"><div class="line-detail-heading"><strong>六爻详释（由下至上）</strong></div>${content}</section>`;
    }

    function lineIndexLabel(index) {
      return ["", "初", "二", "三", "四", "五", "上"][index] || String(index || "-");
    }

    function htmlListSection(title, values) {
      const block = htmlListBlock("", values);
      return block ? `<section><h2>${escapeHtml(title)}</h2>${block}</section>` : "";
    }

    function htmlListBlock(title, values, className = "") {
      const items = cleanTextList(values);
      if (!items.length) {
        return "";
      }
      const classAttr = className ? ` class="${className}"` : "";
      return `<div${classAttr}>${title ? `<strong>${escapeHtml(title)}</strong>` : ""}<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`;
    }

    function htmlChips(title, values, extraClass = "") {
      const items = cleanTextList(values);
      if (!items.length) {
        return "";
      }
      const chipClass = extraClass ? `chip ${extraClass}` : "chip";
      return `<div class="chips">${title ? `<span class="label">${escapeHtml(title)}</span>` : ""}${items.map((item) => `<span class="${chipClass}">${escapeHtml(item)}</span>`).join("")}</div>`;
    }

    function htmlField(label, value) {
      return `<div class="field"><span class="label">${escapeHtml(label)}</span><span class="value">${escapeHtml(value || "未提供")}</span></div>`;
    }

    function htmlSummaryCard(label, value) {
      return `<div class="summary-card"><span class="label">${escapeHtml(label)}</span><span class="value">${escapeHtml(value || "未提供")}</span></div>`;
    }

    function reportModelLabel(data = latestResultData) {
      return data?.demo ? "示例数据（未调用 API）" : (serviceStatus.textContent || "-");
    }

    function escapeHtml(value) {
      return cleanDisplayText(value, "未提供")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function appendKeyValue(lines, label, value) {
      const text = mdText(value || "未提供");
      lines.push(`- ${label}：${text}`);
    }

    function appendList(lines, label, values) {
      const text = cleanTextList(values).join("、") || "无";
      lines.push(`- ${label}：${text}`);
    }

    function appendDetailList(lines, title, values) {
      const items = cleanTextList(values);
      if (!items.length) {
        return;
      }
      lines.push(title);
      items.forEach((item) => {
        lines.push(`- ${mdListText(item)}`);
      });
      lines.push("");
    }

    function mdText(value) {
      return cleanDisplayText(value, "未提供").trim();
    }

    function mdListText(value) {
      return mdText(value).replace(/\\n/g, "\\n  ");
    }

    function formatBirthDate(chartInput) {
      if (chartInput.lunar_date) {
        return chartInput.lunar_date;
      }
      const parts = [chartInput.year, chartInput.month, chartInput.day].filter(Boolean);
      return parts.length === 3 ? `${parts[0]}-${pad2(parts[1])}-${pad2(parts[2])}` : "未提供";
    }

    function formatBirthTime(chartInput) {
      if (chartInput.hour === null || chartInput.hour === undefined) {
        return "未知";
      }
      return `${pad2(chartInput.hour)}:${pad2(chartInput.minute || 0)}`;
    }

    function formatDateTime(value) {
      const date = value instanceof Date ? value : new Date(value);
      if (Number.isNaN(date.getTime())) {
        return "未知";
      }
      return new Intl.DateTimeFormat("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
      }).format(date);
    }

    function dateSlug(value) {
      const date = value instanceof Date ? value : new Date(value);
      return [
        date.getFullYear(),
        pad2(date.getMonth() + 1),
        pad2(date.getDate()),
        pad2(date.getHours()),
        pad2(date.getMinutes())
      ].join("");
    }

    function pad2(value) {
      return String(value).padStart(2, "0");
    }

    async function copyText(text) {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        return;
      }
      const area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }

    function setExportStatus(text) {
      exportStatus.textContent = text;
    }

    function updateDebugToggle() {
      debugToggle.textContent = debugPanel.open ? "收起" : "展开";
    }

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

      renderHexagramPanel(report.hexagram);
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
      if (typeof interpretation === "string") {
        const embedded = parseEmbeddedJsonObject(interpretation);
        if (embedded?.sections) {
          return normalizeInterpretation({
            ...embedded,
            mode: embedded.mode || "llm_json",
            parsed_from_response: true,
            raw_response: interpretation
          });
        }
        return {
          schema_version: "mingli_interpretation.v1",
          mode: "llm_text",
          overview: cleanDisplayText(
            interpretation,
            "模型返回了未完全解析的结构化文本，以下先按本地排盘信号整理。"
          ),
          sections: [],
          follow_up_questions: [],
          caveats: ["llm_response_not_valid_json"],
          parsed_from_response: false,
          raw_response: interpretation
        };
      }
      if (!interpretation || typeof interpretation !== "object") {
        return interpretation;
      }
      const sources = [
        interpretation.overview,
        interpretation.raw_response,
        ...(interpretation.sections || []).map((section) => section?.summary)
      ];
      for (const source of sources) {
        const embedded = parseEmbeddedJsonObject(source);
        if (embedded?.sections) {
          return sanitizeInterpretation({
            ...interpretation,
            ...embedded,
            mode: embedded.mode || "llm_json",
            parsed_from_response: true,
            raw_response: interpretation.raw_response || source
          });
        }
      }
      return sanitizeInterpretation(interpretation);
    }

    function sanitizeInterpretation(interpretation) {
      if (!interpretation || typeof interpretation !== "object") {
        return interpretation;
      }
      return {
        ...interpretation,
        overview: cleanDisplayText(
          interpretation.overview,
          "模型返回了结构化内容，已按下方段落整理。"
        ),
        sections: (interpretation.sections || []).map(normalizeSection),
        follow_up_questions: cleanTextList(interpretation.follow_up_questions),
        caveats: cleanTextList(interpretation.caveats)
      };
    }

    function normalizeSection(section) {
      if (!section || typeof section !== "object") {
        return {
          title: "未命名段落",
          summary: cleanDisplayText(section, ""),
          evidence: [],
          caveats: []
        };
      }
      return {
        ...section,
        title: cleanDisplayText(section.title, "未命名段落"),
        summary: cleanDisplayText(section.summary, ""),
        evidence: cleanTextList(section.evidence),
        caveats: cleanTextList(section.caveats)
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
        current = tryParseJson(current);
        if (current === null) {
          return null;
        }
      }
      return current && typeof current === "object" && !Array.isArray(current) ? current : null;
    }

    function tryParseJson(value) {
      const cleaned = value.trim();
      const candidates = [
        cleaned,
        escapeControlCharsInJsonStrings(cleaned),
        removeTrailingCommas(cleaned),
        removeTrailingCommas(escapeControlCharsInJsonStrings(cleaned))
      ];
      for (const candidate of candidates) {
        try {
          return JSON.parse(candidate);
        } catch (_error) {
          // Try the next lenient candidate.
        }
      }
      return null;
    }

    function escapeControlCharsInJsonStrings(value) {
      let result = "";
      let inString = false;
      let escaped = false;
      for (const char of value) {
        if (escaped) {
          result += char;
          escaped = false;
          continue;
        }
        if (char === "\\\\") {
          result += char;
          escaped = true;
          continue;
        }
        if (char === '"') {
          result += char;
          inString = !inString;
          continue;
        }
        if (inString && char === "\\n") {
          result += "\\\\n";
          continue;
        }
        if (inString && char === "\\r") {
          result += "\\\\r";
          continue;
        }
        if (inString && char === "\\t") {
          result += "\\\\t";
          continue;
        }
        result += char;
      }
      return result;
    }

    function removeTrailingCommas(value) {
      return value.replace(/,\\s*([}\\]])/g, "$1");
    }

    function cleanDisplayText(value, fallback) {
      if (value === null || value === undefined) {
        return fallback;
      }
      const text = String(value).trim();
      if (!text) {
        return fallback;
      }
      if (looksLikeRawJsonText(text)) {
        return fallback;
      }
      return text.replace(/\\\\n/g, "\\n").replace(/\\\\t/g, "\\t");
    }

    function cleanTextList(value) {
      const items = Array.isArray(value) ? value : (value ? [value] : []);
      return items
        .map((item) => cleanDisplayText(item, ""))
        .filter(Boolean);
    }

    function looksLikeRawJsonText(text) {
      const trimmed = text.trim();
      return (
        trimmed.startsWith("{") &&
        (trimmed.includes('"schema_version"') || trimmed.includes('"sections"'))
      );
    }

    function renderInterpretation(interpretation) {
      const container = document.getElementById("llmResponse");
      container.replaceChildren();
      container.className = "interpretation";
      appendInterpretationContent(container, interpretation, {includeBoundary: true});
    }

    function appendInterpretationContent(container, interpretation, options = {}) {
      interpretation = normalizeInterpretation(interpretation);
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
        answerRow.appendChild(makeTag(`生成方式：${formatModeLabel(interpretation.mode)}`, "tag-source"));
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

    function formatModeLabel(mode) {
      if (mode === "llm_json") {
        return "LLM 结构化";
      }
      if (mode === "llm_text") {
        return "LLM 文本兜底";
      }
      if (mode === "local") {
        return "本地规则";
      }
      return mode || "未知";
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
        turn.interpretation = normalizeInterpretation(turn.interpretation);
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
