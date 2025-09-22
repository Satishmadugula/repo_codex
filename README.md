# AI-Driven Omnichannel Merchant Onboarding Platform

This repository contains two FastAPI-based backends that implement the merchant and PSP (AI agent) side requirements for an AI-driven omnichannel merchant onboarding solution. Both services use MongoDB as the data store and integrate with Ollama for OCR-assisted document processing.

## Repository Structure

- `merchant_portal/` – Merchant-facing APIs that power account creation, KYC submission, verification, assisted onboarding, and multilingual support needs.
- `psp_ai_agent/` – PSP representative (AI agent) APIs that automate OCR, risk scoring, compliance, fraud detection, case triage, and proactive alerts.

Each project is self-contained with its own FastAPI app, dependency modules, and service layers.

## Merchant Portal Service

### Key Features
- OTP-based and passwordless account creation with device fingerprinting and MFA helpers.
- KYC checklist generation per entity type, multi-format uploads, inline compliance notes, and document status tracking.
- Bank verification workflow with penny-drop status updates, business verification via PAN/GSTIN placeholders, and compliance notes.
- Assisted onboarding scheduler with kiosk/call-centre options, progress dashboards, and automated nudges.
- Vernacular FAQs, AI chat session scaffolding, and escalation-ready ticket logging.

### Running the Service

```bash
cd merchant_portal
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MERCHANT_MONGODB_URI="mongodb://localhost:27017"
uvicorn app.main:app --reload --port 8000
```

### Notable Modules
- `app/services/account_service.py` – Handles OTP, MFA, and fraud detection heuristics.
- `app/services/kyc_service.py` – Manages entity checklists, uploads, and document feedback.
- `app/services/onboarding_service.py` – Tracks progress, schedules assistance, and generates nudges.

## PSP AI Agent Service

### Key Features
- OCR pipeline orchestrated via Ollama (`llava` by default) for PAN/GSTIN extraction and scoring.
- Risk scoring engine with configurable modifiers, fraud checks, and dynamic transaction limit settings.
- Compliance automation for CPV, OVD verification, re-KYC scheduling, and regulatory logs.
- Field verification orchestration, ops dashboards, funnel analytics, and proactive alerts.
- Anomaly detection that pauses settlements, escalates to internal ops, and notifies merchants.

### Running the Service

```bash
cd psp_ai_agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PSP_MONGODB_URI="mongodb://localhost:27017"
export OLLAMA_BASE_URL="http://localhost:11434"
uvicorn app.main:app --reload --port 8100
```

Ensure `ollama serve` is running with the configured vision-capable model (e.g. `llava`).

### Notable Modules
- `app/services/ocr_service.py` – Upload handling, OCR calls to Ollama, scoring, and merchant feedback.
- `app/services/risk_service.py` – Comprehensive risk engine with underwriting recommendations.
- `app/services/alert_service.py` – Merchant nudges, internal ops alerts, and anomaly management.

## Environment Variables

| Service | Variable | Description |
| --- | --- | --- |
| Merchant Portal | `MERCHANT_MONGODB_URI` | MongoDB connection string |
| Merchant Portal | `MERCHANT_DB_NAME` | Optional override for database name |
| Merchant Portal | `MERCHANT_APP_NAME` | Custom FastAPI title |
| PSP AI Agent | `PSP_MONGODB_URI` | MongoDB connection string |
| PSP AI Agent | `PSP_DB_NAME` | Optional override for database name |
| PSP AI Agent | `PSP_APP_NAME` | Custom FastAPI title |
| PSP AI Agent | `OLLAMA_BASE_URL` | URL where `ollama serve` is reachable |
| PSP AI Agent | `OLLAMA_OCR_MODEL` | Ollama model to use for OCR (default `llava`) |

## Development Notes

- Both services rely on Motor (async MongoDB driver) to keep request handlers non-blocking.
- File uploads are persisted to local directories (`uploads/` and `psp_uploads/`) before OCR/validation.
- Risk scoring combines merchant category, geography, and credit history with fraud signals to derive dynamic transaction policies.
- Compliance helpers keep CPV/OVD audit logs and ensure re-KYC cycles remain compliant with RBI guidelines.
- Alerting services centralise merchant and internal notifications to support proactive onboarding assistance.

## Running Tests

Unit tests are not bundled, but you can validate that both FastAPI apps load by running:

```bash
uvicorn merchant_portal.app.main:app --reload
uvicorn psp_ai_agent.app.main:app --reload
```

## License

MIT
