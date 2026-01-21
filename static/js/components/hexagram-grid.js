/**
 * Hexagram Grid Component
 * Displays all 64 hexagrams
 */

class HexagramGrid {
    constructor(containerId = 'hexagram-grid') {
        this.container = document.getElementById(containerId);
        this.hexagrams = [];
        this.load();
    }

    async load() {
        try {
            const data = await api.getHexagrams();
            this.hexagrams = data;
            this.render();
        } catch (error) {
            console.error('Error loading hexagrams:', error);
            this.showError();
        }
    }

    render() {
        this.container.innerHTML = '';

        this.hexagrams.forEach(hexagram => {
            const card = HexagramRenderer.createCard(hexagram);

            // Add click handler
            card.addEventListener('click', () => {
                this.showDetails(hexagram);
            });

            this.container.appendChild(card);
        });
    }

    showDetails(hexagram) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'hexagram-modal';
        modal.innerHTML = `
            <div class="hexagram-modal-content">
                <button class="hexagram-modal-close">&times;</button>
                <div class="hexagram-modal-header">
                    <div class="hexagram-modal-unicode">${HexagramRenderer.getUnicode(hexagram.number)}</div>
                    <div class="hexagram-modal-info">
                        <h2>Hexagram ${hexagram.number}</h2>
                        <h3>${hexagram.name_chinese} (${hexagram.name_pinyin})</h3>
                        <p>${hexagram.name_english}</p>
                    </div>
                </div>
                <div class="hexagram-modal-body">
                    <div class="hexagram-modal-section">
                        <h4>Binary Representation</h4>
                        <p class="binary-display">${hexagram.binary}</p>
                    </div>
                    <div class="hexagram-modal-section">
                        <h4>Trigrams</h4>
                        <p>Lower: ${hexagram.lower_trigram_name} (${hexagram.lower_trigram})</p>
                        <p>Upper: ${hexagram.upper_trigram_name} (${hexagram.upper_trigram})</p>
                    </div>
                    <div class="hexagram-modal-section">
                        <h4>Description</h4>
                        <p>${hexagram.description}</p>
                    </div>
                    <div class="hexagram-modal-section">
                        <h4>Keywords</h4>
                        <div class="keywords">
                            ${hexagram.keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add styles if not present
        this.addModalStyles();

        // Add close handler
        const closeBtn = modal.querySelector('.hexagram-modal-close');
        closeBtn.addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

        document.body.appendChild(modal);
    }

    addModalStyles() {
        if (document.getElementById('hexagram-modal-styles')) return;

        const style = document.createElement('style');
        style.id = 'hexagram-modal-styles';
        style.textContent = `
            .hexagram-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }

            .hexagram-modal-content {
                background: var(--bg-tertiary);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                max-width: 600px;
                max-height: 80vh;
                overflow-y: auto;
                position: relative;
            }

            .hexagram-modal-close {
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: none;
                border: none;
                color: var(--text-secondary);
                font-size: 2rem;
                cursor: pointer;
                z-index: 10;
            }

            .hexagram-modal-close:hover {
                color: var(--accent-green);
            }

            .hexagram-modal-header {
                padding: 2rem;
                text-align: center;
                border-bottom: 1px solid var(--border-color);
            }

            .hexagram-modal-unicode {
                font-size: 4rem;
                margin-bottom: 1rem;
            }

            .hexagram-modal-info h2 {
                color: var(--accent-green);
                margin-bottom: 0.5rem;
            }

            .hexagram-modal-info h3 {
                font-size: 1.2rem;
                margin-bottom: 0.25rem;
            }

            .hexagram-modal-info p {
                color: var(--text-secondary);
            }

            .hexagram-modal-body {
                padding: 2rem;
            }

            .hexagram-modal-section {
                margin-bottom: 1.5rem;
            }

            .hexagram-modal-section h4 {
                color: var(--accent-green);
                margin-bottom: 0.5rem;
            }

            .binary-display {
                font-family: var(--font-mono);
                font-size: 1.2rem;
                letter-spacing: 0.25rem;
            }

            .keywords {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .keyword-tag {
                background: var(--bg-primary);
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.875rem;
                border: 1px solid var(--border-color);
            }
        `;

        document.head.appendChild(style);
    }

    showError() {
        this.container.innerHTML = `
            <div class="error-message">
                Failed to load hexagrams. Please refresh the page.
            </div>
        `;
    }
}

// Export
window.HexagramGrid = HexagramGrid;
