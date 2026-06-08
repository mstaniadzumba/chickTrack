// Global batch management
class BatchManager {
    constructor() {
        this.currentBatchId = localStorage.getItem('selectedBatchId');
        this.batches = [];
    }

    async loadBatches() {
        try {
            const response = await fetch('/api/batches');
            if (response.status === 401) {
                window.location.href = '/login';
                return [];
            }
            this.batches = await response.json();
            return this.batches;
        } catch (error) {
            console.error('Error loading batches:', error);
            return [];
        }
    }

    hasBatches() {
        return this.batches.length > 0;
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

// Is the logged-in user an admin?
window.isAdmin = function () {
    return !!(window.CURRENT_USER && window.CURRENT_USER.is_admin);
};

// Wire up the "Log out" button (present on every page) once the DOM is ready.
document.addEventListener('DOMContentLoaded', function () {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function () {
            try {
                await fetch('/api/logout', { method: 'POST' });
            } catch (e) {
                // ignore — we redirect either way
            }
            localStorage.removeItem('currentUser');
            localStorage.removeItem('selectedBatchId');
            window.location.href = '/login';
        });
    }
});
