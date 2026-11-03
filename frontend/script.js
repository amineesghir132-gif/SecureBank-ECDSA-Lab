
const form = document.getElementById("transferForm");
const messageBox = document.getElementById("message");
const transferResult = document.getElementById("transferResult");
const transferButton = document.getElementById("transferButton");
const refreshButton = document.getElementById("refreshButton");


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


async function loadAccounts() {
    try {
        const response = await fetch("/api/accounts");

        if (!response.ok) {
            throw new Error("Unable to load accounts");
        }

        const data = await response.json();

        // Store the latest balances for future dashboard features.
        window.secureBankAccounts = data.accounts;

        // Update existing account elements if they are present.
        for (const account of data.accounts) {
            const element = document.getElementById(
                "balance-" + account.username.toLowerCase()
            );

            if (element) {
                element.textContent =
                    Number(account.balance).toLocaleString(
                        "en-US",
                        {
                            style: "currency",
                            currency: account.currency
                        }
                    );
            }
        }

    } catch (error) {
        console.error("Account loading error:", error);
    }
}


async function loadTransfers() {
    try {
        const response = await fetch("/api/transfers");

        if (!response.ok) {
            throw new Error("Unable to load transfers");
        }

        const data = await response.json();

        document.getElementById("totalTransfers").textContent =
            data.count;

        const table = document.getElementById("transferTable");
        table.replaceChildren();

        // PostgreSQL already returns newest transactions first.
        for (const transaction of data.transfers) {
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

    } catch (error) {
        console.error("Transfer history error:", error);
    }
}


async function refreshDashboard() {
    await Promise.all([
        loadAccounts(),
        loadTransfers()
    ]);
}


form.addEventListener("submit", async function(event) {
    event.preventDefault();

    messageBox.textContent = "";
    transferButton.disabled = true;

    const receiver = document.getElementById("receiver").value;
    const amountInput = document.getElementById("amount").value;

    const amount = Number(amountInput).toFixed(2);

    const transfer = {
        receiver: receiver,
        amount: amount,
        currency: "EUR"
    };

    try {
        const response = await fetch("/api/transfer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
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

        // Refresh balances and history after successful transfer.
        await refreshDashboard();

    } catch (error) {
        messageBox.className = "error";
        messageBox.textContent = error.message;

    } finally {
        transferButton.disabled = false;
    }
});


refreshButton.addEventListener("click", refreshDashboard);

// Load real PostgreSQL data when the page opens.
refreshDashboard();

