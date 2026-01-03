// Global batch management
class BatchManager {
    constructor() {
        this.currentBatchId = localStorage.getItem('selectedBatchId');
        this.batches = [];
    }

    async loadBatches() {
        try {
            const response = await fetch('/api/batches');
            this.batches = await response.json();
            return this.batches;
        } catch (error) {
            console.error('Error loading batches:', error);
            return [];
        }
    }

    setCurrentBatch(batchId) {
        this.currentBatchId = batchId;
        if (batchId) {
            localStorage.setItem('selectedBatchId', batchId);
        } else {
            localStorage.removeItem('selectedBatchId');
        }
        
        // Trigger custom event for other pages to listen
        window.dispatchEvent(new CustomEvent('batchChanged', { 
            detail: { batchId: batchId } 
        }));
    }

    getCurrentBatch() {
        return this.currentBatchId;
    }

    async populateDropdown(selectElement) {
        const batches = await this.loadBatches();
        // Clear all existing options first
        selectElement.innerHTML = '';
        
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select a batch';
        selectElement.appendChild(defaultOption);
        
        batches.forEach(batch => {
            const option = document.createElement('option');
            option.value = batch.id;
            option.textContent = batch.month;
            if (batch.id == this.currentBatchId) {
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    }

    async populateDropdownWithAll(selectElement, allText) {
        const batches = await this.loadBatches();
        selectElement.innerHTML = `<option value="">${allText}</option>`;
        
        batches.forEach(batch => {
            const option = document.createElement('option');
            option.value = batch.id;
            option.textContent = batch.month;
            if (batch.id == this.currentBatchId) {
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    }
}

// Global instance
window.batchManager = new BatchManager();