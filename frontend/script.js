// DOM Elements
const emailForm = document.getElementById("emailForm");
const tabs = document.querySelectorAll(".tab");
const tabContents = document.querySelectorAll(".tab-content");
const fileUploadArea = document.getElementById("fileUploadArea");
const fileInput = document.getElementById("email_file");
const fileSelected = document.getElementById("fileSelected");
const fileName = document.getElementById("fileName");
const removeFileBtn = document.getElementById("removeFile");
const submitBtn = document.getElementById("submitBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const resultsSection = document.getElementById("resultsSection");
const categoryBadge = document.getElementById("categoryBadge");
const confidenceValue = document.getElementById("confidenceValue");
const responseContent = document.getElementById("responseContent");
const copyBtn = document.getElementById("copyBtn");
const newAnalysisBtn = document.getElementById("newAnalysisBtn");

// Tab Navigation
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const tabName = tab.dataset.tab;

    // Remove active class from all tabs
    tabs.forEach((t) => t.classList.remove("active"));
    tabContents.forEach((tc) => tc.classList.remove("active"));

    // Add active class to clicked tab
    tab.classList.add("active");
    document.getElementById(`${tabName}-content`).classList.add("active");

    // Clear form when switching tabs
    if (tabName === "text") {
      document.getElementById("email_text").value = "";
      fileInput.value = "";
      hideFileSelected();
    } else {
      document.getElementById("email_text").value = "";
    }
  });
});

// File Upload Interactions
fileUploadArea.addEventListener("click", () => {
  fileInput.click();
});

fileUploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileUploadArea.style.borderColor = "var(--primary)";
  fileUploadArea.style.background = "rgba(102, 126, 234, 0.05)";
});

fileUploadArea.addEventListener("dragleave", (e) => {
  e.preventDefault();
  fileUploadArea.style.borderColor = "var(--border)";
  fileUploadArea.style.background = "transparent";
});

fileUploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  fileUploadArea.style.borderColor = "var(--border)";
  fileUploadArea.style.background = "transparent";

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (isValidFile(file)) {
      fileInput.files = files;
      showFileSelected(file.name);
    } else {
      showError("Formato de arquivo inválido. Use .txt ou .pdf");
    }
  }
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    const file = e.target.files[0];
    if (isValidFile(file)) {
      showFileSelected(file.name);
    } else {
      showError("Formato de arquivo inválido. Use .txt ou .pdf");
      fileInput.value = "";
    }
  }
});

removeFileBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  fileInput.value = "";
  hideFileSelected();
});

function isValidFile(file) {
  const validTypes = ["text/plain", "application/pdf"];
  return validTypes.includes(file.type);
}

function showFileSelected(name) {
  fileUploadArea.style.display = "none";
  fileSelected.style.display = "flex";
  fileName.textContent = name;
}

function hideFileSelected() {
  fileUploadArea.style.display = "block";
  fileSelected.style.display = "none";
  fileName.textContent = "";
}

// Form Submission
emailForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const emailText = document.getElementById("email_text").value;
  const emailFile = fileInput.files[0];

  // Validation
  if (!emailText.trim() && !emailFile) {
    showError("Por favor, insira um texto ou selecione um arquivo");
    return;
  }

  // Prepare form data
  const formData = new FormData();
  if (emailText.trim()) {
    formData.append("text", emailText);
  }
  if (emailFile) {
    formData.append("file", emailFile);
  }

  // Show loading
  showLoading();

  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      displayResults(data);
    } else {
      showError(data.detail || data.message || "Erro ao processar email");
    }
  } catch (error) {
    console.error("Error:", error);
    showError(
      "Erro ao se comunicar com o servidor. Verifique se o backend está rodando.",
    );
  } finally {
    hideLoading();
  }
});

// Display Results
function displayResults(data) {
  // Show results section
  resultsSection.classList.remove("is-empty");
  resultsSection.classList.add("has-results");

  // Display category
  const category = data.category.toLowerCase();
  categoryBadge.textContent = data.category;
  categoryBadge.className = `category-badge ${category}`;

  // Display confidence
  const confidencePercent = data.confidence
    ? Math.round(data.confidence * 100)
    : 0;
  confidenceValue.textContent = `${confidencePercent}%`;

  // Display suggested response
  responseContent.textContent = data.suggested_reply;
}

// Copy Response
copyBtn.addEventListener("click", () => {
  const text = responseContent.textContent;
  navigator.clipboard
    .writeText(text)
    .then(() => {
      const originalText = copyBtn.innerHTML;
      copyBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <polyline points="20 6 9 17 4 12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Copiado!
        `;
      setTimeout(() => {
        copyBtn.innerHTML = originalText;
      }, 2000);
    })
    .catch((err) => {
      console.error("Error copying text:", err);
      showError("Erro ao copiar texto");
    });
});

// New Analysis
newAnalysisBtn.addEventListener("click", () => {
  resultsSection.classList.add("is-empty");
  resultsSection.classList.remove("has-results");
  document.getElementById("email_text").value = "";
  fileInput.value = "";
  hideFileSelected();
  responseContent.textContent = "";
  categoryBadge.textContent = "";
  confidenceValue.textContent = "";
});

// Loading Functions
function showLoading() {
  loadingOverlay.style.display = "flex";
  submitBtn.disabled = true;
}

function hideLoading() {
  loadingOverlay.style.display = "none";
  submitBtn.disabled = false;
}

// Error Handling - Modal Dialog
function showError(message) {
  // Criar modal se não existir
  let modal = document.getElementById("errorModal");
  if (!modal) {
    modal = createErrorModal();
    document.body.appendChild(modal);
  }

  // Atualizar mensagem e exibir
  document.getElementById("errorMessage").textContent = message;
  modal.style.display = "flex";
}

function createErrorModal() {
  const modal = document.createElement("div");
  modal.id = "errorModal";
  modal.innerHTML = `
    <div class="error-modal-content">
      <div class="error-modal-header">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>Aviso</span>
      </div>
      <div class="error-modal-body">
        <p id="errorMessage"></p>
      </div>
      <div class="error-modal-footer">
        <button onclick="closeErrorModal()" class="error-modal-btn">OK</button>
      </div>
    </div>
  `;
  return modal;
}

function closeErrorModal() {
  const modal = document.getElementById("errorModal");
  if (modal) {
    modal.style.display = "none";
  }
}

// Fechar modal ao clicar fora
document.addEventListener("click", (e) => {
  const modal = document.getElementById("errorModal");
  if (modal && e.target === modal) {
    closeErrorModal();
  }
});

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  console.log("Email Classifier AI initialized");
});
