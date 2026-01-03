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

        const createdByCell = document.createElement("td")
        createdByCell.textContent = orderData.created_by || 'Unknown'

        const updatedByCell = document.createElement("td")
        updatedByCell.textContent = orderData.updated_by || '-'

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
        newRow.appendChild(createdByCell)
        newRow.appendChild(updatedByCell)
        newRow.appendChild(actionsCell)

        tableBody.appendChild(newRow)
    }

    orderForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const submitBtn = e.target.querySelector('button[type="submit"]');
        const isUpdate = submitBtn.dataset.mode === 'update';
        const orderId = submitBtn.dataset.orderId;

        const payload = {
            customer_name: document.getElementById("customerName").value,
            customer_location: document.getElementById("customerLocation").value,
            customer_cell: document.getElementById("customerCell").value,
            chickens_ordered: parseInt(document.getElementById("chickensOrdered").value),
            amount_paid: parseInt(document.getElementById("amountPaid").value),
            batch_id: batchManager.getCurrentBatch(),
            created_by: JSON.parse(localStorage.getItem('currentUser') || '{}').name || 'Unknown'
        };

        const url = isUpdate ? `/api/update-order/${orderId}` : "/api/add-order";
        const method = isUpdate ? "PUT" : "POST";

        fetch(url, {
            method: method,
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            if (data.data) {
                if (isUpdate) {
                    // Reload the orders to show updated data
                    loadOrders(batchManager.getCurrentBatch());
                    // Reset form
                    submitBtn.textContent = 'Add Order';
                    delete submitBtn.dataset.mode;
                    delete submitBtn.dataset.orderId;
                } else {
                    addOrderToTable(data.data);
                }
                orderForm.reset();
            }
        })
        .catch(error => {
            console.error('Error with order:', error);
            alert('Error with order');
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