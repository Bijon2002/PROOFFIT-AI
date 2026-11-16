/**
 * PROOFFIT AI - Client Application Controller
 * Handles interactive file ingest, AI mapping validation, and audit dashboard rendering.
 */

// State
let useCases = {};
let selectedUseCase = "demand_forecasting";
let activeFile = null;
let currentMappingResponse = null;
let latestReport = null;

// DOM Elements
const $ = (id) => document.getElementById(id);
const useCaseGrid = $("useCaseGrid");
const dropzone = $("dropzone");
const fileInput = $("fileInput");
const fileInfoBar = $("fileInfoBar");
const fileNameLabel = $("fileNameLabel");
const fileSizeLabel = $("fileSizeLabel");
const btnChangeFile = $("btnChangeFile");
const btnDemoRetail = $("btnDemoRetail");
const btnDemoChurn = $("btnDemoChurn");
const btnToStep2 = $("btnToStep2");
const btnBackToStep1 = $("btnBackToStep1");
const btnRunAssessment = $("btnRunAssessment");
const btnPrintReport = $("btnPrintReport");
const btnDownloadJson = $("btnDownloadJson");
const btnRestart = $("btnRestart");

const step1Container = $("step1Container");
const step2Container = $("step2Container");
const step3Container = $("step3Container");

const stepIndicator1 = $("stepIndicator1");
const stepIndicator2 = $("stepIndicator2");
const stepIndicator3 = $("stepIndicator3");

const step1Error = $("step1Error");
const step2Error = $("step2Error");

// Initialize application
document.addEventListener("DOMContentLoaded", async () => {
  await loadUseCases();
  setupDragAndDrop();
  setupEventListeners();
});

// Load available use cases from backend
async function loadUseCases() {
  try {
    const res = await fetch("/api/use-cases");
    if (!res.ok) throw new Error("Failed to load use cases");
    useCases = await res.json();
    renderUseCaseGrid();
  } catch (err) {
    showError(step1Error, "Could not load use cases: " + err.message);
  }
}

function renderUseCaseGrid() {
  useCaseGrid.innerHTML = "";
  const icons = {
    demand_forecasting: "📈",
    customer_churn: "👥",
    predictive_maintenance: "⚙️",
    fraud_detection: "🛡️",
    rag_knowledge_base: "✨"
  };

  Object.entries(useCases).forEach(([key, uc]) => {
    const card = document.createElement("div");
    card.className = `use-case-card ${key === selectedUseCase ? "selected" : ""}`;
    card.dataset.key = key;

    const icon = icons[key] || "📊";

    card.innerHTML = `
      <div>
        <div class="uc-header">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:18px;">${icon}</span>
            <span class="uc-title">${uc.title}</span>
          </div>
          <span class="uc-badge">${uc.required.length} Required</span>
        </div>
        <p class="uc-desc">${uc.description}</p>
      </div>
      <div>
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px;font-weight:600;">CANONICAL FIELDS:</div>
        <div class="uc-fields">
          ${uc.required.map(f => `<span class="field-pill">${f}</span>`).join("")}
        </div>
      </div>
    `;

    card.addEventListener("click", () => {
      document.querySelectorAll(".use-case-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      selectedUseCase = key;
    });

    useCaseGrid.appendChild(card);
  });
}

function setupDragAndDrop() {
  dropzone.addEventListener("click", (e) => {
    if (e.target !== btnChangeFile) fileInput.click();
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  btnChangeFile.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.value = "";
    fileInput.click();
  });
}

function handleFileSelected(file) {
  if (!file.name.toLowerCase().endsWith(".csv")) {
    showError(step1Error, "Please select a valid CSV file (.csv)");
    return;
  }
  clearError(step1Error);
  activeFile = file;
  fileNameLabel.textContent = file.name;
  fileSizeLabel.textContent = `${(file.size / 1024).toFixed(1)} KB`;
  fileInfoBar.classList.remove("hidden");
}

function setupEventListeners() {
  // Demo loaders
  btnDemoRetail.addEventListener("click", () => loadSampleDataset("sample_retail", "demand_forecasting"));
  btnDemoChurn.addEventListener("click", () => loadSampleDataset("sample_churn", "customer_churn"));

  // Navigation: Step 1 -> Step 2
  btnToStep2.addEventListener("click", async () => {
    if (!activeFile) {
      showError(step1Error, "Please upload a CSV file or load a sample dataset first.");
      return;
    }
    clearError(step1Error);
    setButtonLoading(btnToStep2, true, "Analyzing Schema...");

    try {
      const formData = new FormData();
      formData.append("file", activeFile);
      formData.append("use_case", selectedUseCase);

      const res = await fetch("/api/suggest-mapping", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Schema analysis failed");

      currentMappingResponse = data;
      renderMappingStep(data);
      goToStep(2);
    } catch (err) {
      showError(step1Error, err.message);
    } finally {
      setButtonLoading(btnToStep2, false, "Continue to Schema Mapping →");
    }
  });

  // Navigation: Step 2 -> Step 1
  btnBackToStep1.addEventListener("click", () => {
    goToStep(1);
  });

  // Navigation: Step 2 -> Step 3 (Run Assessment)
  btnRunAssessment.addEventListener("click", async () => {
    clearError(step2Error);
    setButtonLoading(btnRunAssessment, true, "Assessing Data Quality...");

    try {
      // Gather mapping selections
      const mapping = {};
      document.querySelectorAll(".mapping-select").forEach((sel) => {
        const canonicalKey = sel.dataset.canonical;
        mapping[canonicalKey] = sel.value || null;
      });

      const formData = new FormData();
      formData.append("file", activeFile);
      formData.append("use_case", selectedUseCase);
      formData.append("mapping", JSON.stringify(mapping));

      const res = await fetch("/api/assess", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Assessment computation failed");

      latestReport = data;
      renderReportStep(data);
      goToStep(3);
    } catch (err) {
      showError(step2Error, err.message);
    } finally {
      setButtonLoading(btnRunAssessment, false, "Run Readiness Assessment ⚡");
    }
  });

  // Export buttons
  btnPrintReport.addEventListener("click", () => {
    window.print();
  });

  btnDownloadJson.addEventListener("click", () => {
    if (!latestReport) return;
    const blob = new Blob([JSON.stringify(latestReport, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `PROOFFIT_AI_Audit_${selectedUseCase}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Restart
  btnRestart.addEventListener("click", () => {
    goToStep(1);
  });
}

async function loadSampleDataset(datasetName, targetUseCase) {
  clearError(step1Error);
  try {
    // Switch selected use case card
    selectedUseCase = targetUseCase;
    document.querySelectorAll(".use-case-card").forEach(c => {
      c.classList.toggle("selected", c.dataset.key === targetUseCase);
    });

    const res = await fetch(`/api/sample-data/${datasetName}`);
    if (!res.ok) throw new Error("Could not fetch sample dataset");
    const blob = await res.blob();
    const file = new File([blob], `${datasetName}.csv`, { type: "text/csv" });
    handleFileSelected(file);
  } catch (err) {
    showError(step1Error, "Error loading sample: " + err.message);
  }
}

function renderMappingStep(data) {
  const mappingGrid = $("mappingGrid");
  mappingGrid.innerHTML = "";
  const tpl = useCases[selectedUseCase];
  const requiredFields = new Set(tpl.required);
  const allFields = [...tpl.required, ...(tpl.optional || [])];

  allFields.forEach((field) => {
    const isRequired = requiredFields.has(field);
    const suggestedCol = data.mapping[field] || "";
    const card = document.createElement("div");
    card.className = "mapping-card";

    const fieldLabel = field.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());

    let optionsHtml = `<option value="">-- Do Not Map / Not Available --</option>`;
    data.columns.forEach((col) => {
      const selected = col === suggestedCol ? "selected" : "";
      optionsHtml += `<option value="${escapeHtml(col)}" ${selected}>${escapeHtml(col)}</option>`;
    });

    card.innerHTML = `
      <div class="mapping-field-header">
        <div class="mapping-field-name">${fieldLabel}</div>
        <span class="${isRequired ? 'badge-required' : 'badge-optional'}">
          ${isRequired ? 'REQUIRED' : 'OPTIONAL'}
        </span>
      </div>
      <div style="font-size:12px;color:var(--text-muted);font-family:monospace;">canonical: ${field}</div>
      <select class="mapping-select" data-canonical="${field}">
        ${optionsHtml}
      </select>
    `;

    mappingGrid.appendChild(card);
  });

  // Render Preview Table
  $("previewStats").textContent = `${data.total_rows.toLocaleString()} rows, ${data.total_columns} columns`;
  const thead = $("previewTableHead");
  const tbody = $("previewTableBody");
  thead.innerHTML = "";
  tbody.innerHTML = "";

  if (data.columns && data.columns.length > 0) {
    const headRow = document.createElement("tr");
    data.columns.forEach(col => {
      const th = document.createElement("th");
      th.textContent = col;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);

    (data.preview || []).forEach(row => {
      const tr = document.createElement("tr");
      data.columns.forEach(col => {
        const td = document.createElement("td");
        td.textContent = row[col] !== undefined ? String(row[col]) : "-";
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }
}

function renderReportStep(r) {
  // Score Ring Animation
  const score = r.readiness;
  const circle = $("scoreCircleProgress");
  const scoreText = $("scoreTextValue");
  
  scoreText.textContent = score;
  circle.setAttribute("stroke-dasharray", `${score}, 100`);

  let strokeColor = "#10b981"; // pass
  if (score < 55) strokeColor = "#ef4444"; // fail
  else if (score < 80) strokeColor = "#f59e0b"; // warn
  circle.setAttribute("stroke", strokeColor);

  // Verdict Badge
  const badge = $("verdictBadge");
  badge.className = `verdict-badge verdict-${r.verdict_badge || 'ready'}`;
  badge.textContent = r.verdict;

  // Executive summary
  $("executiveSummaryText").textContent = r.summary;

  // Key stats matrix
  $("metricRows").textContent = (r.rows_analysed || 0).toLocaleString();
  $("metricConfidence").textContent = r.confidence;
  
  const passed = (r.all_checks || []).filter(c => c.status === "pass").length;
  const totalChecks = (r.all_checks || []).length;
  $("metricPassedChecks").textContent = `${passed}/${totalChecks}`;

  const blockersCount = (r.blockers || []).length;
  $("metricBlockers").textContent = blockersCount;
  $("metricBlockers").style.color = blockersCount > 0 ? "var(--color-fail)" : "var(--color-pass)";

  // Blockers List
  const blockersContainer = $("blockersContainer");
  const blockersList = $("blockersList");
  blockersList.innerHTML = "";

  if (blockersCount > 0) {
    blockersContainer.classList.remove("hidden");
    r.blockers.forEach((b) => {
      const item = document.createElement("div");
      item.className = "blocker-card";
      
      const evidenceStr = Object.entries(b.evidence || {})
        .map(([k, v]) => `<strong>${k.replace(/_/g, " ")}:</strong> ${v}`)
        .join(" &bull; ");

      item.innerHTML = `
        <div class="blocker-title">
          <span>🚨</span>
          <span>${b.label || b.check} (Score: ${(b.score * 100).toFixed(0)}%)</span>
        </div>
        <div class="blocker-evidence">${evidenceStr}</div>
        <div class="blocker-fix"><strong>Remediation:</strong> ${b.fix}</div>
      `;
      blockersList.appendChild(item);
    });
  } else {
    blockersContainer.classList.add("hidden");
  }

  // Diagnostic Health Checks
  const checksGrid = $("checksGrid");
  checksGrid.innerHTML = "";

  (r.all_checks || []).forEach((c) => {
    const card = document.createElement("div");
    card.className = "check-card";
    const pct = Math.round(c.score * 100);
    const statusClass = c.status === "pass" ? "score-pass" : c.status === "warn" ? "score-warn" : "score-fail";
    const barColor = c.status === "pass" ? "var(--color-pass)" : c.status === "warn" ? "var(--color-warn)" : "var(--color-fail)";

    const evidenceStr = Object.entries(c.evidence || {})
      .map(([k, v]) => `${k.replace(/_/g, " ")}: ${v}`)
      .join(" &bull; ");

    card.innerHTML = `
      <div class="check-card-header">
        <span class="check-name">${c.label || c.check}</span>
        <span class="check-score-badge ${statusClass}">${pct}% &bull; ${c.status.toUpperCase()}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width:${pct}%;background:${barColor};"></div>
      </div>
      <div class="check-meta-row">
        <span>${evidenceStr}</span>
        <span style="font-style:italic;">${c.fix}</span>
      </div>
    `;
    checksGrid.appendChild(card);
  });

  // Dataset Vitals
  const vitals = $("profileVitals");
  vitals.innerHTML = "";
  if (r.dataset_profile) {
    const p = r.dataset_profile;
    vitals.innerHTML = `
      <div><strong>Total Records:</strong> ${p.total_rows.toLocaleString()}</div>
      <div><strong>Features:</strong> ${p.total_columns}</div>
      <div><strong>Missing Cells:</strong> ${p.missing_cells_pct}%</div>
      <div><strong>Duplicate Rows:</strong> ${p.duplicate_rows_pct}%</div>
      <div><strong>Memory Footprint:</strong> ${p.memory_mb} MB</div>
    `;
  }
}

function goToStep(step) {
  step1Container.classList.add("hidden");
  step2Container.classList.add("hidden");
  step3Container.classList.add("hidden");

  stepIndicator1.classList.remove("active", "completed");
  stepIndicator2.classList.remove("active", "completed");
  stepIndicator3.classList.remove("active", "completed");

  if (step === 1) {
    step1Container.classList.remove("hidden");
    stepIndicator1.classList.add("active");
  } else if (step === 2) {
    step2Container.classList.remove("hidden");
    stepIndicator1.classList.add("completed");
    stepIndicator2.classList.add("active");
  } else if (step === 3) {
    step3Container.classList.remove("hidden");
    stepIndicator1.classList.add("completed");
    stepIndicator2.classList.add("completed");
    stepIndicator3.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function showError(el, message) {
  el.textContent = message;
  el.classList.remove("hidden");
}

function clearError(el) {
  el.textContent = "";
  el.classList.add("hidden");
}

function setButtonLoading(btn, isLoading, text) {
  btn.disabled = isLoading;
  if (isLoading) {
    btn.innerHTML = `<span class="spinner"></span> <span>${text}</span>`;
  } else {
    btn.innerHTML = text;
  }
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
