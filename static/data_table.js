const tableHead = document.querySelector("#offers-head");
const tableBody = document.querySelector("#offers-body");
const rowCount = document.querySelector("#row-count");
const chatAnswer = document.querySelector("#chat-answer");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");

// Empty-state text the server rendered into the answer box; reused for blank input.
const chatPlaceholder = chatAnswer.textContent;

// Convert database column names into readable table headers.
function formatHeader(value) {
  return value.replaceAll("_", " ").toLowerCase();
}

// Build the table headers and rows from API data.
function renderTable(rows) {
  if (rows.length === 0) {
    tableHead.innerHTML = "";
    tableBody.innerHTML = '<tr><td class="loading-cell">No offers found.</td></tr>';
    rowCount.textContent = "0 rows";
    return;
  }

  const columns = Object.keys(rows[0]);
  tableHead.innerHTML = `
    <tr>
      ${columns.map((column) => `<th scope="col">${formatHeader(column)}</th>`).join("")}
    </tr>
  `;

  tableBody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          ${columns.map((column) => `<td><div class="cell">${row[column] || ""}</div></td>`).join("")}
        </tr>
      `,
    )
    .join("");

  rowCount.textContent = `${rows.length} row${rows.length === 1 ? "" : "s"}`;
}

// Send the browser to the login page when a request returns 401 Unauthorized.
function redirectIfUnauthorized(response) {
  if (response.status === 401) {
    window.location.href = "/login";
    return true;
  }
  return false;
}

// Fetch offer data from the API and render it into the table.
async function loadOffers() {
  try {
    const response = await fetch("/api/data");

    if (redirectIfUnauthorized(response)) {
      return;
    }
    if (!response.ok) {
      throw new Error("Could not load offers");
    }

    const payload = await response.json();
    renderTable(payload.data);
  } catch (error) {
    tableBody.innerHTML = '<tr><td class="loading-cell">Unable to load offers.</td></tr>';
    rowCount.textContent = "Error";
  }
}

// Send the user's question to the chat API and display the answer.
async function submitChat(message) {
  chatAnswer.textContent = "Thinking...";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (redirectIfUnauthorized(response)) {
      return;
    }
    if (!response.ok) {
      throw new Error("Could not load chat answer");
    }

    const payload = await response.json();
    chatAnswer.textContent = payload.answer;
  } catch (error) {
    chatAnswer.textContent = "Unable to answer right now.";
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const message = chatInput.value.trim();

  if (!message) {
    chatAnswer.textContent = chatPlaceholder;
    return;
  }

  submitChat(message);
  chatInput.value = "";
});

loadOffers();
