# 流水线契约 · 出片

> 渲染本身由 `html2video-for-mcode` 完成，本文件只记**这个专题**的约定与坑。

---

## 一、目录契约

```
project/
  slides/<id>-<name>.html     每页一个；文件名与 script.json 的 html 字段一致
  slides/tokens.css           受管区，勿手改
  slides/_template.html       版式骨架参考
  script.json                 id / layout / html / audio / clauses[].stage
  audio/<id>.mp3              每页一段；ffprobe 实测时长的唯一来源
  assets/…                    配图 + MANIFEST.md
  research/notes.md           事实底稿
  build/timings.json          plan-timings 产出（单一时序来源）
  build/frames/<id>/          motion 捕获的帧
  build/substills/            字幕静帧
  preview/*.png               still 终态预览
  preview/play/index.html     自包含放映页
  out/final.mp4 out/subs.srt  成片
  asr/                        ASR 分句与校验清单
```

---

## 二、阶段与闸门（详细版见 SKILL.md）

### Gate 0 · 研究
`research/notes.md` 有内容，且每个数字能追到出处文件。
**不确定的单列一节「不进片」。**

### Gate 1 · 脚本
`script.json` 的 `clauses[]` 全部填好，`stage` 与页面层级对应。
**先写口播，后写 HTML** —— 画面服务于讲解，不是反过来。

### Gate 2 · TTS + 实测时序
1. 音色试听 + ASR 反查（见 `narration.md`）。
2. 批量合成，**每页一段**（不是一句一段）。
3. `plan-timings.mjs` → `build/timings.json`（实测）。
4. 用真实 durations 复核每页的 `stage` 分布是否还合理。

> ⚠ `plan-timings` 的「语速与期望差 20%+」警告通常是**基线不匹配**：
> 基线是按默认音色算的字/秒，换成女声就会差 20~25%。
> 时长以 ffprobe 实测为准，**不要为了消警告去改 TTS 的 speed**。

### Gate 2b · 句读对时（**必做**）
`plan-timings` 按**字数比例**分配每句时长，TTS 的真实开口时刻并不按字数走
（标点停顿、难词都会让分配漂）。实测本项目**平均偏差 0.66s、最大 2.39s** ——
2.4s 的偏差意味着字幕比人声晚了两秒多，观众一定看得见。

```bash
node <skill>/scripts/check-timing.mjs <project>                 # 对比表
node <skill>/scripts/check-timing.mjs <project> --calibrate     # 按静音检测写回 clauses[].start 与 stages{}
# 校准后必须重跑：capture --mode motion → build-video
```

**为什么必须重跑**：字幕关键帧是**烧进画面**的（浏览器里用 CSS keyframes 渲染），
改了 `clauses[].start` 就得重截帧；`build/substills/*.json` 的清单也会失效。

`--calibrate` 只写回**全部句边界都有实测**的 slide（有静音段缺口的只展示不写回）。
校准后先跑一次 `check-timing` 确认偏差收敛，再进 Gate 4。

### Gate 3 · 素材
配图齐、`MANIFEST.md` 写全来源与许可。

### Gate 4 · HTML
- `check-slides.mjs` → **0 错误**（提示项逐条看，别盲扫）。
- `check-theme.mjs` → 全部通过。
- `init-project.mjs --check-css` → `ok`（否则 capture/build-video 会拒绝运行）。
- `capture --mode still` → 17/17，**逐张目视看**（找错位、溢出、空白页）。

### Gate 5 · 渲染 + ASR
- `capture --mode motion`（全量）。
  ⚠ 改过 HTML 后重跑 still 会**清空该页的帧目录** → 必须重跑同 id 的 motion。
- `build-video.mjs --asr` → 出片 + `out/subs.srt` + `asr/checklist.md`。
- ASR 校验：mcode 沙箱用 `upload_temp_url` + `connector__matrix__listen_audio`；
  其他环境用 `scripts/asr.mjs`（需 mmx-cli）。

### Gate 6 · 交付
成片 + 字幕 + 工程包 + 放映页。

---

## 三、渲染相关的三个坑

### 1. `data-stage` 的基础态是 `opacity:0`

只写 `data-stage` 不写 fx 类 → 元素永远停在透明态 → **整页空白，但脚本全报成功**。
必须与 `fx-*` 同时用；`.fx-stagger` 容器自身不能再带 `data-stage`（子元素自己管入场）。

### 2. 自定义布局类必须定义

没定义的类不报错，只是静默竖排。`.grid4` 这种容易漏。

### 3. 图文页要给 figure 限宽

`.img-frame` 满宽会按 `--img-ratio` 把高度放到 900px+，撑破版面。
`figure` 加 `max-width` / `width` 限一下。

---

## 四、ASR 校验怎么做

1. `build-video --asr` 会把每页音频按句切分到 `asr/part-<id>-<k>.mp3` 并生成 `asr/checklist.md`。
2. 逐条送 ASR，与 `clauses[].text` 比对：
   - **数字必须一致**（`四点零` ↔ `4.00`）
   - 繁体字 = 粤语输出 = 音色选错
3. 若某句转写里**混进了上一句的开头**，说明那句实际开口比估算晚 → 跑 `check-timing --calibrate`，
   然后**删掉该页帧目录重渲**。

### ⚠ 三个必须知道的 ASR 陷阱

**① 技术词会被系统性听错。** 实测（普通话女声）：
`纯文生视频`→`纯文声视频`/`春文升视频`、`首帧`→`手真`/`所捉手真`、`红晕`→`红运`/`鸿运`、
`带子`→`袋子`、`量`→`亮`、`四档肤色`→`涂色`。
→ **分句 ASR 的同音字差异一律不判失败**，只判数字、语种、缺字。

**② 切点落在估算边界上会串句。** 分句片段里混入上一句的尾巴（`…区间。两`）。
→ 先 `--calibrate` 再切。

**③ 交叉验证：整段 ASR。** 对有疑问的整页音频跑一次 ASR：
整段转写干净、完整、数字全对 → 证明**音频本身没问题**，问题在切点或 ASR 模型。
这是区分「配音缺陷」与「校验工具噪声」的唯一可靠办法。

**④ 数字比对要自己写中文数字转换。** `四点零`=4.0、`二点一五`=2.15、`二十八`=28、`三十六`=36；
连续数字无单位时按十进制拼接（`一五`=15），有单位时按单位算。
别用简单的字符替换 —— 那是假阳性来源。

---

## 五、出片后的自检

```bash
ffprobe -v error -show_entries format=duration -of json out/final.mp4   # 总时长
ffmpeg -v error -i out/final.mp4 -f null -                             # 完整解码自检
```

- 总时长应 ≈ `build/timings.json` 的合计（+ 首尾淡入淡出）。
- 抽查首帧、随机中间帧、末帧：字幕在、动效停稳了、图没错位。

---

## 六、交付清单

- [ ] `out/final.mp4`（1920×1080，H.264 + AAC）
- [ ] `out/subs.srt`
- [ ] `preview/play/index.html`（自包含放映页，用户双击即看）
- [ ] 工程包（排除 `build/frames` 与中间帧，避免几十 MB 的冗余）
- [ ] `00-项目索引.md`（每页结构表 + 数字出处）
- [ ] `README.md`（四步出片流程 + 改数据怎么改）
