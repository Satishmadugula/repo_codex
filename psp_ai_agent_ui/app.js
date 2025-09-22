const defaultPspBase = "http://localhost:8100";
const pspBaseInput = document.getElementById("psp-api-base");

const resolveBaseUrl = () => pspBaseInput.value.trim() || defaultPspBase;

const setBusy = (button, busy) => {
  if (!button) return;
  button.disabled = busy;
  button.dataset.busy = busy ? "true" : "false";
};

const renderResult = (targetId, payload) => {
  const target = document.getElementById(targetId);
  if (!target) return;
  if (payload instanceof Error) {
    target.textContent = `Error: ${payload.message}`;
    target.classList.add("has-error");
  } else {
    target.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
    target.classList.remove("has-error");
  }
};

const request = async (method, path, { body, query, formData } = {}) => {
  const base = resolveBaseUrl();
  const url = new URL(path, base.endsWith("/") ? base : `${base}/`);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") return;
      url.searchParams.append(key, value);
    });
  }

  const options = { method };
  if (formData) {
    options.body = formData;
  } else if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  const text = await response.text();
  let data = text;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (err) {
      data = text;
    }
  } else {
    data = { status: response.status, message: response.statusText };
  }

  if (!response.ok) {
    const detail = typeof data === "object" && data !== null ? data.detail || data.message : data;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return data;
};

const handleForm = (formId, handler, resultTarget) => {
  const form = document.getElementById(formId);
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = form.querySelector('[type="submit"]');
    setBusy(submitButton, true);
    try {
      const formData = new FormData(form);
      const result = await handler(formData, form);
      renderResult(resultTarget, result);
    } catch (error) {
      renderResult(resultTarget, error);
    } finally {
      setBusy(submitButton, false);
    }
  });
};

const ocrForm = document.getElementById("ocr-form");
if (ocrForm) {
  ocrForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = ocrForm.querySelector('[type="submit"]');
    setBusy(button, true);
    try {
      const formData = new FormData(ocrForm);
      const merchantEmail = formData.get("merchant_email");
      const documentType = formData.get("document_type");
      if (!merchantEmail || !documentType) {
        throw new Error("Merchant email and document type are required");
      }
      const payload = new FormData();
      const file = formData.get("file");
      if (!(file instanceof File) || !file.name) {
        throw new Error("Select a document to process");
      }
      payload.append("file", file);
      const result = await request("POST", `ocr/process/${encodeURIComponent(documentType)}`, {
        query: { merchant_email: merchantEmail },
        formData: payload,
      });
      renderResult("ocr-result", result);
    } catch (error) {
      renderResult("ocr-result", error);
    } finally {
      setBusy(button, false);
    }
  });
}

handleForm(
  "ocr-feedback-form",
  async (formData) =>
    request("POST", "ocr/feedback", {
      body: {
        merchant_email: formData.get("merchant_email"),
        document_type: formData.get("document_type"),
        reason: formData.get("reason"),
      },
    }),
  "ocr-result"
);

handleForm(
  "risk-score-form",
  async (formData) => {
    const fraudFlags = (formData.get("fraud_flags") || "")
      .split(",")
      .map((flag) => flag.trim())
      .filter(Boolean);
    return request("POST", "risk/score", {
      body: {
        merchant_email: formData.get("merchant_email"),
        category: formData.get("category"),
        location: formData.get("location"),
        credit_score: formData.get("credit_score"),
        fraud_flags: fraudFlags,
      },
    });
  },
  "risk-result"
);

handleForm(
  "fraud-form",
  async (formData) =>
    request("POST", "risk/fraud-check", {
      query: {
        merchant_email: formData.get("merchant_email"),
        business_name: formData.get("business_name"),
        pan: formData.get("pan"),
      },
    }),
  "risk-result"
);

const riskDashboardButton = document.getElementById("risk-dashboard-button");
if (riskDashboardButton) {
  riskDashboardButton.addEventListener("click", async () => {
    setBusy(riskDashboardButton, true);
    try {
      const result = await request("GET", "risk/dashboard");
      renderResult("risk-result", result);
    } catch (error) {
      renderResult("risk-result", error);
    } finally {
      setBusy(riskDashboardButton, false);
    }
  });
}

handleForm(
  "cpv-form",
  async (formData) =>
    request("POST", "compliance/cpv", {
      query: {
        merchant_email: formData.get("merchant_email"),
        address: formData.get("address"),
      },
    }),
  "compliance-result"
);

handleForm(
  "ovd-form",
  async (formData) =>
    request("POST", "compliance/ovd", {
      query: {
        merchant_email: formData.get("merchant_email"),
        document_type: formData.get("document_type"),
        reference_number: formData.get("reference_number"),
      },
    }),
  "compliance-result"
);

handleForm(
  "rekyc-form",
  async (formData) => {
    const completedAt = formData.get("completed_at");
    let isoDate = null;
    if (completedAt) {
      const parsed = new Date(completedAt);
      if (Number.isNaN(parsed.getTime())) {
        throw new Error("Provide a valid completion timestamp");
      }
      isoDate = parsed.toISOString();
    }
    return request("POST", "compliance/rekyc", {
      body: {
        merchant_email: formData.get("merchant_email"),
        completed_at: isoDate,
      },
    });
  },
  "compliance-result"
);

const complianceUpdatesButton = document.getElementById("compliance-updates-button");
if (complianceUpdatesButton) {
  complianceUpdatesButton.addEventListener("click", async () => {
    setBusy(complianceUpdatesButton, true);
    try {
      const result = await request("GET", "compliance/updates");
      renderResult("compliance-result", result);
    } catch (error) {
      renderResult("compliance-result", error);
    } finally {
      setBusy(complianceUpdatesButton, false);
    }
  });
}

handleForm(
  "assign-field-form",
  async (formData) =>
    request("POST", "onboarding/assign-field", {
      query: {
        merchant_email: formData.get("merchant_email"),
        location: formData.get("location"),
      },
    }),
  "onboarding-result"
);

handleForm(
  "orchestrate-form",
  async (formData) =>
    request("GET", "onboarding/orchestrate", {
      query: { merchant_email: formData.get("merchant_email") },
    }),
  "onboarding-result"
);

handleForm(
  "summary-form",
  async (formData) => {
    const highlights = (formData.get("highlights") || "")
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);
    return request("POST", "onboarding/summary", {
      body: {
        merchant_email: formData.get("merchant_email"),
        risk_level: formData.get("risk_level"),
        highlights,
      },
    });
  },
  "onboarding-result"
);

handleForm(
  "merchant-alert-form",
  async (formData) =>
    request("POST", "alerts/merchant", {
      query: {
        merchant_email: formData.get("merchant_email"),
        message: formData.get("message"),
        channel: formData.get("channel"),
      },
    }),
  "alerts-result"
);

handleForm(
  "internal-alert-form",
  async (formData) =>
    request("POST", "alerts/internal", {
      query: {
        message: formData.get("message"),
        severity: formData.get("severity"),
      },
    }),
  "alerts-result"
);

handleForm(
  "anomaly-form",
  async (formData) =>
    request("POST", "alerts/anomaly", {
      query: {
        merchant_email: formData.get("merchant_email"),
        transaction_amount: formData.get("transaction_amount"),
      },
    }),
  "alerts-result"
);

const opsCasesButton = document.getElementById("ops-cases-button");
if (opsCasesButton) {
  opsCasesButton.addEventListener("click", async () => {
    setBusy(opsCasesButton, true);
    try {
      const result = await request("GET", "ops/cases");
      renderResult("alerts-result", result);
    } catch (error) {
      renderResult("alerts-result", error);
    } finally {
      setBusy(opsCasesButton, false);
    }
  });
}

const opsAnalyticsButton = document.getElementById("ops-analytics-button");
if (opsAnalyticsButton) {
  opsAnalyticsButton.addEventListener("click", async () => {
    setBusy(opsAnalyticsButton, true);
    try {
      const result = await request("GET", "ops/analytics");
      renderResult("alerts-result", result);
    } catch (error) {
      renderResult("alerts-result", error);
    } finally {
      setBusy(opsAnalyticsButton, false);
    }
  });
}

renderResult("ocr-result", "Awaiting action…");
renderResult("risk-result", "Awaiting action…");
renderResult("compliance-result", "Awaiting action…");
renderResult("onboarding-result", "Awaiting action…");
renderResult("alerts-result", "Awaiting action…");
