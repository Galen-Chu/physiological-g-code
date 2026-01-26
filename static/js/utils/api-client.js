/**
 * API Client for Physiological G-Code
 * Handles communication with the Django REST API
 */

class ApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    async get(endpoint) {
        const response = await fetch(`${this.baseUrl}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    async post(endpoint, data) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    // ========== Analysis endpoints ==========
    async analyzeSequence(sequence, options = {}) {
        return this.post('/analysis/analyze_sequence/', {
            sequence,
            name: options.name || 'Untitled',
            sequence_type: options.sequenceType || 'DNA',
            mapping_scheme: options.mappingScheme || 'scheme_1',
        });
    }

    async analyzeCodon(codon, scheme = 'scheme_1') {
        return this.post('/analysis/analyze_codon/', {
            codon,
            mapping_scheme: scheme,
        });
    }

    async translateCodons(codons, scheme = 'scheme_1') {
        return this.post('/analysis/translate_codons/', {
            codons,
            mapping_scheme: scheme,
        });
    }

    // ========== Reference data ==========
    async getHexagrams() {
        return this.get('/hexagrams/');
    }

    async getHexagram(number) {
        return this.get(`/hexagrams/${number}/`);
    }

    async getCodons() {
        return this.get('/codons/');
    }

    async getCodonsByAminoAcid(code) {
        return this.get(`/codons/by_amino_acid/?code=${code}`);
    }

    // ========== Mappings ==========
    async getActiveMapping() {
        return this.get('/mappings/active/');
    }

    async getMappingSchemes() {
        return this.get('/analysis/mapping_schemes/');
    }

    // ========== Pattern Analysis endpoints (Phase 3) ==========
    async patternPositionAnalysis(sequence, mappingScheme = 'scheme_1') {
        return this.post('/patterns/position_analysis/', {
            sequence,
            mapping_scheme: mappingScheme
        });
    }

    async patternSlidingWindow(sequence, windowSize = 3, stepSize = 1, mappingScheme = 'scheme_1') {
        return this.post('/patterns/sliding_window/', {
            sequence,
            window_size: windowSize,
            step_size: stepSize,
            mapping_scheme: mappingScheme
        });
    }

    async patternMotifDiscovery(sequence, motifLengths = [2, 3, 4], minOccurrences = 3, mappingScheme = 'scheme_1') {
        return this.post('/patterns/motif_discovery/', {
            sequence,
            motif_lengths: motifLengths,
            min_occurrences: minOccurrences,
            mapping_scheme: mappingScheme
        });
    }

    async patternConservation(sequences, sequenceNames = null, mappingScheme = 'scheme_1') {
        return this.post('/patterns/conservation/', {
            sequences,
            sequence_names: sequenceNames,
            mapping_scheme: mappingScheme
        });
    }

    async patternEntropy(sequence, windowSize = 10, mappingScheme = 'scheme_1') {
        return this.post('/patterns/entropy/', {
            sequence,
            window_size: windowSize,
            mapping_scheme: mappingScheme
        });
    }

    // ========== Comparative Analysis endpoints (Phase 3) ==========
    async comparativeSideBySide(sequence1, sequence2, options = {}) {
        return this.post('/comparative/side_by_side/', {
            sequence1,
            sequence2,
            sequence1_name: options.sequence1_name || 'Sequence 1',
            sequence2_name: options.sequence2_name || 'Sequence 2',
            mapping_scheme: options.mappingScheme || 'scheme_1',
            include_alignment: options.includeAlignment || false
        });
    }

    async comparativeMappingComparison(sequence, schemes = ['scheme_1', 'scheme_2', 'scheme_3', 'scheme_4']) {
        return this.post('/comparative/mapping_comparison/', {
            sequence,
            schemes
        });
    }

    async comparativeStatisticalTest(sequence1, sequence2, testType = 'chi_square', mappingScheme = 'scheme_1') {
        return this.post('/comparative/statistical_test/', {
            sequence1,
            sequence2,
            test_type: testType,
            mapping_scheme: mappingScheme
        });
    }

    async comparativeMultipleSequences(sequences, sequenceNames = null, mappingScheme = 'scheme_1') {
        return this.post('/comparative/multiple_sequences/', {
            sequences,
            sequence_names: sequenceNames,
            mapping_scheme: mappingScheme
        });
    }

    // ========== Visualization endpoints (Phase 3) ==========
    async vizFrequency(hexagramSequence, chartType = 'bar', topN = 20) {
        return this.post('/visualizations/frequency/', {
            hexagram_sequence: hexagramSequence,
            chart_type: chartType,
            top_n: topN
        });
    }

    async vizTransitions(hexagramSequence, minEdgeWeight = 1) {
        return this.post('/visualizations/transitions/', {
            hexagram_sequence: hexagramSequence,
            min_edge_weight: minEdgeWeight
        });
    }

    async vizHeatmap(hexagramSequence, windowSize = 10) {
        return this.post('/visualizations/heatmap/', {
            hexagram_sequence: hexagramSequence,
            window_size: windowSize
        });
    }

    async viz3dRelations(sequences, sequenceNames = null) {
        return this.post('/visualizations/3d_relations/', {
            sequences,
            sequence_names: sequenceNames
        });
    }

    async vizRadar(sequences, sequenceNames = null) {
        return this.post('/visualizations/radar/', {
            sequences,
            sequence_names: sequenceNames
        });
    }

    async vizSunburst(hexagramSequence, sequenceName = 'Sequence') {
        return this.post('/visualizations/sunburst/', {
            hexagram_sequence: hexagramSequence,
            sequence_name: sequenceName
        });
    }

    async vizGauge(metricName, value, minValue = 0, maxValue = 1, thresholds = null) {
        return this.post('/visualizations/gauge/', {
            metric_name: metricName,
            value,
            min_value: minValue,
            max_value: maxValue,
            thresholds
        });
    }

    // ========== Export endpoints (Phase 3) ==========
    async exportCsv(data, includeMetadata = true) {
        return this.post('/export/csv/', {
            data,
            include_metadata: includeMetadata
        });
    }

    async exportJson(data, pretty = true, includeMetadata = true) {
        return this.post('/export/json/', {
            data,
            pretty,
            include_metadata: includeMetadata
        });
    }

    async exportFasta(sequence, hexagramSequence, sequenceName = 'sequence') {
        return this.post('/export/fasta/', {
            sequence,
            hexagram_sequence: hexagramSequence,
            sequence_name: sequenceName
        });
    }

    async exportPdfData(data, title = 'Analysis Report') {
        return this.post('/export/pdf_data/', {
            data,
            title
        });
    }

    async exportImageData(data, chartType = 'bar', width = 800, height = 600) {
        return this.post('/export/image_data/', {
            data,
            chart_type: chartType,
            width,
            height
        });
    }

    async exportBatch(data, formats = ['csv', 'json'], baseFilename = 'analysis') {
        return this.post('/export/batch/', {
            data,
            formats,
            base_filename: baseFilename
        });
    }
}

// Export singleton
const api = new ApiClient();
