/**
 * mini-charts.js — Compact vanilla-JS canvas charting library
 * Supports: line/area, grouped bar, bell curve (normal distribution)
 * No external dependencies — fully offline capable.
 */
(function (root) {
  'use strict';

  // ─── Global style constants ───────────────────────────────────────────────
  const STYLE = {
    primary:   '#06b6d4',
    secondary: '#0891b2',
    bg:        '#ffffff',
    gridLine:  '#f1f5f9',
    border:    '#e2e8f0',
    font:      "'Sarabun', sans-serif",
    pad: { top: 50, right: 30, bottom: 55, left: 65 },
  };

  // ─── Helpers ──────────────────────────────────────────────────────────────

  /** Lighten a hex color by `amount` (0–255). */
  function lightenColor(hex, amount) {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.min(255, (num >> 16) + amount);
    const g = Math.min(255, ((num >> 8) & 0xff) + amount);
    const b = Math.min(255, (num & 0xff) + amount);
    return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
  }

  /** Hex color → rgba string with given opacity. */
  function hexAlpha(hex, alpha) {
    const num = parseInt(hex.replace('#', ''), 16);
    return `rgba(${num >> 16},${(num >> 8) & 0xff},${num & 0xff},${alpha})`;
  }

  /** Draw a rounded-rectangle path (does not stroke/fill). */
  function roundRect(ctx, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  /** Apply a subtle drop-shadow to ctx. */
  function drawShadow(ctx) {
    ctx.shadowColor = 'rgba(0,0,0,0.08)';
    ctx.shadowBlur  = 8;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 2;
  }

  /** Clear shadow state. */
  function clearShadow(ctx) {
    ctx.shadowColor   = 'transparent';
    ctx.shadowBlur    = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
  }

  /**
   * Set up canvas for devicePixelRatio and return a context whose coordinate
   * system matches the CSS pixel dimensions.
   */
  function setupCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const w   = canvas.clientWidth  || canvas.width;
    const h   = canvas.clientHeight || canvas.height;
    canvas.width  = w * dpr;
    canvas.height = h * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    // White background + border via style (canvas element itself)
    canvas.style.background   = STYLE.bg;
    canvas.style.borderRadius = '8px';
    canvas.style.border       = `1px solid ${STYLE.border}`;
    return { ctx, w, h };
  }

  /** Format a number for axis labels. Percent-like if range is 100-200. */
  function fmtNum(v, isPercent) {
    if (isPercent) return v.toFixed(1) + '%';
    if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(1) + 'M';
    if (Math.abs(v) >= 1e3) return (v / 1e3).toFixed(1) + 'k';
    return Number.isInteger(v) ? v.toString() : v.toFixed(2);
  }

  /** Compute a clean set of ~5 tick values for [min, max]. */
  function niceAxis(min, max, count) {
    count = count || 5;
    const range = max - min || 1;
    const step  = Math.pow(10, Math.floor(Math.log10(range / count)));
    const nice  = [1, 2, 2.5, 5, 10].find(f => (range / (step * f)) <= count) * step;
    const lo    = Math.floor(min / nice) * nice;
    const ticks = [];
    for (let t = lo; t <= max + nice * 0.01; t += nice) ticks.push(parseFloat(t.toFixed(10)));
    return ticks;
  }

  /** Draw chart title (centered top) and caption (centered bottom). */
  function drawTitleCaption(ctx, w, h, title, caption) {
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'middle';
    if (title) {
      ctx.font      = `bold 15px ${STYLE.font}`;
      ctx.fillStyle = '#1e293b';
      ctx.fillText(title, w / 2, 18);
    }
    if (caption) {
      ctx.font      = `10px ${STYLE.font}`;
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(caption, w / 2, h - 10);
    }
  }

  /** Draw a legend box at top-left of the plot area. */
  function drawLegend(ctx, datasets, px) {
    const swSize  = 12;
    const padding = 7;
    const lineH   = 20;
    const boxW    = Math.max(...datasets.map(d => {
      ctx.font = `11px ${STYLE.font}`;
      return ctx.measureText(d.label || '').width;
    })) + swSize + padding * 2 + 8;
    const boxH = datasets.length * lineH + padding * 2 - 4;
    const bx   = px + 8;
    const by   = STYLE.pad.top + 8;

    // background
    drawShadow(ctx);
    roundRect(ctx, bx, by, boxW, boxH, 5);
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.fill();
    clearShadow(ctx);
    ctx.strokeStyle = STYLE.border;
    ctx.lineWidth   = 1;
    ctx.stroke();

    datasets.forEach((d, i) => {
      const cy = by + padding + i * lineH + 6;
      ctx.fillStyle = d.color || STYLE.primary;
      roundRect(ctx, bx + padding, cy - swSize / 2, swSize, swSize, 2);
      ctx.fill();
      ctx.font      = `11px ${STYLE.font}`;
      ctx.fillStyle = '#334155';
      ctx.textAlign    = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(d.label || '', bx + padding + swSize + 6, cy);
    });
  }

  // ─── Line / Area Chart ────────────────────────────────────────────────────

  function drawLine(canvas, opts) {
    opts = opts || {};
    const { ctx, w, h } = setupCanvas(canvas);
    const pad = STYLE.pad;
    const px  = pad.left, py = pad.top;
    const pw  = w - px - pad.right;
    const ph  = h - py - pad.bottom;

    const datasets = opts.datasets || [];
    const labels   = opts.labels   || [];
    const title    = opts.title    || '';
    const caption  = opts.caption  || '';

    // Compute Y range
    const allVals = datasets.flatMap(d => d.data || []);
    let yMin = opts.yMin != null ? opts.yMin : Math.min(...allVals);
    let yMax = opts.yMax != null ? opts.yMax : Math.max(...allVals);
    if (yMin === yMax) { yMin -= 1; yMax += 1; }
    const isPercent = yMin >= 80 && yMax <= 210;

    const ticks = niceAxis(yMin, yMax);
    const tMin  = ticks[0];
    const tMax  = ticks[ticks.length - 1];

    function xPos(i) { return px + (i / Math.max(labels.length - 1, 1)) * pw; }
    function yPos(v) { return py + ph - ((v - tMin) / (tMax - tMin)) * ph; }

    // Background
    ctx.fillStyle = STYLE.bg;
    ctx.fillRect(0, 0, w, h);

    // Gridlines
    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = STYLE.gridLine;
    ctx.lineWidth   = 1;
    ticks.forEach(t => {
      const y = yPos(t);
      ctx.beginPath();
      ctx.moveTo(px, y);
      ctx.lineTo(px + pw, y);
      ctx.stroke();
    });
    ctx.restore();

    // Y-axis labels
    ctx.font      = `11px ${STYLE.font}`;
    ctx.fillStyle = '#64748b';
    ctx.textAlign    = 'right';
    ctx.textBaseline = 'middle';
    ticks.forEach(t => ctx.fillText(fmtNum(t, isPercent), px - 8, yPos(t)));

    // Y-axis title
    if (opts.yLabel) {
      ctx.save();
      ctx.translate(14, py + ph / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'middle';
      ctx.font      = `11px ${STYLE.font}`;
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(opts.yLabel, 0, 0);
      ctx.restore();
    }

    // X-axis labels — left-align first, right-align last to prevent clipping
    ctx.font      = `10px ${STYLE.font}`;
    ctx.fillStyle = '#64748b';
    ctx.textBaseline = 'top';
    labels.forEach((lbl, i) => {
      if (labels.length <= 12 || i % Math.ceil(labels.length / 10) === 0) {
        ctx.textAlign = (i === 0) ? 'left' : (i === labels.length - 1) ? 'right' : 'center';
        ctx.fillText(lbl, xPos(i), py + ph + 6);
      }
    });
    ctx.textAlign = 'center';

    // Axis lines
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(px, py + ph);
    ctx.lineTo(px + pw, py + ph);
    ctx.stroke();

    // Datasets — fills first, then lines on top
    datasets.forEach(d => {
      if (d.pointOnly || !d.fill || !d.data.length) return;
      const color = d.color || STYLE.primary;
      ctx.beginPath();
      d.data.forEach((v, i) => {
        i === 0 ? ctx.moveTo(xPos(i), yPos(v)) : ctx.lineTo(xPos(i), yPos(v));
      });
      ctx.lineTo(xPos(d.data.length - 1), py + ph);
      ctx.lineTo(xPos(0), py + ph);
      ctx.closePath();
      ctx.fillStyle = hexAlpha(color, 0.12);
      ctx.fill();
    });

    datasets.forEach(d => {
      if (!d.data.length) return;
      const color = d.color || STYLE.primary;
      // pointOnly: draw isolated markers, no connecting line — for single
      // reference points (e.g. "Fractional Kelly") where a line would
      // misleadingly interpolate through null gaps as if it were a curve.
      if (d.pointOnly) {
        d.data.forEach((v, i) => {
          if (v == null) return;
          ctx.beginPath();
          ctx.fillStyle = color;
          ctx.arc(xPos(i), yPos(v), 5, 0, 2 * Math.PI);
          ctx.fill();
          ctx.lineWidth   = 2;
          ctx.strokeStyle = '#ffffff';
          ctx.stroke();
        });
        return;
      }
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth   = 2.5;
      ctx.lineJoin    = 'round';
      ctx.lineCap     = 'round';
      d.data.forEach((v, i) => {
        i === 0 ? ctx.moveTo(xPos(i), yPos(v)) : ctx.lineTo(xPos(i), yPos(v));
      });
      ctx.stroke();
    });

    drawTitleCaption(ctx, w, h, title, caption);
    if (datasets.some(d => d.label)) drawLegend(ctx, datasets, px);
  }

  // ─── Grouped Bar Chart ────────────────────────────────────────────────────

  function drawBar(canvas, opts) {
    opts = opts || {};
    const { ctx, w, h } = setupCanvas(canvas);
    const pad = STYLE.pad;
    const px  = pad.left, py = pad.top;
    const pw  = w - px - pad.right;
    const ph  = h - py - pad.bottom;

    const groups   = opts.groups   || [];
    const datasets = opts.datasets || [];
    const title    = opts.title    || '';
    const caption  = opts.caption  || '';

    const nGroups = groups.length;
    const nSets   = datasets.length;

    const allVals = datasets.flatMap(d => d.data || []);
    let yMin = (opts.yMin != null) ? opts.yMin : Math.min(...allVals, 0);
    let yMax = (opts.yMax != null) ? opts.yMax : Math.max(...allVals, 0);
    if (yMax === yMin) { yMin -= 1; yMax += 1; }
    const ticks = niceAxis(yMin, yMax);
    const tMin  = ticks[0];
    const tMax  = ticks[ticks.length - 1];

    function yPos(v) { return py + ph - ((v - tMin) / (tMax - tMin)) * ph; }

    const groupW   = pw / nGroups;
    const barGap   = 4;
    const barW     = Math.max(8, (groupW * 0.7) / Math.max(nSets, 1) - barGap);

    // Background
    ctx.fillStyle = STYLE.bg;
    ctx.fillRect(0, 0, w, h);

    // Gridlines
    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = STYLE.gridLine;
    ctx.lineWidth   = 1;
    ticks.forEach(t => {
      const y = yPos(t);
      ctx.beginPath();
      ctx.moveTo(px, y);
      ctx.lineTo(px + pw, y);
      ctx.stroke();
    });
    ctx.restore();

    // Y-axis labels
    ctx.font      = `11px ${STYLE.font}`;
    ctx.fillStyle = '#64748b';
    ctx.textAlign    = 'right';
    ctx.textBaseline = 'middle';
    ticks.forEach(t => ctx.fillText(fmtNum(t, false), px - 8, yPos(t)));

    // Y-axis title
    if (opts.yLabel) {
      ctx.save();
      ctx.translate(14, py + ph / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'middle';
      ctx.font      = `11px ${STYLE.font}`;
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(opts.yLabel, 0, 0);
      ctx.restore();
    }

    // Axis lines
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(px, py + ph);
    ctx.lineTo(px + pw, py + ph);
    ctx.stroke();

    // Bars — baseline at y=0 (clamped within axis range)
    const baseline = yPos(Math.max(tMin, Math.min(0, tMax)));

    // Zero line when range spans positive and negative
    if (tMin < 0 && tMax > 0) {
      ctx.save();
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth   = 1;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.moveTo(px, baseline);
      ctx.lineTo(px + pw, baseline);
      ctx.stroke();
      ctx.restore();
    }

    groups.forEach((grp, gi) => {
      const groupCenterX = px + (gi + 0.5) * groupW;
      const totalBarsW   = nSets * barW + (nSets - 1) * barGap;
      const startX       = groupCenterX - totalBarsW / 2;

      datasets.forEach((d, di) => {
        const val    = (d.data || [])[gi] || 0;
        const color  = d.color || STYLE.primary;
        const bx     = startX + di * (barW + barGap);
        const isNeg  = val < 0;
        const top    = isNeg ? baseline : yPos(val);
        const bottom = isNeg ? yPos(val) : baseline;
        const barH   = bottom - top;

        if (barH <= 0) return; // skip zero-height bars

        // Gradient fill
        const grad = ctx.createLinearGradient(bx, top, bx, bottom);
        grad.addColorStop(0, lightenColor(color, 40));
        grad.addColorStop(1, color);

        // Rounded corners: top for positive bars, bottom for negative bars
        ctx.save();
        const r = Math.min(4, barW / 2, barH / 2);
        ctx.beginPath();
        if (isNeg) {
          ctx.moveTo(bx, top);
          ctx.lineTo(bx + barW, top);
          ctx.lineTo(bx + barW, bottom - r);
          ctx.quadraticCurveTo(bx + barW, bottom, bx + barW - r, bottom);
          ctx.lineTo(bx + r, bottom);
          ctx.quadraticCurveTo(bx, bottom, bx, bottom - r);
        } else {
          ctx.moveTo(bx + r, top);
          ctx.lineTo(bx + barW - r, top);
          ctx.quadraticCurveTo(bx + barW, top, bx + barW, top + r);
          ctx.lineTo(bx + barW, bottom);
          ctx.lineTo(bx, bottom);
          ctx.lineTo(bx, top + r);
          ctx.quadraticCurveTo(bx, top, bx + r, top);
        }
        ctx.closePath();
        ctx.fillStyle = grad;
        drawShadow(ctx);
        ctx.fill();
        clearShadow(ctx);
        ctx.restore();

        // Value label: above bar for positive, below for negative
        if (barH > 12) {
          ctx.font      = `9px ${STYLE.font}`;
          ctx.fillStyle = '#475569';
          ctx.textAlign    = 'center';
          if (isNeg) {
            ctx.textBaseline = 'top';
            ctx.fillText(fmtNum(val, false), bx + barW / 2, bottom + 2);
          } else {
            ctx.textBaseline = 'bottom';
            ctx.fillText(fmtNum(val, false), bx + barW / 2, top - 2);
          }
        }
      });

      // X group label at baseline (zero line)
      ctx.font      = `10px ${STYLE.font}`;
      ctx.fillStyle = '#64748b';
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(grp, groupCenterX, baseline + 6);
    });

    drawTitleCaption(ctx, w, h, title, caption);
    if (datasets.some(d => d.label)) drawLegend(ctx, datasets, px);
  }

  // ─── Bell Curve / Normal Distribution ────────────────────────────────────

  function drawBell(canvas, opts) {
    opts = opts || {};
    const { ctx, w, h } = setupCanvas(canvas);
    const pad = STYLE.pad;
    const px  = pad.left, py = pad.top;
    const pw  = w - px - pad.right;
    const ph  = h - py - pad.bottom;

    const mean        = opts.mean  || 0;
    const std         = opts.std   || 1;
    const title       = opts.title || '';
    const caption     = opts.caption     || '';
    const denseLabel  = opts.denseLabel  || '68% of trades';
    const sparseLabel = opts.sparseLabel || '27% of trades';

    const xMin = mean - 3 * std;
    const xMax = mean + 3 * std;

    function normalPDF(x) {
      const z = (x - mean) / std;
      return Math.exp(-0.5 * z * z) / (std * Math.sqrt(2 * Math.PI));
    }

    const STEPS = 300;
    const dx    = (xMax - xMin) / STEPS;
    const ys    = Array.from({ length: STEPS + 1 }, (_, i) => normalPDF(xMin + i * dx));
    const yMax  = Math.max(...ys) * 1.15;

    function xPos(v) { return px + ((v - xMin) / (xMax - xMin)) * pw; }
    function yPos(v) { return py + ph - (v / yMax) * ph; }

    const baseline   = py + ph;
    const s1lo = xPos(mean - std);
    const s1hi = xPos(mean + std);
    const s2lo = xPos(mean - 2 * std);
    const s2hi = xPos(mean + 2 * std);

    // Background
    ctx.fillStyle = STYLE.bg;
    ctx.fillRect(0, 0, w, h);

    // Dense gridlines (inside ±1σ)
    ctx.save();
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = '#e0f2fe';
    ctx.lineWidth   = 1;
    for (let i = 0; i <= 6; i++) {
      const gx = s1lo + (i / 6) * (s1hi - s1lo);
      ctx.beginPath();
      ctx.moveTo(gx, py);
      ctx.lineTo(gx, baseline);
      ctx.stroke();
    }
    ctx.restore();

    // Sparse gridlines (outside ±1σ, inside ±2σ)
    ctx.save();
    ctx.setLineDash([4, 6]);
    ctx.strokeStyle = STYLE.gridLine;
    ctx.lineWidth   = 1;
    [[s2lo, s1lo], [s1hi, s2hi]].forEach(([lo, hi]) => {
      for (let i = 0; i <= 3; i++) {
        const gx = lo + (i / 3) * (hi - lo);
        ctx.beginPath();
        ctx.moveTo(gx, py);
        ctx.lineTo(gx, baseline);
        ctx.stroke();
      }
    });
    ctx.restore();

    // ±2σ sparse fill (outline region)
    const buildCurve = (lo, hi) => {
      const pts = [];
      for (let i = 0; i <= STEPS; i++) {
        const xv = xMin + i * dx;
        if (xv >= lo && xv <= hi) pts.push([xPos(xv), yPos(normalPDF(xv))]);
      }
      return pts;
    };

    const drawRegion = (lo, hi, fillStyle, strokeStyle) => {
      const pts = buildCurve(lo, hi);
      if (!pts.length) return;
      ctx.beginPath();
      ctx.moveTo(pts[0][0], baseline);
      pts.forEach(([cx, cy]) => ctx.lineTo(cx, cy));
      ctx.lineTo(pts[pts.length - 1][0], baseline);
      ctx.closePath();
      if (fillStyle)   { ctx.fillStyle   = fillStyle;   ctx.fill();   }
      if (strokeStyle) { ctx.strokeStyle = strokeStyle; ctx.lineWidth = 1.5; ctx.stroke(); }
    };

    // Sparse zones (±2σ excluding ±1σ)
    drawRegion(mean - 2 * std, mean - std, 'rgba(148,163,184,0.15)', '#94a3b8');
    drawRegion(mean + std,     mean + 2 * std, 'rgba(148,163,184,0.15)', '#94a3b8');

    // Dense zone (±1σ) — cyan
    drawRegion(mean - std, mean + std, hexAlpha(STYLE.primary, 0.25), STYLE.primary);

    // Full curve outline
    ctx.beginPath();
    ctx.strokeStyle = STYLE.secondary;
    ctx.lineWidth   = 2.5;
    ctx.lineJoin    = 'round';
    for (let i = 0; i <= STEPS; i++) {
      const xv = xMin + i * dx;
      i === 0
        ? ctx.moveTo(xPos(xv), yPos(normalPDF(xv)))
        : ctx.lineTo(xPos(xv), yPos(normalPDF(xv)));
    }
    ctx.stroke();

    // Axis lines
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(px, baseline);
    ctx.lineTo(px + pw, baseline);
    ctx.stroke();

    // X-axis labels: -2σ -1σ μ +1σ +2σ
    const sigmaLabels = [
      { v: mean - 2 * std, lbl: '-2σ' },
      { v: mean - std,     lbl: '-1σ' },
      { v: mean,           lbl: 'μ'   },
      { v: mean + std,     lbl: '+1σ' },
      { v: mean + 2 * std, lbl: '+2σ' },
    ];
    ctx.font      = `11px ${STYLE.font}`;
    ctx.fillStyle = '#64748b';
    ctx.textAlign    = 'center';
    ctx.textBaseline = 'top';
    sigmaLabels.forEach(({ v, lbl }) => ctx.fillText(lbl, xPos(v), baseline + 6));

    // Annotation helper
    function annotationBox(bx, by, bw, bh, header, body, bgColor, borderColor) {
      ctx.save();
      drawShadow(ctx);
      roundRect(ctx, bx, by, bw, bh, 5);
      ctx.fillStyle   = bgColor     || 'rgba(255,255,255,0.92)';
      ctx.fill();
      clearShadow(ctx);
      ctx.strokeStyle = borderColor || STYLE.border;
      ctx.lineWidth   = 1;
      ctx.stroke();
      ctx.restore();
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'middle';
      ctx.font      = `bold 9px ${STYLE.font}`;
      ctx.fillStyle = '#0e7490';
      ctx.fillText(header, bx + bw / 2, by + bh / 3);
      ctx.font      = `9px ${STYLE.font}`;
      ctx.fillStyle = '#334155';
      ctx.fillText(body,   bx + bw / 2, by + bh * 2 / 3);
    }

    // Center dense-zone box
    const cboxW = Math.min(140, s1hi - s1lo - 8);
    const cboxH = 34;
    const cboxX = (s1lo + s1hi) / 2 - cboxW / 2;
    const cboxY = py + ph * 0.55;
    annotationBox(cboxX, cboxY, cboxW, cboxH,
      'Dense Zone (±1σ)', denseLabel,
      'rgba(236,254,255,0.95)', '#67e8f9');

    // Left sparse box
    const sboxW = Math.min(90, s1lo - s2lo - 8);
    const sboxH = 30;
    const sboxY = py + ph * 0.62;
    annotationBox(s2lo + 4, sboxY, sboxW, sboxH,
      'Sparse Zone', sparseLabel,
      'rgba(248,250,252,0.92)', '#cbd5e1');

    // Right sparse box
    annotationBox(s1hi + 4, sboxY, sboxW, sboxH,
      'Sparse Zone', sparseLabel,
      'rgba(248,250,252,0.92)', '#cbd5e1');

    drawTitleCaption(ctx, w, h, title, caption);
  }

  // ─── Public API ───────────────────────────────────────────────────────────
  root.MiniChart = {
    line: drawLine,
    bar:  drawBar,
    bell: drawBell,
    /** Expose internal helpers for external use / testing. */
    _util: { lightenColor, roundRect, drawShadow, hexAlpha },
  };

}(window));
