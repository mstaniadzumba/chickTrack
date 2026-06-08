document.addEventListener("DOMContentLoaded", async () => {
    const tableBody = document.getElementById("historyTableBody");
    const emptyMsg = document.getElementById("emptyMsg");
    const batchSelect = document.getElementById("batchSelect");

    // Show every batch, plus an "All Batches" option (default).
    await batchManager.populateDropdownWithAll(batchSelect, 'All Batches');
    loadHistory(batchManager.getCurrentBatch());

    batchSelect.addEventListener('change', function() {
        const selectedBatchId = this.value;
        batchManager.setCurrentBatch(selectedBatchId);
        loadHistory(selectedBatchId);
    });

    // Friendly colours for each kind of action.
    const ACTION_CLASS = { added: 'text-success', edited: 'text-warning', deleted: 'text-danger' };

    function loadHistory(batchId = null) {
        const url = batchId ? `/api/history/${batchId}` : '/api/history';

        fetch(url)
        .then(res => {
            if (res.status === 401) { window.location.href = '/login'; return []; }
            return res.json();
        })
        .then(entries => {
            tableBody.innerHTML = '';
            if (!entries || entries.length === 0) {
                emptyMsg.classList.remove('d-none');
                return;
            }
            emptyMsg.classList.add('d-none');
            entries.forEach(addRow);
        })
        .catch(error => console.error('Error loading history:', error));
    }

    function addRow(entry) {
        const row = document.createElement("tr");

        const whenCell = document.createElement("td");
        whenCell.textContent = entry.created_at || '';

        const whoCell = document.createElement("td");
        whoCell.textContent = entry.user_name || 'Unknown';

        const recordCell = document.createElement("td");
        // e.g. "Order", "Expense", "Batch"
        recordCell.textContent = (entry.record_type || '').charAt(0).toUpperCase() + (entry.record_type || '').slice(1);

        const actionCell = document.createElement("td");
        actionCell.textContent = entry.action || '';
        actionCell.className = ACTION_CLASS[entry.action] || '';

        const detailsCell = document.createElement("td");
        detailsCell.textContent = entry.changes || '';

        row.appendChild(whenCell);
        row.appendChild(whoCell);
        row.appendChild(recordCell);
        row.appendChild(actionCell);
        row.appendChild(detailsCell);
        tableBody.appendChild(row);
    }
});
