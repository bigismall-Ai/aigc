"""Measure a skin-colour effect the way it has to be measured: against the same subject's own baseline.

Reports, for the effect region:
  R-B      red minus blue (how red the flush is)
  P        pinkness index = dG/dR against the same face's own baseline
  S, V     HSL saturation and value
  H, L*, a*, C*   CIELAB
  dL*, da*, dC*   versus the same-frame unblushed skin
plus the coverage of the detected flush region.

Usage:
  python3 measure_skin_color.py <in.mp4> [--core x0,y0,x1,y1] [--frame -1]
"""
import subprocess, sys, json, colorsys
import numpy as np
from PIL import Image
from dilute_skin_color import (srgb_to_lab, skin_mask, blush_mask, dilate_bool, read_frames)


def rgb_to_hsl(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    mx, mn = c.max(-1), c.min(-1)
    d = mx - mn
    l = (mx + mn) / 2
    s = np.where(d == 0, 0, d / (1 - np.abs(2 * l - 1)))
    h = np.zeros_like(mx)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    m = (d != 0)
    mh = (mx == r) & m
    h[mh] = ((g - b)[mh] / d[mh]) % 6
    mh = (mx == g) & m
    h[mh] = ((b - r)[mh] / d[mh]) + 2
    mh = (mx == b) & m
    h[mh] = ((r - g)[mh] / d[mh]) + 4
    return h * 60, s * 100, l * 100


def pack(rgb):
    h, s, l = rgb_to_hsl(rgb)
    lab = srgb_to_lab(rgb)
    return {'rgb': [round(float(v), 1) for v in rgb], 'H': round(float(h), 1),
            'S': round(float(s), 1), 'V': round(float(l), 1),
            'Lstar': round(float(lab[0]), 1), 'a': round(float(lab[1]), 1),
            'b': round(float(lab[2]), 1), 'C': round(float(np.hypot(lab[1], lab[2])), 1),
            'RB': round(float(rgb[0] - rgb[2]), 1)}


def main():
    path = sys.argv[1]
    core = None
    frame_idx = -1
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == '--core':
            core = tuple(int(v) for v in args[i + 1].split(','))
        elif a == '--frame':
            frame_idx = int(args[i + 1])
    frames, w, h, fps = read_frames(path)
    f = frames[frame_idx].astype(np.float64)
    lab = srgb_to_lab(f)
    skin = skin_mask(f)
    cm, binm = blush_mask(f, lab)

    if core:
        x0, y0, x1, y1 = core
        sel = np.zeros((h, w), bool)
        sel[y0:y1, x0:x1] = True
        sel &= (skin | (f[..., 0] > f[..., 2] + 6))
    else:
        sel = binm
    if sel.sum() < 50:
        print('no effect region detected; pass --core x0,y0,x1,y1')
        return

    # baseline: skin just outside the flush, same lighting plane, same frame
    ring = dilate_bool(sel, 27) & (~sel) & skin
    if ring.sum() < 300:
        ring = (~sel) & skin
    base_px = f[ring]
    base = pack(np.median(base_px, 0))
    flush = pack(np.median(f[sel], 0))

    dR = flush['rgb'][0] - base['rgb'][0]
    dG = flush['rgb'][1] - base['rgb'][1]
    P = round(dG / dR, 3) if abs(dR) >= 8 else None
    print(json.dumps({
        'file': path, 'frame': frame_idx, 'flush_px': int(sel.sum()),
        'coverage_pct': round(float(sel.sum()) / (w * h) * 100, 2),
        'flush': flush, 'baseline': base,
        'P': P, 'RB_delta': round(dR - (flush['rgb'][2] - base['rgb'][2]), 1),
        'dLstar': round(flush['Lstar'] - base['Lstar'], 2),
        'da': round(flush['a'] - base['a'], 2),
        'dC': round(flush['C'] - base['C'], 2),
        'Cratio': round(flush['C'] / max(base['C'], 1e-6), 3),
        'Sratio': round(flush['S'] / max(base['S'], 1e-6), 3),
    }, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
