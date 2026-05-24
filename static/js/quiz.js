const LS_KEY = 'pa_quiz_state';

let state = {
  age_band: null,
  questions: [],
  current_index: 0,
  answers: [],
};

function loadState() {
  const saved = localStorage.getItem(LS_KEY);
  if (saved) {
    try { state = JSON.parse(saved); } catch (e) {}
    if (state.questions && state.questions.length > 0) {
      showResumePrompt();
    }
  }
}

function showResumePrompt() {
  const ageSel = document.getElementById('age-selection');
  const resumeDiv = document.createElement('div');
  resumeDiv.id = 'resume-prompt';
  resumeDiv.innerHTML = `
    <div style="background:var(--c-card);border:1px solid var(--c-border);border-radius:4px;padding:20px;margin:20px 0;text-align:center;">
      <div style="font-size:0.85rem;color:var(--c-ink-light);margin-bottom:16px;">
        检测到未完成的答题（${state.age_band}岁 · 第 ${state.current_index + 1} / ${state.questions.length} 题）
      </div>
      <div style="display:flex;gap:12px;justify-content:center;">
        <button class="btn-primary" onclick="resumeQuiz()" style="padding:10px 24px;font-size:0.85rem;">继续答题</button>
        <button onclick="restartQuiz()" style="background:none;border:1.5px solid var(--c-border);color:var(--c-ink-muted);padding:10px 24px;border-radius:4px;font-size:0.85rem;cursor:pointer;">重新开始</button>
      </div>
    </div>
  `;
  ageSel.insertBefore(resumeDiv, ageSel.children[1]);
}

function resumeQuiz() {
  const prompt = document.getElementById('resume-prompt');
  if (prompt) prompt.remove();
  showQuiz();
  renderQuestion();
}

function restartQuiz() {
  localStorage.removeItem(LS_KEY);
  localStorage.removeItem('pa_current_report');
  window.location.reload();
}

function saveState() {
  localStorage.setItem(LS_KEY, JSON.stringify(state));
}

async function trackEvent(event_type, age_band) {
  try {
    await fetch('/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_type, age_band })
    });
  } catch (e) {}
}

/* ===== Age Selection ===== */
document.querySelectorAll('.age-card').forEach(card => {
  card.addEventListener('click', async () => {
    const band = card.dataset.band;
    state.age_band = band;
    state.answers = new Array(40).fill(null);
    state.current_index = 0;

    const res = await fetch(`/api/questions/${band}`);
    if (!res.ok) { alert('加载题目失败，请刷新重试'); return; }
    const data = await res.json();
    state.questions = data.questions;
    saveState();
    trackEvent('quiz_start', band);

    showQuiz();
    renderQuestion();
  });
});

function showQuiz() {
  document.getElementById('age-selection').style.display = 'none';
  document.getElementById('quiz-container').style.display = 'block';
}

const DIM_NAMES = { DEV: '儿童发展', REL: '亲子关系', ENV: '家庭环境', PAR: '父母状态', RISK: '风险筛查' };

function renderQuestion() {
  const q = state.questions[state.current_index];
  if (!q) return;

  document.getElementById('dim-tag').textContent = DIM_NAMES[q.dim] || q.dim;
  document.getElementById('progress-text').textContent = `${state.current_index + 1} / ${state.questions.length}`;
  document.getElementById('progress-fill').style.width = `${((state.current_index + 1) / state.questions.length) * 100}%`;
  document.getElementById('question-text').textContent = q.text;

  const optionsDiv = document.getElementById('option-list');
  optionsDiv.innerHTML = '';

  q.options.forEach((opt, idx) => {
    const div = document.createElement('div');
    div.className = 'option-item';
    if (state.answers[state.current_index] === idx + 1) {
      div.classList.add('selected');
    }
    div.textContent = opt;
    div.onclick = () => selectOption(idx + 1);
    optionsDiv.appendChild(div);
  });

  document.getElementById('btn-prev').style.visibility = state.current_index === 0 ? 'hidden' : 'visible';
  document.getElementById('btn-next').textContent = state.current_index === state.questions.length - 1 ? '提交' : '下一题';
}

function selectOption(value) {
  state.answers[state.current_index] = value;
  saveState();
  renderQuestion();
  if (state.current_index < state.questions.length - 1) {
    setTimeout(() => nextQuestion(), 200);
  }
}

function nextQuestion() {
  if (state.answers[state.current_index] == null) {
    alert('请选择一个选项');
    return;
  }
  if (state.current_index < state.questions.length - 1) {
    state.current_index++;
    saveState();
    renderQuestion();
  } else {
    submitQuiz();
  }
}

function prevQuestion() {
  if (state.current_index > 0) {
    state.current_index--;
    saveState();
    renderQuestion();
  }
}

async function submitQuiz() {
  document.getElementById('quiz-container').style.display = 'none';
  document.getElementById('loading').style.display = 'block';

  const res = await fetch('/api/assess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      age_band: state.age_band,
      answers: state.answers
    })
  });

  if (!res.ok) {
    alert('提交失败，请重试');
    document.getElementById('loading').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    return;
  }

  const report = await res.json();
  localStorage.setItem('pa_current_report', JSON.stringify(report));
  localStorage.removeItem(LS_KEY);
  window.location.href = '/report';
}

loadState();
