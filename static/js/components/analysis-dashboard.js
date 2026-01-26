/**
 * Analysis Dashboard - Main dashboard integrating Phase 3 analysis features
 */

class AnalysisDashboard {
    constructor(containerId, apiClient) {
        this.containerId = containerId;
        this.api = apiClient;
        this.currentTab = 'pattern';
        this.charts = {};
        this.currentData = null;
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.render();
        this.attachEventListeners();
    }

    /**
     * Render the dashboard UI
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="analysis-dashboard">
                <div class="dashboard-header">
                    <h2 class="dashboard-title">Advanced Analysis Dashboard</h2>
                    <div class="dashboard-controls">
                        <select id="mapping-scheme" class="form-select">
                            <option value="scheme_1">Scheme 1: Purine/Pyrimidine</option>
                            <option value="scheme_2">Scheme 2: AT/GC Alternation</option>
                            <option value="scheme_3">Scheme 3: Hydrogen Bond Count</option>
                            <option value="scheme_4">Scheme 4: Molecular Weight</option>
                        </select>
                    </div>
                </div>

                <div class="dashboard-tabs">
                    <button class="tab-btn active" data-tab="pattern">
                        <span class="tab-icon">◈</span> Pattern Analysis
                    </button>
                    <button class="tab-btn" data-tab="comparative">
                        <span class="tab-icon">⤥</span> Comparative
                    </button>
                    <button class="tab-btn" data-tab="visualization">
                        <span class="tab-icon">📊</span> Visualizations
                    </button>
                    <button class="tab-btn" data-tab="export">
                        <span class="tab-icon">⬇</span> Export
                    </button>
                </div>

                <div class="dashboard-content">
                    <!-- Pattern Analysis Tab -->
                    <div class="tab-content active" id="pattern-tab">
                        <div class="analysis-section">
                            <h3>Pattern Detection</h3>
                            <div class="pattern-controls">
                                <button class="btn btn-primary" id="btn-position-analysis">
                                    Position Analysis
                                </button>
                                <button class="btn btn-primary" id="btn-sliding-window">
                                    Sliding Window
                                </button>
                                <button class="btn btn-primary" id="btn-motif-discovery">
                                    Motif Discovery
                                </button>
                                <button class="btn btn-primary" id="btn-entropy">
                                    Entropy Analysis
                                </button>
                            </div>
                            <div class="analysis-results" id="pattern-results"></div>
                        </div>
                    </div>

                    <!-- Comparative Analysis Tab -->
                    <div class="tab-content" id="comparative-tab">
                        <div class="analysis-section">
                            <h3>Comparative Analysis</h3>
                            <div class="comparative-controls">
                                <div class="input-group">
                                    <textarea id="compare-seq1" placeholder="Enter first sequence..."
                                        rows="3"></textarea>
                                    <textarea id="compare-seq2" placeholder="Enter second sequence..."
                                        rows="3"></textarea>
                                </div>
                                <button class="btn btn-primary" id="btn-compare-sequences">
                                    Compare Sequences
                                </button>
                                <button class="btn btn-secondary" id="btn-statistical-test">
                                    Statistical Test
                                </button>
                            </div>
                            <div class="analysis-results" id="comparative-results"></div>
                        </div>
                    </div>

                    <!-- Visualization Tab -->
                    <div class="tab-content" id="visualization-tab">
                        <div class="analysis-section">
                            <h3>Interactive Visualizations</h3>
                            <div class="viz-controls">
                                <button class="btn btn-primary" id="btn-viz-frequency">
                                    Frequency Chart
                                </button>
                                <button class="btn btn-primary" id="btn-viz-transitions">
                                    Transition Network
                                </button>
                                <button class="btn btn-primary" id="btn-viz-heatmap">
                                    Heatmap
                                </button>
                                <button class="btn btn-primary" id="btn-viz-3d">
                                    3D Relations
                                </button>
                                <button class="btn btn-primary" id="btn-viz-sunburst">
                                    Sunburst
                                </button>
                            </div>
                            <div class="viz-container" id="viz-display">
                                <div class="viz-placeholder">
                                    <p>Select a visualization type to display</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Export Tab -->
                    <div class="tab-content" id="export-tab">
                        <div class="analysis-section">
                            <h3>Export Results</h3>
                            <div class="export-controls">
                                <div class="export-format-options">
                                    <label><input type="checkbox" value="csv" checked> CSV</label>
                                    <label><input type="checkbox" value="json" checked> JSON</label>
                                    <label><input type="checkbox" value="fasta"> FASTA</label>
                                    <label><input type="checkbox" value="image"> Image Data</label>
                                </div>
                                <button class="btn btn-success" id="btn-export-all">
                                    Export All Formats
                                </button>
                                <button class="btn btn-primary" id="btn-export-csv">
                                    Export CSV
                                </button>
                                <button class="btn btn-primary" id="btn-export-json">
                                    Export JSON
                                </button>
                            </div>
                            <div class="analysis-results" id="export-results"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Tab switching
        const tabButtons = this.container.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Pattern analysis buttons
        document.getElementById('btn-position-analysis')?.addEventListener('click', () => {
            this.runPositionAnalysis();
        });

        document.getElementById('btn-sliding-window')?.addEventListener('click', () => {
            this.runSlidingWindowAnalysis();
        });

        document.getElementById('btn-motif-discovery')?.addEventListener('click', () => {
            this.runMotifDiscovery();
        });

        document.getElementById('btn-entropy')?.addEventListener('click', () => {
            this.runEntropyAnalysis();
        });

        // Comparative analysis buttons
        document.getElementById('btn-compare-sequences')?.addEventListener('click', () => {
            this.runSequenceComparison();
        });

        document.getElementById('btn-statistical-test')?.addEventListener('click', () => {
            this.runStatisticalTest();
        });

        // Visualization buttons
        document.getElementById('btn-viz-frequency')?.addEventListener('click', () => {
            this.showFrequencyChart();
        });

        document.getElementById('btn-viz-transitions')?.addEventListener('click', () => {
            this.showTransitionNetwork();
        });

        document.getElementById('btn-viz-heatmap')?.addEventListener('click', () => {
            this.showHeatmap();
        });

        document.getElementById('btn-viz-3d')?.addEventListener('click', () => {
            this.show3DRelations();
        });

        document.getElementById('btn-viz-sunburst')?.addEventListener('click', () => {
            this.showSunburst();
        });

        // Export buttons
        document.getElementById('btn-export-csv')?.addEventListener('click', () => {
            this.exportTo('csv');
        });

        document.getElementById('btn-export-json')?.addEventListener('click', () => {
            this.exportTo('json');
        });

        document.getElementById('btn-export-all')?.addEventListener('click', () => {
            this.exportAll();
        });
    }

    /**
     * Switch to a different tab
     */
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });

        this.currentTab = tabName;
    }

    /**
     * Run position analysis
     */
    async runPositionAnalysis() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        this.showLoading('pattern-results');

        try {
            const response = await fetch('/api/patterns/position_analysis/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sequence,
                    mapping_scheme: mappingScheme
                })
            });

            const data = await response.json();
            this.displayPatternResults(data, 'position');
        } catch (error) {
            this.showError('pattern-results', error.message);
        }
    }

    /**
     * Run sliding window analysis
     */
    async runSlidingWindowAnalysis() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        this.showLoading('pattern-results');

        try {
            const response = await fetch('/api/patterns/sliding_window/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sequence,
                    mapping_scheme: mappingScheme,
                    window_size: 3,
                    step_size: 1
                })
            });

            const data = await response.json();
            this.displayPatternResults(data, 'sliding_window');
        } catch (error) {
            this.showError('pattern-results', error.message);
        }
    }

    /**
     * Run motif discovery
     */
    async runMotifDiscovery() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        this.showLoading('pattern-results');

        try {
            const response = await fetch('/api/patterns/motif_discovery/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sequence,
                    mapping_scheme: mappingScheme,
                    motif_lengths: [2, 3, 4],
                    min_occurrences: 3
                })
            });

            const data = await response.json();
            this.displayPatternResults(data, 'motif');
        } catch (error) {
            this.showError('pattern-results', error.message);
        }
    }

    /**
     * Run entropy analysis
     */
    async runEntropyAnalysis() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        this.showLoading('pattern-results');

        try {
            const response = await fetch('/api/patterns/entropy/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sequence,
                    mapping_scheme: mappingScheme,
                    window_size: 10
                })
            });

            const data = await response.json();
            this.displayPatternResults(data, 'entropy');
        } catch (error) {
            this.showError('pattern-results', error.message);
        }
    }

    /**
     * Display pattern analysis results
     */
    displayPatternResults(data, type) {
        const container = document.getElementById('pattern-results');
        if (!container) return;

        if (data.error) {
            container.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }

        let html = '<div class="results-summary">';

        if (type === 'position') {
            html += `<h4>Position Analysis Results</h4>`;
            html += `<p>Average Bias: ${data.average_bias?.toFixed(4) || 'N/A'}</p>`;
            html += `<p>High Bias Positions: ${Object.keys(data.high_bias_positions || {}).length || 0}</p>`;
        } else if (type === 'sliding_window') {
            html += `<h4>Sliding Window Results</h4>`;
            html += `<p>Total Windows: ${data.total_windows || 0}</p>`;
            html += `<p>Unique Patterns: ${data.unique_patterns || 0}</p>`;
            html += `<p>Pattern Entropy: ${data.pattern_entropy?.toFixed(4) || 'N/A'}</p>`;
        } else if (type === 'motif') {
            html += `<h4>Motif Discovery Results</h4>`;
            html += `<p>Motifs Found: ${data.motifs_found || 0}</p>`;
            html += `<p>Coverage Ratio: ${data.motif_coverage_ratio?.toFixed(4) || 'N/A'}</p>`;
        } else if (type === 'entropy') {
            html += `<h4>Entropy Analysis Results</h4>`;
            html += `<p>Overall Entropy: ${data.overall_entropy?.toFixed(4) || 'N/A'}</p>`;
            html += `<p>Complexity Score: ${data.complexity_score?.toFixed(4) || 'N/A'}</p>`;
        }

        html += '</div>';

        // Add detailed results
        if (data.patterns && data.patterns.motifs) {
            html += '<div class="motifs-list"><h5>Discovered Motifs:</h5><ul>';
            data.patterns.motifs.slice(0, 10).forEach(motif => {
                html += `<li>Motif: [${motif.motif.join(', ')}] - ${motif.occurrences} occurrences</li>`;
            });
            html += '</ul></div>';
        }

        container.innerHTML = html;
        this.currentData = data;
    }

    /**
     * Show frequency chart
     */
    async showFrequencyChart() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        document.getElementById('viz-display').innerHTML = '<div class="loading">Loading chart...</div>';

        try {
            const response = await fetch('/api/visualizations/frequency/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hexagram_sequence: await this.getHexagramSequence(sequence, mappingScheme),
                    chart_type: 'bar',
                    top_n: 20
                })
            });

            const data = await response.json();
            document.getElementById('viz-display').innerHTML = '<div id="frequency-chart" style="width:100%;height:500px;"></div>';
            this.charts.frequency = new FrequencyChart('frequency-chart');
            this.charts.frequency.render(data);
        } catch (error) {
            document.getElementById('viz-display').innerHTML = `<div class="error">${error.message}</div>`;
        }
    }

    /**
     * Show transition network
     */
    async showTransitionNetwork() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        document.getElementById('viz-display').innerHTML = '<div class="loading">Loading network...</div>';

        try {
            const response = await fetch('/api/visualizations/transitions/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hexagram_sequence: await this.getHexagramSequence(sequence, mappingScheme),
                    min_edge_weight: 1
                })
            });

            const data = await response.json();
            document.getElementById('viz-display').innerHTML = '<div id="transition-chart" style="width:100%;height:500px;"></div>';
            this.charts.transitions = new TransitionNetwork('transition-chart');
            this.charts.transitions.render(data);
        } catch (error) {
            document.getElementById('viz-display').innerHTML = `<div class="error">${error.message}</div>`;
        }
    }

    /**
     * Show heatmap
     */
    async showHeatmap() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        document.getElementById('viz-display').innerHTML = '<div class="loading">Loading heatmap...</div>';

        try {
            const response = await fetch('/api/visualizations/heatmap/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hexagram_sequence: await this.getHexagramSequence(sequence, mappingScheme),
                    window_size: 10
                })
            });

            const data = await response.json();
            document.getElementById('viz-display').innerHTML = '<div id="heatmap-chart" style="width:100%;height:500px;"></div>';
            this.charts.heatmap = new HeatmapChart('heatmap-chart');
            this.charts.heatmap.render(data);
        } catch (error) {
            document.getElementById('viz-display').innerHTML = `<div class="error">${error.message}</div>`;
        }
    }

    /**
     * Show 3D relations
     */
    async show3DRelations() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        alert('3D Relations requires multiple sequences. Please use comparative analysis with multiple sequences.');
    }

    /**
     * Show sunburst chart
     */
    async showSunburst() {
        const sequence = this.getCurrentSequence();
        if (!sequence) return;

        const mappingScheme = document.getElementById('mapping-scheme')?.value || 'scheme_1';

        document.getElementById('viz-display').innerHTML = '<div class="loading">Loading chart...</div>';

        try {
            const response = await fetch('/api/visualizations/sunburst/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hexagram_sequence: await this.getHexagramSequence(sequence, mappingScheme),
                    sequence_name: 'Current Sequence'
                })
            });

            const data = await response.json();
            document.getElementById('viz-display').innerHTML = '<div id="sunburst-chart" style="width:100%;height:500px;"></div>';
            PlotlyWrapper.createChart('sunburst-chart', data.data, data.layout, data.config);
        } catch (error) {
            document.getElementById('viz-display').innerHTML = `<div class="error">${error.message}</div>`;
        }
    }

    /**
     * Export data to format
     */
    async exportTo(format) {
        if (!this.currentData) {
            alert('No analysis data to export. Please run an analysis first.');
            return;
        }

        try {
            const response = await fetch(`/api/export/${format}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: this.currentData,
                    include_metadata: true
                })
            });

            const result = await response.json();
            this.downloadFile(result.filename, result.content, result.content_type);
        } catch (error) {
            alert(`Export failed: ${error.message}`);
        }
    }

    /**
     * Export to all formats
     */
    async exportAll() {
        if (!this.currentData) {
            alert('No analysis data to export. Please run an analysis first.');
            return;
        }

        const formats = ['csv', 'json'];

        try {
            const response = await fetch('/api/export/batch/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: this.currentData,
                    formats: formats,
                    base_filename: 'analysis'
                })
            });

            const result = await response.json();

            // Download each file
            for (const [filename, content] of Object.entries(result.exports)) {
                if (!content.startsWith('Error')) {
                    const ext = filename.split('.').pop();
                    const contentType = ext === 'json' ? 'application/json' : 'text/csv';
                    this.downloadFile(filename, content, contentType);
                }
            }
        } catch (error) {
            alert(`Export failed: ${error.message}`);
        }
    }

    /**
     * Download file
     */
    downloadFile(filename, content, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Get current sequence from page
     */
    getCurrentSequence() {
        const seqInput = document.querySelector('#sequence-input') || document.querySelector('#sequence');
        return seqInput?.value?.toUpperCase().replace(/\s/g, '') || '';
    }

    /**
     * Get hexagram sequence for current sequence
     */
    async getHexagramSequence(sequence, mappingScheme) {
        try {
            const response = await fetch('/api/analysis/translate_codons/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    codons: [sequence[i:i+3] for i in range(0, sequence.length, 3)],
                    mapping_scheme: mappingScheme
                })
            });
            const data = await response.json();
            return data.hexagrams || [];
        } catch (error) {
            console.error('Error translating sequence:', error);
            return [];
        }
    }

    /**
     * Show loading indicator
     */
    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="loading">Analyzing...</div>';
        }
    }

    /**
     * Show error message
     */
    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="error">${message}</div>`;
        }
    }
}
