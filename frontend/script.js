
const form = document.getElementById("transferForm");
const messageBox = document.getElementById("message");
const transferResult = document.getElementById("transferResult");
const transferButton = document.getElementById("transferButton");
const refreshButton = document.getElementById("refreshButton");
const logoutButton = document.getElementById("logoutButton");
const adminPanel = document.getElementById("adminPanel");
const usersTable = document.getElementById("usersTable");
const refreshUsersButton = document.getElementById("refreshUsersButton");
const userManagementMessage = document.getElementById("userManagementMessage");
const receiverSelect = document.getElementById("receiver");
const amountInput = document.getElementById("amount");

let currentUser = null;
async function loadUsers() {
    try {
        userManagementMessage.textContent = "Loading users...";
        userManagementMessage.className = "";

        const response = await fetch("/api/admin/users", {
            credentials: "same-origin",
            cache: "no-store"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to load users.");
        }

        usersTable.replaceChildren();

        for (const user of data.users) {
            const row = document.createElement("tr");

            const values = [
                user.id,
                user.username,
                user.role,
                user.is_active ? "Active" : "Inactive"
            ];

            for (const value of values) {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            }

            const actionCell = document.createElement("td");

          if (user.role !== "admin") {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "secondary-button";

    button.textContent = user.is_active ? "Deactivate" : "Activate";

    button.addEventListener("click", async () => {
        const action = user.is_active ? "deactivate" : "activate";

        if (!confirm(`${action} ${user.username}?`)) {
            return;
        }

        try {
            const url = user.is_active
                ? `/api/admin/users/${user.id}`
                : `/api/admin/users/${user.id}/activate`;

            const response = await fetch(url, {
                method: user.is_active ? "DELETE" : "POST",
                credentials: "same-origin"
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `Failed to ${action} user.`);
            }

            userManagementMessage.textContent =
                `${user.username} ${action}d successfully.`;

            await loadUsers();

        } catch (error) {
            userManagementMessage.textContent = error.message;
            userManagementMessage.className = "error";
        }
    });

    actionCell.appendChild(button);
} else {
    actionCell.textContent = "—";
}

            row.appendChild(actionCell);
            usersTable.appendChild(row);
        }

        userManagementMessage.textContent = `${data.users.length} users found.`;

    } catch (error) {
        console.error("User management error:", error);
        userManagementMessage.textContent = error.message;
        userManagementMessage.className = "error";
    }
}

function formatMoney(amount, currency = "EUR") {
    return Number(amount).toLocaleString("en-US", {
        style: "currency",
        currency: currency
    });
}


function addDetail(container, label, value) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");

    strong.textContent = label + ": ";

    paragraph.appendChild(strong);
    paragraph.appendChild(document.createTextNode(String(value)));

    container.appendChild(paragraph);
}


function displayTransfer(data) {
    transferResult.replaceChildren();
    transferResult.className = "signature-details";

    addDetail(transferResult, "Transaction ID", data.transaction_id);
    addDetail(transferResult, "Receiver", data.receiver);
    addDetail(
        transferResult,
        "Amount",
        data.amount + " " + data.currency
    );
    addDetail(transferResult, "Status", data.status);
}


async function loadCurrentUser() {
    const response = await fetch("/api/me", {
        credentials: "same-origin",
        cache: "no-store"
    });

    if (response.status === 401) {
        window.location.replace("/login");
        return false;
    }

    if (!response.ok) {
        throw new Error("Unable to load authenticated account");
    }

    const rawResponse = await response.text();

console.log("HTTP status:", response.status);
console.log("Server response:", rawResponse);

let data;

try {
    data = JSON.parse(rawResponse);
} catch {
    throw new Error(
        `Server returned HTTP ${response.status} instead of JSON. ` +
        "Check the Flask terminal for errors."
    );
}

    currentUser = data.user;
if (currentUser.role === "admin") {
    adminPanel.hidden = false;
    await loadUsers();
} else {
    adminPanel.hidden = true;
}
    document.getElementById("currentUsername").textContent =
        currentUser.username;

    document.getElementById("navUsername").textContent =
        currentUser.username;

    document.getElementById("accountNumber").textContent =
        currentUser.account_number;

    document.getElementById("currentBalance").textContent =
        formatMoney(currentUser.balance, currentUser.currency);

    document.getElementById("sender").value =
        currentUser.username;

    // The transaction processor still restricts transfers
       // Load available recipients dynamically
    receiverSelect.replaceChildren();

    const accountsResponse = await fetch("/api/accounts", {
        credentials: "same-origin",
        cache: "no-store"
    });

    if (!accountsResponse.ok) {
        throw new Error("Unable to load recipient accounts");
    }

    const accountsData = await accountsResponse.json();

    for (const account of accountsData.accounts) {
        const option = document.createElement("option");

        option.value = account.username;
        option.textContent =
            `${account.username} (${account.account_number})`;

        receiverSelect.appendChild(option);
    }

    const canTransfer = accountsData.accounts.length > 0;

    receiverSelect.disabled = !canTransfer;
    amountInput.disabled = !canTransfer;
    transferButton.disabled = !canTransfer;

    messageBox.className = "";
    messageBox.textContent = canTransfer
        ? ""
        : "No recipient accounts available.";

    return true;
}


async function loadTransfers() {
    if (!currentUser) {
        return;
    }

    const response = await fetch("/api/transfers", {
        credentials: "same-origin",
        cache: "no-store"
    });

    if (response.status === 401) {
        window.location.replace("/login");
        return;
    }

    if (!response.ok) {
        throw new Error("Unable to load transaction history");
    }

    const data = await response.json();

    // Only display transactions involving the logged-in user.
    // This is a UI filter; server-side filtering is still needed.
    const ownTransfers = data.transfers.filter(transaction =>
        transaction.sender === currentUser.username ||
        transaction.receiver === currentUser.username
    );

    const completedTransfers = ownTransfers.filter(transaction =>
        transaction.status === "COMPLETED"
    );

    document.getElementById("totalTransfers").textContent =
        completedTransfers.length;

    const table = document.getElementById("transferTable");
    table.replaceChildren();

    for (const transaction of ownTransfers) {
        const row = document.createElement("tr");

        const values = [
            transaction.transaction_id,
            transaction.sender,
            transaction.receiver,
            transaction.amount + " " + transaction.currency,
            transaction.status
        ];

        for (const value of values) {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        }

        table.appendChild(row);
    }
}


async function refreshDashboard() {
    try {
        const authenticated = await loadCurrentUser();

        if (!authenticated) {
            return;
        }

        await loadTransfers();

    } catch (error) {
        console.error("Dashboard loading error:", error);
        messageBox.className = "error";
        messageBox.textContent = error.message;
    }
}


form.addEventListener("submit", async function(event) {
    event.preventDefault();

    if (!currentUser || receiverSelect.disabled || !receiverSelect.value) {
    messageBox.className = "error";
    messageBox.textContent = "No recipient account selected.";
    return;
}

    messageBox.textContent = "";
    transferButton.disabled = true;

    const receiver = receiverSelect.value;
    const amount = Number(amountInput.value).toFixed(2);

    const transfer = {
        receiver: receiver,
        amount: amount,
        currency: currentUser.currency
    };

    try {
        const response = await fetch("/api/transfer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify(transfer)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || data.message || "Transfer request failed"
            );
        }

        messageBox.className = "success";
        messageBox.textContent = data.message;

        displayTransfer(data);

        await refreshDashboard();

    } catch (error) {
        messageBox.className = "error";
        messageBox.textContent = error.message;

    } finally {
             
        transferButton.disabled =
            !currentUser || receiverSelect.options.length === 0;
    
    }
});


refreshButton.addEventListener("click", refreshDashboard);
refreshUsersButton.addEventListener("click", loadUsers);

logoutButton.addEventListener("click", async function() {
    logoutButton.disabled = true;

    try {
        const response = await fetch("/api/logout", {
            method: "POST",
            credentials: "same-origin"
        });

        if (!response.ok) {
            throw new Error("Logout failed");
        }

        window.location.replace("/login");

    } catch (error) {
        logoutButton.disabled = false;
        messageBox.className = "error";
        messageBox.textContent = error.message;
    }
});


refreshDashboard();

