---
name: micro-expression-tutorial
description: Build a topic tutorial as an HTML slide deck + Chinese-narrated MP4, the way the "微表情视频生成" tutorial was built — measurement-first, method-not-process, self-drawn SVG charts, cards instead of mermaid. Trigger when the user wants to turn a finished project (measured data, real photos, generated clips) into a teaching video/tutorial deck: 做成教程 / 教程片 / 教学视频 / 把项目做成视频 / 实测数据做成教程 / 微表情教程 / 教程 HTML 幻灯. Also trigger when the tutorial already exists and the user complains it 太注重过程 / 图表太丑 / 版本号太多 / 说人话 / 图文并茂 — the full revision checklist is in references/deck-craft.md and references/narration.md. Pairs with html2video-for-mcode (rendering pipeline) and micro-expression-video (the method being taught); this skill owns the *teaching artifact*, not the method and not the renderer.
---

# 微表情教程片 · 把一个实测项目做成「能照着做」的教程

一条生产线：**实测项目 → 事实底稿 → 口播脚本 → HTML 幻灯 → 成片**。
产出物不是「我们干了什么」的汇报，是「读者照着能做」的教程。

> 本 Skill 负责**教学交付物**这一层。
> - 方法本身（怎么量、怎么写提示词、怎么验收）→ `micro-expression-video`
> - 渲染流水线（HTML → MP4 的七阶段与闸门）→ `html2video-for-mcode`
> - 本 Skill：怎么把方法**讲成一堂课**，以及这门课的工程规范。

---

## 四条铁律（违反任何一条，片子一定会被打回）

### 铁律 1 · 只讲方法，不讲过程

读者要的是「照着能做」，不是「我们怎么试出来的」。

**必须删掉**：版本号迭代史（V1/V7/V8）、「我们试了 N 次才…」、「返工过一次」、
「结论来自 8 版实测与 18 张参考图」这类出处交代、「你不需要知道我们试了多少版」。

**必须换成**：「方法是什么」+「为什么这样就成立」+「可执行的下一步」。
需要交代结论来源时，**一笔带过**（一句话，或干脆不写）。

> 自检：把片子里所有带「我们 / 实测 / 第 N 版 / 试了」的话圈出来，逐条问「删掉会让人做不下去吗？」
> 不会 → 删。

### 铁律 2 · 不出现版本号

版本号是给作者看的时间线，不是给读者看的知识。
「V1 像晒伤」要写成「**愤怒的面红耳赤**：整脸一片红、烧到脖子下巴」——
用**现象名**代替版本号，读者还能对照现实。

### 铁律 3 · 不用 mermaid

mermaid 的默认观感撑不住深色技术主题：节点框生硬、字号不可控、
`xychart-beta` 自带**白色画布**（深色主题上是一块白板）。

| 需求 | 做法 |
|---|---|
| 流程 / 判定 / 架构 | **卡片 + 箭头**（`.flowrow` 组件，见 `references/deck-craft.md`） |
| 数据图表（柱 / 折线 / 区间） | **自绘 SVG**，颜色直接取主题令牌（`scripts/svg_charts.py`） |
| 表格 / 清单 / 数值带 | 表格 + 卡片，或 SVG 区间带 |

自绘 SVG 的三个必踩坑（都写在 `references/deck-craft.md`）：
柱位内缩、右侧留白、轴标题避让。

### 铁律 4 · 时长只来自 ffprobe

`build/timings.json` 的秒数**不手写**。占位值只用于版面与动画窗校验，
出片前必须被 TTS 实测覆盖。TTS 音色必须**试听 + ASR 反查**后再合成。

---

## 产出物清单

```
project/
  slides/*.html          每页一个 HTML，含入场动画（data-stage + fx-*）
  slides/tokens.css      主题令牌（html2video-for-mcode 的受管区）
  script.json            口播契约：clauses[] + stage
  audio/<id>.mp3         每页一段 TTS（实测时长的唯一来源）
  assets/                配图 + MANIFEST.md（来源与许可）
  research/notes.md      事实底稿：每个数字的出处与口径
  build/timings.json     实测时序
  preview/play/index.html 自包含放映页（双击即看）
  out/final.mp4          成片 + subs.srt
```

---

## 七阶段 · 六闸门

| 阶段 | 做什么 | 闸门 | 卡点 |
|---|---|---|---|
| 0 研究 | 收素材、跑测量、写 `research/notes.md` | **Gate 0** | 数字必须能追溯到文件；不确定项要标注「不进片」 |
| 1 脚本 | 写 `script.json` 的 `clauses[]` | **Gate 1** | 口播先于 HTML；数字在口播里用**读出来的形式**（四点零 / 百分之二十八） |
| 2 TTS | 合成每页音频、实测时长 | **Gate 2** | 音色先试听 + ASR 反查；`plan-timings.mjs` 出 `build/timings.json` |
| 3 素材 | 配图 + `assets/MANIFEST.md` | **Gate 3** | 每张图有来源与许可；自己裁的切片要标注 |
| 4 HTML | 写 17 张幻灯 | **Gate 4** | `check-slides` 0 错误 + `capture --mode still` 17/17 |
| 5 渲染 | 逐帧动效 + ASR 校验 | **Gate 5** | `capture --mode motion` 全量 + `build-video --asr` |
| 6 交付 | 成片 + 字幕 + 工程包 | — | 占位 timings 必须已被实测覆盖 |

---

## 命令速查

```bash
SK=/workspace/.skills/html2video-for-mcode

# 0. 起项目
node $SK/scripts/init-project.mjs <project>

# 1~4. 写内容（scripts/build_slides.py 自己写，图表用 scripts/svg_charts.py）
python3 build_slides.py
node $SK/scripts/check-slides.mjs  <project>
node $SK/scripts/check-theme.mjs   <project>

# 2. TTS（mcode 沙箱：批量 ≤10 条/批）
mcode-tools connector call connector__matrix__batch_text_to_audio --args-file /tmp/tts.json
# → success_items[].node_id → mcode-tools get_asset_url <node_id> → 下载到 audio/<id>.mp3

# 2. 实测时序
node $SK/scripts/plan-timings.mjs <project>

# 3. 素材
python3 prep_assets.py          # 自己写：抽帧、切片、建 MANIFEST

# 4. 终态预览
node $SK/scripts/capture.mjs <project> --mode still

# 5. 动效渲染 + 出片
node $SK/scripts/capture.mjs    <project> --mode motion
node $SK/scripts/build-video.mjs <project> --asr

# 6. 放映页（可随时给用户看）
node $SK/scripts/preview-page.mjs <project>
```

---

## 参考文件（按需读，不用全读）

| 文件 | 什么时候读 |
|---|---|
| `references/deck-craft.md` | 写 HTML 时：卡片组件、SVG 图表规范、版式避坑清单、主题令牌 |
| `references/narration.md` | 写口播时：说人话、字数与时长换算、显示形式 vs 朗读形式 |
| `references/content-source.md` | 需要素材与数字时：测量口径、数值带、哪些数字可以上台面 |
| `references/pipeline.md` | 需要出片时：七阶段契约、闸门、产物路径、常见报错 |

---

## 常见症状 → 一句话诊断

| 症状 | 病因 | 修法 |
|---|---|---|
| 片子「像汇报不像教程」 | 叙事按迭代顺序组织 | 改成按方法步骤组织；删版本号 |
| 图表丑 / 颜色跟主题对不上 | 用了 mermaid | 换自绘 SVG，颜色取主题令牌 |
| 柱子有一半在坐标区外 | 类别中心放在了坐标区两端 | 柱位内缩 `px0 + slot*(i+0.5)` |
| 某页整页空白但脚本全报成功 | `data-stage` 没配 fx 类（基础态 `opacity:0`） | `data-stage` 必须与 `fx-*` 同时用 |
| 图文页高度爆掉 | `.img-frame` 满宽会按比例放大 | 给 figure 限宽 |
| 字幕和画面错位 | 时长是估的不是测的 | 重跑 `plan-timings` → 重渲该页 |
| 成片比预期长一大截 | 语速基线与实际音色不符 | 以 ffprobe 实测为准；换音色要重新试听 |
