const API_BASE = window.location.origin;

const csvFileEl = document.getElementById("csvFile");
const resetDbEl = document.getElementById("resetDb");
const runBtn = document.getElementById("runBtn");

const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const outputEl = document.getElementById("output");
const adviceEl = document.getElementById("advice");

function setStatus(msg, ok = false) {
  statusEl.textContent = msg;
  statusEl.className = ok ? "ok" : "";
}

function setError(msg) {
  errorEl.textContent = msg || "";
}

function renderAdvice(adviceList) {
  adviceEl.innerHTML = "";
  if (!adviceList || adviceList.length === 0) {
    adviceEl.textContent = "No advice generated.";
    return;
  }
  const ul = document.createElement("ul");
  for (const line of adviceList) {
    const li = document.createElement("li");
    li.textContent = line;
    ul.appendChild(li);
  }
  adviceEl.appendChild(ul);
}

runBtn.addEventListener("click", async () => {
  setError("");
  setStatus("");

  const file = csvFileEl.files[0];
  if (!file) {
    setError("Please choose a CSV file first.");
    return;
  }

  runBtn.disabled = true;
  setStatus("Uploading + running analysis...");

  try {
    const formData = new FormData();
    formData.append("file", file);

    const reset = resetDbEl.checked ? "true" : "false";
    const url = `${API_BASE}/run-all?reset=${reset}`;

    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const detail = data?.detail
        ? JSON.stringify(data.detail)
        : "Unknown error";
      throw new Error(`API error (${res.status}): ${detail}`);
    }

    setStatus("Done ✅", true);

    outputEl.textContent = JSON.stringify(data, null, 2);
    renderAdvice(data.advice);
  } catch (err) {
    setError(err.message);
    setStatus("Failed ❌");
  } finally {
    runBtn.disabled = false;
  }
});
