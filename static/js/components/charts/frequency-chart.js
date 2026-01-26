/**
 * Frequency Chart Component - Displays hexagram frequency distribution
 */

class FrequencyChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.currentData = null;
    }

    /**
     * Render frequency chart from API data
     * @param {object} data - API response data
     * @param {string} chartType - Type of chart ('bar', 'pie', 'donut')
     */
    render(data, chartType = 'bar') {
        if (data.error) {
            this.showError(data.error);
            return;
        }

        this.currentData = data;

        if (data.data && data.layout) {
            // Data already formatted for Plotly
            PlotlyWrapper.createChart(
                this.containerId,
                data.data,
                data.layout,
                data.config
            );
        } else {
            // Legacy data format - need to format
            this.renderLegacyFormat(data, chartType);
        }
    }

    /**
     * Render from legacy data format
     */
    renderLegacyFormat(data, chartType) {
        const hexagramFrequency = data.hexagram_frequency || {};

        if (Object.keys(hexagramFrequency).length === 0) {
            this.showError('No frequency data available');
            return;
        }

        // Sort by frequency
        const sortedHexagrams = Object.entries(hexagramFrequency)
            .sort((a, b) => b[1] - a[1]);

        const hexagramNumbers = sortedHexagrams.map(h => h[0]);
        const frequencies = sortedHexagrams.map(h => h[1]);

        if (chartType === 'bar') {
            PlotlyWrapper.createBarChart(
                this.containerId,
                hexagramNumbers,
                frequencies,
                {
                    title: 'Hexagram Frequency Distribution',
                    xTitle: 'Hexagram Number',
                    yTitle: 'Count',
                    colorBarTitle: 'Frequency'
                }
            );
        } else if (chartType === 'pie' || chartType === 'donut') {
            const labels = hexagramNumbers.map(h => `Hexagram ${h}`);
            PlotlyWrapper.createPieChart(
                this.containerId,
                labels,
                frequencies,
                {
                    title: 'Hexagram Distribution',
                    hole: chartType === 'donut' ? 0.4 : 0
                }
            );
        }
    }

    /**
     * Update chart with new data
     */
    update(data, chartType = 'bar') {
        this.render(data, chartType);
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `
                <div class="chart-error" style="color: #ff0055; padding: 20px; text-align: center;">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <p style="margin-top: 10px;">${message}</p>
                </div>
            `;
        }
    }

    /**
     * Download chart as image
     */
    download(format = 'png') {
        PlotlyWrapper.downloadChart(this.containerId, format);
    }

    /**
     * Clear the chart
     */
    clear() {
        PlotlyWrapper.clearChart(this.containerId);
    }
}
