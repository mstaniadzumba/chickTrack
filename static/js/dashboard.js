document.addEventListener('DOMContentLoaded', async function() {
    const batchSelect = document.getElementById('batchSelect');
    const noBatchMsg = document.getElementById('noBatchMsg');

    // Initialize batch dropdown
    await batchManager.populateDropdown(batchSelect);

    // If nothing is selected yet (or the saved batch is gone), default to the most
    // recent batch so the dashboard isn't blank.
    let currentBatch = batchManager.getCurrentBatch();
    const exists = batchManager.batches.some(b => String(b.id) === String(currentBatch));
    if ((!currentBatch || !exists) && batchManager.hasBatches()) {
        currentBatch = batchManager.batches[0].id;
        batchManager.setCurrentBatch(currentBatch);
        batchSelect.value = currentBatch;
    }

    if (!batchManager.hasBatches()) {
        if (noBatchMsg) noBatchMsg.classList.remove('d-none');
    } else if (currentBatch) {
        loadDashboardData(currentBatch);
    }

    // Handle batch selection change
    batchSelect.addEventListener('change', function() {
        const selectedBatchId = this.value;
        batchManager.setCurrentBatch(selectedBatchId);
        if (selectedBatchId) {
            loadDashboardData(selectedBatchId);
        } else {
            resetDashboardCards();
        }
    });

    // The Add/Update Batch form only exists for the admin.
    const batchForm = document.getElementById('batchForm');
    if (batchForm) {
        batchForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const isUpdate = submitBtn.dataset.mode === 'update';
            const batchId = submitBtn.dataset.batchId;

            const formData = {
                start_date: document.getElementById('batchDate').value,
                chickens_bought: parseInt(document.getElementById('chickBought').value),
                dead_chicken: parseInt(document.getElementById('chickDead').value)
            };

            const url = isUpdate ? `/api/update-batch/${batchId}` : '/api/add-batch';
            const method = isUpdate ? 'PUT' : 'POST';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                if (!response.ok) {
                    alert(result.message || 'Could not save batch');
                    return;
                }

                if (isUpdate) {
                    alert('Batch updated successfully!');
                    submitBtn.textContent = 'Add batch';
                    delete submitBtn.dataset.mode;
                    delete submitBtn.dataset.batchId;
                } else {
                    alert('Batch added successfully!');
                    batchManager.setCurrentBatch(result.batch_id);
                }

                // Reload batches and update dropdown
                await batchManager.populateDropdown(batchSelect);
                const activeId = isUpdate ? batchId : result.batch_id;
                batchSelect.value = activeId;
                if (noBatchMsg) noBatchMsg.classList.add('d-none');
                loadDashboardData(activeId);

                this.reset();
            } catch (error) {
                console.error('Error with batch:', error);
                alert('Error with batch');
            }
        });
    }

    const updateBatchBtn = document.getElementById('updateBatchBtn');
    if (updateBatchBtn) {
        updateBatchBtn.addEventListener('click', function() {
            const currentBatchId = batchManager.getCurrentBatch();
            if (!currentBatchId) {
                alert('Please select a batch first');
                return;
            }
            loadBatchForUpdate(currentBatchId);
        });
    }

    async function loadBatchForUpdate(batchId) {
        try {
            const response = await fetch(`/api/dashboard/${batchId}`);
            const data = await response.json();

            document.getElementById('batchDate').value = data.batch.start_date;
            document.getElementById('chickBought').value = data.batch.chickens_bought;
            document.getElementById('chickDead').value = data.batch.dead_chicken;

            const submitBtn = document.querySelector('#batchForm button[type="submit"]');
            submitBtn.textContent = 'Update Batch';
            submitBtn.dataset.mode = 'update';
            submitBtn.dataset.batchId = batchId;
        } catch (error) {
            console.error('Error loading batch for update:', error);
        }
    }
});

function resetDashboardCards() {
    document.getElementById('boughtDisplay').textContent = 0;
    document.getElementById('deadDisplay').textContent = 0;
    document.getElementById('soldDisplay').textContent = 0;
    document.getElementById('liveDisplay').textContent = 0;
}

async function loadDashboardData(batchId) {
    try {
        const response = await fetch(`/api/dashboard/${batchId}`);
        if (!response.ok) return;
        const data = await response.json();

        document.getElementById('boughtDisplay').textContent = data.bought;
        document.getElementById('deadDisplay').textContent = data.dead;
        document.getElementById('soldDisplay').textContent = data.sold;
        document.getElementById('liveDisplay').textContent = data.live;
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}
