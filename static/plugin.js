/**
 * SEO Autonomous Plugin — Embeddable Widget
 * 
 * Usage: Add this script tag to any website:
 * <script src="https://your-server.com/static/plugin.js" data-server="https://your-server.com"></script>
 * 
 * The widget injects a floating button that opens a slide-in SEO analysis panel.
 * Runs inside Shadow DOM for complete style isolation.
 */
(function () {
    'use strict';

    // ─── Configuration ───
    const scriptEl = document.currentScript;
    const SERVER = (scriptEl && scriptEl.getAttribute('data-server')) || window.location.origin;
    const CSS_URL = SERVER + '/static/plugin.css';

    // ─── Create Shadow DOM Host ───
    const host = document.createElement('div');
    host.id = 'seo-plugin-root';
    host.style.cssText = 'all:initial; position:fixed; z-index:2147483647;';
    document.body.appendChild(host);

    const shadow = host.attachShadow({ mode: 'open' });

    // Load stylesheet
    const linkEl = document.createElement('link');
    linkEl.rel = 'stylesheet';
    linkEl.href = CSS_URL;
    shadow.appendChild(linkEl);

    // ─── Build DOM Structure ───
    const container = document.createElement('div');
    container.innerHTML = `
        <!-- Backdrop -->
        <div class="seo-backdrop" id="seo-backdrop"></div>

        <!-- Floating Trigger Button -->
        <button class="seo-trigger-btn" id="seo-trigger" title="SEO Analysis">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
        </button>

        <!-- Slide-in Panel -->
        <div class="seo-panel" id="seo-panel">
            <div class="seo-panel-header">
                <h2>SEO Analysis</h2>
                <button class="seo-close-btn" id="seo-close">✕</button>
            </div>

            <div class="seo-panel-body">
                <!-- Tabs -->
                <div class="seo-tabs">
                    <button class="seo-tab-btn active" data-tab="seo-standard">Standard</button>
                    <button class="seo-tab-btn" data-tab="seo-autonomous">Autonomous</button>
                </div>

                <!-- Standard Analysis Tab -->
                <div class="seo-tab-panel active" id="seo-standard">
                    <form id="seo-standard-form">
                        <div class="seo-form-group">
                            <label>Target Domain</label>
                            <input type="text" class="seo-input" name="domain" placeholder="https://example.com" required>
                        </div>
                        <div class="seo-form-group">
                            <label>Crawl Limit (Pages)</label>
                            <input type="number" class="seo-input" name="limit" value="50" min="1" required>
                        </div>
                        <button type="submit" class="seo-submit-btn">Run Engine</button>
                    </form>
                </div>

                <!-- Autonomous Analysis Tab -->
                <div class="seo-tab-panel" id="seo-autonomous">
                    <p style="color: var(--seo-text-muted); font-size: 0.85rem; margin-bottom: 16px;">
                        Crawl, analyze, fix SEO loopholes, generate new content, and deploy back.
                    </p>
                    <form id="seo-plugin-form">
                        <div class="seo-form-group">
                            <label>Site URL</label>
                            <input type="text" class="seo-input" name="site_url" placeholder="https://example.com" required>
                        </div>
                        <div class="seo-form-group">
                            <label>Competitor Domains (comma separated)</label>
                            <input type="text" class="seo-input" name="competitors" placeholder="competitor1.com, competitor2.com">
                        </div>
                        <div class="seo-form-group">
                            <label>Crawl Limit</label>
                            <input type="number" class="seo-input" name="limit" value="100" min="1" required>
                        </div>
                        <hr class="seo-divider">
                        <div class="seo-form-group">
                            <label>OpenAI API Key (Optional)</label>
                            <input type="password" class="seo-input" name="openai_key" placeholder="sk-...">
                        </div>
                        <div class="seo-form-group">
                            <label>Gemini API Key (Optional)</label>
                            <input type="password" class="seo-input" name="gemini_key" placeholder="AIza...">
                        </div>
                        <div class="seo-form-group">
                            <label>Ollama Host (Optional)</label>
                            <input type="text" class="seo-input" name="ollama_host" placeholder="http://localhost:11434">
                        </div>
                        <button type="submit" class="seo-submit-btn">Run Autonomous Analysis</button>
                    </form>
                </div>

                <!-- Progress Area (shared) -->
                <div class="seo-progress seo-hidden" id="seo-progress-area">
                    <div class="seo-progress-title">Analysis in Progress</div>
                    <ul class="seo-progress-steps" id="seo-progress-steps"></ul>
                </div>

                <!-- Results Area (shared) -->
                <div class="seo-results seo-hidden" id="seo-results-area"></div>
            </div>

            <div class="seo-powered-by">
                Powered by <a href="#">SEO Autonomous Plugin</a>
            </div>
        </div>
    `;
    shadow.appendChild(container);

    // ─── Element References ───
    const trigger = shadow.getElementById('seo-trigger');
    const panel = shadow.getElementById('seo-panel');
    const backdrop = shadow.getElementById('seo-backdrop');
    const closeBtn = shadow.getElementById('seo-close');
    const progressArea = shadow.getElementById('seo-progress-area');
    const progressSteps = shadow.getElementById('seo-progress-steps');
    const resultsArea = shadow.getElementById('seo-results-area');
    const standardForm = shadow.getElementById('seo-standard-form');
    const pluginForm = shadow.getElementById('seo-plugin-form');
    const tabBtns = shadow.querySelectorAll('.seo-tab-btn');

    // ─── Panel Toggle ───
    function openPanel() {
        panel.classList.add('open');
        backdrop.classList.add('visible');
    }

    function closePanel() {
        panel.classList.remove('open');
        backdrop.classList.remove('visible');
    }

    trigger.addEventListener('click', openPanel);
    closeBtn.addEventListener('click', closePanel);
    backdrop.addEventListener('click', closePanel);

    // ─── Tab Switching ───
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            shadow.querySelectorAll('.seo-tab-panel').forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            shadow.getElementById(btn.dataset.tab).classList.add('active');

            // Clear progress & results when switching tabs
            progressArea.classList.add('seo-hidden');
            resultsArea.classList.add('seo-hidden');
            progressSteps.innerHTML = '';
            resultsArea.innerHTML = '';
        });
    });

    // ─── API Helpers ───
    async function apiPost(endpoint, formData) {
        const res = await fetch(SERVER + endpoint, {
            method: 'POST',
            body: formData,
            mode: 'cors'
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || err.message || `HTTP ${res.status}`);
        }
        return res.json();
    }

    async function apiGet(endpoint) {
        const res = await fetch(SERVER + endpoint, { mode: 'cors' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    // ─── Poll Progress ───
    function pollProgress(taskId, mode) {
        let lastStatus = '';
        const interval = setInterval(async () => {
            try {
                const data = await apiGet(`/progress?task_id=${taskId}`);
                const status = data.status || 'Initializing...';

                if (status === 'Unknown task' || !status) return;

                if (data.state === 'error') {
                    clearInterval(interval);
                    if (progressSteps.lastElementChild) {
                        progressSteps.lastElementChild.innerHTML = `<span style="color:var(--seo-error)">✕</span> ${status}`;
                    }
                    resetFormButtons();
                    return;
                }

                if (status !== lastStatus) {
                    // Mark previous step as done
                    if (progressSteps.lastElementChild) {
                        progressSteps.lastElementChild.innerHTML = `<span style="color:var(--seo-primary)">✓</span> ${lastStatus}`;
                    }
                    lastStatus = status;
                    const li = document.createElement('li');
                    li.innerHTML = `<span style="display:inline-block;animation:seo-spin 1s linear infinite">⏳</span> ${status}`;
                    progressSteps.appendChild(li);
                }

                if (data.state === 'completed') {
                    clearInterval(interval);
                    setTimeout(() => loadResults(taskId, mode), 500);
                }
            } catch (e) { /* silent */ }
        }, 1200);

        return interval;
    }

    // ─── Load Results ───
    async function loadResults(taskId, mode) {
        try {
            const data = await apiGet(`/api/results?task_id=${taskId}`);
            if (!data || data.error) {
                resultsArea.innerHTML = `<div class="seo-result-card"><h4 style="color:var(--seo-error)">Error</h4><p>${data?.error || 'No results found'}</p></div>`;
                resultsArea.classList.remove('seo-hidden');
                return;
            }

            let html = '';
            const engineResult = data.engine_result || {};
            const score = data.seo_score_after || engineResult.seo_score || 0;
            const scoreClass = score >= 80 ? 'good' : score >= 50 ? 'average' : 'bad';
            const scoreLabel = score >= 80 ? 'Excellent' : score >= 50 ? 'Average' : 'Poor';

            html += `
                <div class="seo-result-card" style="text-align:center">
                    <div class="seo-score-ring ${scoreClass}">${Math.round(score)}</div>
                    <h4 style="color:var(--seo-primary)">${scoreLabel} SEO Health</h4>
                    <p style="color:var(--seo-text-muted);font-size:0.8rem">Analysis completed successfully</p>
                </div>
            `;

            // Strategy
            if (engineResult.strategy) {
                html += `
                    <div class="seo-result-card">
                        <h4>AI Strategy</h4>
                        <p style="color:var(--seo-text-muted);font-size:0.85rem;line-height:1.6">${engineResult.strategy}</p>
                    </div>
                `;
            }

            // Actions
            const actions = data.suggested_actions || engineResult.actions || [];
            if (actions.length > 0) {
                html += `<div class="seo-result-card"><h4>Suggested Fixes (${actions.length})</h4><ul class="seo-issue-list">`;
                actions.slice(0, 15).forEach(a => {
                    html += `<li><span class="seo-action-badge">${a.type || 'fix'}</span>${a.description || a.tag || a.fix_type || 'Apply SEO fix'}</li>`;
                });
                if (actions.length > 15) html += `<li style="color:var(--seo-text-muted)">...and ${actions.length - 15} more</li>`;
                html += `</ul></div>`;
            }

            // Modules issues summary
            const modules = engineResult.modules || {};
            const issueSections = [
                { key: 'meta', label: 'Meta Tags' },
                { key: 'image_seo', label: 'Image SEO' },
                { key: 'heading_structure', label: 'Headings' },
                { key: 'mobile_seo', label: 'Mobile' },
                { key: 'page_speed', label: 'Performance' },
                { key: 'broken_links', label: 'Links' }
            ];

            issueSections.forEach(sec => {
                const mod = modules[sec.key] || {};
                const issues = mod.issues || [];
                if (issues.length > 0) {
                    html += `<div class="seo-result-card"><h4>${sec.label} Issues (${issues.length})</h4><ul class="seo-issue-list">`;
                    issues.slice(0, 5).forEach(iss => {
                        const text = typeof iss === 'string' ? iss : (iss.issue || iss.description || JSON.stringify(iss));
                        html += `<li>${text}</li>`;
                    });
                    if (issues.length > 5) html += `<li style="color:var(--seo-text-muted)">...and ${issues.length - 5} more</li>`;
                    html += `</ul></div>`;
                }
            });

            // Link to full dashboard
            html += `
                <div class="seo-result-card" style="text-align:center">
                    <a href="${SERVER}/results?task_id=${taskId}" target="_blank" style="color:var(--seo-primary);font-weight:600;text-decoration:none;font-size:0.9rem">
                        Open Full Report →
                    </a>
                </div>
            `;

            resultsArea.innerHTML = html;
            resultsArea.classList.remove('seo-hidden');
            resetFormButtons();

        } catch (e) {
            resultsArea.innerHTML = `<div class="seo-result-card"><h4 style="color:var(--seo-error)">Error Loading Results</h4><p style="color:var(--seo-text-muted)">${e.message}</p></div>`;
            resultsArea.classList.remove('seo-hidden');
            resetFormButtons();
        }
    }

    // ─── Reset Form Buttons ───
    function resetFormButtons() {
        shadow.querySelectorAll('.seo-submit-btn').forEach(btn => {
            btn.disabled = false;
            btn.textContent = btn.closest('#seo-standard') ? 'Run Engine' : 'Run Autonomous Analysis';
        });
    }

    // ─── Form Submission Handler ───
    function handleSubmit(form, endpoint, mode) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = form.querySelector('.seo-submit-btn');
            btn.disabled = true;
            btn.textContent = 'Processing...';

            // Clear previous results
            resultsArea.classList.add('seo-hidden');
            resultsArea.innerHTML = '';
            progressSteps.innerHTML = '';
            progressArea.classList.remove('seo-hidden');

            const taskId = Math.random().toString(36).substring(2, 15);
            const formData = new FormData(form);
            formData.append('task_id', taskId);

            // Start polling
            const pollHandle = pollProgress(taskId, mode);

            try {
                await apiPost(endpoint, formData);
            } catch (err) {
                clearInterval(pollHandle);
                progressArea.classList.add('seo-hidden');
                resultsArea.innerHTML = `<div class="seo-result-card"><h4 style="color:var(--seo-error)">Submission Failed</h4><p style="color:var(--seo-text-muted)">${err.message}</p></div>`;
                resultsArea.classList.remove('seo-hidden');
                resetFormButtons();
            }
        });
    }

    handleSubmit(standardForm, '/generate', 'standard');
    handleSubmit(pluginForm, '/plugin/run', 'plugin');

    // ─── Auto-fill current site URL if on a real page ───
    try {
        const currentUrl = window.location.origin;
        if (currentUrl && !currentUrl.includes('localhost')) {
            const domainInput = standardForm.querySelector('[name="domain"]');
            const siteInput = pluginForm.querySelector('[name="site_url"]');
            if (domainInput && !domainInput.value) domainInput.value = currentUrl;
            if (siteInput && !siteInput.value) siteInput.value = currentUrl;
        }
    } catch (e) { /* cross-origin guard */ }

})();
