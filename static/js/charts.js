/* ===== Charts ===== */

function initRadarChart(scores, containerId) {
  const container = document.getElementById(containerId);
  if (!container || typeof echarts === 'undefined') return;

  const dims = Object.keys(scores);
  const vals = Object.values(scores);
  const labels = {
    DEV: '发展能力',
    REL: '亲子关系',
    ENV: '家庭环境',
    PAR: '父母养育',
    RISK: '风险因素',
  };

  const chart = echarts.init(container);
  const option = {
    color: ['#b07d4a'],
    radar: {
      indicator: dims.map(d => ({ name: labels[d] || d, max: 100 })),
      radius: '60%',
      center: ['50%', '52%'],
      axisName: { color: '#6b7d8f', fontSize: 12, fontWeight: 600 },
      splitArea: {
        areaStyle: { color: ['#f7f6f3', '#fff'] },
      },
      axisLine: { lineStyle: { color: '#e5e2dc' } },
      splitLine: { lineStyle: { color: '#e5e2dc' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: vals,
        name: '得分',
        areaStyle: { color: 'rgba(176,125,74,0.15)' },
        lineStyle: { color: '#b07d4a', width: 2 },
        itemStyle: { color: '#b07d4a' },
        symbol: 'circle',
        symbolSize: 6,
      }],
    }],
  };
  chart.setOption(option);
  window.addEventListener('resize', () => chart.resize());
  return chart;
}

function animateScoreRing(targetValue, ringFillId, ringNumId) {
  const ringFill = document.getElementById(ringFillId);
  const ringNum = document.getElementById(ringNumId);
  if (!ringFill || !ringNum) return;

  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  ringFill.style.strokeDasharray = `${circumference} ${circumference}`;
  ringFill.style.strokeDashoffset = circumference;

  const duration = 1200;
  const startTime = performance.now();
  const startValue = 0;

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = easeOutCubic(progress);

    const currentValue = Math.round(startValue + (targetValue - startValue) * eased);
    ringNum.textContent = currentValue;

    const offset = circumference - (currentValue / 100) * circumference;
    ringFill.style.strokeDashoffset = offset;

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      if (typeof setRingLevel === 'function') setRingLevel(targetValue);
    }
  }
  requestAnimationFrame(step);
}
