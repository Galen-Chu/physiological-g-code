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

    // Analysis endpoints
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

    // Reference data
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

    // Mappings
    async getActiveMapping() {
        return this.get('/mappings/active/');
    }

    async getMappingSchemes() {
        return this.get('/analysis/mapping_schemes/');
    }
}

// Export singleton
const api = new ApiClient();
