// app.js - Main application controller
// Handles: navigation, lesson rendering, chart updates, sandbox, state management

const App = (() => {
  // ============================================================
  // State
  // ============================================================

  const state = {
    currentIndex: 0,
    params: {},
    visited: new Set(),
    sandboxLegs: []
  };

  // ============================================================
  // Initialization
  // ============================================================

  function init() {
    loadProgress();
    buildSidebar();
    bindGlobalEvents();

    // Start at saved position or first lesson
    const saved = localStorage.getItem('payoff_currentIndex');
    const startIdx = saved ? parseInt(saved, 10) : 0;
    navigateTo(Math.min(startIdx, LESSONS.length - 1));
  }

  // ============================================================
  // Sidebar Navigation
  // ============================================================

  function buildSidebar() {
    const navList = document.getElementById('nav-list');
    if (!navList) return;

    let html = '';
    let currentSection = -1;

    LESSONS.forEach((lesson, idx) => {
      if (lesson.section !== currentSection) {
        currentSection = lesson.section;
        html += '<li class="nav-section">' + currentSection + '. ' + lesson.sectionTitle + '</li>';
      }

      const visitedClass = state.visited.has(idx) ? ' visited' : '';
      const checkMark = state.visited.has(idx) ? '&#10003;' : '';
      html += '<li class="nav-item' + visitedClass + '" data-index="' + idx + '">' +
        '<span class="check">' + checkMark + '</span>' +
        '<span class="title">' + lesson.id + ' ' + lesson.title + '</span>' +
        '</li>';
    });

    navList.innerHTML = html;
    updateProgress();
  }

  function updateSidebarActive() {
    const items = document.querySelectorAll('.nav-item');
    items.forEach(item => {
      const idx = parseInt(item.dataset.index, 10);
      item.classList.toggle('active', idx === state.currentIndex);
      if (state.visited.has(idx)) {
        item.classList.add('visited');
        item.querySelector('.check').innerHTML = '&#10003;';
      }
    });
  }

  function updateProgress() {
    const total = LESSONS.length;
    const done = state.visited.size;
    const pct = Math.round((done / total) * 100);

    const progressText = document.getElementById('progress-text');
    const progressFill = document.getElementById('progress-fill');
    if (progressText) progressText.textContent = done + ' / ' + total + ' บทเรียน';
    if (progressFill) progressFill.style.width = pct + '%';
  }

  // ============================================================
  // Navigation
  // ============================================================

  function navigateTo(index) {
    if (index < 0 || index >= LESSONS.length) return;

    state.currentIndex = index;
    state.visited.add(index);
    saveProgress();

    const lesson = LESSONS[index];
    state.params = Object.assign({}, lesson.defaultParams);
    state.sandboxLegs = [];

    renderLesson(lesson);
    updateSidebarActive();
    updateProgress();

    // Scroll to top
    const mainEl = document.getElementById('main');
    if (mainEl) mainEl.scrollTop = 0;
    window.scrollTo(0, 0);

    // Close mobile sidebar
    closeSidebar();
  }

  // ============================================================
  // Lesson Rendering
  // ============================================================

  function renderLesson(lesson) {
    const contentEl = document.getElementById('content');
    if (!contentEl) return;

    let html = '';

    // Header
    html += '<div class="lesson-header">';
    html += '<span class="section-tag">Section ' + lesson.section + '</span>';
    html += '<h2>' + lesson.id + ' ' + lesson.title + '</h2>';
    html += '</div>';

    // Body content
    html += '<div class="lesson-body">' + lesson.content + '</div>';

    // Chart (if not static)
    if (lesson.chartType !== 'static') {
      html += '<div class="chart-container"><div class="chart-wrapper">';
      html += '<canvas id="payoffCanvas"></canvas>';
      html += '</div></div>';
    }

    // Controls
    if (lesson.chartType === 'sandbox') {
      html += renderSandboxControls(lesson);
    } else if (lesson.controls && lesson.controls.length > 0) {
      html += renderControls(lesson);
    }

    // Summary panel (for non-static, non-sandbox)
    if (lesson.chartType !== 'static' && lesson.chartType !== 'sandbox') {
      html += '<div class="summary-panel"><h3>สรุปตัวเลขสำคัญ</h3>';
      html += '<div class="summary-grid" id="summaryGrid"></div></div>';
    }

    // Sandbox summary
    if (lesson.chartType === 'sandbox') {
      html += '<div class="summary-panel"><h3>สรุป Payoff</h3>';
      html += '<div class="summary-grid" id="summaryGrid"></div></div>';
    }

    // Navigation buttons
    html += renderNavButtons();

    contentEl.innerHTML = html;

    // Render chart after DOM is ready
    requestAnimationFrame(() => {
      renderChart(lesson);
      if (lesson.chartType !== 'static') {
        updateSummary(lesson);
      }
    });
  }

  // ============================================================
  // Controls Rendering
  // ============================================================

  function renderControls(lesson) {
    let html = '<div class="controls-panel"><h3>ปรับค่าพารามิเตอร์</h3>';
    html += '<div class="controls-grid">';

    lesson.controls.forEach(ctrl => {
      const val = state.params[ctrl.key] !== undefined ? state.params[ctrl.key] : ctrl.default;
      state.params[ctrl.key] = val;

      if (ctrl.type === 'range') {
        html += '<div class="control-group">';
        html += '<label>' + ctrl.label + ' <span class="value-display" id="val_' + ctrl.key + '">' + val + '</span></label>';
        html += '<input type="range" id="ctrl_' + ctrl.key + '" ' +
          'min="' + ctrl.min + '" max="' + ctrl.max + '" step="' + ctrl.step + '" value="' + val + '" ' +
          'data-key="' + ctrl.key + '">';
        html += '</div>';
      } else if (ctrl.type === 'select') {
        html += '<div class="control-group">';
        html += '<label>' + ctrl.label + '</label>';
        html += '<select id="ctrl_' + ctrl.key + '" data-key="' + ctrl.key + '">';
        (ctrl.options || []).forEach(opt => {
          const selected = val === opt.value ? ' selected' : '';
          html += '<option value="' + opt.value + '"' + selected + '>' + opt.label + '</option>';
        });
        html += '</select></div>';
      }
    });

    html += '</div>';

    // Show legs toggle
    if (lesson.showLegs) {
      html += '<div class="toggle-group">';
      html += '<input type="checkbox" id="toggleLegs" checked>';
      html += '<label for="toggleLegs">แสดงเส้น Payoff แต่ละขา</label>';
      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  // ============================================================
  // Sandbox Controls
  // ============================================================

  function renderSandboxControls(lesson) {
    let html = '<div class="controls-panel">';

    // Strategy presets (for section 8)
    if (lesson.section === 8) {
      html += '<h3>Strategy Presets</h3>';
      html += '<div class="strategy-selector">';
      const presets = [
        { name: 'Bull Call Spread', legs: [
          { type: 'call', position: 'long', strike: 95, premium: 8, quantity: 1 },
          { type: 'call', position: 'short', strike: 105, premium: 3, quantity: 1 }
        ]},
        { name: 'Long Straddle', legs: [
          { type: 'call', position: 'long', strike: 100, premium: 5, quantity: 1 },
          { type: 'put', position: 'long', strike: 100, premium: 5, quantity: 1 }
        ]},
        { name: 'Iron Condor', legs: [
          { type: 'put', position: 'long', strike: 85, premium: 1, quantity: 1 },
          { type: 'put', position: 'short', strike: 90, premium: 3, quantity: 1 },
          { type: 'call', position: 'short', strike: 110, premium: 3, quantity: 1 },
          { type: 'call', position: 'long', strike: 115, premium: 1, quantity: 1 }
        ]},
        { name: 'Butterfly', legs: [
          { type: 'call', position: 'long', strike: 90, premium: 12, quantity: 1 },
          { type: 'call', position: 'short', strike: 100, premium: 6, quantity: 2 },
          { type: 'call', position: 'long', strike: 110, premium: 2, quantity: 1 }
        ]},
        { name: 'Clear', legs: [] }
      ];
      presets.forEach((preset, i) => {
        html += '<button class="strategy-btn" data-preset="' + i + '">' + preset.name + '</button>';
      });
      html += '</div>';

      // Store presets for later use
      window._sandboxPresets = presets;
    }

    // Leg builder table
    html += '<h3>Leg Builder</h3>';
    html += '<div id="legBuilderContainer">';
    html += renderLegTable();
    html += '</div>';

    html += '<button class="btn-add-leg" id="btnAddLeg">+ เพิ่มขา</button>';
    html += '</div>';
    return html;
  }

  function renderLegTable() {
    let html = '<table class="leg-builder">';
    html += '<thead><tr><th>ประเภท</th><th>ทิศทาง</th><th>Strike</th><th>Premium</th><th>จำนวน</th><th></th></tr></thead>';
    html += '<tbody id="legTableBody">';

    state.sandboxLegs.forEach((leg, i) => {
      html += '<tr data-leg="' + i + '">';
      html += '<td><select class="leg-type" data-idx="' + i + '">' +
        '<option value="call"' + (leg.type === 'call' ? ' selected' : '') + '>Call</option>' +
        '<option value="put"' + (leg.type === 'put' ? ' selected' : '') + '>Put</option>' +
        '</select></td>';
      html += '<td><select class="leg-position" data-idx="' + i + '">' +
        '<option value="long"' + (leg.position === 'long' ? ' selected' : '') + '>Long</option>' +
        '<option value="short"' + (leg.position === 'short' ? ' selected' : '') + '>Short</option>' +
        '</select></td>';
      html += '<td><input type="number" class="leg-strike" data-idx="' + i + '" value="' + leg.strike + '" min="1" max="500" step="1"></td>';
      html += '<td><input type="number" class="leg-premium" data-idx="' + i + '" value="' + leg.premium + '" min="0.1" max="100" step="0.5"></td>';
      html += '<td><input type="number" class="leg-quantity" data-idx="' + i + '" value="' + (leg.quantity || 1) + '" min="1" max="10" step="1"></td>';
      html += '<td><button class="btn-remove" data-idx="' + i + '">&#10005;</button></td>';
      html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
  }

  function addSandboxLeg() {
    state.sandboxLegs.push({
      type: 'call',
      position: 'long',
      strike: 100,
      premium: 5,
      quantity: 1
    });
    refreshSandbox();
  }

  function removeSandboxLeg(idx) {
    state.sandboxLegs.splice(idx, 1);
    refreshSandbox();
  }

  function refreshSandbox() {
    const container = document.getElementById('legBuilderContainer');
    if (container) container.innerHTML = renderLegTable();

    const lesson = LESSONS[state.currentIndex];
    renderChart(lesson);
    updateSummary(lesson);
    bindSandboxEvents();
  }

  // ============================================================
  // Chart Rendering
  // ============================================================

  function renderChart(lesson) {
    const canvas = document.getElementById('payoffCanvas');
    if (!canvas) return;

    switch (lesson.chartType) {
      case 'payoff':
        renderPayoffChart(lesson);
        break;
      case 'comparison':
        renderComparisonChart(lesson);
        break;
      case 'sandbox':
        renderSandboxChart(lesson);
        break;
      case 'greeks':
        renderGreeksChart(lesson);
        break;
      case 'timeCurve':
        renderTimeCurveChart(lesson);
        break;
      case 'static':
        // No chart
        break;
    }
  }

  function renderPayoffChart(lesson) {
    const legs = Payoff.buildStrategy(lesson.strategy, state.params);
    if (legs.length === 0) return;

    const payoffData = Payoff.generatePayoffData(legs);
    const summary = Payoff.getSummary(legs);
    const strikes = legs.filter(l => l.strike).map(l => l.strike);

    const legLabels = lesson.legLabels && lesson.legLabels.length > 0
      ? lesson.legLabels
      : legs.map((l, i) => (l.position === 'long' ? 'Long ' : 'Short ') + l.type.charAt(0).toUpperCase() + l.type.slice(1) + ' K=' + l.strike);

    ChartManager.createPayoffChart('payoffCanvas', payoffData, {
      showLegs: lesson.showLegs,
      legLabels: legLabels,
      strikes: strikes,
      summary: summary,
      mainLabel: lesson.title
    });
  }

  function renderComparisonChart(lesson) {
    const p = state.params;
    let datasets = [];

    if (lesson.id === '2.5') {
      // Put-Call Parity: overlay two sides
      const legsLeft = Payoff.buildStrategy('putCallParityLeft', p);
      const legsRight = Payoff.buildStrategy('putCallParityRight', p);
      const range = { min: Math.max(0, p.strike * 0.5), max: p.strike * 1.5 };
      const dataLeft = Payoff.generatePayoffData(legsLeft, 200, range);
      const dataRight = Payoff.generatePayoffData(legsRight, 200, range);

      ChartManager.createPayoffChart('payoffCanvas', dataLeft, {
        mainLabel: 'Call + Bond (ซ้ายของสมการ)',
        overlayData: [{ label: 'Put + Stock (ขวาของสมการ)', data: dataRight.data, color: '#f97316', dashed: true }],
        strikes: [p.strike]
      });
    } else if (lesson.id === '2.6') {
      // Synthetic Positions
      const legsReal = [{ type: 'stock', position: 'long', entryPrice: p.strike, quantity: 1 }];
      const legsSynthetic = Payoff.buildStrategy('syntheticLongStock', p);
      const range = { min: Math.max(0, p.strike * 0.5), max: p.strike * 1.5 };
      const dataReal = Payoff.generatePayoffData(legsReal, 200, range);
      const dataSynthetic = Payoff.generatePayoffData(legsSynthetic, 200, range);

      ChartManager.createPayoffChart('payoffCanvas', dataReal, {
        mainLabel: 'Long Stock (จริง)',
        overlayData: [{ label: 'Synthetic (Long Call + Short Put)', data: dataSynthetic.data, color: '#f97316', dashed: true }],
        strikes: [p.strike]
      });
    } else if (lesson.id === '7.1') {
      // Bullish comparison
      const legsCall = Payoff.buildStrategy('longCall', { strike: p.strike, premium: p.premium });
      const legsBull = Payoff.buildStrategy('bullCallSpread', {
        strike1: p.strike, premium1: p.premium,
        strike2: p.strike + 10, premium2: p.premium * 0.4
      });
      const legsStock = [{ type: 'stock', position: 'long', entryPrice: p.strike, quantity: 1 }];
      const range = { min: Math.max(0, p.strike * 0.7), max: p.strike * 1.3 };
      const dataCall = Payoff.generatePayoffData(legsCall, 200, range);
      const dataBull = Payoff.generatePayoffData(legsBull, 200, range);
      const dataStock = Payoff.generatePayoffData(legsStock, 200, range);

      ChartManager.createPayoffChart('payoffCanvas', dataCall, {
        mainLabel: 'Long Call',
        overlayData: [
          { label: 'Bull Call Spread', data: dataBull.data, color: '#16a34a' },
          { label: 'Long Stock', data: dataStock.data, color: '#8b5cf6', dashed: true }
        ],
        strikes: [p.strike]
      });
    } else if (lesson.id === '7.2') {
      // Neutral comparison
      const legsStraddle = Payoff.buildStrategy('longStraddle', {
        strike: p.strike, premiumCall: p.premium, premiumPut: p.premium
      });
      const dataStraddle = Payoff.generatePayoffData(legsStraddle, 200);
      // Short Straddle = negate
      const shortStraddleData = dataStraddle.data.map(v => -v);

      const legsCondor = Payoff.buildStrategy('ironCondor', {
        strike1: p.strike - 15, premium1: 1,
        strike2: p.strike - 5, premium2: 3,
        strike3: p.strike + 5, premium3: 3,
        strike4: p.strike + 15, premium4: 1
      });
      const dataCondor = Payoff.generatePayoffData(legsCondor, 200, { min: dataStraddle.labels[0], max: dataStraddle.labels[dataStraddle.labels.length - 1] });

      const legsBfly = Payoff.buildStrategy('butterflySpread', {
        strike1: p.strike - 10, premium1: 10,
        strike2: p.strike, premium2: 5,
        strike3: p.strike + 10, premium3: 2
      });
      const dataBfly = Payoff.generatePayoffData(legsBfly, 200, { min: dataStraddle.labels[0], max: dataStraddle.labels[dataStraddle.labels.length - 1] });

      ChartManager.createPayoffChart('payoffCanvas', {
        labels: dataStraddle.labels,
        data: shortStraddleData,
        legData: []
      }, {
        mainLabel: 'Short Straddle',
        overlayData: [
          { label: 'Iron Condor', data: dataCondor.data, color: '#16a34a' },
          { label: 'Butterfly Spread', data: dataBfly.data, color: '#8b5cf6', dashed: true }
        ],
        strikes: [p.strike]
      });
    } else if (lesson.id === '7.3') {
      // Volatility comparison
      const legsStraddle = Payoff.buildStrategy('longStraddle', {
        strike: p.strike, premiumCall: p.premium, premiumPut: p.premium
      });
      const legsStrangle = Payoff.buildStrategy('longStrangle', {
        strike1: p.strike - 10, premiumPut: p.premium * 0.6,
        strike2: p.strike + 10, premiumCall: p.premium * 0.6
      });
      const range = Payoff.getPriceRange(legsStrangle, 0.5);
      const dataStraddle = Payoff.generatePayoffData(legsStraddle, 200, range);
      const dataStrangle = Payoff.generatePayoffData(legsStrangle, 200, range);

      ChartManager.createPayoffChart('payoffCanvas', dataStraddle, {
        mainLabel: 'Long Straddle',
        overlayData: [
          { label: 'Long Strangle', data: dataStrangle.data, color: '#f97316' }
        ],
        strikes: [p.strike, p.strike - 10, p.strike + 10]
      });
    } else {
      // Generic: just render first available strategy
      renderPayoffChart(lesson);
    }
  }

  function renderSandboxChart(lesson) {
    if (state.sandboxLegs.length === 0) {
      ChartManager.destroy();
      return;
    }

    const payoffData = Payoff.generatePayoffData(state.sandboxLegs);
    const summary = Payoff.getSummary(state.sandboxLegs);
    const strikes = state.sandboxLegs.filter(l => l.strike).map(l => l.strike);

    const legLabels = state.sandboxLegs.map((l, i) =>
      (l.position === 'long' ? 'L ' : 'S ') +
      l.type.charAt(0).toUpperCase() + l.type.slice(1) +
      ' K=' + l.strike + (l.quantity > 1 ? ' x' + l.quantity : '')
    );

    ChartManager.createPayoffChart('payoffCanvas', payoffData, {
      showLegs: true,
      legLabels: legLabels,
      strikes: [...new Set(strikes)],
      summary: summary,
      mainLabel: 'Payoff รวม'
    });
  }

  function renderGreeksChart(lesson) {
    const p = state.params;
    const K = p.strike || 100;
    const premium = p.premium || 5;
    const T = (p.daysToExpiry || 30) / 365;
    const sigma = (p.sigma || 25) / 100;
    const r = Greeks.DEFAULTS.r;

    const range = { min: Math.max(1, K * 0.6), max: K * 1.4 };
    const pnlCurve = Greeks.generatePnLCurve('call', 'long', K, premium, T, r, sigma, range);

    let greekFn, greekLabel, axisLabel;

    if (lesson.id === '5.2') {
      greekFn = (S, params) => Greeks.delta('call', S, params.K, params.T, params.r, params.sigma);
      greekLabel = 'Delta (Δ)';
      axisLabel = 'Delta';
    } else if (lesson.id === '5.3') {
      greekFn = (S, params) => Greeks.gamma(S, params.K, params.T, params.r, params.sigma);
      greekLabel = 'Gamma (Γ)';
      axisLabel = 'Gamma';
    } else if (lesson.id === '5.4') {
      greekFn = (S, params) => Greeks.theta('call', S, params.K, params.T, params.r, params.sigma);
      greekLabel = 'Theta (Θ)';
      axisLabel = 'Theta (฿/วัน)';
    } else if (lesson.id === '5.5') {
      greekFn = (S, params) => Greeks.vega(S, params.K, params.T, params.r, params.sigma);
      greekLabel = 'Vega (ν)';
      axisLabel = 'Vega (฿/1%σ)';
    }

    if (greekFn) {
      const greekCurve = Greeks.generateGreekCurve(greekFn, { K, T, r, sigma }, range);

      ChartManager.createGreekChart('payoffCanvas', pnlCurve, greekCurve, {
        greekLabel: greekLabel,
        greekAxisLabel: axisLabel,
        payoffLabel: 'P&L (Long Call)'
      });
    }
  }

  function renderTimeCurveChart(lesson) {
    const p = state.params;
    const K = p.strike || 100;
    const premium = p.premium || 5;
    const sigma = (p.sigma || 25) / 100;
    const r = Greeks.DEFAULTS.r;
    const mainDays = p.daysToExpiry || 30;

    const range = { min: Math.max(1, K * 0.6), max: K * 1.4 };
    const type = p.type || 'call';
    const position = p.position || 'long';

    // Generate curves at different time points
    const daysArray = [];
    if (mainDays >= 90) daysArray.push(90);
    if (mainDays >= 60) daysArray.push(60);
    if (mainDays >= 30) daysArray.push(30);
    if (mainDays >= 14) daysArray.push(14);
    if (mainDays >= 7) daysArray.push(7);
    daysArray.push(mainDays);

    // Remove duplicates and sort descending
    const uniqueDays = [...new Set(daysArray)].sort((a, b) => b - a).slice(0, 4);

    const timeCurves = Greeks.generateTimeCurves(type, position, K, premium, r, sigma, range, uniqueDays);

    // At-expiry payoff
    const atExpiryLegs = position === 'long'
      ? [{ type: type, position: 'long', strike: K, premium: premium, quantity: 1 }]
      : [{ type: type, position: 'short', strike: K, premium: premium, quantity: 1 }];
    const atExpiryData = Payoff.generatePayoffData(atExpiryLegs, 200, range);

    ChartManager.createTimeCurveChart('payoffCanvas', timeCurves, atExpiryData);
  }

  // ============================================================
  // Summary Panel
  // ============================================================

  function updateSummary(lesson) {
    const grid = document.getElementById('summaryGrid');
    if (!grid) return;

    let legs;
    if (lesson.chartType === 'sandbox') {
      legs = state.sandboxLegs;
    } else if (lesson.strategy) {
      legs = Payoff.buildStrategy(lesson.strategy, state.params);
    } else {
      // For comparison/greeks - compute from first strategy if possible
      grid.innerHTML = '';
      return;
    }

    if (!legs || legs.length === 0) {
      grid.innerHTML = '<div class="summary-item"><span class="label">สถานะ</span><span class="value neutral">เพิ่ม Option legs เพื่อดูสรุป</span></div>';
      return;
    }

    const summary = Payoff.getSummary(legs);

    let html = '';

    // Max Profit
    const profitLabel = summary.maxProfit.value === Infinity ? 'ไม่จำกัด' : (summary.maxProfit.value >= 0 ? '+' : '') + summary.maxProfit.value.toFixed(2);
    html += '<div class="summary-item"><span class="label">กำไรสูงสุด (Max Profit)</span>';
    html += '<span class="value profit">' + profitLabel + '</span></div>';

    // Max Loss
    const lossLabel = summary.maxLoss.value === -Infinity ? 'ไม่จำกัด' : summary.maxLoss.value.toFixed(2);
    html += '<div class="summary-item"><span class="label">ขาดทุนสูงสุด (Max Loss)</span>';
    html += '<span class="value loss">' + lossLabel + '</span></div>';

    // Break-evens
    const beLabel = summary.breakevens.length > 0 ? summary.breakevens.join(', ') : 'ไม่มี';
    html += '<div class="summary-item"><span class="label">จุดคุ้มทุน (Break-even)</span>';
    html += '<span class="value neutral">' + beLabel + '</span></div>';

    // Risk/Reward ratio
    if (summary.maxProfit.value !== Infinity && summary.maxLoss.value !== -Infinity && summary.maxLoss.value !== 0) {
      const ratio = Math.abs(summary.maxProfit.value / summary.maxLoss.value).toFixed(2);
      html += '<div class="summary-item"><span class="label">Risk/Reward Ratio</span>';
      html += '<span class="value neutral">1:' + ratio + '</span></div>';
    }

    grid.innerHTML = html;
  }

  // ============================================================
  // Nav Buttons
  // ============================================================

  function renderNavButtons() {
    const hasPrev = state.currentIndex > 0;
    const hasNext = state.currentIndex < LESSONS.length - 1;
    const prevLesson = hasPrev ? LESSONS[state.currentIndex - 1] : null;
    const nextLesson = hasNext ? LESSONS[state.currentIndex + 1] : null;

    let html = '<div class="lesson-nav">';

    if (hasPrev) {
      html += '<button class="btn-nav" id="btnPrev">&larr; ' + prevLesson.id + ' ' + prevLesson.title + '</button>';
    } else {
      html += '<button class="btn-nav" disabled>&larr; ก่อนหน้า</button>';
    }

    if (hasNext) {
      html += '<button class="btn-nav primary" id="btnNext">' + nextLesson.id + ' ' + nextLesson.title + ' &rarr;</button>';
    } else {
      html += '<button class="btn-nav" disabled>จบบทเรียน</button>';
    }

    html += '</div>';
    return html;
  }

  // ============================================================
  // Event Binding
  // ============================================================

  function bindGlobalEvents() {
    // Sidebar navigation clicks (event delegation)
    document.getElementById('nav-list').addEventListener('click', function(e) {
      const item = e.target.closest('.nav-item');
      if (item) {
        navigateTo(parseInt(item.dataset.index, 10));
      }
    });

    // Content area events (delegation)
    document.getElementById('content').addEventListener('input', function(e) {
      if (e.target.matches('input[type="range"]') && e.target.dataset.key) {
        onParamChange(e.target.dataset.key, parseFloat(e.target.value));
      }
    });

    document.getElementById('content').addEventListener('change', function(e) {
      if (e.target.matches('select') && e.target.dataset.key) {
        onParamChange(e.target.dataset.key, e.target.value);
      }
      // Sandbox leg changes
      if (e.target.matches('.leg-type, .leg-position, .leg-strike, .leg-premium, .leg-quantity')) {
        onSandboxLegChange(e.target);
      }
    });

    document.getElementById('content').addEventListener('input', function(e) {
      if (e.target.matches('.leg-strike, .leg-premium, .leg-quantity')) {
        onSandboxLegChange(e.target);
      }
    });

    document.getElementById('content').addEventListener('click', function(e) {
      // Nav buttons
      if (e.target.id === 'btnPrev' || e.target.closest('#btnPrev')) {
        navigateTo(state.currentIndex - 1);
      }
      if (e.target.id === 'btnNext' || e.target.closest('#btnNext')) {
        navigateTo(state.currentIndex + 1);
      }
      // Add leg
      if (e.target.id === 'btnAddLeg' || e.target.closest('#btnAddLeg')) {
        addSandboxLeg();
      }
      // Remove leg
      if (e.target.matches('.btn-remove') || e.target.closest('.btn-remove')) {
        const btn = e.target.closest('.btn-remove');
        if (btn) removeSandboxLeg(parseInt(btn.dataset.idx, 10));
      }
      // Strategy presets
      if (e.target.matches('.strategy-btn')) {
        const presetIdx = parseInt(e.target.dataset.preset, 10);
        if (window._sandboxPresets && window._sandboxPresets[presetIdx]) {
          state.sandboxLegs = JSON.parse(JSON.stringify(window._sandboxPresets[presetIdx].legs));
          refreshSandbox();
          // Highlight active preset
          document.querySelectorAll('.strategy-btn').forEach(b => b.classList.remove('active'));
          e.target.classList.add('active');
        }
      }
      // Toggle legs
      if (e.target.id === 'toggleLegs') {
        const chart = ChartManager.getChart();
        if (chart) {
          const show = e.target.checked;
          chart.data.datasets.forEach((ds, i) => {
            if (i > 0) ds.hidden = !show;
          });
          chart.update();
        }
      }
    });

    // Hamburger menu
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (hamburger) {
      hamburger.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
      });
    }
    if (overlay) {
      overlay.addEventListener('click', closeSidebar);
    }
  }

  function bindSandboxEvents() {
    // Re-bind after sandbox DOM refresh - handled by delegation, nothing needed
  }

  function onParamChange(key, value) {
    state.params[key] = value;

    // Update display
    const display = document.getElementById('val_' + key);
    if (display) display.textContent = value;

    // Re-render chart
    const lesson = LESSONS[state.currentIndex];
    renderChart(lesson);
    updateSummary(lesson);
  }

  function onSandboxLegChange(el) {
    const idx = parseInt(el.dataset.idx, 10);
    if (isNaN(idx) || !state.sandboxLegs[idx]) return;

    const leg = state.sandboxLegs[idx];
    if (el.matches('.leg-type')) leg.type = el.value;
    if (el.matches('.leg-position')) leg.position = el.value;
    if (el.matches('.leg-strike')) leg.strike = parseFloat(el.value) || 100;
    if (el.matches('.leg-premium')) leg.premium = parseFloat(el.value) || 5;
    if (el.matches('.leg-quantity')) leg.quantity = parseInt(el.value, 10) || 1;

    const lesson = LESSONS[state.currentIndex];
    renderChart(lesson);
    updateSummary(lesson);
  }

  function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
  }

  // ============================================================
  // Persistence
  // ============================================================

  function saveProgress() {
    localStorage.setItem('payoff_currentIndex', state.currentIndex);
    localStorage.setItem('payoff_visited', JSON.stringify([...state.visited]));
  }

  function loadProgress() {
    try {
      const visited = JSON.parse(localStorage.getItem('payoff_visited') || '[]');
      visited.forEach(v => state.visited.add(v));
    } catch (e) {
      // ignore
    }
  }

  // ============================================================
  // Public API
  // ============================================================

  return { init, navigateTo };
})();

// Boot the app
document.addEventListener('DOMContentLoaded', App.init);
