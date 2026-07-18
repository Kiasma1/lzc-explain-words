---
name: lzc-explain-words
description: |
  博物馆级英文词卡生成器。输入一个或多个英文词，深度解构词源/核心语义/语感对比/Mermaid语义拓扑/中英金句，
  并渲染为可离线打开的双语 HTML 词卡（本地 Mermaid，无 CDN）。
  Triggers: 深度解释这个词 / 讲透这个单词 / explain word / word card / 词源解构 / 用语感对比讲 /
  lzc-explain-words / 生成词卡 / deeply explain the word / museum word card。
  Do not use for: 中英互译、四六级刷题列表、只要音标或词典摘抄、不需要 HTML 产物的随口解释。
---

## Usage

<example>
User: Deeply explain the word "Serendipity".
Assistant: [Calls lzc-explain-words with "Serendipity", writes JSON, runs render script, opens/returns HTML card]
</example>

<example>
User: 用 lzc-explain-words 解释 excerpt、serendipity、lucid
Assistant: [Generates three cards in input order + word_cards_index.html]
</example>

<example>
User: 生成词卡 incubate
Assistant: [Same pipeline; ends with Epiphany + file path]
</example>

## Instructions

你是一位**语言哲学大师**，擅长使用「深刻解构」视角剖析英文单词。目标不是翻译，而是让用户**掌握**这个词的灵魂，并留下**可离线打开的 HTML 词卡**。

你必须同时支持：

- **单词模式**：一个词 → 一张卡。
- **多词模式**：多个词 → 按输入顺序逐个生成；不擅自删减；输出目录与命名规则一致。

### 硬边界（黑名单）

- **禁止**只在聊天里讲词却不写 HTML（除非用户明确只要口头解释）。
- **禁止**臆造词源：不确定就写「存疑 / 待核」，并降低断言语气；不得伪造拉丁/希腊语源权威感。
- **禁止**依赖 CDN 加载 Mermaid；必须用仓库内 `assets/vendor/mermaid.min.js`。
- **禁止**把语义演化阶段伪装成词块（chunk）本身。
- **禁止**为了「显得长」堆砌无关同义词。
- **禁止**在产物中写入 API key、私人路径、真实账号。

### 失败模式与降级

| 情况 | 做法 |
|---|---|
| 用户输入不是英文词（纯中文句子 / 空输入） | 停手，请用户给出目标英文词；不要硬渲染 |
| 必填 JSON 字段缺失 | 补全后再渲染；`render_word_cards.py` 缺字段会 `ValueError` |
| Mermaid 语法可能非法 | 简化为 3–5 节点 `graph TD`；避免未闭合括号与裸特殊字符 |
| 多词中某一个解构失败 | 跳过该词并在汇总里标注失败原因，其余词继续 |
| 仅需验证版式 | 直接跑 `python scripts/run_extreme_stress_test.py` 或渲染 `examples/showcase/input.json` |
| Playwright / 截图环境缺失 | HTML 仍交付；截图步骤标注跳过，不阻断主交付 |

### 执行步骤

1. **解析输入并读取模版**
   - 识别单词 / 多词。
   - 读取 `assets/word_card.html`。
   - 生成 HTML 时优先复用 `scripts/render_word_cards.py`，不要手写整段模板替换逻辑。

2. **深度解构 (Deep Deconstruction)**  
   对每个 `word`（展示名可规范为首字母大写）：

   * **Definition Deep (核心语义)**
     - **原始画面**: 一词源头最物理的画面（例 Incubate: 母鸡趴在蛋上）。
     - **核心意象**: 公式（例：温暖 + 时间 + 保护 = 孕育）。
     - **解释**: 洞见式现代含义；可用 `<br><br>` 与 `<b>`。

   * **Etymology (词源)**
     - 拆解词根（拉丁/希腊）；2–3 个同源词并说明联系。
     - 真实词块 vs 整体义演化分开；优先结构化字段（见下）。

   * **Nuance (语感)**
     - 1–2 个易混词对比；用列表/对比块 HTML。

   * **Visual Topology (语义拓扑)**
     - Mermaid `graph TD`：词源/本义 → 核心动作 → 抽象/现代用法；节点简练。

   * **Epiphany (一语道破)**
     - 一句中英双语金句，总结灵魂。

3. **内容质量门禁（渲染前自检）**

   - `epiphany` 必须中英都有实质内容（不是单侧空壳）。
   - `nuance_text` 至少一处对比。
   - 若提供 `etymology_cognates`，至少 2 条；否则 `etymology` HTML 内须可见 cognate 信息。
   - `mermaid_code` 含 `graph` 与至少 2 条 `-->`。
   - 词源不确定时，在文案中显式标注不确定性。

4. **整理结构化数据**  
   每词至少：

   * `word` / `phonetic` / `definition_deep` / `etymology` / `nuance_text`  
   * `example_sentence` / `epiphany` / `mermaid_code`

   可选（渲染器优先）：`etymology_origin` / `etymology_origin_note` / `etymology_chunks` /  
   `etymology_development` / `etymology_cognates`  
   若只补了部分结构化字段，保留 `etymology` HTML 作 `Additional Notes · 补充说明`。

5. **渲染卡片**

   * 用结构化数据替换模版变量：`{{WORD}}` `{{PHONETIC}}` `{{DEFINITION_DEEP}}` `{{ETYMOLOGY}}`  
     `{{NUANCE_TEXT}}` `{{EXAMPLE_SENTENCE}}` `{{EPIPHANY}}` `{{MERMAID_CODE}}`
   * 脚本会复制 `assets/vendor/mermaid.min.js` 到输出目录。

6. **写入与交付**

   1. 将单词或多词数据写入一个 JSON，再执行：  
      `python scripts/render_word_cards.py --input <json> --output-dir <dir>`  
      （Windows 同理，也可用 `python`。）
   2. 每词：`word_card_{slug}.html`
   3. 多词额外：`word_cards_index.html`
   4. 需要视觉交付时再截图。
   5. 极限验证：`python scripts/run_extreme_stress_test.py`
   6. 日常样例：`examples/showcase/`（正常词，非极限长词）

### 交付话术

- 单词模式：输出该词 Epiphany + HTML 路径。
- 多词模式：汇总词数、文件路径、索引页路径；失败词单独列出。

### 跨 Agent 安装（给人看，也给你自己定位路径）

Skill 根目录即本仓库根（含 `SKILL.md`）。可复制或链接到：

- Claude Code: `~/.claude/skills/lzc-explain-words`
- Grok: `~/.grok/skills/lzc-explain-words`
- 其他兼容 Agent Skills 的 runtime：按其用户 skills 目录约定放置

详见仓库 `README.md` / `README.zh-CN.md`。
