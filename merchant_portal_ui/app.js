const defaultMerchantBase = "http://localhost:8000";
const merchantBaseInput = document.getElementById("merchant-api-base");

const resolveBaseUrl = () => merchantBaseInput.value.trim() || defaultMerchantBase;

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

handleForm(
  "signup-form",
  async (formData) =>
    request("POST", "accounts/signup", {
      body: {
        email: formData.get("email"),
        phone_number: formData.get("phone_number"),
        preferred_language: formData.get("preferred_language"),
      },
    }),
  "account-result"
);

handleForm(
  "otp-form",
  async (formData) =>
    request("POST", "accounts/verify-otp", {
      body: {
        email: formData.get("email"),
        otp: formData.get("otp"),
      },
    }),
  "account-result"
);

handleForm(
  "device-form",
  async (formData) =>
    request("POST", "accounts/register-device", {
      body: {
        email: formData.get("email"),
        device_fingerprint: formData.get("device_fingerprint"),
        mfa_token: formData.get("mfa_token") || null,
      },
    }),
  "account-result"
);

handleForm(
  "checklist-form",
  async (formData) =>
    request("POST", "kyc/checklist", {
      body: { entity_type: formData.get("entity_type") },
    }),
  "kyc-result"
);

const kycUploadForm = document.getElementById("kyc-upload-form");
if (kycUploadForm) {
  kycUploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = kycUploadForm.querySelector('[type="submit"]');
    setBusy(button, true);
    try {
      const formData = new FormData(kycUploadForm);
      const documentType = formData.get("document_type");
      const merchantEmail = formData.get("merchant_email");
      if (!documentType || !merchantEmail) {
        throw new Error("Document type and merchant email are required");
      }
      const payload = new FormData();
      const file = formData.get("file");
      if (!(file instanceof File) || !file.name) {
        throw new Error("Select a document to upload");
      }
      payload.append("file", file);
      const result = await request("POST", `kyc/upload/${encodeURIComponent(documentType)}`, {
        query: { merchant_email: merchantEmail },
        formData: payload,
      });
      renderResult("kyc-result", result);
    } catch (error) {
      renderResult("kyc-result", error);
    } finally {
      setBusy(button, false);
    }
  });
}

handleForm(
  "kyc-status-form",
  async (formData) =>
    request("GET", "kyc/status", {
      query: { merchant_email: formData.get("merchant_email") },
    }),
  "kyc-result"
);

handleForm(
  "bank-verify-form",
  async (formData) =>
    request("POST", "banking/verify-bank", {
      body: {
        merchant_email: formData.get("merchant_email"),
        account_number: formData.get("account_number"),
        ifsc: formData.get("ifsc"),
      },
    }),
  "banking-result"
);

handleForm(
  "business-verify-form",
  async (formData) =>
    request("POST", "banking/business-verification", {
      body: {
        merchant_email: formData.get("merchant_email"),
        pan: formData.get("pan") || null,
        gstin: formData.get("gstin") || null,
        website_url: formData.get("website_url") || null,
      },
    }),
  "banking-result"
);

handleForm(
  "progress-form",
  async (formData) =>
    request("GET", "onboarding/progress", {
      query: { merchant_email: formData.get("merchant_email") },
    }),
  "onboarding-result"
);

handleForm(
  "checklist-update-form",
  async (formData) =>
    request("POST", "onboarding/update-checklist", {
      query: {
        merchant_email: formData.get("merchant_email"),
        item: formData.get("item"),
        completed: formData.get("completed") ? "true" : "false",
      },
    }),
  "onboarding-result"
);

handleForm(
  "assistance-form",
  async (formData) =>
    request("POST", "onboarding/assistance", {
      body: {
        merchant_email: formData.get("merchant_email"),
        assistance_mode: formData.get("assistance_mode"),
        preferred_time: formData.get("preferred_time") || null,
        location: formData.get("location") || null,
      },
    }),
  "onboarding-result"
);

const nudgesButton = document.getElementById("nudges-button");
if (nudgesButton) {
  nudgesButton.addEventListener("click", async () => {
    setBusy(nudgesButton, true);
    try {
      const result = await request("POST", "onboarding/nudges");
      renderResult("onboarding-result", result);
    } catch (error) {
      renderResult("onboarding-result", error);
    } finally {
      setBusy(nudgesButton, false);
    }
  });
}

handleForm(
  "faq-form",
  () => request("GET", "support/faqs"),
  "support-result"
);

handleForm(
  "ticket-form",
  async (formData) =>
    request("POST", "support/ticket", {
      body: {
        merchant_email: formData.get("merchant_email"),
        language: formData.get("language"),
        question: formData.get("question"),
      },
    }),
  "support-result"
);

handleForm(
  "chat-start-form",
  async (formData) =>
    request("POST", "support/chat/start", {
      query: {
        merchant_email: formData.get("merchant_email"),
        language: formData.get("language"),
      },
    }),
  "support-result"
);

handleForm(
  "chat-message-form",
  async (formData) =>
    request("POST", `support/chat/${encodeURIComponent(formData.get("session_id"))}`, {
      body: {
        role: "merchant",
        content: formData.get("content"),
      },
    }),
  "support-result"
);

renderResult("account-result", "Awaiting action…");
renderResult("kyc-result", "Awaiting action…");
renderResult("banking-result", "Awaiting action…");
renderResult("onboarding-result", "Awaiting action…");
renderResult("support-result", "Awaiting action…");
