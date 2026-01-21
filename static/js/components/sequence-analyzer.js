/**
 * Sequence Analyzer Component
 * Handles sequence input and analysis
 */

class SequenceAnalyzer {
    constructor() {
        this.input = document.getElementById('sequence-input');
        this.sequenceType = document.getElementById('sequence-type');
        this.mappingScheme = document.getElementById('mapping-scheme');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.exportBtn = document.getElementById('export-btn');
        this.resultsContainer = document.getElementById('results-container');

        this.initListeners();
    }

    initListeners() {
        this.analyzeBtn.addEventListener('click', () => this.analyze());
        this.clearBtn.addEventListener('click', () => this.clear());
        this.exportBtn.addEventListener('click', () => this.export());
    }

    async analyze() {
        const sequence = this.input.value.trim().toUpperCase().replace(/\s/g, '');

        if (!sequence) {
            alert('Please enter a sequence');
            return;
        }

        if (sequence.length % 3 !== 0) {
            alert('Sequence length must be a multiple of 3 (complete codons)');
            return;
        }

        // Show loading state
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Analyzing...';

        try {
            const results = await api.analyzeSequence(sequence, {
                sequenceType: this.sequenceType.value,
                mappingScheme: this.mappingScheme.value,
            });

            this.displayResults(results);
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Error analyzing sequence: ' + error.message);
        } finally {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.innerHTML = '<span class="btn-icon">⚡</span>Analyze Sequence';
        }
    }

    displayResults(results) {
        // Update statistics
        document.getElementById('stat-length').textContent = results.length;
        document.getElementById('stat-codons').textContent = results.codon_count;
        document.getElementById('stat-gc').textContent = results.gc_content.toFixed(1) + '%';
        document.getElementById('stat-dominant').textContent = results.dominant_hexagram || '-';

        // Display hexagram sequence
        const hexagramContainer = document.getElementById('hexagram-sequence');
        hexagramContainer.innerHTML = '';

        results.hexagram_sequence.forEach((hexNum, index) => {
            const symbol = HexagramRenderer.createSymbol(hexNum);
            symbol.title = `Codon: ${results.codons[index]}\nHexagram: ${hexNum}`;
            hexagramContainer.appendChild(symbol);
        });

        // Display amino acid sequence
        const aaContainer = document.getElementById('amino-acid-sequence');
        aaContainer.innerHTML = '';

        for (const aa of results.amino_acid_sequence) {
            const span = document.createElement('span');
            span.className = 'amino-acid';
            span.textContent = aa;
            aaContainer.appendChild(span);
        }

        // Show results
        this.resultsContainer.classList.remove('hidden');

        // Store results for export
        this.currentResults = results;

        // Scroll to results
        this.resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    clear() {
        this.input.value = '';
        this.resultsContainer.classList.add('hidden');
        this.currentResults = null;
    }

    export() {
        if (!this.currentResults) return;

        const data = JSON.stringify(this.currentResults, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Export
window.SequenceAnalyzer = SequenceAnalyzer;
