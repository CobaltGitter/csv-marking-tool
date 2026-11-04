console.log("SCRIPT VERSION: 2026-03-19-fix1");

const API_BASE = "";
const el = (id) => document.getElementById(id);

const fileInput = el("file");
const fileInfo = el("fileInfo");

const pingBtn = el("pingBtn");
const markBtn = el("markBtn");
const downloadBtn = el("downloadBtn");

const statusEl = el("status");
const inputPreview = el("inputPreview");
const outputPreview = el("outputPreview");

let outputBlobUrl = null;
let outputFilename = "results.csv";

function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.style.color = isError ? "#b00020" : "";
}

function clearOutput() {
  outputPreview.textContent = "";
  downloadBtn.disabled = true;

  if (outputBlobUrl) {
    URL.revokeObjectURL(outputBlobUrl);
    outputBlobUrl = null;
  }
}

function previewFirstLines(text, lines = 12) {
  return text.split(/\r?\n/).slice(0, lines).join("\n");
}

fileInput.addEventListener("change", async () => {
  clearOutput();
  setStatus("Ready.");

  const file = fileInput.files?.[0];
  if (!file) {
    fileInfo.textContent = "";
    inputPreview.textContent = "";
    return;
  }

  fileInfo.textContent = `${file.name} (${file.size.toLocaleString()} bytes)`;
  outputFilename = file.name.replace(/\.csv$/i, "") + "_results.csv";

  const text = await file.text();
  inputPreview.textContent = previewFirstLines(text);
});

pingBtn.addEventListener("click", async () => {
  setStatus("Pinging...");
  try {
    const res = await fetch(`${API_BASE}/ping`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setStatus(`Ping OK: ${JSON.stringify(data)}`);
  } catch (err) {
    setStatus("Ping failed: " + String(err), true);
  }
});

markBtn.addEventListener("click", async () => {
  clearOutput();

  const file = fileInput.files?.[0];
  if (!file) {
    setStatus("Please choose a CSV file first.", true);
    return;
  }

  const number_mode = el("number_mode").value;
  const tolerance = el("tolerance").value;
  const spell_threshold = el("spell_threshold").value;
  const list_order = el("list_order").value;
  const list_delim = el("list_delim").value.trim();

  const fd = new FormData();
  fd.append("file", file);
  fd.append("number_mode", number_mode);
  fd.append("tolerance", String(tolerance));
  fd.append("spell_threshold", String(spell_threshold));
  fd.append("list_order", list_order);
  if (list_delim !== "") {
    fd.append("list_delim", list_delim);
  }

  setStatus("Marking...");

  try {
    const res = await fetch(`${API_BASE}/mark`, {
      method: "POST",
      body: fd
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }

    const csvText = await res.text();
    outputPreview.textContent = previewFirstLines(csvText);

    const blob = new Blob([csvText], { type: "text/csv;charset=utf-8" });
    outputBlobUrl = URL.createObjectURL(blob);

    downloadBtn.disabled = false;
    setStatus("Done. Output received.");
  } catch (err) {
    setStatus("Mark failed: " + String(err), true);
  }
});

downloadBtn.addEventListener("click", () => {
  if (!outputBlobUrl) return;

  const a = document.createElement("a");
  a.href = outputBlobUrl;
  a.download = outputFilename;
  document.body.appendChild(a);
  a.click();
  a.remove();
});