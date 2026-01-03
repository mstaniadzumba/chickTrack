document.addEventListener('DOMContentLoaded', () => {
    const orderForm = document.getElementById("orderForm")
    const tableBody = document.getElementById("ordersTableBody")
    const batchSelect = document.getElementById("batchSelect")

    // Initialize batch dropdown and load orders
    batchManager.populateDropdownWithAll(batchSelect, 'All Orders');
    loadOrders(batchManager.getCurrentBatch());

    // Handle batch selection change
    batchSelect.addEventListener('change', function() {
        const selectedBatchId = this.value;
        batchManager.setCurrentBatch(selectedBatchId);
        loadOrders(selectedBatchId);
    });

    // Listen for batch changes from other pages
    window.addEventListener('batchChanged', function(event) {
        batchSelect.value = event.detail.batchId || '';
        loadOrders(event.detail.batchId);
    });

    function loadOrders(batchId = null) {
        const url = batchId ? `/api/orders?batch_id=${batchId}` : '/api/orders';
        
        fetch(url)
        .then(res => res.json())
        .then(orders => {
            tableBody.innerHTML = '';
            orders.forEach(order => {
                addOrderToTable(order);
            });
        })
        .catch(error => {
            console.error('Error loading orders:', error);
        });
    }

    function addOrderToTable(orderData) {
        const newRow = document.createElement("tr")
        
        const nameCell = document.createElement("td")
        nameCell.textContent = orderData.customer_name

        const locationCell = document.createElement("td")
        locationCell.textContent = orderData.customer_location

        const numberCell = document.createElement("td")
        numberCell.textContent = orderData.customer_cell

        const chickensCell = document.createElement("td")
        chickensCell.textContent = orderData.no_of_chickens 

        const totalAmountCell = document.createElement("td")
        totalAmountCell.textContent = orderData.total_amount

        const amountPaidCell = document.createElement("td")
        amountPaidCell.textContent = orderData.amount_paid

        const outstandingCell = document.createElement("td")
        outstandingCell.textContent = orderData.outstanding_amount

        const actionsCell = document.createElement("td")
        const updateBtn = document.createElement("button")
        updateBtn.className = "btn btn-sm btn-warning"
        updateBtn.textContent = "Update"
        updateBtn.onclick = () => updateOrder(orderData)
        actionsCell.appendChild(updateBtn)

        newRow.appendChild(nameCell)
        newRow.appendChild(locationCell)
        newRow.appendChild(numberCell)
        newRow.appendChild(chickensCell)
        newRow.appendChild(totalAmountCell)
        newRow.appendChild(amountPaidCell)
        newRow.appendChild(outstandingCell)
        newRow.appendChild(actionsCell)

        tableBody.appendChild(newRow)
    }

    orderForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const payload = {
            customer_name: document.getElementById("customerName").value,
            customer_location: document.getElementById("customerLocation").value,
            customer_cell: document.getElementById("customerCell").value,
            chickens_ordered: parseInt(document.getElementById("chickensOrdered").value),
            amount_paid: parseInt(document.getElementById("amountPaid").value),
            batch_id: batchManager.getCurrentBatch()
        };

        fetch("/api/add-order", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            if (data.data) {
                addOrderToTable(data.data);
                orderForm.reset();
            }
        })
        .catch(error => {
            console.error('Error adding order:', error);
            alert('Error adding order');
        });
    });

    function updateOrder(orderData) {
        // Populate form with existing data
        document.getElementById("customerName").value = orderData.customer_name;
        document.getElementById("customerLocation").value = orderData.customer_location;
        document.getElementById("customerCell").value = orderData.customer_cell;
        document.getElementById("chickensOrdered").value = orderData.no_of_chickens;
        document.getElementById("amountPaid").value = orderData.amount_paid;
        
        // Change form to update mode
        const submitBtn = document.querySelector('#orderForm button[type="submit"]');
        submitBtn.textContent = 'Update Order';
        submitBtn.dataset.mode = 'update';
        submitBtn.dataset.orderId = orderData.id;
    }
});