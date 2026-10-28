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

    addDetail(
        transferResult,
        "Transaction ID",
        data.transaction_id
    );

    addDetail(
        transferResult,
        "Receiver",
        data.receiver
    );

    addDetail(
        transferResult,
        "Amount",
        data.amount + " " + data.currency
    );

    addDetail(
        transferResult,
        "Status",
        data.status
    );
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
            throw new Error(data.error || "Transfer request failed");
        }

        messageBox.className = "success";
        messageBox.textContent = data.message;

        displayTransfer(data);

        await loadTransfers();

    } catch (error) {
        messageBox.className = "error";
        messageBox.textContent = error.message;

    } finally {
        transferButton.disabled = false;
    }
});


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

        for (const record of data.transfers.slice().reverse()) {
            const row = document.createElement("tr");

            const transaction = record.transaction;

            const values = [
                transaction.transaction_id,
                transaction.sender,
                transaction.receiver,
                transaction.amount + " " + transaction.currency,
                record.status
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


refreshButton.addEventListener("click", loadTransfers);

loadTransfers();
