const API_BASE = '/api/admin';
let password = '';

async function fetchData(endpoint) {
  const res = await fetch(`${API_BASE}/${endpoint}?password=${encodeURIComponent(password)}`);
  if (!res.ok) {
    if (res.status === 401) {
      document.getElementById('login-error').style.display = 'block';
      document.getElementById('login-section').style.display = 'block';
      document.getElementById('dashboard').style.display = 'none';
    }
    return null;
  }
  return res.json();
}

function login() {
  password = document.getElementById('admin-pw').value.trim();
  if (!password) return;
  document.getElementById('login-error').style.display = 'none';
  loadDashboard();
}

async function loadDashboard() {
  const stats = await fetchData('stats');
  if (!stats) return;

  document.getElementById('login-section').style.display = 'none';
  document.getElementById('dashboard').style.display = 'block';

  // KPI
  document.getElementById('kpi-total').textContent = stats.total_reports || 0;
  document.getElementById('kpi-today').textContent = stats.today_reports || 0;
  document.getElementById('kpi-avg').textContent = stats.avg_score || 0;
  document.getElementById('kpi-flags').textContent = stats.flag_reports || 0;

  // Trend chart
  const funnelData = await fetchData('funnel');
  if (funnelData && funnelData.funnel) {
    const dates = funnelData.funnel.map(r => r.date).reverse();
    const completes = funnelData.funnel.map(r => r.quiz_complete || 0).reverse();
    echarts.init(document.getElementById('trend-chart')).setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 10, color: '#6b7d8f' } },
      yAxis: { type: 'value', axisLabel: { fontSize: 10, color: '#6b7d8f' } },
      series: [{
        type: 'line',
        data: completes,
        smooth: true,
        lineStyle: { color: '#b07d4a', width: 2 },
        itemStyle: { color: '#b07d4a' },
        areaStyle: { color: 'rgba(176,125,74,0.1)' },
      }]
    });
  }

  // Risk chart
  const highRisk = await fetchData('high-risk');
  if (highRisk && highRisk.high_risk) {
    const ageDist = {};
    highRisk.high_risk.forEach(r => {
      ageDist[r.age_band] = (ageDist[r.age_band] || 0) + 1;
    });
    echarts.init(document.getElementById('risk-chart')).setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: Object.entries(ageDist).map(([k, v]) => ({ name: k + '岁', value: v })),
        label: { fontSize: 11, color: '#6b7d8f' },
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      }]
    });

    // Table
    document.getElementById('records-body').innerHTML = highRisk.high_risk.slice(0, 20).map(r => `
      <tr>
        <td>${r.created_at || ''}</td>
        <td>${r.age_band || ''}</td>
        <td style="color:${r.overall_score < 40 ? 'var(--c-red)' : 'var(--c-amber)'};font-weight:600;">${Math.round(r.overall_score || 0)}</td>
        <td><span class="risk-badge ${r.overall_score < 40 ? 'high' : 'medium'}">${r.flag_count || 0}</span></td>
      </tr>
    `).join('');
  }
}

// Auto-login from URL param
const urlPw = new URLSearchParams(window.location.search).get('password');
if (urlPw) {
  password = urlPw;
  document.getElementById('admin-pw').value = urlPw;
  loadDashboard();
}
