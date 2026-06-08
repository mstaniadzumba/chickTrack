document.addEventListener("DOMContentLoaded", () => {
    const userForm = document.getElementById("userForm");
    const tableBody = document.getElementById("usersTableBody");

    loadUsers();

    function loadUsers() {
        fetch('/api/users')
        .then(res => {
            if (res.status === 401) { window.location.href = '/login'; return []; }
            return res.json();
        })
        .then(users => {
            tableBody.innerHTML = '';
            users.forEach(addUserToTable);
        })
        .catch(error => console.error('Error loading users:', error));
    }

    function addUserToTable(user) {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.textContent = user.name;

        const phoneCell = document.createElement("td");
        phoneCell.textContent = user.phone;

        const roleCell = document.createElement("td");
        roleCell.textContent = user.is_admin ? 'Admin' : 'User';

        const actionsCell = document.createElement("td");
        // Don't show a delete button for your own account.
        const isSelf = window.CURRENT_USER && window.CURRENT_USER.phone === user.phone;
        if (!isSelf) {
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "btn btn-sm btn-danger";
            deleteBtn.textContent = "Remove";
            deleteBtn.onclick = () => removeUser(user);
            actionsCell.appendChild(deleteBtn);
        } else {
            actionsCell.textContent = '(you)';
        }

        row.appendChild(nameCell);
        row.appendChild(phoneCell);
        row.appendChild(roleCell);
        row.appendChild(actionsCell);
        tableBody.appendChild(row);
    }

    userForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const payload = {
            name: document.getElementById("userName").value,
            phone: document.getElementById("userPhone").value,
            password: document.getElementById("userPassword").value,
            is_admin: document.getElementById("userIsAdmin").checked
        };

        fetch('/api/add-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            alert(data.message);
            if (ok) {
                userForm.reset();
                loadUsers();
            }
        })
        .catch(error => {
            console.error('Error adding user:', error);
            alert('Error adding user');
        });
    });

    function removeUser(user) {
        if (!confirm(`Remove ${user.name}? They will no longer be able to log in.`)) return;

        fetch(`/api/delete-user/${user.id}`, { method: 'DELETE' })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            alert(data.message);
            if (ok) loadUsers();
        })
        .catch(error => {
            console.error('Error removing user:', error);
            alert('Error removing user');
        });
    }
});
