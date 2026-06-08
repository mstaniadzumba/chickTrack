document.addEventListener('DOMContentLoaded', async () => {
    const orderForm = document.getElementById("orderForm")
    const orderFormCard = document.getElementById("orderFormCard")
    const noBatchMsg = document.getElementById("noBatchMsg")
    const tableBody = document.getElementById("ordersTableBody")
    const batchSelect = document.getElementById("batchSelect")

    // Initialize batch dropdown and load orders
    await batchManager.populateDropdownWithAll(batchSelect, 'All Orders');
    updateBatchGuard();
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

    function updateBatchGuard() {
        // No batches at all -> can't add orders.
        if (!batchManager.hasBatches()) {
            if (noBatchMsg) noBatchMsg.classList.remove('d-none');
            if (orderFormCard) orderFormCard.classList.add('d-none');
        } else {
            if (noBatchMsg) noBatchMsg.classList.add('d-none');
            if (orderFormCard) orderFormCard.classList.remove('d-none');
        }
    }

    function loadOrders(batchId = null) {
        const url = batchId ? `/api/orders?batch_id=${batchId}` : '/api/orders';

        fetch(url)
        .then(res => {
            if (res.status === 401) { window.location.href = '/login'; return []; }
            return res.json();
        })
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

        if (orderData.is_deleted) {
            // Crossed-out record: show it, but no editing. Explain who/why on hover.
            newRow.classList.add("text-muted")
            newRow.style.textDecoration = "line-through"
            newRow.title = `Deleted by ${orderData.deleted_by || 'someone'}`
                + (orderData.deleted_reason ? `: ${orderData.deleted_reason}` : '')
            actionsCell.textContent = "Deleted"
        } else {
            const updateBtn = document.createElement("button")
            updateBtn.className = "btn btn-sm btn-warning"
            updateBtn.textContent = "Update"
            updateBtn.onclick = () => updateOrder(orderData)
            actionsCell.appendChild(updateBtn)

            // Only the admin can delete, and a reason is always required.
            if (window.isAdmin && window.isAdmin()) {
                const deleteBtn = document.createElement("button")
                deleteBtn.className = "btn btn-sm btn-danger ms-1"
                deleteBtn.textContent = "Delete"
                deleteBtn.onclick = () => deleteOrder(orderData)
                actionsCell.appendChild(deleteBtn)
            }
        }

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

        const batchId = batchManager.getCurrentBatch();
        if (!isUpdate && !batchId) {
            alert('Please select a batch first (top of the page) before adding an order.');
            return;
        }

        const payload = {
            customer_name: document.getElementById("customerName").value,
            customer_location: document.getElementById("customerLocation").value,
            customer_cell: document.getElementById("customerCell").value,
            chickens_ordered: parseInt(document.getElementById("chickensOrdered").value),
            amount_paid: parseInt(document.getElementById("amountPaid").value),
            batch_id: batchId
        };

        const url = isUpdate ? `/api/update-order/${orderId}` : "/api/add-order";
        const method = isUpdate ? "PUT" : "POST";

        fetch(url, {
            method: method,
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            alert(data.message);
            if (!ok) return;

            if (isUpdate) {
                loadOrders(batchManager.getCurrentBatch());
                submitBtn.textContent = 'Add Order';
                delete submitBtn.dataset.mode;
                delete submitBtn.dataset.orderId;
            } else {
                // Reload so the table reflects the current batch filter.
                loadOrders(batchManager.getCurrentBatch());
            }
            orderForm.reset();
        })
        .catch(error => {
            console.error('Error with order:', error);
            alert('Error with order');
        });
    });

    function updateOrder(orderData) {
        document.getElementById("customerName").value = orderData.customer_name;
        document.getElementById("customerLocation").value = orderData.customer_location;
        document.getElementById("customerCell").value = orderData.customer_cell;
        document.getElementById("chickensOrdered").value = orderData.no_of_chickens;
        document.getElementById("amountPaid").value = orderData.amount_paid;

        const submitBtn = document.querySelector('#orderForm button[type="submit"]');
        submitBtn.textContent = 'Update Order';
        submitBtn.dataset.mode = 'update';
        submitBtn.dataset.orderId = orderData.id;
    }

    function deleteOrder(orderData) {
        if (!confirm(`Are you sure you want to delete ${orderData.customer_name}'s order?\n\nThe record will be crossed out and will no longer be counted.`)) {
            return;
        }
        const reason = prompt(`Why are you deleting ${orderData.customer_name}'s order? (required)`);
        if (reason === null) return;            // cancelled
        if (!reason.trim()) {
            alert('A reason is required to delete.');
            return;
        }

        fetch(`/api/delete-order/${orderData.id}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason.trim() })
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            alert(data.message);
            if (ok) loadOrders(batchManager.getCurrentBatch());
        })
        .catch(error => {
            console.error('Error deleting order:', error);
            alert('Error deleting order');
        });
    }
});
