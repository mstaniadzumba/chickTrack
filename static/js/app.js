document.addEventListener("DOMContentLoaded", () => {
    const expenseForm = document.getElementById("expenseForm");
    if (expenseForm) {
        expenseForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const payload = {
                expense_name: document.getElementById("expenseDesc").value,
                expense_amount: parseInt(document.getElementById("expenseAmount").value)
            };

            fetch("/api/add-expense", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(err => console.error("Add expense error:", err));
        });
    }

});
