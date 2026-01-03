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

        newRow.appendChild(descCell);
        newRow.appendChild(amountCell);
        newRow.appendChild(dateCell);
        newRow.appendChild(commentsCell);

        tableBody.appendChild(newRow);
    }

    if (expenseForm) {
        expenseForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const payload = {
                expense_name: document.getElementById("expenseDesc").value,
                expense_amount: parseInt(document.getElementById("expenseAmount").value),
                expense_date: document.getElementById("expenseDate").value,
                comments: document.getElementById("comments").value,
                batch_id: batchManager.getCurrentBatch()
            };

            fetch("/api/add-expense", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if (data.data) {
                    addExpenseToTable(data.data);
                    expenseForm.reset();
                }
            })
            .catch(err => console.error("Add expense error:", err));
        });
    }
});