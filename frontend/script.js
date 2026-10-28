const form = document.getElementById("transactionForm");
const messageBox = document.getElementById("message");
const signatureResult = document.getElementById("signatureResult");
const signButton = document.getElementById("signButton");


function addDetail(container, label, value, isSignature = false) {
    const labelElement = document.createElement("p");
    const strong = document.createElement("strong");

    strong.textContent = label + ": ";
    labelElement.appendChild(strong);

    if (isSignature) {
        const code = document.createElement("code");
        code.className = "signature-value";
        code.textContent = value;

        container.appendChild(labelElement);
        container.appendChild(code);
    } else {
        labelElement.appendChild(
            document.createTextNode(value)
        );

        container.appendChild(labelElement);
    }
}


function displaySignature(data) {
    signatureResult.replaceChildren();
    signatureResult.className = "signature-details";

    addDetail(
        signatureResult,
        "Transaction ID",
        data.transaction.transaction_id
    );

    addDetail(
        signatureResult,
        "Receiver",
        data.transaction.receiver
    );

    addDetail(
        signatureResult,
        "Amount",
        data.transaction.amount + " EUR"
    );

    addDetail(
        signatureResult,
        "SHA-256",
        data.hash,
        true
    );

    addDetail(
        signatureResult,
        "Signature r",
        data.signature.r,
        true
    );

    addDetail(
        signatureResult,
        "Signature s",
        data.signature.s,
        true
    );

    addDetail(
        signatureResult,
        "Verification",
        data.signature_valid ? "VALID" : "INVALID"
    );

    addDetail(
        signatureResult,
        "Status",
        data.status
    );
}


form.addEventListener("submit", async function(event) {
    event.preventDefault();

    messageBox.textContent = "";
    signButton.disabled = true;

    const receiver = document.getElementById("receiver").value;
    const amountInput = document.getElementById("amount").value;

    const amount = Number(amountInput).toFixed(2);

    const transaction = {
        sender: "BANK",
        receiver: receiver,
        amount: amount,
        currency: "EUR"
    };

    try {
        const response = await fetch("/api/transactions/sign", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transaction)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Signing failed");
        }

        messageBox.className = "success";
        messageBox.textContent = "Transaction signed successfully!";

        displaySignature(data);

        await loadTransactions();

    } catch (error) {
        messageBox.className = "error";
        messageBox.textContent = error.message;

    } finally {
        signButton.disabled = false;
    }
});


async function loadTransactions() {
    try {
        const response = await fetch("/api/transactions");

        if (!response.ok) {
            throw new Error("Unable to load transactions");
        }

        const data = await response.json();

        document.getElementById("totalTransactions").textContent =
            data.count;

        const table = document.getElementById("transactionTable");
        table.replaceChildren();

        for (const record of data.transactions.slice().reverse()) {
            const row = document.createElement("tr");

            const values = [
                record.transaction.transaction_id,
                record.transaction.receiver,
                record.transaction.amount + " EUR",
                record.signature_valid ? "VALID" : "INVALID",
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
        console.error(error);
    }
}


loadTransactions();
