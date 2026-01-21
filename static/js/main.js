/**
 * Physiological G-Code - Main Application
 */

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    const sequenceAnalyzer = new SequenceAnalyzer();
    const hexagramGrid = new HexagramGrid();

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to analyze
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const analyzer = document.querySelector('#analyzer');
            if (analyzer) {
                const input = document.getElementById('sequence-input');
                if (input.value.trim()) {
                    sequenceAnalyzer.analyze();
                }
            }
        }
    });

    console.log('Physiological G-Code initialized');
});
