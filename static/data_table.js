const tableHead = document.querySelector("#offers-head");
const tableBody = document.querySelector("#offers-body");
const rowCount = document.querySelector("#row-count");

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
          ${columns.map((column) => `<td>${row[column] || ""}</td>`).join("")}
        </tr>
      `,
    )
    .join("");

  rowCount.textContent = `${rows.length} row${rows.length === 1 ? "" : "s"}`;
}

// Fetch offer data from the API and render it into the table.
async function loadOffers() {
  try {
    const response = await fetch("/api/data");

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

loadOffers();
