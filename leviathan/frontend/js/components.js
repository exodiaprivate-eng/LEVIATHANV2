/**
 * Reusable UI component generators
 */

function createPositionCard(p) {
    return `
        <div class="flex items-center justify-between p-3 rounded-xl bg-bg-tertiary">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                    <span class="text-xs font-bold text-accent-purple">${p.symbol.slice(0, 2)}</span>
                </div>
                <div>
                    <p class="font-medium">${p.symbol}</p>
                    <p class="text-xs text-gray-500">${p.qty} shares</p>
                </div>
            </div>
            <div class="text-right">
                <p class="font-medium">$${p.current_price.toFixed(2)}</p>
                <p class="text-xs ${p.pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}">
                    ${p.pnl_pct >= 0 ? '&#9650;' : '&#9660;'} ${Math.abs(p.pnl_pct).toFixed(2)}%
                </p>
            </div>
        </div>`;
}

function createActivityEntry(type, message) {
    const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const typeColors = {
        'SYSTEM': 'text-blue-400', 'OPUS': 'text-purple-400',
        'TRADE': 'text-green-400', 'ERROR': 'text-red-400', 'WARNING': 'text-yellow-400'
    };
    return `
        <div class="flex items-start gap-3 p-2 rounded-lg hover:bg-bg-tertiary">
            <span class="text-xs text-gray-500 whitespace-nowrap">${now}</span>
            <span class="text-xs font-medium ${typeColors[type] || 'text-gray-400'}">${type}</span>
            <span class="text-sm text-gray-300">${message}</span>
        </div>`;
}

function createStatCard(label, value, change, changeLabel) {
    const isPositive = parseFloat(change) >= 0;
    return `
        <div class="bg-bg-secondary rounded-2xl p-5 border border-border-color card-hover">
            <p class="text-gray-500 text-xs uppercase tracking-wide mb-2">${label}</p>
            <h2 class="text-3xl font-bold">${value}</h2>
            <div class="flex items-center gap-2 mt-2">
                <span class="text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}">${change}</span>
                <span class="text-xs text-gray-500">${changeLabel}</span>
            </div>
        </div>`;
}
