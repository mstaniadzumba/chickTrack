document.addEventListener("DOMContentLoaded", () => {
    const expenseForm = document.getElementById("expenseForm");
    const tableBody =  document.getElementById("expensesTableBody")
    if (expenseForm) {
        expenseForm.addEventListener("submit", function (e) {
            e.preventDefault();//lets you submit the data without losing formstate

            const payload = {
                expense_name: document.getElementById("expenseDesc").value,
                expense_amount: parseInt(document.getElementById("expenseAmount").value),
                expense_date: document.getElementById("expenseDate").value,
                comments:document.getElementById("comments").value
            };

            fetch("/api/add-expense", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                
                 if (tableBody && data.data) {
                    const newRow = document.createElement("tr");

                    const descCell = document.createElement("td");
                    descCell.textContent = data.data.expense_name;

                    const amountCell = document.createElement("td");
                    amountCell.textContent = data.data.expense_amount;

                    const dateCell = document.createElement("td");
                    dateCell.textContent = data.data.expense_date;

                    const commentsCell = document.createElement("td");
                    commentsCell.textContent = data.data.comments;

                    newRow.appendChild(descCell);
                    newRow.appendChild(amountCell);
                    newRow.appendChild(dateCell);
                    newRow.appendChild(commentsCell)

                    tableBody.appendChild(newRow);
                    expenseForm.reset();
                }

            })
            .catch(err => console.error("Add expense error:", err));
        });
    }


    //document.getElementById('expense-table')

});
