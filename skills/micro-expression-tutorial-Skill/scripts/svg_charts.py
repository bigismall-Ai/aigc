#!/usr/bin/env python3
"""自绘 SVG 图表组件库 —— 教学片的图表默认用这个，不要用 mermaid。

设计目标：颜色直接取主题令牌、零运行时依赖、宽高比可控。

用法：
    from svg_charts import PALETTE, band_bar, line_chart, stacked_bar
    html = band_bar(cats=[('真人中位', 4.00), ('纯文生视频', 12.71)],
                    band=(-2.15, 10.90), band_labels=('真人带下界 −2.15','真人带上界 +10.90'),
                    title='彩度增量 ΔC*（红晕区 − 同脸基线）', ylabel='彩度增量 ΔC*')

三条硬规矩（写在这里就是为了不被忘掉）：
1. 柱位必须内缩：centers = px0 + slot*(i+0.5)，不要用 px0 + inner*i/(n-1)
   —— 两端对齐会让首尾柱子各挂出去一半（压住刻度 / 被区间边界切开）。
2. 区间上下界标注放坐标区**右侧留白**，viewBox 宽度要留够，否则文字被裁。
3. 刻度数字贴 px0-18，旋转轴标题放 x=34，两者留间距；信息重复时直接删轴标题。
"""
from __future__ import annotations

# ── 主题令牌（tokyo-night）—— 换成别的主题时只改这里
PALETTE = dict(
    bg='#1A1B26', panel='#2F334D', line='rgba(192,202,245,.14)',
    fg='#C0CAF5', muted='#A9B1D6', dim='#565F89',
    accent='#7AA2F7', accent2='#BB9AF7', accent3='#7DCFFF',
    good='#9ECE6A', warn='#E0AF68', bad='#F7768E',
)
FONT = 'Noto Sans CJK SC, Noto Sans SC, Microsoft YaHei, sans-serif'


def _svg(w, h, body, cls='chart'):
    return (f'<div class="{cls}"><svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="{FONT}">{body}</svg></div>')


def _axes(vmin, vmax, px0, px1, py0, py1, step, tick_font=20, fmt='{:g}'):
    """返回 (Y 函数, 轴与网格线 svg 片段)"""
    def Y(v):
        return py1 - (v - vmin) / (vmax - vmin) * (py1 - py0)
    out = []
    v = vmin
    while v <= vmax + 1e-9:
        y = Y(v)
        out.append(f'<line x1="{px0}" y1="{y:.1f}" x2="{px1}" y2="{y:.1f}" '
                   f'stroke="{PALETTE["line"]}" stroke-width="1"/>')
        out.append(f'<text x="{px0-18}" y="{y+7:.1f}" fill="{PALETTE["dim"]}" '
                   f'font-size="{tick_font}" text-anchor="end">{fmt.format(v)}</text>')
        v += step
    return Y, ''.join(out)


def band_bar(cats, band=None, band_labels=None, title='', ylabel='',
             vmin=-4.0, vmax=14.0, step=2, colors=None, width=1340, height=430,
             value_fmt='{:+.2f}', label_font=22):
    """区间底色 + 柱状图。

    cats   : [(名称, 数值), ...]
    band   : (下界, 上界)；None = 不画区间
    colors : 每个柱子的颜色；None = 按 accent/bad/accent2/good 轮转
    """
    n = len(cats)
    px0, px1, py0, py1 = 128, width - 250, 74, height - 100
    slot = (px1 - px0) / n
    centers = [px0 + slot * (i + 0.5) for i in range(n)]
    bw = slot * 0.52
    Y, grid = _axes(vmin, vmax, px0, px1, py0, py1, step)
    s = []
    if band:
        lo, hi = band
        s.append(f'<rect x="{px0}" y="{Y(hi):.1f}" width="{px1-px0}" '
                 f'height="{Y(lo)-Y(hi):.1f}" fill="rgba(122,162,247,.09)"/>')
        for v, lab in ((hi, (band_labels or ['', ''])[1]), (lo, (band_labels or ['', ''])[0])):
            s.append(f'<line x1="{px0}" y1="{Y(v):.1f}" x2="{px1}" y2="{Y(v):.1f}" '
                     f'stroke="{PALETTE["accent"]}" stroke-width="1" stroke-dasharray="6 6" opacity=".75"/>')
            if lab:
                s.append(f'<text x="{px1+18}" y="{Y(v)+7:.1f}" fill="{PALETTE["accent"]}" '
                         f'font-size="21" text-anchor="start">{lab}</text>')
    s.append(grid)
    s.append(f'<line x1="{px0}" y1="{Y(0):.1f}" x2="{px1}" y2="{Y(0):.1f}" '
             f'stroke="{PALETTE["line"]}" stroke-width="1.5"/>')
    if ylabel:
        mid = (py0 + py1) / 2
        s.append(f'<text x="34" y="{mid:.0f}" fill="{PALETTE["muted"]}" font-size="20" '
                 f'transform="rotate(-90 34 {mid:.0f})" text-anchor="middle">{ylabel}</text>')
    default = [PALETTE['accent'], PALETTE['bad'], PALETTE['accent2'], PALETTE['good'],
               PALETTE['accent3'], PALETTE['warn']]
    for i, (name, val) in enumerate(cats):
        col = (colors[i] if colors else default[i % len(default)])
        x = centers[i] - bw / 2
        y = Y(max(val, 0))
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                 f'height="{Y(0)-y:.1f}" rx="4" fill="{col}" opacity=".92"/>')
        s.append(f'<text x="{centers[i]:.1f}" y="{y-16:.1f}" fill="{PALETTE["fg"]}" '
                 f'font-size="25" font-weight="700" text-anchor="middle">{value_fmt.format(val)}</text>')
        s.append(f'<text x="{centers[i]:.1f}" y="{py1+44:.1f}" fill="{PALETTE["muted"]}" '
                 f'font-size="{label_font}" text-anchor="middle">{name}</text>')
    if title:
        s.append(f'<text x="{px0}" y="38" fill="{PALETTE["fg"]}" font-size="24" '
                 f'font-weight="700">{title}</text>')
    return _svg(width, height, ''.join(s))


def line_chart(pts, title='', xlabel='', xmax=None, vmin=-2.0, vmax=10.0, step=2,
               annotate=None, width=1180, height=400, fill=True):
    """折线图（带渐变面积 + 数据点）。pts = [(x, y), ...]"""
    px0, px1, py0, py1 = 110, width - 50, 74, height - 94
    xmax = xmax or max(p[0] for p in pts)
    Y, grid = _axes(vmin, vmax, px0, px1, py0, py1, step, tick_font=19)
    def X(x): return px0 + (px1 - px0) * x / xmax
    s = []
    if fill:
        s.append(f'<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{PALETTE["accent"]}" stop-opacity=".30"/>'
                 f'<stop offset="1" stop-color="{PALETTE["accent"]}" stop-opacity="0"/>'
                 f'</linearGradient></defs>')
    s.append(grid)
    s.append(f'<line x1="{px0}" y1="{Y(0):.1f}" x2="{px1}" y2="{Y(0):.1f}" '
             f'stroke="{PALETTE["line"]}" stroke-width="1.5"/>')
    n = int(xmax) + 1
    for t in range(n):
        s.append(f'<text x="{X(t):.1f}" y="{py1+36:.1f}" fill="{PALETTE["dim"]}" '
                 f'font-size="19" text-anchor="middle">{t}.0</text>')
    poly = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
    if fill:
        s.append(f'<polygon points="{px0},{Y(0):.1f} {poly} {px1},{Y(0):.1f}" fill="url(#ag)"/>')
    s.append(f'<polyline points="{poly}" fill="none" stroke="{PALETTE["accent"]}" stroke-width="4" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y in pts:
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="6" fill="{PALETTE["bg"]}" '
                 f'stroke="{PALETTE["accent"]}" stroke-width="3"/>')
    if annotate:
        ax, ay, tx, ty, lab = annotate
        s.append(f'<line x1="{X(ax):.1f}" y1="{Y(ay)-16:.1f}" x2="{X(ax)+150:.1f}" y2="{Y(ay)-92:.1f}" '
                 f'stroke="{PALETTE["accent2"]}" stroke-width="2"/>')
        s.append(f'<text x="{X(ax)+160:.1f}" y="{Y(ay)-96:.1f}" fill="{PALETTE["accent2"]}" '
                 f'font-size="22">{lab}</text>')
    if title:
        s.append(f'<text x="{px0}" y="38" fill="{PALETTE["fg"]}" font-size="24" font-weight="700">{title}</text>')
    if xlabel:
        s.append(f'<text x="{(px0+px1)/2:.0f}" y="{height-14}" fill="{PALETTE["muted"]}" '
                 f'font-size="19" text-anchor="middle">{xlabel}</text>')
    return _svg(width, height, ''.join(s))


def stacked_bar(segments, width=560, height=96, bar_h=34, y=26):
    """占比条。segments = [(数量, 颜色, 标签), ...]"""
    total = sum(n for n, _, _ in segments) or 1
    s = []
    x = 0
    span = width - 40
    for n, col, lab in segments:
        w = span * n / total
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{bar_h}" fill="{col}" rx="3"/>')
        s.append(f'<text x="{x+w/2:.0f}" y="{y+bar_h+30}" fill="{PALETTE["muted"]}" '
                 f'font-size="20" text-anchor="middle">{lab}</text>')
        x += w
    return _svg(width, height, ''.join(s))


if __name__ == '__main__':
    # 冒烟：打印三张图的首行，确认能生成
    print(band_bar(cats=[('真人中位', 4.00), ('纯文生视频', 12.71),
                         ('锁首帧生成', 8.39), ('后期稀释后', 3.87)],
                   band=(-2.15, 10.90),
                   band_labels=('真人带下界 −2.15', '真人带上界 +10.90'),
                   title='彩度增量 ΔC*（红晕区 − 同脸基线）', ylabel='彩度增量 ΔC*')[:120])
    print(line_chart([(0, 0), (1, 1), (2, 4), (3, 8)], title='t')[:120])
    print(stacked_bar([(9, PALETTE['accent'], '过门 9 张'),
                       (9, 'rgba(192,202,245,.20)', '剔除 9 张')])[:120])
