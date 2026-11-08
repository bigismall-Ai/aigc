# 幻灯工程规范 · HTML 教学片

> 目标：每页 **图文并茂**、**一眼看懂**、**不溢出**、**不空转**。
> 配色一律取主题令牌（`tokens.css` 的 `--fg/--muted/--accent/--good/--bad/--line/--panel-2`），
> 不要写死十六进制 —— 换主题时不会串色。

---

## 一、页面骨架

```html
<!doctype html>
<html lang="zh-CN" data-theme="tokyo-night">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="tokens.css">
<style> /* 自定义规则写这里 */ </style>
</head>
<body>
<div class="stage">
  <span class="brand">栏目标题 · 一句话定位</span>
  <main class="layout">
    <h1 class="fx-up" data-stage="1">主标题</h1>
    <p class="lead fx-fade" data-stage="1">导语（这句话要能独立成立）</p>
    <div class="fx-fade" data-stage="2"> … 内容 … </div>
  </main>
  <span class="slide-num">03 / 17</span>
</div>
</body>
</html>
```

**强同步原则**：讲「大数字 / 关键图」的那一句口播，对应的元素要**在那一句开口时入场**。
所以「先标题、后图、再卡片」这种固定顺序不一定对 —— 看口播顺序。

---

## 二、卡片组件（替代 mermaid flowchart）

```css
.flowrow { display:flex; align-items:stretch; gap:var(--sp-3); width:100%; }
.flowrow .fcard { flex:1; background:var(--panel-2); border-radius:var(--radius-sm);
                  padding:var(--sp-4) var(--sp-4); border-top:2px solid var(--accent); }
.flowrow .fcard.plain { border-top-color:var(--line-strong); }
.flowrow .fcard .step { font-family:var(--font-mono); font-size:var(--fs-tiny);
                        letter-spacing:.16em; color:var(--accent); }
.flowrow .fcard h3 { font-size:var(--fs-h3); line-height:1.22; margin:8px 0 10px; }
.flowrow .fcard p { font-size:var(--fs-caption); color:var(--muted); line-height:1.55; }
.flowrow .fcard .tag { display:inline-block; margin-top:12px; padding:3px 12px;
                       border-radius:999px; font-size:var(--fs-tiny); }
.flowrow .fcard .tag.ok { color:var(--good); border:1px solid var(--good); }
.flowrow .fcard .tag.no { color:var(--bad);  border:1px solid var(--bad); }
.flowrow .farrow { align-self:center; flex:none; font-size:var(--fs-h2);
                   color:var(--accent); opacity:.75; }
```

用法：

```html
<div class="flowrow fx-fade" data-stage="2">
  <div class="fcard">
    <p class="step">STEP 01</p>
    <h3>量</h3>
    <p>找 8~20 张真人参考图，每张手工框两块。</p>
  </div>
  <div class="farrow">→</div>
  <div class="fcard"> … </div>
</div>
```

**要点**
- 卡片高度由 `align-items:stretch` 统一，最长那段的文字决定整体高度 → **先把每张卡的文字写到差不多长度**。
- 4 张卡以上慎用（1920 宽每张不到 400px，字会挤）；超过 4 个步骤就拆成两页。
- 步骤序号用 `.step`（等宽 + 字距），不要用「第一步/第二步」占空间。

---

## 三、判定条（两栏结论）

```css
.verdict { display:flex; gap:var(--sp-3); width:100%; }
.verdict .v { flex:1; border-radius:var(--radius-sm); padding:var(--sp-3) var(--sp-4);
              font-size:var(--fs-caption); line-height:1.5; }
.verdict .v.no { background:rgba(247,118,142,.10); border:1px solid rgba(247,118,142,.38); color:var(--bad); }
.verdict .v.ok { background:rgba(158,206,106,.10); border:1px solid rgba(158,206,106,.38); color:var(--good); }
.verdict .v b { display:block; font-size:var(--fs-h3); margin-bottom:4px; }
```

---

## 四、三联样片（对比页）

```css
.trio { display:grid; grid-template-columns:repeat(3,1fr); gap:var(--sp-5); }
.trio figure { margin:0; }
.trio img { display:block; width:100%; max-height:430px; object-fit:cover;
           border-radius:var(--radius-sm); border:1px solid var(--line); }
.trio figcaption { margin-top:12px; font-size:var(--fs-caption); line-height:1.5; }
.trio .lab { display:block; font-size:var(--fs-h3); font-weight:700; margin-bottom:6px; }
.trio .sub { color:var(--muted); }
```

**三联图的语义必须分清**：三张图不是「三个版本」，而是**三种不同的东西**
（例如：真人的 / 情绪错的 / 我们要的）。标签要写**现象名**，不写版本号。

---

## 五、自绘 SVG 图表规范

用 `scripts/svg_charts.py`（可直接 import），或照它的规则手写。

### 5.1 三条硬规矩

1. **柱位必须内缩**
   ```python
   slot = (px1 - px0) / n
   centers = [px0 + slot * (i + 0.5) for i in range(n)]   # ← 不要用 px0 + inner*i/(n-1)
   bw = slot * 0.52
   ```
   用两端对齐的算法（`i/(n-1)`）会让**第一根和最后一根柱子各挂出去一半**：
   第一根压住 y 轴刻度，最后一根被区间底色的右边界切过去。这是「图表错位」最常见的病因。

2. **右侧留白放区间标注**
   区间上下界的文字放在坐标区**外面**（`x = px1 + 18`，`text-anchor="start"`），
   viewBox 宽度要留够，否则文字被裁（出现过「+10.9」少个 0）。

3. **轴标题与刻度数字分层**
   刻度数字贴 `px0 - 18`，旋转的轴标题放 `x = 34`；两者必须留出间距。
   标题重复了轴标题能表达的信息时，**直接删掉轴标题**。

### 5.2 区间底色 + 柱状图（真人带对照）

```python
s.append(f'<rect x="{px0}" y="{Y(10.90):.1f}" width="{px1-px0}" '
         f'height="{Y(-2.15)-Y(10.90):.1f}" fill="rgba(122,162,247,.09)"/>')
for v, lab in [(10.90,'真人带上界 +10.90'), (-2.15,'真人带下界 −2.15')]:
    s.append(f'<line x1="{px0}" y1="{Y(v):.1f}" x2="{px1}" y2="{Y(v):.1f}" '
             f'stroke="{C["accent"]}" stroke-width="1" stroke-dasharray="6 6" opacity=".75"/>')
    s.append(f'<text x="{px1+18}" y="{Y(v)+7:.1f}" fill="{C["accent"]}" '
             f'font-size="21" text-anchor="start">{lab}</text>')
```

### 5.3 折线图（时序）

- 折线下方加一层渐变面积（`linearGradient` + `stop-opacity .30 → 0`），视觉更像「升起」。
- 每个采样点画 `circle`（`fill=背景色`，`stroke=线色`，`stroke-width=3`），点更清楚。
- 关键节点加引线标注（引线用另一个色 `accent2`，别和线同色）。
- x 轴刻度写一位小数（`0.0 / 0.5 / …`），末尾补轴名「时间（秒）」。

### 5.4 配色

深色主题令牌（tokyo-night）：

| 用途 | 值 |
|---|---|
| 正文 | `#C0CAF5` |
| 次要 | `#A9B1D6` |
| 弱 | `#565F89` |
| 主强调 | `#7AA2F7` |
| 副强调 | `#BB9AF7` |
| 正向 | `#9ECE6A` |
| 负向 | `#F7768E` |

柱子颜色要有语义：中性蓝 / 负向红 / 正向绿，不要同色系随便挑。

---

## 六、版式避坑清单（每条都踩过）

| 坑 | 症状 | 修法 |
|---|---|---|
| `data-stage` 没有配 fx 类 | **整页静默空白**，所有脚本却报成功 | `data-stage` 必须与 `fx-*` 同时用；`.fx-stagger` 容器自身不能再带 `data-stage` |
| 自定义布局类没定义 | 静默竖排，不报错 | 在公共 CSS 里补齐；或直接内联 `display:grid` |
| `.img-frame` 满宽 | 按 `--img-ratio` 把高度放到 900px+，撑破版面 | 给 `figure` 限宽（如 `max-width:600px`） |
| 柱位用两端对齐 | 首尾柱子挂出坐标区 | 按 `slot*(i+0.5)` 内缩 |
| 区间标注放坐标区内 | 压在柱子上 / 被裁 | 放右侧留白，viewBox 留够 |
| 口播超长 | 字幕折 3 行，可读性差 | 一句 ≤ 60 字符；`plan-timings` 会警告 |
| 竖排文字当正文 | 中文竖排在大屏不可读 | 只有标签/标题可竖排 |

---

## 七、图文页的图怎么选

- **实拍 / 实测优先**：真人参考图、生成帧、量出来的曲线。装饰性插画在技术教程里是负资产。
- **自己裁的切片要标注**：从大图裁出来的颊部特写、对比条，figcaption 要说清裁的是哪部分。
- **删掉版本号命名的素材**：`seq-v1.png` / `cmp-versions.png` 这类文件不要进片，
  它们会把「过程」带回来。
- **配图来源写进 `assets/MANIFEST.md`**：文件、它是什么、从哪来、许可。

---

## 八、主题与受管区

`tokens.css` 的受管区由 `html2video-for-mcode` 生成，**不要手改里面的规则**；
自己的样式写在文件末尾或幻灯的 `<style>` 里。

改过受管区的规则后跑：

```bash
node <skill>/scripts/init-project.mjs <project> --check-css
```

返回 `ok` 才继续 —— `check-slides` / `capture` / `build-video` 在受管区过期时会拒绝运行。
