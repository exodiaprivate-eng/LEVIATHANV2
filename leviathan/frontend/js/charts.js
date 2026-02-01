/**
 * TradingView Lightweight Charts for portfolio performance
 */

let performanceChart = null;
let areaSeries = null;

function initChart() {
    const container = document.getElementById('performance-chart');
    if (!container || typeof LightweightCharts === 'undefined') return;

    performanceChart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: 256,
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#6b7280',
            fontFamily: 'Inter, sans-serif',
        },
        grid: {
            vertLines: { color: 'rgba(45, 45, 58, 0.4)' },
            horzLines: { color: 'rgba(45, 45, 58, 0.4)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: { color: 'rgba(139, 92, 246, 0.3)', width: 1, style: 2 },
            horzLine: { color: 'rgba(139, 92, 246, 0.3)', width: 1, style: 2 },
        },
        rightPriceScale: {
            borderColor: 'rgba(45, 45, 58, 0.4)',
        },
        timeScale: {
            borderColor: 'rgba(45, 45, 58, 0.4)',
            timeVisible: true,
        },
    });

    areaSeries = performanceChart.addAreaSeries({
        topColor: 'rgba(139, 92, 246, 0.4)',
        bottomColor: 'rgba(139, 92, 246, 0.0)',
        lineColor: '#8b5cf6',
        lineWidth: 2,
    });

    // Responsive
    new ResizeObserver(() => {
        performanceChart.applyOptions({ width: container.clientWidth });
    }).observe(container);
}

function updateChart(data) {
    if (areaSeries && data && data.length > 0) {
        const chartData = data.map(d => ({
            time: Math.floor(new Date(d.timestamp).getTime() / 1000),
            value: d.value,
        }));
        areaSeries.setData(chartData);
        performanceChart.timeScale().fitContent();
    }
}
