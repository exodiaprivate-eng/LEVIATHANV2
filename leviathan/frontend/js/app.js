/**
 * Main application logic - Trading controls, UI updates, data refresh
 */

// ============================================
// TRADING CONTROLS
// ============================================

async function startTrading() {
    const result = await callPython('start_trading');
    if (result && result.status === 'running') {
        updateStatus('running');
        document.getElementById('start-btn').disabled = true;
        document.getElementById('start-btn').className = 'w-full py-4 rounded-xl bg-bg-quaternary text-gray-500 font-semibold text-lg cursor-not-allowed';
        document.getElementById('stop-btn').disabled = false;
        document.getElementById('stop-btn').className = 'w-full py-4 rounded-xl bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold text-lg shadow-glow-red hover:shadow-lg transition-all hover:-translate-y-0.5';
        addActivity('SYSTEM', 'Trading started - Opus brain active');
    }
}

async function stopTrading() {
    const result = await callPython('stop_trading');
    if (result && result.status === 'stopped') {
        updateStatus('stopped');
        document.getElementById('start-btn').disabled = false;
        document.getElementById('start-btn').className = 'w-full py-4 rounded-xl bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold text-lg shadow-glow-green hover:shadow-lg transition-all hover:-translate-y-0.5';
        document.getElementById('stop-btn').disabled = true;
        document.getElementById('stop-btn').className = 'w-full py-4 rounded-xl bg-bg-quaternary text-gray-500 font-semibold text-lg cursor-not-allowed';
        addActivity('SYSTEM', 'Trading stopped - all orders cancelled');
    }
}

// ============================================
// UI UPDATE FUNCTIONS
// ============================================

function updateStatus(status) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (status === 'running') {
        dot.className = 'w-2 h-2 rounded-full bg-green-500 pulse-running';
        text.textContent = 'RUNNING';
        text.className = 'text-sm font-medium text-green-500';
    } else {
        dot.className = 'w-2 h-2 rounded-full bg-gray-500';
        text.textContent = 'STOPPED';
        text.className = 'text-sm font-medium text-gray-400';
    }
}

function updatePortfolio(data) {
    document.getElementById('portfolio-value').textContent = `$${data.balance.toFixed(2)}`;
    const changeEl = document.getElementById('portfolio-change');
    changeEl.textContent = `${data.total_pnl_pct >= 0 ? '+' : ''}${data.total_pnl_pct.toFixed(2)}%`;
    changeEl.className = `text-sm font-medium ${data.total_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`;

    document.getElementById('today-pnl').textContent = `$${data.today_pnl.toFixed(2)}`;
    const todayPctEl = document.getElementById('today-pnl-pct');
    todayPctEl.textContent = `${data.today_pnl_pct >= 0 ? '+' : ''}${data.today_pnl_pct.toFixed(2)}%`;
    todayPctEl.className = `text-sm font-medium ${data.today_pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`;

    document.getElementById('opus-decisions').textContent = data.opus_decisions;
    document.getElementById('opus-cost').textContent = `$${data.opus_cost.toFixed(2)} cost`;
    document.getElementById('win-rate').textContent = `${(data.win_rate * 100).toFixed(0)}%`;
    document.getElementById('win-loss').textContent = `${data.wins}W / ${data.losses}L`;
}

function updatePositions(positions) {
    const container = document.getElementById('positions-list');
    if (!positions || positions.length === 0) {
        container.innerHTML = '<div class="text-gray-500 text-sm text-center py-8">No open positions</div>';
        return;
    }
    container.innerHTML = positions.map(p => createPositionCard(p)).join('');
}

function addActivity(type, message) {
    const container = document.getElementById('activity-log');
    const placeholder = container.querySelector('.text-center');
    if (placeholder) placeholder.remove();

    const entry = document.createElement('div');
    entry.innerHTML = createActivityEntry(type, message);
    container.insertBefore(entry.firstElementChild, container.firstChild);

    while (container.children.length > 50) {
        container.removeChild(container.lastChild);
    }
}

// ============================================
// DATA REFRESH
// ============================================

async function refreshData() {
    try {
        const data = await callPython('get_dashboard_data');
        if (data) {
            updatePortfolio(data.portfolio);
            updatePositions(data.positions);
            updateChart(data.chart_data);
            updateStatus(data.is_running ? 'running' : 'stopped');
            if (data.mode) {
                document.getElementById('mode-text').textContent = data.mode;
            }
        }
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

// ============================================
// NAVIGATION
// ============================================

function showPage(page) {
    // Map page names to HTML files
    const pageMap = {
        'dashboard': 'index.html',
        'training': 'training.html',
        'settings': 'settings.html',
        'crypto_swap': 'crypto.html',
        'crypto': 'crypto.html',
        'options': 'options.html',
        'analytics': 'analytics.html',
    };

    const target = pageMap[page] || page;
    window.location.href = target;
}

function openSettings() { window.location.href = 'settings.html'; }
function openCryptoSwap() { window.location.href = 'crypto.html'; }
function openAutopilot() { window.location.href = 'analytics.html'; }

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    refreshData();
    setInterval(refreshData, 5000);
});
