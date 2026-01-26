/**
 * Plotly Wrapper - Standardized styling and configuration for Plotly.js charts
 */

class PlotlyWrapper {
    /**
     * Standard Plotly configuration for the dark terminal theme
     */
    static getStandardConfig() {
        return {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'genetic-hexagram-chart',
                height: 600,
                width: 800,
                scale: 2
            }
        };
    }

    /**
     * Standard layout for dark theme
     */
    static getDarkLayout() {
        return {
            paper_bgcolor: '#1a1a2e',
            plot_bgcolor: '#16213e',
            font: {
                color: '#e4e4e7',
                family: '"JetBrains Mono", "Courier New", monospace'
            },
            margin: { l: 60, r: 40, t: 60, b: 60 },
            xaxis: {
                gridcolor: '#2a2a4a',
                zerolinecolor: '#4a4a6a'
            },
            yaxis: {
                gridcolor: '#2a2a4a',
                zerolinecolor: '#4a4a6a'
            }
        };
    }

    /**
     * Color palette for hexagram visualizations
     */
    static getColorPalette() {
        return [
            '#00ff9f', // Terminal green
            '#ff0055', // Accent red
            '#00d9ff', // Cyan
            '#ffaa00', // Amber
            '#bd00ff', // Purple
            '#ff00aa', // Pink
            '#00ff00', // Green
            '#0099ff'  // Blue
        ];
    }

    /**
     * Create a chart in a container element
     * @param {string} containerId - ID of the container element
     * @param {object} data - Plotly data array
     * @param {object} layout - Plotly layout object
     * @param {object} config - Plotly config object (optional)
     */
    static createChart(containerId, data, layout, config = null) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        // Merge with standard dark layout
        const standardLayout = {
            ...this.getDarkLayout(),
            ...layout
        };

        // Use standard config if not provided
        const chartConfig = config || this.getStandardConfig();

        // Create the chart
        Plotly.newPlot(container, data, standardLayout, chartConfig);

        return container;
    }

    /**
     * Create a bar chart
     * @param {string} containerId - ID of the container element
     * @param {array} x - X-axis values
     * @param {array} y - Y-axis values
     * @param {object} options - Additional options
     */
    static createBarChart(containerId, x, y, options = {}) {
        const trace = {
            type: 'bar',
            x: x,
            y: y,
            marker: {
                color: y,
                colorscale: 'Viridis',
                colorbar: options.showColorBar !== false ? {
                    title: { text: options.colorBarTitle || 'Count' },
                    tickfont: { color: '#e4e4e7' }
                } : undefined
            },
            text: y.map((val, i) => `${x[i]}: ${val}`),
            hoverinfo: 'text+y',
            name: options.name || 'Count'
        };

        const layout = {
            title: {
                text: options.title || 'Bar Chart',
                font: { size: 18, color: '#00ff9f' }
            },
            xaxis: { title: { text: options.xTitle || 'X' } },
            yaxis: { title: { text: options.yTitle || 'Y' } }
        };

        return this.createChart(containerId, [trace], layout, options.config);
    }

    /**
     * Create a pie chart
     * @param {string} containerId - ID of the container element
     * @param {array} labels - Labels for pie slices
     * @param {array} values - Values for pie slices
     * @param {object} options - Additional options
     */
    static createPieChart(containerId, labels, values, options = {}) {
        const trace = {
            type: 'pie',
            labels: labels,
            values: values,
            textinfo: 'label+percent',
            textposition: 'inside',
            marker: {
                colors: options.colors || this.getColorPalette()
            },
            hole: options.hole || 0,
            name: options.name || 'Distribution'
        };

        const layout = {
            title: {
                text: options.title || 'Pie Chart',
                font: { size: 18, color: '#00ff9f' }
            },
            showlegend: options.showLegend !== false
        };

        return this.createChart(containerId, [trace], layout, options.config);
    }

    /**
     * Create a line chart
     * @param {string} containerId - ID of the container element
     * @param {array} x - X-axis values
     * @param {array} y - Y-axis values
     * @param {object} options - Additional options
     */
    static createLineChart(containerId, x, y, options = {}) {
        const trace = {
            type: 'scatter',
            mode: options.mode || 'lines+markers',
            x: x,
            y: y,
            line: {
                color: options.lineColor || '#00ff9f',
                width: options.lineWidth || 2
            },
            marker: {
                size: options.markerSize || 6,
                color: options.markerColor || '#00d9ff'
            },
            name: options.name || 'Value'
        };

        const layout = {
            title: {
                text: options.title || 'Line Chart',
                font: { size: 18, color: '#00ff9f' }
            },
            xaxis: { title: { text: options.xTitle || 'X' } },
            yaxis: { title: { text: options.yTitle || 'Y' } }
        };

        return this.createChart(containerId, [trace], layout, options.config);
    }

    /**
     * Create a heatmap
     * @param {string} containerId - ID of the container element
     * @param {array} x - X-axis labels
     * @param {array} y - Y-axis labels
     * @param {array} z - 2D array of z values
     * @param {object} options - Additional options
     */
    static createHeatmap(containerId, x, y, z, options = {}) {
        const trace = {
            type: 'heatmap',
            x: x,
            y: y,
            z: z,
            colorscale: options.colorscale || 'Viridis',
            colorbar: {
                title: { text: options.colorBarTitle || 'Count' },
                tickfont: { color: '#e4e4e7' }
            }
        };

        const layout = {
            title: {
                text: options.title || 'Heatmap',
                font: { size: 18, color: '#00ff9f' }
            },
            xaxis: { title: { text: options.xTitle || 'X' } },
            yaxis: { title: { text: options.yTitle || 'Y' } }
        };

        return this.createChart(containerId, [trace], layout, options.config);
    }

    /**
     * Create a scatter plot
     * @param {string} containerId - ID of the container element
     * @param {array} x - X-axis values
     * @param {array} y - Y-axis values
     * @param {object} options - Additional options
     */
    static createScatter(containerId, x, y, options = {}) {
        const trace = {
            type: 'scatter',
            mode: options.mode || 'markers',
            x: x,
            y: y,
            marker: {
                size: options.markerSize || 10,
                color: options.markerColor || '#00ff9f',
                opacity: options.opacity || 0.8
            },
            text: options.text,
            name: options.name || 'Points'
        };

        const layout = {
            title: {
                text: options.title || 'Scatter Plot',
                font: { size: 18, color: '#00ff9f' }
            },
            xaxis: { title: { text: options.xTitle || 'X' } },
            yaxis: { title: { text: options.yTitle || 'Y' } }
        };

        return this.createChart(containerId, [trace], layout, options.config);
    }

    /**
     * Update an existing chart
     * @param {string} containerId - ID of the container element
     * @param {object} data - New data array
     * @param {object} layout - New layout object (optional)
     */
    static updateChart(containerId, data, layout = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        Plotly.react(container, data, layout, this.getStandardConfig());
    }

    /**
     * Resize a chart to fit its container
     * @param {string} containerId - ID of the container element
     */
    static resizeChart(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            Plotly.Plots.resize(container);
        }
    }

    /**
     * Download a chart as an image
     * @param {string} containerId - ID of the container element
     * @param {string} format - Image format ('png', 'jpeg', 'webp', 'svg')
     * @param {number} width - Image width (pixels)
     * @param {number} height - Image height (pixels)
     * @param {number} scale - Scale factor for resolution
     */
    static downloadChart(containerId, format = 'png', width = 800, height = 600, scale = 2) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        Plotly.downloadImage(container, {
            format: format,
            width: width,
            height: height,
            scale: scale,
            filename: `genetic-hexagram-${containerId}-${Date.now()}`
        });
    }

    /**
     * Clear a chart container
     * @param {string} containerId - ID of the container element
     */
    static clearChart(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            Plotly.purge(container);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PlotlyWrapper;
}
