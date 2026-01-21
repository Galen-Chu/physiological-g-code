/**
 * Hexagram Renderer
 * Renders hexagram symbols and their lines
 */

class HexagramRenderer {
    /**
     * Get Unicode character for hexagram
     * @param {number} hexagramNumber - Hexagram number (1-64)
     * @returns {string} Unicode character
     */
    static getUnicode(hexagramNumber) {
        const offset = 0x4DC0; // Unicode hexagram range starts at U+4DC0
        return String.fromCodePoint(offset + hexagramNumber - 1);
    }

    /**
     * Render hexagram lines from binary representation
     * @param {string} binary - Binary string (e.g., "111111")
     * @returns {HTMLElement} Element with hexagram lines
     */
    static renderLines(binary) {
        const container = document.createElement('div');
        container.className = 'hexagram-lines';

        // Lines are drawn bottom to top
        for (let i = binary.length - 1; i >= 0; i--) {
            const line = document.createElement('div');
            line.className = binary[i] === '1' ? 'line-yang' : 'line-yin';
            container.appendChild(line);
        }

        return container;
    }

    /**
     * Create a hexagram card element
     * @param {Object} hexagram - Hexagram data
     * @returns {HTMLElement} Card element
     */
    static createCard(hexagram) {
        const card = document.createElement('div');
        card.className = 'hexagram-card';
        card.dataset.number = hexagram.number;

        card.innerHTML = `
            <div class="hexagram-card-unicode">${this.getUnicode(hexagram.number)}</div>
            <div class="hexagram-card-number">#${hexagram.number}</div>
            <div class="hexagram-card-name">${hexagram.name_english}</div>
        `;

        return card;
    }

    /**
     * Create a hexagram symbol element
     * @param {number} number - Hexagram number
     * @returns {HTMLElement} Symbol element
     */
    static createSymbol(number) {
        const symbol = document.createElement('div');
        symbol.className = 'hexagram-symbol';
        symbol.dataset.number = number;

        symbol.innerHTML = `
            <div class="hexagram-unicode">${this.getUnicode(number)}</div>
            <div class="hexagram-number">${number}</div>
        `;

        return symbol;
    }

    /**
     * Parse hexagram from binary representation
     * @param {string} binary - Binary string
     * @returns {number|null} Hexagram number or null
     */
    static binaryToNumber(binary) {
        const value = parseInt(binary, 2);
        if (value >= 0 && value <= 63) {
            return value + 1; // Convert to 1-64 range
        }
        return null;
    }

    /**
     * Convert codon to hexagram number using binary mapping
     * @param {string} codon - Three-nucleotide codon
     * @param {Object} scheme - Binary mapping scheme
     * @returns {number} Hexagram number
     */
    static codonToHexagram(codon, scheme = 'scheme_1') {
        const schemes = {
            scheme_1: { 'A': '0', 'T': '0', 'G': '1', 'C': '1', 'U': '0' },
            scheme_2: { 'A': '0', 'T': '1', 'G': '0', 'C': '1', 'U': '1' },
            scheme_3: { 'A': '0', 'T': '0', 'G': '1', 'C': '1', 'U': '0' },
        };

        const mapping = schemes[scheme] || schemes.scheme_1;
        let binary = '';

        for (const base of codon.toUpperCase()) {
            binary += mapping[base] || '0';
        }

        // Reverse for hexagram ordering (bottom to top)
        const reversed = binary.split('').reverse().join('');
        return this.binaryToNumber(reversed) || 1;
    }
}

// Export
window.HexagramRenderer = HexagramRenderer;
