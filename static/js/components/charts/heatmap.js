/**
 * Heatmap Component - Displays position vs hexagram heatmap
 */

class HeatmapChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.currentData = null;
    }

    /**
     * Render heatmap from API data
     * @param {object} data - API response data
     */
    render(data) {
        if (data.error) {
            this.showError(data.error);
            return;
        }

        this.currentData = data;

        if (data.data && data.data[0] && data.data[0].type === 'heatmap') {
            // Data already formatted for Plotly
            PlotlyWrapper.createChart(
                this.containerId,
                data.data,
                data.layout,
                data.config
            );
        } else {
            this.showError('Invalid data format for heatmap');
        }
    }

    /**
     * Update heatmap with new data
     */
    update(data) {
        this.render(data);
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
