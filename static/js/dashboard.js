document.addEventListener('DOMContentLoaded', function() {
    const batchSelect = document.getElementById('batchSelect');
    
    // Initialize batch dropdown
    batchManager.populateDropdown(batchSelect);
    
    // Load dashboard data for current batch
    if (batchManager.getCurrentBatch()) {
        loadDashboardData(batchManager.getCurrentBatch());
    }

    // Handle batch selection change
    batchSelect.addEventListener('change', function() {
        const selectedBatchId = this.value;
        batchManager.setCurrentBatch(selectedBatchId);
        if (selectedBatchId) {
            loadDashboardData(selectedBatchId);
        }
    });

    // Handle batch form submission
    document.getElementById('batchForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            start_date: document.getElementById('batchDate').value,
            chickens_bought: parseInt(document.getElementById('chickBought').value),
            dead_chicken: parseInt(document.getElementById('chickDead').value)
        };
        
        try {
            const response = await fetch('/api/add-batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            alert('Batch added successfully!');
            
            // Reload batches and select the new one
            await batchManager.populateDropdown(batchSelect);
            batchManager.setCurrentBatch(result.batch_id);
            batchSelect.value = result.batch_id;
            loadDashboardData(result.batch_id);
            
            this.reset();
        } catch (error) {
            console.error('Error adding batch:', error);
            alert('Error adding batch');
        }
    });

    // Handle update batch button
    document.getElementById('updateBatchBtn').addEventListener('click', function() {
        const currentBatchId = batchManager.getCurrentBatch();
        if (!currentBatchId) {
            alert('Please select a batch first');
            return;
        }
        
        // Load current batch data into form
        loadBatchForUpdate(currentBatchId);
    });

    async function loadBatchForUpdate(batchId) {
        try {
            const response = await fetch(`/api/dashboard/${batchId}`);
            const data = await response.json();
            
            // Populate form with existing data
            document.getElementById('batchDate').value = data.batch.start_date;
            document.getElementById('chickBought').value = data.batch.chickens_bought;
            document.getElementById('chickDead').value = data.batch.dead_chicken;
            
            // Change form to update mode
            const submitBtn = document.querySelector('#batchForm button[type="submit"]');
            submitBtn.textContent = 'Update Batch';
            submitBtn.dataset.mode = 'update';
            submitBtn.dataset.batchId = batchId;
            
        } catch (error) {
            console.error('Error loading batch for update:', error);
        }
    }
});

async function loadDashboardData(batchId) {
    try {
        const response = await fetch(`/api/dashboard/${batchId}`);
        const data = await response.json();
        
        document.getElementById('boughtDisplay').textContent = data.batch.chickens_bought;
        document.getElementById('deadDisplay').textContent = data.batch.dead_chicken;
        document.getElementById('liveDisplay').textContent = data.batch.live_chicken;
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}


