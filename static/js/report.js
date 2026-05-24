const DIM_META = {
  DEV: { name: '儿童发展', abbr: 'DEV', color: '#3d6b52', bg: '#eef5f0', layer: '个体层', theory: 'Gesell发展量表 · DDST · WHO儿童生长标准' },
  REL: { name: '亲子关系', abbr: 'REL', color: '#5a4a7a', bg: '#f0eef5', layer: '关系层', theory: 'Bowlby依恋理论 · Gottman情绪教练 · Patterson强制循环模型' },
  ENV: { name: '家庭环境', abbr: 'ENV', color: '#3a6b6b', bg: '#eef5f5', layer: '环境层', theory: 'Baumrind教养方式 · Minuchin家庭系统理论 · McMaster家庭功能模式' },
  PAR: { name: '父母状态', abbr: 'PAR', color: '#b07d4a', bg: '#fdf7f0', layer: '个体层', theory: 'Roskam父母倦怠 · Deci自我决定理论 · Luthans心理资本' },
  RISK: { name: '风险筛查', abbr: 'RISK', color: '#9c3b3b', bg: '#fdf0f0', layer: '环境层', theory: 'CBCL儿童行为检核表 · SDQ长处与困难问卷 · C-SSRS' },
};
const RADAR_ORDER = ['DEV', 'REL', 'ENV', 'PAR', 'RISK'];

function loadReport() {
  const raw = localStorage.getItem('pa_current_report');
  if (!raw) {
    document.body.innerHTML = '<div class="container" style="padding-top:60px;text-align:center;"><h2 style="font-size:1.2rem;font-weight:700;margin-bottom:8px;">未找到报告</h2><p style="color:var(--c-ink-muted);font-size:0.85rem;margin-bottom:24px;">请先完成评估问卷</p><a href="/quiz" class="btn-primary">去评估</a></div>';
    return;
  }
  const report = JSON.parse(raw);
  document.getElementById('report-container').innerHTML = buildReportHTML(report);

  if (report.scores && typeof initRadarChart === 'function') {
    initRadarChart(report.scores, 'radar-chart');
  }
  if (report.meta && report.meta.overall_score != null && typeof animateScoreRing === 'function') {
    animateScoreRing(report.meta.overall_score, 'ring-fill', 'ring-num');
  }
}

function buildReportHTML(r) {
  const meta = r.meta || {};
  const scores = r.scores || {};
  const dimAnalysis = r.dimension_analysis || {};
  const flags = r.flags || [];
  const actions = r.priority_actions || {};
  const overall = meta.overall_score || 50;

  // Affirmation
  const affirmation = overall >= 70
    ? { highlight: '整体发展良好', body: '在同龄人中处于中等偏上水平。评估显示您已具备较好的养育基础，部分领域仍有提升空间。', level: '良好' }
    : overall >= 50
    ? { highlight: '发展平稳', body: '与同龄人相比处于平均水平。评估发现了几个值得关注的领域，好消息是：这些都是可以通过小步调整来改善的。', level: '平稳' }
    : { highlight: '需关注', body: '这次评估帮助您识别了一些需要优先关注的领域。请不要焦虑——发现问题就是改善的第一步。很多父母在得到适当支持后都能看到明显的积极变化。', level: '需关注' };

  // Score summary pills
  const counts = { '优秀': 0, '良好': 0, '需关注': 0, '需重点关注': 0 };
  Object.values(dimAnalysis).forEach(d => { counts[d.level || '良好'] = (counts[d.level || '良好'] || 0) + 1; });
  let scoreSummaryHtml = '<div class="score-pill-row">';
  const goodCount = (counts['优秀'] || 0) + (counts['良好'] || 0);
  if (goodCount > 0) scoreSummaryHtml += `<span class="score-pill badge-good">${goodCount} 项良好</span>`;
  if (counts['需关注']) scoreSummaryHtml += `<span class="score-pill badge-attention">${counts['需关注']} 项需关注</span>`;
  if (counts['需重点关注']) scoreSummaryHtml += `<span class="score-pill badge-urgent">${counts['需重点关注']} 项需重点关注</span>`;
  scoreSummaryHtml += '</div>';

  // Assessment statement
  const assessmentStatement = `
    <div style="background:var(--c-bg);border:1px solid var(--c-border);border-radius:4px;padding:16px;margin-bottom:16px;">
      <div style="font-size:0.7rem;font-weight:700;color:var(--c-ink-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">评估声明</div>
      <div style="font-size:0.8rem;color:var(--c-ink-light);line-height:1.7;">
        本评估基于<strong>发展心理学</strong>与<strong>生态系统理论</strong>，采用 Likert 5 点量表与 T-score 标准化计分（0—100），以 50 分为同龄百分位中位数参照。
        五大维度覆盖儿童发展、亲子关系、家庭环境、父母状态与风险筛查，理论来源包括 Gesell 发展量表、Bowlby 依恋理论、Baumrind 教养方式、CBCL 行为检核表等经典工具。
      </div>
    </div>
  `;

  // Dim list sorted by score
  const sortedDims = RADAR_ORDER.map(d => ({...DIM_META[d], code: d, score: scores[d] || 50, level: (dimAnalysis[d] || {}).level || '良好'})).sort((a, b) => a.score - b.score);
  const dimListHtml = sortedDims.map(d => `
    <div class="dim-row">
      <div class="dim-icon" style="background:${d.bg};color:${d.color};">${d.abbr}</div>
      <div class="dim-info">
        <h4>${d.name}</h4>
        <div class="dim-meta">${d.layer} · ${d.level}</div>
      </div>
      <div class="dim-score">
        <div style="font-size:1rem;font-weight:700;color:${d.color};">${Math.round(d.score)}</div>
        <div class="dim-bar-wrap"><div class="dim-bar" style="width:${Math.round(d.score)}%;background:${d.color};"></div></div>
      </div>
    </div>
  `).join('');

  // Dim detail with theory annotations
  const dimDetailHtml = RADAR_ORDER.map(d => {
    const a = dimAnalysis[d];
    if (!a) return '';
    const conf = DIM_META[d];
    let html = `<div class="detail-card">`;
    html += `<div class="detail-header">`;
    html += `<div style="display:flex;align-items:center;gap:10px;"><div class="dim-icon" style="background:${conf.bg};color:${conf.color};width:28px;height:28px;font-size:0.6rem;">${conf.abbr}</div><div class="detail-name">${a.dim_name}</div></div>`;
    html += `<div class="detail-score">${a.score} 分 · ${a.level}</div></div>`;
    html += `<div style="font-size:0.7rem;color:var(--c-ink-muted);margin-bottom:14px;padding:8px 12px;background:var(--c-bg);border-radius:4px;border-left:2px solid var(--c-gold);">理论来源：${conf.theory}</div>`;

    html += `<div class="detail-section"><h5>深度解读</h5><p>${a.interpretation}</p></div>`;

    [['strengths','优势领域'],['concerns','关注要点'],['development_tips','发展建议'],['reflections','家长反思']].forEach(([k, title]) => {
      const items = a[k] || [];
      if (items.length) {
        html += `<div class="detail-section"><h5>${title}</h5><ul>`;
        items.forEach(s => html += `<li>${s}</li>`);
        html += '</ul></div>';
      }
    });

    const scripts = a.scripts || [];
    if (scripts.length) {
      html += `<div class="detail-section"><h5>推荐话术</h5>`;
      scripts.forEach(s => html += `<div class="script-box">${s}</div>`);
      html += '</div>';
    }
    html += '</div>';
    return html;
  }).join('');

  // Flags with professional risk framework
  let flagIntro = '';
  if (flags.length) {
    flagIntro = `<div style="font-size:0.8rem;color:var(--c-ink-light);line-height:1.7;margin-bottom:16px;padding:12px;background:var(--c-bg);border-radius:4px;border:1px solid var(--c-border);">本筛查基于 <strong>CBCL 儿童行为检核表</strong> 与 <strong>SDQ 长处与困难问卷</strong> 设计。红旗信号分为三级：紧急级（自杀/自伤意念）需立即阻断并转介专业资源；严重级（虐待/重大心理问题）建议完全阻断并寻求专业帮助；一般级（冲突/压力）标记关注并建议改善资源。</div>`;
  }

  const riskAdviceMap = {
    DEV: { concern: '该信号提示儿童发展里程碑可能出现延迟，建议关注语言、运动或社会情绪发展是否在正常范围内。', action: '可结合 Gesell 发展量表进行进一步观察，必要时咨询儿童保健科或发育行为儿科。' },
    REL: { concern: '该信号提示亲子互动质量可能受到影响，需关注依恋安全与强制循环风险。', action: '参考 Bowlby 依恋理论，观察日常互动中是否存在批评、蔑视、防御或冷战（Gottman「四骑士」），必要时寻求家庭治疗师支持。' },
    ENV: { concern: '该信号提示家庭教养环境可能存在功能缺陷，需关注规则一致性、情感表达与物理环境。', action: '参考 McMaster 家庭功能模式，评估家庭在问题解决、沟通、角色分工与行为控制方面的功能，逐步优化家庭系统结构。' },
    PAR: { concern: '该信号提示父母状态可能接近倦怠阈值，需关注养育压力与情绪调节能力。', action: '参考 Roskam 父母倦怠理论，评估自身在自主、胜任与关系三方面的心理需求满足程度，优先进行自我关怀。' },
    RISK: { concern: '该信号提示存在内化或外化问题的风险迹象，需持续观察并评估严重程度。', action: '参考 CBCL/SDQ 筛查框架，记录该行为的发生频率、持续时长与功能损害程度。如持续 2 周以上或影响日常生活，建议寻求儿童心理科专业评估。' },
  };

  const riskScore = scores.RISK || 50;
  const flagHtml = flags.length
    ? flags.map(f => {
        const advice = riskAdviceMap[f.dim] || riskAdviceMap['DEV'];
        return `
      <div class="flag-card ${f.critical ? 'danger' : ''}">
        <div class="flag-tag ${f.critical ? 'critical' : 'warning'}">${f.critical ? '重点关注' : '需关注'}</div>
        <h4>${f.question}</h4>
        <p style="margin-bottom:12px;">所属维度：${DIM_META[f.dim]?.name || f.dim}</p>
        <div style="background:var(--c-bg);border-radius:4px;padding:12px;margin-bottom:8px;">
          <div style="font-size:0.7rem;font-weight:700;color:var(--c-ink-muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">关注点</div>
          <div style="font-size:0.8rem;color:var(--c-ink-light);line-height:1.6;">${advice.concern}</div>
        </div>
        <div style="background:var(--c-bg);border-radius:4px;padding:12px;border-left:2px solid var(--c-gold);">
          <div style="font-size:0.7rem;font-weight:700;color:var(--c-ink-muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;">建议</div>
          <div style="font-size:0.8rem;color:var(--c-ink-light);line-height:1.6;">${advice.action}</div>
        </div>
      </div>
    `;
      }).join('')
    : riskScore < 60
    ? '<div style="text-align:center;padding:24px;font-size:0.85rem;color:var(--c-ink-muted);">未触发具体红旗信号，但风险维度整体得分偏低，建议参考上方维度解读中的关注要点与发展建议。</div>'
    : '<div style="text-align:center;padding:24px;font-size:0.85rem;color:var(--c-green);">未发现明显风险信号，继续保持。</div>';

  // Actions with CONNECT model reference


  // Resources based on classic book mapping
  const resourceHtml = (actions.resources || []).map(r => {
    const parts = r.split('——');
    const title = parts[0].trim();
    const subtitle = parts[1]?.trim() || '';
    return `<div class="res-item"><div class="res-icon">Ref</div><div class="res-info" style="flex:1;"><div style="font-size:0.85rem;font-weight:600;color:var(--c-ink);margin-bottom:2px;">${title}</div><div style="font-size:0.75rem;color:var(--c-ink-muted);">${subtitle}</div></div><div class="res-arrow">›</div></div>`;
  }).join('');

  // Cross-analysis note
  const crossNote = r.cross_analysis?.analysis
    ? `<div style="background:var(--c-bg);border:1px solid var(--c-border);border-radius:4px;padding:16px;margin-bottom:16px;"><div style="font-size:0.7rem;font-weight:700;color:var(--c-ink-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">交叉分析</div><p style="font-size:0.85rem;color:var(--c-ink-light);line-height:1.8;">${r.cross_analysis.analysis}</p></div>`
    : '';

  return `
    <div class="report-hero">
      <div style="font-size:0.65rem;color:rgba(255,255,255,0.5);margin-bottom:12px;text-transform:uppercase;letter-spacing:2px;">${meta.name || ''} · ${meta.date || ''}</div>
      <h1>亲子教育评估报告</h1>
      <div style="font-size:0.75rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:2px;">基于发展心理学与家庭系统理论的五维度深度分析</div>
      <div style="background:rgba(255,255,255,0.06);border-radius:4px;padding:20px;margin-top:20px;text-align:left;">
        <div style="font-size:0.75rem;font-weight:700;color:var(--c-gold);margin-bottom:6px;text-transform:uppercase;letter-spacing:1px;">${affirmation.highlight} · ${affirmation.level}</div>
        <div style="font-size:0.85rem;color:rgba(255,255,255,0.75);line-height:1.7;">${affirmation.body}</div>
      </div>
    </div>

    <div class="container">
      ${assessmentStatement}

      <div class="card">
        <h2>综合评估</h2>
        <div class="score-ring-wrap">
          <div class="score-ring">
            <svg width="140" height="140" viewBox="0 0 140 140">
              <circle class="ring-bg" cx="70" cy="70" r="52"/>
              <circle id="ring-fill" class="ring-fill" cx="70" cy="70" r="52" stroke-dasharray="326.73" stroke-dashoffset="326.73"/>
            </svg>
            <div class="center-text"><div class="num" id="ring-num">0</div><div class="label">综合评分</div></div>
          </div>
          <div class="ring-level" id="ring-level">计算中</div>
          ${scoreSummaryHtml}
        </div>
      </div>

      <div class="card" style="padding:20px;">
        <p style="font-size:0.9rem;color:var(--c-ink-light);line-height:1.8;">${r.summary || ''}</p>
      </div>

      ${crossNote}

      <div class="card">
        <h2>五维度画像</h2>
        <div style="font-size:0.75rem;color:var(--c-ink-muted);margin-bottom:12px;">圆圈 = 同龄孩子平均水平（50）· T-score 标准化计分</div>
        <div id="radar-chart" style="width:100%;height:280px;"></div>
      </div>

      <div class="card">
        <h2>维度明细</h2>
        <div style="font-size:0.75rem;color:var(--c-ink-muted);margin-bottom:16px;">从低到高排列 · 分数范围 0—100 · 50 分为同龄中位数</div>
        ${dimListHtml}
      </div>

      <div class="card">
        <h2>深度分析</h2>
        <div style="font-size:0.8rem;color:var(--c-ink-muted);line-height:1.6;margin-bottom:16px;">每一维度均标注其理论来源与评估依据，报告遵循"由外到内"的系统视角：先改善外部环境，再优化关系质量，最后关注个体状态。</div>
        ${dimDetailHtml}
      </div>

      <div class="card">
        <h2>风险筛查</h2>
        ${flagIntro}
        ${flagHtml}
        ${r.risk_analysis?.analysis ? `<div style="margin-top:16px;padding:16px;background:var(--c-bg);border-radius:4px;font-size:0.85rem;color:var(--c-ink-light);line-height:1.7;border:1px solid var(--c-border);">${r.risk_analysis.analysis}</div>` : ''}
      </div>

      <div class="card">
        <h2>推荐阅读</h2>
        <div style="font-size:0.8rem;color:var(--c-ink-muted);line-height:1.6;margin-bottom:16px;">基于评估结果与经典图书映射系统智能匹配，涵盖东西方教育心理学核心著作。</div>
        ${resourceHtml || '<div style="padding:10px;color:var(--c-ink-muted);font-size:0.85rem;">暂无推荐</div>'}
      </div>

      <div class="ai-section" id="ai-section">
        <h3>智能深度解读</h3>
        <p style="font-size:0.85rem;color:var(--c-ink-muted);margin-bottom:16px;line-height:1.6;">基于您的评估数据，运用八步诊断决策树（情绪识别 → 问题识别 → 阶段确认 → 场景确认 → 孩子反应识别 → 归因分析 → 交叉匹配 → 安全红线检查）生成个性化综合分析。</p>
        <button class="btn-ai" onclick="loadAIDiagnosis()">获取深度解读</button>
        <div id="ai-content" class="ai-output"></div>
      </div>

      <div style="text-align:center;padding:20px 0 32px;">
        <button class="btn-download" onclick="downloadPDF()">下载 PDF 报告</button>
        <a href="/quiz" style="display:inline-block;padding:14px 24px;color:var(--c-ink-muted);font-size:0.85rem;text-decoration:none;margin-top:8px;">重新评估</a>
      </div>

      <div class="footer" style="font-size:0.7rem;color:var(--c-ink-muted);padding:20px 0 40px;line-height:1.8;">
        <p>本评估仅供教育参考，不能替代专业医疗诊断</p>
        <p style="margin-top:4px;">理论基础：发展心理学 · 生态系统理论 · Bowlby依恋理论 · Baumrind教养方式 · CBCL/SDQ</p>
        <p style="margin-top:4px;">计分方法：Likert 5点量表 · T-score标准化 · 同龄百分位参照</p>
      </div>
    </div>
  `;
}

async function loadAIDiagnosis() {
  const raw = localStorage.getItem('pa_current_report');
  if (!raw) return;
  const report = JSON.parse(raw);
  const btn = document.querySelector('#ai-section button');
  btn.textContent = '正在生成中...';
  btn.disabled = true;

  const res = await fetch('/api/ai-diagnosis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ report_data: report })
  });

  btn.textContent = '获取深度解读';
  btn.disabled = false;

  if (!res.ok) {
    document.getElementById('ai-content').innerHTML = '<p style="color:var(--c-red);">服务暂时不可用，请检查 API Key 配置</p>';
    return;
  }
  const data = await res.json();
  document.getElementById('ai-content').innerHTML = typeof marked !== 'undefined' ? marked.parse(data.content) : data.content.replace(/\n/g, '<br>');
  document.getElementById('ai-content').classList.add('show');
}

function downloadPDF() {
  const raw = localStorage.getItem('pa_current_report');
  if (!raw) return;
  const report = JSON.parse(raw);
  const reportId = report.meta?.report_id;
  if (reportId) {
    window.open(`/api/report/${reportId}.pdf`, '_blank');
  } else {
    alert('报告 ID 不存在，请重新生成报告');
  }
}

function setRingLevel(score) {
  const el = document.getElementById('ring-level');
  if (!el) return;
  let text = '需关注';
  if (score >= 80) text = '优秀';
  else if (score >= 60) text = '良好';
  else if (score >= 40) text = '平稳';
  el.textContent = text;
}

loadReport();
