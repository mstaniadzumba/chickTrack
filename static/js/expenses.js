document.addEventListener("DOMContentLoaded", async () => {
    const expenseForm = document.getElementById("expenseForm");
    const expenseFormCard = document.getElementById("expenseFormCard");
    const noBatchMsg = document.getElementById("noBatchMsg");
    const tableBody = document.getElementById("expensesTableBody");
    const batchSelect = document.getElementById("batchSelect");

    // Initialize batch dropdown and load expenses
    await batchManager.populateDropdownWithAll(batchSelect, 'All Expenses');
    updateBatchGuard();
    loadExpenses(batchManager.getCurrentBatch());

    // Handle batch selection change
    batchSelect.addEventListener('change', function() {
        const selectedBatchId = this.value;
        batchManager.setCurrentBatch(selectedBatchId);
        loadExpenses(selectedBatchId);
    });

    // Listen for batch changes from other pages
    window.addEventListener('batchChanged', function(event) {
        batchSelect.value = event.detail.batchId || '';
        loadExpenses(event.detail.batchId);
    });

    function updateBatchGuard() {
        if (!batchManager.hasBatches()) {
            if (noBatchMsg) noBatchMsg.classList.remove('d-none');
            if (expenseFormCard) expenseFormCard.classList.add('d-none');
        } else {
            if (noBatchMsg) noBatchMsg.classList.add('d-none');
            if (expenseFormCard) expenseFormCard.classList.remove('d-none');
        }
    }

    function loadExpenses(batchId = null) {
        const url = batchId ? `/api/expenses?batch_id=${batchId}` : '/api/expenses';

        fetch(url)
        .then(res => {
            if (res.status === 401) { window.location.href = '/login'; return []; }
            return res.json();
        })
        .then(expenses => {
            tableBody.innerHTML = '';
            expenses.forEach(expense => {
                addExpenseToTable(expense);
            });
        })
        .catch(error => {
            console.error('Error loading expenses:', error);
        });
    }

    function addExpenseToTable(expenseData) {
        const newRow = document.createElement("tr");

        const descCell = document.createElement("td");
        descCell.textContent = expenseData.expense_name;

        const amountCell = document.createElement("td");
        amountCell.textContent = expenseData.expense_amount;

        const dateCell = document.createElement("td");
        dateCell.textContent = expenseData.expense_date;

        const commentsCell = document.createElement("td");
        commentsCell.textContent = expenseData.comments || '';

        const createdByCell = document.createElement("td");
        createdByCell.textContent = expenseData.created_by || 'Unknown';

        const updatedByCell = document.createElement("td");
        updatedByCell.textContent = expenseData.updated_by || '-';

        const actionsCell = document.createElement("td");

        if (expenseData.is_deleted) {
            // Crossed-out record: show it, but no editing. Explain who/why on hover.
            newRow.classList.add("text-muted");
            newRow.style.textDecoration = "line-through";
            newRow.title = `Deleted by ${expenseData.deleted_by || 'someone'}`
                + (expenseData.deleted_reason ? `: ${expenseData.deleted_reason}` : '');
            actionsCell.textContent = "Deleted";
        } else {
            const updateBtn = document.createElement("button");
            updateBtn.className = "btn btn-sm btn-warning";
            updateBtn.textContent = "Update";
            updateBtn.onclick = () => updateExpense(expenseData);
            actionsCell.appendChild(updateBtn);

            // Only the admin can delete, and a reason is always required.
            if (window.isAdmin && window.isAdmin()) {
                const deleteBtn = document.createElement("button");
                deleteBtn.className = "btn btn-sm btn-danger ms-1";
                deleteBtn.textContent = "Delete";
                deleteBtn.onclick = () => deleteExpense(expenseData);
                actionsCell.appendChild(deleteBtn);
            }
        }

        newRow.appendChild(descCell);
        newRow.appendChild(amountCell);
        newRow.appendChild(dateCell);
        newRow.appendChild(commentsCell);
        newRow.appendChild(createdByCell);
        newRow.appendChild(updatedByCell);
        newRow.appendChild(actionsCell);

        tableBody.appendChild(newRow);
    }

    if (expenseForm) {
        expenseForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const isUpdate = submitBtn.dataset.mode === 'update';
            const expenseId = submitBtn.dataset.expenseId;

            const batchId = batchManager.getCurrentBatch();
            if (!isUpdate && !batchId) {
                alert('Please select a batch first (top of the page) before adding an expense.');
                return;
            }

            const payload = {
                expense_name: document.getElementById("expenseDesc").value,
                expense_amount: parseInt(document.getElementById("expenseAmount").value),
                expense_date: document.getElementById("expenseDate").value,
                comments: document.getElementById("comments").value,
                batch_id: batchId
            };

            const url = isUpdate ? `/api/update-expense/${expenseId}` : "/api/add-expense";
            const method = isUpdate ? "PUT" : "POST";

            fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json().then(data => ({ ok: res.ok, data })))
            .then(({ ok, data }) => {
                alert(data.message);
                if (!ok) return;

                loadExpenses(batchManager.getCurrentBatch());
                if (isUpdate) {
                    submitBtn.textContent = 'Add Expense';
                    delete submitBtn.dataset.mode;
                    delete submitBtn.dataset.expenseId;
                }
                expenseForm.reset();
            })
            .catch(err => {
                console.error("Expense error:", err);
                alert('Error saving expense');
            });
        });
    }

    function updateExpense(expenseData) {
        document.getElementById("expenseDesc").value = expenseData.expense_name;
        document.getElementById("expenseAmount").value = expenseData.expense_amount;
        document.getElementById("expenseDate").value = expenseData.expense_date;
        document.getElementById("comments").value = expenseData.comments || '';

        const submitBtn = document.querySelector('#expenseForm button[type="submit"]');
        submitBtn.textContent = 'Update Expense';
        submitBtn.dataset.mode = 'update';
        submitBtn.dataset.expenseId = expenseData.id;
    }

    function deleteExpense(expenseData) {
        if (!confirm(`Are you sure you want to delete the expense "${expenseData.expense_name}"?\n\nThe record will be crossed out and will no longer be counted.`)) {
            return;
        }
        const reason = prompt(`Why are you deleting the expense "${expenseData.expense_name}"? (required)`);
        if (reason === null) return;            // cancelled
        if (!reason.trim()) {
            alert('A reason is required to delete.');
            return;
        }

        fetch(`/api/delete-expense/${expenseData.id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason.trim() })
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            alert(data.message);
            if (ok) loadExpenses(batchManager.getCurrentBatch());
        })
        .catch(error => {
            console.error('Error deleting expense:', error);
            alert('Error deleting expense');
        });
    }
});
