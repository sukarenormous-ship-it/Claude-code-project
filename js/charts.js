// charts.js - Chart.js wrapper for payoff chart rendering
// Handles: segment coloring, annotations, tooltips, dual-axis for Greeks

const ChartManager = (() => {
  let currentChart = null;

  const COLORS = {
    profit: '#16a34a',
    loss: '#dc2626',
    neutral: '#6b7280',
    primary: '#2563eb',
    secondary: '#8b5cf6',
    accent: '#f59e0b',
    leg1: 'rgba(37, 99, 235, 0.5)',
    leg2: 'rgba(220, 38, 38, 0.5)',
    leg3: 'rgba(245, 158, 11, 0.5)',
    leg4: 'rgba(139, 92, 246, 0.5)',
    theoreticalLine: '#f97316',
    gridColor: 'rgba(0, 0, 0, 0.06)'
  };

  const LEG_COLORS = [COLORS.leg1, COLORS.leg2, COLORS.leg3, COLORS.leg4];

  // ============================================================
  // Segment coloring: red below zero, green above zero
  // ============================================================

  function getSegmentColor(ctx) {
    const y0 = ctx.p0.parsed.y;
    const y1 = ctx.p1.parsed.y;
    if (y0 < 0 && y1 < 0) return COLORS.loss;
    if (y0 >= 0 && y1 >= 0) return COLORS.profit;
    return COLORS.neutral;
  }

  // ============================================================
  // Build annotation config for break-evens and strikes
  // ============================================================

  function buildAnnotations(breakevens, strikes, maxProfit, maxLoss) {
    const annotations = {};

    // Zero line
    annotations.zeroLine = {
      type: 'line',
      yMin: 0,
      yMax: 0,
      borderColor: 'rgba(0, 0, 0, 0.3)',
      borderWidth: 1.5,
      borderDash: []
    };

    // Break-even lines
    if (breakevens) {
      breakevens.forEach((be, i) => {
        annotations['breakeven' + i] = {
          type: 'line',
          xMin: be,
          xMax: be,
          borderColor: '#f59e0b',
          borderWidth: 1.5,
          borderDash: [6, 4],
          label: {
            display: true,
            content: 'BE: ' + be,
            position: 'start',
            backgroundColor: 'rgba(245, 158, 11, 0.85)',
            color: '#fff',
            font: { size: 11, family: 'Sarabun' },
            padding: 4
          }
        };
      });
    }

    // Strike price lines
    if (strikes) {
      strikes.forEach((s, i) => {
        annotations['strike' + i] = {
          type: 'line',
          xMin: s,
          xMax: s,
          borderColor: 'rgba(100, 100, 100, 0.25)',
          borderWidth: 1,
          borderDash: [3, 3]
        };
      });
    }

    // Max profit line (if finite)
    if (maxProfit && maxProfit.value !== Infinity && maxProfit.value > 0) {
      annotations.maxProfit = {
        type: 'line',
        yMin: maxProfit.value,
        yMax: maxProfit.value,
        borderColor: 'rgba(22, 163, 74, 0.4)',
        borderWidth: 1,
        borderDash: [4, 4],
        label: {
          display: true,
          content: 'Max +' + maxProfit.label,
          position: 'end',
          backgroundColor: 'rgba(22, 163, 74, 0.8)',
          color: '#fff',
          font: { size: 10, family: 'Sarabun' },
          padding: 3
        }
      };
    }

    // Max loss line (if finite)
    if (maxLoss && maxLoss.value !== -Infinity && maxLoss.value < 0) {
      annotations.maxLoss = {
        type: 'line',
        yMin: maxLoss.value,
        yMax: maxLoss.value,
        borderColor: 'rgba(220, 38, 38, 0.4)',
        borderWidth: 1,
        borderDash: [4, 4],
        label: {
          display: true,
          content: 'Max ' + maxLoss.label,
          position: 'end',
          backgroundColor: 'rgba(220, 38, 38, 0.8)',
          color: '#fff',
          font: { size: 10, family: 'Sarabun' },
          padding: 3
        }
      };
    }

    return annotations;
  }

  // ============================================================
  // Create main payoff chart
  // ============================================================

  function createPayoffChart(canvasId, payoffData, options) {
    options = options || {};
    destroy();

    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const datasets = [];

    // Combined payoff line (main)
    datasets.push({
      label: options.mainLabel || 'Payoff รวม',
      data: payoffData.data,
      borderWidth: 2.5,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: COLORS.primary,
      tension: 0.1,
      fill: false,
      segment: {
        borderColor: ctx2 => getSegmentColor(ctx2)
      },
      order: 0
    });

    // Individual leg lines (dashed)
    if (options.showLegs && payoffData.legData) {
      payoffData.legData.forEach((legPoints, i) => {
        datasets.push({
          label: options.legLabels ? options.legLabels[i] : ('Leg ' + (i + 1)),
          data: legPoints,
          borderWidth: 1.5,
          borderDash: [5, 5],
          borderColor: LEG_COLORS[i % LEG_COLORS.length],
          pointRadius: 0,
          tension: 0.1,
          fill: false,
          hidden: options.legsHidden || false,
          order: 1
        });
      });
    }

    // Additional overlay lines (e.g., theoretical curve, comparison)
    if (options.overlayData) {
      options.overlayData.forEach((overlay, i) => {
        datasets.push({
          label: overlay.label || 'Overlay ' + (i + 1),
          data: overlay.data,
          borderWidth: overlay.borderWidth || 2,
          borderDash: overlay.dashed ? [6, 3] : [],
          borderColor: overlay.color || COLORS.theoreticalLine,
          pointRadius: 0,
          tension: 0.1,
          fill: false,
          order: overlay.order || 2
        });
      });
    }

    // Build annotations
    const summary = options.summary || {};
    const annotations = buildAnnotations(
      summary.breakevens,
      options.strikes,
      summary.maxProfit,
      summary.maxLoss
    );

    currentChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: payoffData.labels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: options.animate !== false ? { duration: 300 } : false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            display: datasets.length > 1,
            position: 'top',
            labels: {
              font: { family: 'Sarabun', size: 12 },
              usePointStyle: true,
              padding: 15
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleFont: { family: 'Sarabun', size: 13 },
            bodyFont: { family: 'Sarabun', size: 12 },
            padding: 10,
            callbacks: {
              title: function(items) {
                return 'ราคา: ฿' + items[0].label;
              },
              label: function(context) {
                const val = context.parsed.y;
                const prefix = val >= 0 ? 'กำไร' : 'ขาดทุน';
                const color = val >= 0 ? '+' : '';
                return context.dataset.label + ': ' + color + val.toFixed(2) + ' (' + prefix + ')';
              }
            }
          },
          annotation: {
            annotations: annotations
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'ราคาสินทรัพย์อ้างอิง ณ วันหมดอายุ',
              font: { family: 'Sarabun', size: 13, weight: '500' }
            },
            grid: { color: COLORS.gridColor },
            ticks: {
              font: { family: 'Sarabun', size: 11 },
              maxTicksLimit: 10,
              callback: function(value) {
                return this.getLabelForValue(value);
              }
            }
          },
          y: {
            title: {
              display: true,
              text: 'กำไร / ขาดทุน (฿)',
              font: { family: 'Sarabun', size: 13, weight: '500' }
            },
            grid: { color: COLORS.gridColor },
            ticks: {
              font: { family: 'Sarabun', size: 11 },
              callback: function(value) {
                return value >= 0 ? '+' + value : value;
              }
            }
          }
        }
      }
    });

    return currentChart;
  }

  // ============================================================
  // Create Greeks chart (dual Y-axis: payoff + greek)
  // ============================================================

  function createGreekChart(canvasId, payoffCurve, greekCurve, options) {
    options = options || {};
    destroy();

    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    currentChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: payoffCurve.labels,
        datasets: [
          {
            label: options.payoffLabel || 'P&L',
            data: payoffCurve.data,
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.1,
            fill: false,
            segment: { borderColor: ctx2 => getSegmentColor(ctx2) },
            yAxisID: 'y',
            order: 1
          },
          {
            label: options.greekLabel || 'Greek',
            data: greekCurve.data,
            borderWidth: 2.5,
            borderColor: COLORS.secondary,
            pointRadius: 0,
            tension: 0.2,
            fill: false,
            yAxisID: 'y2',
            order: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              font: { family: 'Sarabun', size: 12 },
              usePointStyle: true,
              padding: 15
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleFont: { family: 'Sarabun', size: 13 },
            bodyFont: { family: 'Sarabun', size: 12 },
            padding: 10,
            callbacks: {
              title: function(items) {
                return 'ราคา: ฿' + items[0].label;
              }
            }
          },
          annotation: {
            annotations: {
              zeroLine: {
                type: 'line',
                yMin: 0,
                yMax: 0,
                yScaleID: 'y',
                borderColor: 'rgba(0, 0, 0, 0.2)',
                borderWidth: 1
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'ราคาสินทรัพย์อ้างอิง',
              font: { family: 'Sarabun', size: 13, weight: '500' }
            },
            grid: { color: COLORS.gridColor },
            ticks: {
              font: { family: 'Sarabun', size: 11 },
              maxTicksLimit: 10
            }
          },
          y: {
            type: 'linear',
            position: 'left',
            title: {
              display: true,
              text: 'กำไร / ขาดทุน (฿)',
              font: { family: 'Sarabun', size: 12, weight: '500' }
            },
            grid: { color: COLORS.gridColor },
            ticks: { font: { family: 'Sarabun', size: 11 } }
          },
          y2: {
            type: 'linear',
            position: 'right',
            title: {
              display: true,
              text: options.greekAxisLabel || 'Greek Value',
              font: { family: 'Sarabun', size: 12, weight: '500' },
              color: COLORS.secondary
            },
            grid: { drawOnChartArea: false },
            ticks: {
              font: { family: 'Sarabun', size: 11 },
              color: COLORS.secondary
            }
          }
        }
      }
    });

    return currentChart;
  }

  // ============================================================
  // Create multi-time curve chart (for Greeks time-lapse)
  // ============================================================

  function createTimeCurveChart(canvasId, timeCurves, atExpiryData, options) {
    options = options || {};
    destroy();

    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const datasets = [];
    const opacity = [1, 0.6, 0.35, 0.2];

    timeCurves.forEach((curve, i) => {
      datasets.push({
        label: curve.days + ' วัน',
        data: curve.data,
        borderWidth: i === 0 ? 2.5 : 1.5,
        borderColor: `rgba(37, 99, 235, ${opacity[i] || 0.2})`,
        pointRadius: 0,
        tension: 0.2,
        fill: false,
        borderDash: i === 0 ? [] : [4, 3]
      });
    });

    // At-expiry line
    if (atExpiryData) {
      datasets.push({
        label: 'วันหมดอายุ',
        data: atExpiryData.data,
        borderWidth: 2,
        borderColor: COLORS.loss,
        pointRadius: 0,
        tension: 0.05,
        fill: false,
        segment: { borderColor: ctx2 => getSegmentColor(ctx2) }
      });
    }

    currentChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeCurves[0].labels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              font: { family: 'Sarabun', size: 12 },
              usePointStyle: true,
              padding: 12
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleFont: { family: 'Sarabun', size: 13 },
            bodyFont: { family: 'Sarabun', size: 12 }
          },
          annotation: {
            annotations: {
              zeroLine: {
                type: 'line', yMin: 0, yMax: 0,
                borderColor: 'rgba(0,0,0,0.2)', borderWidth: 1
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'ราคาสินทรัพย์อ้างอิง',
              font: { family: 'Sarabun', size: 13, weight: '500' }
            },
            grid: { color: COLORS.gridColor },
            ticks: { font: { family: 'Sarabun', size: 11 }, maxTicksLimit: 10 }
          },
          y: {
            title: {
              display: true,
              text: 'กำไร / ขาดทุน (฿)',
              font: { family: 'Sarabun', size: 13, weight: '500' }
            },
            grid: { color: COLORS.gridColor },
            ticks: { font: { family: 'Sarabun', size: 11 } }
          }
        }
      }
    });

    return currentChart;
  }

  // ============================================================
  // Update existing chart data (smooth, no destroy/recreate)
  // ============================================================

  function update(newData, options) {
    if (!currentChart) return;
    options = options || {};

    // Update main dataset
    if (newData.data) {
      currentChart.data.datasets[0].data = newData.data;
    }
    if (newData.labels) {
      currentChart.data.labels = newData.labels;
    }

    // Update leg datasets
    if (newData.legData) {
      newData.legData.forEach((legPoints, i) => {
        if (currentChart.data.datasets[i + 1]) {
          currentChart.data.datasets[i + 1].data = legPoints;
        }
      });
    }

    // Update annotations
    if (newData.summary && currentChart.options.plugins.annotation) {
      const annotations = buildAnnotations(
        newData.summary.breakevens,
        options.strikes,
        newData.summary.maxProfit,
        newData.summary.maxLoss
      );
      currentChart.options.plugins.annotation.annotations = annotations;
    }

    currentChart.update(options.skipAnimation ? 'none' : undefined);
  }

  // ============================================================
  // Destroy current chart
  // ============================================================

  function destroy() {
    if (currentChart) {
      currentChart.destroy();
      currentChart = null;
    }
  }

  function getChart() {
    return currentChart;
  }

  // ============================================================
  // Public API
  // ============================================================

  return {
    createPayoffChart,
    createGreekChart,
    createTimeCurveChart,
    update,
    destroy,
    getChart,
    COLORS
  };
})();
