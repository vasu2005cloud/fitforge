// ═══════════════════════════════════════════════════════════════
//  IronBuddy — app.js  (vanilla JS)
// ═══════════════════════════════════════════════════════════════

let userData      = null;
let workoutDays   = JSON.parse(localStorage.getItem('workout_days') || '[]');
let weeklyGoal    = parseInt(localStorage.getItem('weekly_goal') || '4');
let waterFilled   = 0;
let waterTotal    = 8;
let timerSecs     = 90;
let timerMax      = 90;
let timerRunning  = false;
let timerInterval = null;
let calYear, calMonth;
const today = new Date();
calYear  = today.getFullYear();
calMonth = today.getMonth();

let currentExercises = [];
let currentFilter = 'All';

document.addEventListener('DOMContentLoaded', () => {
  setupNavTabs();
  setupBottomNav();
  document.getElementById('btn-submit').addEventListener('click', handleSubmit);
  checkExistingUser();

  // SVG Muscle Diagram Clicks
  document.querySelectorAll('.muscle-group').forEach(poly => {
    poly.addEventListener('click', () => {
      // Remove active class from all
      document.querySelectorAll('.muscle-group').forEach(p => p.classList.remove('active'));
      
      const day = poly.dataset.day;
      
      // Highlight all polygons matching this day
      document.querySelectorAll(`.muscle-group[data-day="${day}"]`).forEach(p => p.classList.add('active'));
      
      // Update heading title
      const titleEl = document.getElementById('active-muscle-title');
      if(titleEl) titleEl.textContent = day.toUpperCase();
      
      loadWorkout(day);
    });
  });

  // Equip Filters
  document.querySelectorAll('#equip-filters button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#equip-filters button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.equip;
      renderExercisesRow();
    });
  });
  
  // Yoga/Home Mode Switcher
  document.querySelectorAll('#yoga-mode-tabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#yoga-mode-tabs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.dataset.mode;
      document.getElementById('yoga-section').style.display = mode === 'yoga' ? 'block' : 'none';
      document.getElementById('home-section').style.display = mode === 'home' ? 'block' : 'none';
      if (mode === 'yoga') loadYoga('Morning Flow');
      else loadHomeWorkout('Full Body HIIT');
    });
  });

  // Yoga flow tabs
  document.querySelectorAll('#yoga-tabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#yoga-tabs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadYoga(btn.dataset.flow);
    });
  });

  // Home workout tabs
  document.querySelectorAll('#home-tabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#home-tabs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadHomeWorkout(btn.dataset.category);
    });
  });
});

async function checkExistingUser() {
  try {
    const res = await fetch('/api/user-data');
    const data = await res.json();
    if (data && data.age) {
      userData = data;
      showApp();
    }
  } catch(e) {}
}

async function handleSubmit() {
  const name   = document.getElementById('inp-name').value.trim() || 'User';
  const age    = document.getElementById('inp-age').value.trim();
  const weight = document.getElementById('inp-weight').value.trim();
  const height = document.getElementById('inp-height').value.trim();
  const gender = document.querySelector('input[name="gender"]:checked')?.value || 'Male';
  const diet   = document.querySelector('input[name="diet"]:checked')?.value || 'Veg';
  const user_goal = document.getElementById('inp-goal').value;
  const errEl  = document.getElementById('form-error');

  if (!age || !weight || !height) {
    errEl.textContent = 'Please fill in age, weight, and height.';
    errEl.style.display = 'block';
    return;
  }
  errEl.style.display = 'none';

  const btn = document.getElementById('btn-submit');
  btn.disabled = true;
  btn.textContent = 'Configuring Plan...';

  try {
    const res = await fetch('/api/user-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, gender, user_goal, age, weight, height, diet })
    });
    const data = await res.json();
    if (data.ok) { userData = data.user; showApp(); }
  } catch(e) {
    errEl.textContent = 'Server error. Try again.';
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Generate My Plan →';
  }
}

function showApp() {
  document.getElementById('onboarding').style.display = 'none';
  document.getElementById('main-app').style.display   = 'block';
  updateNavProfile();
  loadDiet();
  
  // Set initial SVG state to Chest
  document.querySelectorAll('.muscle-group[data-day="Chest"]').forEach(p => p.classList.add('active'));
  const titleEl = document.getElementById('active-muscle-title');
  if(titleEl) titleEl.textContent = 'CHEST';
  
  loadWorkout('Chest');
  loadYoga('Morning Flow');
  renderCalendar();
  renderTrackerStats();
  renderProfile();
  initGoalUI();
}

function updateNavProfile() {
  if (!userData) return;
  const initial = (userData.name || 'U').charAt(0).toUpperCase();
  document.getElementById('nav-initial').textContent = initial;
  document.getElementById('chip-label').textContent = `${userData.name.split(' ')[0]} · ${userData.weight}kg`;
}

function setupNavTabs() {
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}
function setupBottomNav() {
  document.querySelectorAll('.bottom-nav-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}
function switchTab(id) {
  document.querySelectorAll('.tab-page').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.nav-tab, .bottom-nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).style.display = 'block';
  document.querySelectorAll(`[data-tab="${id}"]`).forEach(b => b.classList.add('active'));
  
  if (id === 'tracker') { renderCalendar(); renderTrackerStats(); }
  if (id === 'profile') renderProfile();
  if (id === 'yoga-home') {
    const mode = document.querySelector('#yoga-mode-tabs button.active')?.dataset.mode || 'yoga';
    if (mode === 'yoga' && !document.getElementById('yoga-list').innerHTML) loadYoga('Morning Flow');
    else if (mode === 'home' && !document.getElementById('home-list').innerHTML) loadHomeWorkout('Full Body HIIT');
  }
}

// ── DIET ──
async function loadDiet() {
  document.getElementById('diet-loading').style.display = 'flex';
  document.getElementById('diet-content').style.display = 'none';
  document.getElementById('diet-error').style.display   = 'none';

  try {
    const res  = await fetch('/api/diet-plan');
    if (!res.ok) throw new Error(await res.text());
    const plan = await res.json();
    renderDiet(plan);
    document.getElementById('diet-loading').style.display = 'none';
    document.getElementById('diet-content').style.display = 'block';
  } catch(e) {
    document.getElementById('diet-loading').style.display = 'none';
    const err = document.getElementById('diet-error');
    err.textContent = 'Could not load diet plan: ' + e.message;
    err.style.display = 'block';
  }
}

function renderDiet(plan) {
  // BMI strip
  document.getElementById('bmi-strip').innerHTML = `
    <div>
      <div style="font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:6px;">Your BMI</div>
      <div class="bmi-num">${plan.bmi}</div>
    </div>
    <div style="text-align:center;">
      <span class="bmi-status ${plan.bmiCls}">${plan.bmiLabel}</span>
      <div style="font-size:13px;color:var(--muted);margin-top:10px;font-weight:500;">
        ${userData.weight}kg · ${userData.height}cm · ${userData.age}yr
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:var(--font-head);font-weight:700;font-size:40px;line-height:1;color:var(--accent2);">${plan.totalCalories}</div>
      <div style="font-size:13px;color:var(--muted);font-weight:500;margin-top:6px;">DAILY KCAL</div>
    </div>`;

  // Macros
  const macros = [
    { label:'Protein', val: plan.proteinG+'g',      color:'var(--accent3)' },
    { label:'Carbs',   val: plan.carbsG+'g',         color:'var(--accent2)' },
    { label:'Fat',     val: plan.fatG+'g',            color:'var(--accent)' },
    { label:'Water',   val: plan.waterLiters+'L',     color:'#8b5cf6' },
  ];
  document.getElementById('macro-row').innerHTML = macros.map(m => `
    <div class="stat-box">
      <div class="stat-num" style="color:${m.color}; line-height:1;">${m.val}</div>
      <div class="stat-lbl">${m.label}</div>
    </div>`).join('');

  // Meals
  const mealOrder = [
    { key:'breakfast',    icon:'🌅', label:'Breakfast' },
    { key:'morningSnack', icon:'🍎', label:'Morning Snack' },
    { key:'lunch',        icon:'☀️',  label:'Lunch' },
    { key:'eveningSnack', icon:'🫐', label:'Evening Snack' },
    { key:'dinner',       icon:'🌙', label:'Dinner' },
  ];
  document.getElementById('meals-container').innerHTML = mealOrder
    .filter(m => plan.meals[m.key])
    .map((m, i) => `
      <div class="meal-card" style="animation: slideUp .4s var(--ease) both; animation-delay: ${i*0.1}s;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <div class="meal-label">${m.icon} ${m.label}</div>
            <div class="meal-name">${plan.meals[m.key].name}</div>
          </div>
          <div class="meal-cal">⚡ ${plan.meals[m.key].calories} kcal</div>
        </div>
        <div class="meal-desc" style="margin-top:12px;">${plan.meals[m.key].description}</div>
      </div>`).join('');

  // Water tracker
  waterTotal  = Math.round(plan.waterLiters * 4);
  waterFilled = 0;
  document.getElementById('water-sub').textContent =
    `Target: ${plan.waterLiters}L · Each drop = 250ml`;
  renderWater();

  // Tip
  if (plan.tip) {
    document.getElementById('tip-text').textContent = plan.tip;
    document.getElementById('diet-tip').style.display = 'block';
  }
}

function renderWater() {
  const row = document.getElementById('water-drops');
  row.innerHTML = '';
  for (let i = 0; i < waterTotal; i++) {
    const span = document.createElement('span');
    span.textContent = '💧';
    span.style.cursor = 'pointer';
    span.style.transition = 'transform .2s';
    span.style.filter = i < waterFilled ? 'none' : 'grayscale(1) opacity(0.2)';
    
    span.onmouseover = () => span.style.transform = 'scale(1.2)';
    span.onmouseout  = () => span.style.transform = 'scale(1)';
    
    span.addEventListener('click', () => {
      waterFilled = i < waterFilled ? i : i + 1;
      renderWater();
    });
    row.appendChild(span);
  }
  document.getElementById('water-counter').textContent =
    `${waterFilled} / ${waterTotal} glasses (${(waterFilled * 0.25).toFixed(2)}L)`;
}

// ── WORKOUT ──
async function loadWorkout(day) {
  try {
    const res  = await fetch('/api/exercise-plan?day=' + day);
    const data = await res.json();
    currentExercises = data.exercises || [];
    renderExercisesRow();
  } catch(e) {
    document.getElementById('exercise-list').innerHTML =
      '<div class="error-msg">Could not load exercises.</div>';
  }
}

function renderExercisesRow() {
  const list = currentExercises.filter(ex => 
    currentFilter === 'All' || ex.equipment === currentFilter
  );
  
  document.getElementById('ex-count').textContent =
    `Showing ${list.length} exercise${list.length !== 1 ? 's' : ''}`;
    
  if (list.length === 0) {
    document.getElementById('exercise-list').innerHTML = `<div style="grid-column: 1 / -1; color:var(--muted); text-align:center; padding: 40px;">No exercises found for this equipment type.</div>`;
    return;
  }
  
  document.getElementById('exercise-list').innerHTML = list.map((ex, i) => {
    const videoId = ex.yt.includes('v=') ? ex.yt.split('v=')[1].split('&')[0] : '';
    const equip = ex.equipment || 'Unknown';
    return `
    <div class="exercise-card" style="animation-delay:${i * 0.05}s;">
      <div class="ex-header">
        <div>
          <div class="ex-name">${ex.name}</div>
          <div style="font-size:13px;color:var(--muted);margin-top:6px;font-weight:500;">🎯 ${ex.muscles}</div>
        </div>
      </div>
      <div class="ex-badges">
        <span class="badge diff-${ex.diff}">${ex.diff}</span>
        <span class="badge badge-equip">${equip}</span>
      </div>
      <div class="ex-desc" style="margin-top:16px;">${ex.desc}</div>
      <div class="ex-actions">
        <button class="btn btn-outline video-toggle" onclick="toggleVideo(this, '${videoId}')" style="padding:10px 16px;">
          ▶ Tutorial
        </button>
        <button class="btn btn-outline" onclick="openTimer(90)" style="padding:10px 16px;">⏱ 90s Rest</button>
      </div>
      <div class="video-dropdown" style="display:none;">
        <div class="video-container">
          <iframe id="yt-${videoId}" frameborder="0" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
        </div>
      </div>
    </div>`;
  }).join('');
}

function toggleVideo(btn, videoId) {
  const card = btn.closest('.exercise-card');
  const dropdown = card.querySelector('.video-dropdown');
  const iframe = dropdown.querySelector('iframe');
  const isOpen = dropdown.style.display === 'block';
  
  document.querySelectorAll('.video-dropdown').forEach(d => {
    d.style.display = 'none';
    const ifr = d.querySelector('iframe');
    if (ifr) ifr.src = '';
  });
  document.querySelectorAll('.video-toggle').forEach(b => {
    b.innerHTML = '▶ Tutorial';
    b.style.background = '';
    b.style.color = '';
  });
  
  if (!isOpen) {
    dropdown.style.display = 'block';
    btn.innerHTML = '▼ Hidden';
    btn.style.background = 'rgba(255,255,255,0.1)';
    btn.style.color = '#fff';
    
    if (iframe) {
        const cleanId = videoId.split('?')[0].split('&')[0];
        iframe.src = `https://www.youtube-nocookie.com/embed/${cleanId}?autoplay=1&rel=0&modestbranding=1&playsinline=1`;
    }
  }
}

// ── YOGA & HOME ──
async function loadYoga(flow) {
  try {
    const res = await fetch('/api/yoga-plan?flow=' + encodeURIComponent(flow));
    const data = await res.json();
    renderYogaPoses(data.poses || [], data.flow);
  } catch(e) {
    document.getElementById('yoga-list').innerHTML = '<div class="error-msg">Could not load yoga poses.</div>';
  }
}

function renderYogaPoses(poses, flow) {
  document.getElementById('yoga-count').textContent =
    `${poses.length} poses · ${flow}`;
  document.getElementById('yoga-list').innerHTML = poses.map((pose, i) => {
    // Check if local video exists
    if (pose.video) {
        const poseId = `vid-${i}-${Math.floor(Math.random() * 1000)}`;
        const videoSrc = `/static/videos/${encodeURIComponent(pose.video)}`;
        
        return `
        <div class="exercise-card" style="border-top: 4px solid #a78bfa; animation-delay:${i * 0.05}s;">
          <div class="ex-header">
            <div>
              <div class="ex-name" style="color:#a78bfa;">${pose.name}</div>
              <div style="font-size:13px;color:var(--muted);margin-top:6px;font-weight:500;">⏱ ${pose.duration}</div>
            </div>
          </div>
          <div class="ex-badges">
            <span class="badge diff-${pose.diff}">${pose.diff}</span>
          </div>
          <div class="ex-desc" style="margin-top:16px;">${pose.desc}</div>
          <div class="ex-actions">
            <button 
              class="btn btn-primary"
              onclick="
                var v = document.getElementById('${poseId}');
                if(v.style.display === 'none'){
                  v.style.display = 'block';
                  this.innerHTML = '▼ Hide Video';
                } else {
                  v.style.display = 'none';
                  v.querySelector('video').pause();
                  this.innerHTML = '▶ Tutorial';
                }
              "
              style="
                background: transparent;
                border: 1px solid rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 600;
                margin-top: 10px;
              ">
              ▶ Tutorial
            </button>
          </div>
          <div class="pose-video-wrap" id="${poseId}" style="display:none; margin-top:12px;">
            <video 
              width="100%" 
              height="220"
              controls
              preload="none"
              style="
                border-radius: 12px;
                background: #000;
                display: block;
                width: 100%;
                height: 220px;
                object-fit: cover;
              ">
              <source src="${videoSrc}" type="video/mp4">
              <p style="color:#888; text-align:center; padding:20px;">Video not available.</p>
            </video>
          </div>
        </div>`;
    }

    // Fallback for poses that only have YouTube (like sequences)
    let videoId = '';
    if (pose.yt) {
        if (pose.yt.includes('embed/')) videoId = pose.yt.split('embed/')[1].split('?')[0];
        else if (pose.yt.includes('v=')) videoId = pose.yt.split('v=')[1].split('&')[0];
        else if (pose.yt.length === 11) videoId = pose.yt;
    }
    
    const ytLink = `https://www.youtube.com/watch?v=${videoId}`;
    const embedUrl = `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&modestbranding=1&playsinline=1`;

    return `
    <div class="exercise-card" style="border-top: 4px solid #a78bfa; animation-delay:${i * 0.05}s;">
      <div class="ex-header">
        <div>
          <div class="ex-name" style="color:#a78bfa;">${pose.name}</div>
          <div style="font-size:13px;color:var(--muted);margin-top:6px;font-weight:500;">⏱ ${pose.duration}</div>
        </div>
      </div>
      <div class="ex-badges">
        <span class="badge diff-${pose.diff}">${pose.diff}</span>
      </div>
      <div class="ex-desc" style="margin-top:16px;">${pose.desc}</div>
      <div class="ex-actions">
        <button class="btn btn-outline video-toggle" onclick="toggleVideo(this, '${videoId}')" style="padding:10px 16px;">
          ▶ Tutorial
        </button>
      </div>
      <div class="video-dropdown" style="display:none; padding-top:20px;">
        <iframe 
          id="yt-${videoId}"
          src="" 
          data-src="${embedUrl}"
          width="100%"
          height="220"
          style="border-radius:12px;border:none;display:block;"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          loading="lazy"
          onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
        ></iframe>
        
        <div class="video-error-fallback" style="display:none; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 24px; text-align: center; color: #888; font-size: 14px;">
           ▶ <a href="${ytLink}" target="_blank" style="color:#ff4757;text-decoration:none;font-weight:600;">Watch on YouTube</a>
        </div>

        <div style="margin-top:16px; text-align:center;">
          <a href="${ytLink}" target="_blank" rel="noopener" class="yt-link-btn" style="text-decoration:none;">
            ▶ Watch on YouTube
          </a>
        </div>
      </div>
    </div>`;
  }).join('');
}

async function loadHomeWorkout(category) {
  try {
    const res = await fetch('/api/home-workout?category=' + encodeURIComponent(category));
    const data = await res.json();
    renderHomeExercises(data.exercises || [], data.category);
  } catch(e) {
    document.getElementById('home-list').innerHTML = '<div class="error-msg">Could not load exercises.</div>';
  }
}

function renderHomeExercises(exercises, category) {
  document.getElementById('home-count').textContent =
    `${exercises.length} exercises · ${category}`;
  document.getElementById('home-list').innerHTML = exercises.map((ex, i) => {
    const videoId = ex.yt.includes('v=') ? ex.yt.split('v=')[1].split('&')[0] : '';
    return `
    <div class="exercise-card" style="border-top: 4px solid #fb923c; animation-delay:${i * 0.05}s;">
      <div class="ex-header">
        <div>
          <div class="ex-name" style="color:#fb923c;">${ex.name}</div>
          <div style="font-size:13px;color:var(--muted);margin-top:6px;font-weight:500;">🎯 Sets: ${ex.reps}</div>
        </div>
      </div>
      <div class="ex-badges">
        <span class="badge diff-${ex.diff}">${ex.diff}</span>
        <span class="badge badge-equip">Bodyweight</span>
      </div>
      <div class="ex-desc" style="margin-top:16px;">${ex.desc}</div>
      <div class="ex-actions">
        <button class="btn btn-outline video-toggle" onclick="toggleVideo(this, '${videoId}')" style="padding:10px 16px;">
          ▶ Watch
        </button>
        <button class="btn btn-outline" onclick="openTimer(45)" style="padding:10px 16px;">⏱ 45s Rest</button>
      </div>
      <div class="video-dropdown" style="display:none;">
        <div class="video-container">
          <iframe id="yt-${videoId}" frameborder="0" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
        </div>
      </div>
    </div>`;
  }).join('');
}

// ── TRACKING ──
function toKey(y, m, d) { return `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`; }

function renderCalendar() {
  const MONTHS = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December'];

  const monthLabel = document.getElementById('cal-month-label');
  if(monthLabel) monthLabel.textContent = `${MONTHS[calMonth]} ${calYear}`;

  const firstDay    = new Date(calYear, calMonth, 1).getDay();
  const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
  const grid        = document.getElementById('cal-grid');
  
  if(!grid) return;
  grid.innerHTML = '';

  for (let i = 0; i < firstDay; i++) {
    const el = document.createElement('div');
    el.style.opacity = 0;
    grid.appendChild(el);
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const k      = toKey(calYear, calMonth, d);
    const isDone = workoutDays.includes(k);
    const isFut  = new Date(calYear, calMonth, d) > today;
    const isTod  = today.getFullYear() === calYear &&
                   today.getMonth()    === calMonth &&
                   today.getDate()     === d;

    const cell = document.createElement('div');
    cell.textContent = d;
    cell.style.aspectRatio = '1';
    cell.style.display = 'flex';
    cell.style.alignItems = 'center';
    cell.style.justifyContent = 'center';
    cell.style.borderRadius = '8px';
    cell.style.fontSize = '14px';
    cell.style.fontWeight = '600';
    cell.style.cursor = isFut ? 'default' : 'pointer';
    cell.style.border = '1px solid transparent';
    cell.style.transition = 'all .2s';

    if (isFut) {
      cell.style.color = 'rgba(255,255,255,0.1)';
    } else {
      if (isDone) {
        cell.style.background = 'rgba(57,255,20,0.1)';
        cell.style.color = 'var(--accent)';
        cell.style.borderColor = 'rgba(57,255,20,0.3)';
        cell.innerHTML = `${d}<span style="position:absolute; font-size:8px; margin-left:14px; margin-top:-14px;">✓</span>`;
      } else {
        cell.style.color = 'var(--text)';
        cell.style.background = 'rgba(255,255,255,0.03)';
      }
      if (isTod) {
        cell.style.borderColor = 'var(--accent2)';
      }
      cell.onmouseover = () => cell.style.borderColor = 'var(--accent)';
      cell.onmouseout  = () => cell.style.borderColor = isDone ? 'rgba(57,255,20,0.3)' : (isTod ? 'var(--accent2)' : 'transparent');
      cell.addEventListener('click', () => toggleDay(calYear, calMonth, d));
    }
    grid.appendChild(cell);
  }
}

async function toggleDay(y, m, d) {
  const k = toKey(y, m, d);
  if (workoutDays.includes(k)) workoutDays = workoutDays.filter(x => x !== k);
  else workoutDays.push(k);
  
  localStorage.setItem('workout_days', JSON.stringify(workoutDays));
  try {
    await fetch('/api/calendar', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ date: k })
    });
  } catch(e) {}
  renderCalendar();
  renderTrackerStats();
}

window.changeMonth = function(delta) {
  calMonth += delta;
  if (calMonth < 0)  { calMonth = 11; calYear--; }
  if (calMonth > 11) { calMonth = 0;  calYear++; }
  renderCalendar();
}

function calcStreak() {
  let streak = 0;
  const d = new Date(today);
  while (true) {
    const k = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    if (!workoutDays.includes(k)) break;
    streak++;
    d.setDate(d.getDate() - 1);
  }
  return streak;
}

function thisWeekDone() {
  const start = new Date(today);
  start.setDate(today.getDate() - today.getDay());
  start.setHours(0,0,0,0);
  return workoutDays.filter(k => {
    const d = new Date(k);
    return d >= start && d <= today;
  }).length;
}

function renderTrackerStats() {
  const streak = calcStreak();
  const week   = thisWeekDone();
  document.getElementById('tracker-stats').innerHTML = `
    <div class="stat-box">
      <div class="stat-num">${workoutDays.length}</div>
      <div class="stat-lbl">Total Logged</div>
    </div>
    <div class="stat-box">
      <div class="stat-num" style="display:flex;align-items:center;justify-content:center;gap:8px;">
        <span style="font-size:24px;">🔥</span>${streak}
      </div>
      <div class="stat-lbl">Day Streak</div>
    </div>
    <div class="stat-box">
      <div class="stat-num" style="color:var(--accent2);">${week}</div>
      <div class="stat-lbl">This Week</div>
    </div>`;
  updateGoalUI(weeklyGoal);
}

// ── GOAL ──
function initGoalUI() {
  const s = document.getElementById('goal-slider');
  if(s) s.value = weeklyGoal;
  updateGoalUI(weeklyGoal);
}

window.updateGoalUI = function(g) {
  weeklyGoal = parseInt(g);
  const week = thisWeekDone();
  const pct  = Math.min(100, Math.round((week / weeklyGoal) * 100));
  
  const gd = document.getElementById('goal-display');
  const gfrac = document.getElementById('goal-fraction');
  const gf = document.getElementById('goal-fill');
  const gp = document.getElementById('goal-pct');
  
  if(gd) gd.textContent = weeklyGoal;
  if(gfrac) gfrac.textContent = `${week}/${weeklyGoal} done`;
  if(gf) gf.style.width = pct + '%';
  if(gp) gp.textContent = pct + '% complete';
}

window.saveGoal = async function(g) {
  weeklyGoal = parseInt(g);
  localStorage.setItem('weekly_goal', String(weeklyGoal));
  try {
    await fetch('/api/goal', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ goal: weeklyGoal })
    });
  } catch(e) {}
}

// ── PROFILE ──
function renderProfile() {
  if (!userData) return;
  const h   = userData.height / 100;
  const bmi = +(userData.weight / (h * h)).toFixed(1);
  let bmiLabel = 'Normal', bmiCls = 'normal';
  if (bmi < 18.5)   { bmiLabel = 'Underweight'; bmiCls = 'under'; }
  else if (bmi < 25) { bmiLabel = 'Normal';      bmiCls = 'normal'; }
  else if (bmi < 30) { bmiLabel = 'Overweight';  bmiCls = 'over'; }
  else               { bmiLabel = 'Obese';        bmiCls = 'over'; }

  document.getElementById('prof-initial').textContent = (userData.name || 'U').charAt(0).toUpperCase();
  document.getElementById('prof-name').textContent = userData.name || 'User Name';
  document.getElementById('profile-sub').textContent = `${userData.gender} · ${userData.age} years old`;

  document.getElementById('profile-stats').innerHTML = [
    { label:'Age',    val: userData.age, sub:'yrs' },
    { label:'Weight', val: userData.weight, sub:'kg' },
    { label:'Height', val: userData.height, sub:'cm' },
    { label:'BMI',    val: bmi, sub:'' },
  ].map(s => `
    <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border); border-radius:12px; padding:20px; text-align:center;">
      <div style="font-family:var(--font-head);font-size:28px;font-weight:700;line-height:1;margin-bottom:8px;color:var(--text);">${s.val}<span style="font-size:14px;color:var(--muted);font-weight:500;">${s.sub}</span></div>
      <div style="font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-weight:600;">${s.label}</div>
    </div>`).join('');

  document.getElementById('profile-bmi-badge').innerHTML =
    `<span class="bmi-status ${bmiCls}">${bmiLabel}</span>`;

  document.getElementById('profile-goal-name').textContent = userData.user_goal || 'Maintenance';
  
  const dietInfo = {
    'Veg':     { name:'🥦 Vegetarian', desc:'Plant-based meals.' },
    'Non-Veg': { name:'🥩 Non-Vegetarian', desc:'Includes meats, fish, dairy.' },
    'Jain':    { name:'🥗 Jain', desc:'No root vegetables.' }
  };
  const di = dietInfo[userData.diet] || {};
  document.getElementById('profile-diet-name').textContent = di.name || userData.diet;
  document.getElementById('profile-diet-desc').textContent = di.desc || '';
}

window.resetProfile = async function() {
  if (!confirm('Are you sure you want to reset your profile and erase all data?')) return;
  try {
    await fetch('/api/user-data', {
      method: 'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ name:'', age:0, weight:0, height:0, gender:'Male', diet:'Veg', user_goal:'Maintenance' })
    });
  } catch(e) {}
  userData = null;
  localStorage.removeItem('workout_days');
  workoutDays = [];
  document.getElementById('main-app').style.display   = 'none';
  document.getElementById('onboarding').style.display = 'block';
  ['inp-name','inp-age','inp-weight','inp-height'].forEach(id =>
    document.getElementById(id).value = '');
}

// ── REST TIMER ──
window.openTimer = function(secs) {
  timerSecs    = secs;
  timerMax     = secs;
  timerRunning = true;
  document.getElementById('timer-box').style.display = 'block';
  clearInterval(timerInterval);
  timerInterval = setInterval(tickTimer, 1000);
  renderTimerNum();
  document.getElementById('timer-toggle').textContent = '⏸ Pause';
  document.getElementById('timer-sub').textContent = 'recovering...';
}

window.closeTimer = function() {
  clearInterval(timerInterval);
  timerRunning = false;
  document.getElementById('timer-box').style.display = 'none';
}

window.toggleTimer = function() {
  if (timerSecs <= 0) { window.resetTimer(timerMax); return; }
  timerRunning = !timerRunning;
  if (timerRunning) {
    timerInterval = setInterval(tickTimer, 1000);
  } else {
    clearInterval(timerInterval);
  }
  document.getElementById('timer-toggle').textContent = timerRunning ? '⏸ Pause' : '▶ Resume';
  document.getElementById('timer-sub').textContent = timerRunning ? 'recovering...' : 'paused';
}

window.resetTimer = function(secs) {
  clearInterval(timerInterval);
  timerSecs    = secs;
  timerMax     = secs;
  timerRunning = true;
  timerInterval = setInterval(tickTimer, 1000);
  renderTimerNum();
  document.getElementById('timer-toggle').textContent = '⏸ Pause';
  document.getElementById('timer-sub').textContent    = 'recovering...';
}

function tickTimer() {
  if (timerSecs <= 0) {
    clearInterval(timerInterval);
    timerRunning = false;
    document.getElementById('timer-toggle').textContent = '↺ Reset';
    document.getElementById('timer-sub').textContent    = '✅ Ready to push!';
    return;
  }
  timerSecs--;
  renderTimerNum();
}

function renderTimerNum() {
  const m = Math.floor(timerSecs / 60);
  const s = timerSecs % 60;
  const el = document.getElementById('timer-num');
  el.textContent = `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  el.style.color = timerSecs <= 10 ? 'var(--accent3)' : 'var(--accent)';
}
