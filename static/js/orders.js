document.addEventListener('DOMContentLoaded', () =>{

    const orderForm = document.getElementById("orderForm")
    const tableBody = document.getElementById("ordersTableBody")

    orderForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const payload = {
            customer_name: document.getElementById("customerName").value,
            customer_location: document.getElementById("customerLocation").value,
            customer_cell: document.getElementById("customerCell").value,
            chickens_ordered: parseInt(document.getElementById("chickensOrdered").value),
            amount_paid: parseInt(document.getElementById("amountPaid").value)
        };

        fetch("/api/add-order",{
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);

            if (tableBody && data.data) {

                const newRow = document.createElement("tr")
            
                const nameCell = document.createElement("td")
                nameCell.textContent = data.data.customer_name

                const locationCell =  document.createElement("td")
                locationCell.textContent = data.data.customer_location

                const numberCell = document.createElement("td")
                numberCell.textContent = data.data.customer_cell

                const chickensCell = document.createElement("td")
                chickensCell.textContent= data.data.no_of_chickens 

                const totalAmountCell = document.createElement("td")
                totalAmountCell.textContent = data.data.total_amount

                const amountPaidCell = document.createElement("td")
                amountPaidCell.textContent = data.data.amount_paid

                const outstandingCell = document.createElement("td")
                outstandingCell.textContent = data.data.outstanding_amount


                newRow.appendChild(nameCell),
                newRow.appendChild(locationCell)
                newRow.appendChild(numberCell)
                newRow.appendChild(chickensCell)
                newRow.appendChild(totalAmountCell)
                newRow.appendChild(amountPaidCell)
                newRow.appendChild(outstandingCell 

                )

                tableBody.appendChild(newRow)
                orderForm.reset()
           
            }
        })

    })



});