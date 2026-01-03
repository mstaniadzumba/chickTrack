document.addEventListener("DOMContentLoaded", () => {
    const expenseForm = document.getElementById("expenseForm");
    const tableBody = document.getElementById("expensesTableBody");
    const batchSelect = document.getElementById("batchSelect");

    // Initialize batch dropdown and load expenses
    batchManager.populateDropdownWithAll(batchSelect, 'All Expenses');
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

    function loadExpenses(batchId = null) {
        const url = batchId ? `/api/expenses?batch_id=${batchId}` : '/api/expenses';
        
        fetch(url)
        .then(res => res.json())
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

        const actionsCell = document.createElement("td");
        const updateBtn = document.createElement("button");
        updateBtn.className = "btn btn-sm btn-warning";
        updateBtn.textContent = "Update";
        updateBtn.onclick = () => updateExpense(expenseData);
        actionsCell.appendChild(updateBtn);

        newRow.appendChild(descCell);
        newRow.appendChild(amountCell);
        newRow.appendChild(dateCell);
        newRow.appendChild(commentsCell);
        newRow.appendChild(createdByCell);
        newRow.appendChild(actionsCell);

        tableBody.appendChild(newRow);
    }

    if (expenseForm) {
        expenseForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const isUpdate = submitBtn.dataset.mode === 'update';
            const expenseId = submitBtn.dataset.expenseId;

            const payload = {
                expense_name: document.getElementById("expenseDesc").value,
                expense_amount: parseInt(document.getElementById("expenseAmount").value),
                expense_date: document.getElementById("expenseDate").value,
                comments: document.getElementById("comments").value,
                batch_id: batchManager.getCurrentBatch(),
                created_by: JSON.parse(localStorage.getItem('currentUser') || '{}').name || 'Unknown'
            };

            const url = isUpdate ? `/api/update-expense/${expenseId}` : "/api/add-expense";
            const method = isUpdate ? "PUT" : "POST";

            fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => {
                console.log('Response status:', res.status);
                return res.json();
            })
            .then(data => {
                console.log('Response data:', data);
                alert(data.message);
                if (data.data) {
                    if (isUpdate) {
                        console.log('Reloading expenses after update');
                        // Reload expenses to show updated data
                        loadExpenses(batchManager.getCurrentBatch());
                        // Reset form
                        submitBtn.textContent = 'Add Expense';
                        delete submitBtn.dataset.mode;
                        delete submitBtn.dataset.expenseId;
                        expenseForm.reset();
                    } else {
                        addExpenseToTable(data.data);
                        expenseForm.reset();
                    }
                }
            })
            .catch(err => {
                console.error("Expense error:", err);
                alert('Error updating expense');
            });
        });
    }

    function updateExpense(expenseData) {
        // Populate form with existing data
        document.getElementById("expenseDesc").value = expenseData.expense_name;
        document.getElementById("expenseAmount").value = expenseData.expense_amount;
        document.getElementById("expenseDate").value = expenseData.expense_date;
        document.getElementById("comments").value = expenseData.comments || '';
        
        // Change form to update mode
        const submitBtn = document.querySelector('#expenseForm button[type="submit"]');
        submitBtn.textContent = 'Update Expense';
        submitBtn.dataset.mode = 'update';
        submitBtn.dataset.expenseId = expenseData.id;
    }
});