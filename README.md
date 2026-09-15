# 🏖️ Destination Management Company (DMC) Operations Platform

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Zero-Dependency Core](https://img.shields.io/badge/core%20deps-zero%20(stdlib)-brightgreen.svg)]()

A modular, full-stack automation platform built for **Destination Management Companies (DMCs)** and incoming tour operators to eliminate manual operational bottlenecks across the entire travel lifecycle.

---

## ⚡ Key Capabilities

* **✨ AI Inquiry Intake & Rapid Quoting**: Parses unstructured emails & RFPs, matches contracted supplier tariffs, applies a dynamic profit margin (e.g., $22\%$), and outputs luxury proposals in under 10 minutes.
* **📲 1-Click Supplier Confirmations**: Generates tokenized accept/decline links dispatched via **WhatsApp Business** or **Email** to local chauffeurs, guides, and hotels. Automatic confirmation updates database and issues client ground vouchers.
* **📋 Daily Operations & Manifest Center**: Assembles next-day driver and guide run-sheets grouped by vehicle plate and certified guide.
* **📡 Live Flight Radar Monitoring**: Monitors flight delays (e.g. `AZ 1284`), auto-reschedules chauffeur airport pickup times, and pings drivers on WhatsApp.
* **💳 30% Booking Deposit Checkout**: Integrated Stripe Checkout session generator to secure client reservations online.
* **💱 FX Volatility Hedging & EU TOMS VAT**: Applies a $2.5\%$ currency risk buffer on USD/GBP quotes and calculates European Travel Margin Scheme VAT (EU Art. 306 / Italian Art. 74-ter).
* **📄 Zero-Dependency Native PDF Exporter**: Headless vector PDF generation using Windows Edge / Chrome CLI (`msedge --headless=new`).
* **📱 VIP Client Mobile Itinerary Portal**: Interactive web portal for traveling guests featuring departure countdowns, day-by-day programs, and 24/7 WhatsApp concierge.

---

## 📁 Repository Structure

```
dmc-workflow-automation/
├── .github/workflows/ci.yml         # GitHub Actions automated CI test suite
├── .env.example                     # API credentials template (Stripe, Twilio, AviationStack)
├── .gitignore                       # Standard git ignore patterns
├── Dockerfile                       # Production container definition
├── docker-compose.yml               # Multi-container orchestration (DMC App + n8n)
├── deploy.sh                        # One-command Linux/macOS deployment script
├── deploy.ps1                       # One-command Windows PowerShell deployment script
├── HANDOVER.md                      # Comprehensive Technical Handover Manual
├── README.md                        # Project overview & quickstart
├── data_schema.md                   # Database entity-relationship documentation
├── requirements.txt                 # Python environment specification
│
├── dashboard.html                   # DMC Operations Command Dashboard (SPA)
├── itinerary_portal.html            # VIP Client Mobile Guest Portal
├── server.py                        # Python stdlib REST API & static file server
├── db.py                            # SQLite database manager & migration engine
├── dmc_operations.db                # Persistent relational database
│
├── comm_gateway.py                  # Multi-channel WhatsApp (Twilio/Meta) & Email gateway
├── flight_tracker.py                # Flight delay detector & transfer auto-rescheduler
├── payment_checkout.py              # Stripe deposit session generator
├── fx_vat_engine.py                 # Multi-currency hedging & EU TOMS VAT engine
├── pdf_exporter.py                  # Native headless PDF generation utility
│
├── sample_data/                     # Seed datasets
│   ├── suppliers_sample.csv         # Partner supplier directory
│   ├── tariffs_sample.csv           # Contract rates & seasonality
│   └── inquiries_sample.csv         # Inbound sample client RFPs
├── templates/                       # HTML presentation templates
│   ├── itinerary_proposal.html      # Luxury guest itinerary proposal
│   └── service_voucher.html         # Ground operator confirmation voucher
└── workflows/                       # Production n8n workflow blueprints
    ├── 01_inquiry_to_proposal.json  # RFP extraction -> Costing -> Proposal
    ├── 02_supplier_confirmation_and_vouchers.json # 1-Click supplier pings
    └── 03_daily_operations_manifest.json # Daily field manifest dispatch
```

---

## 🚀 Quickstart

### 1. Clone & Setup
```bash
git clone https://github.com/your-organization/dmc-workflow-automation.git
cd dmc-workflow-automation
cp .env.example .env
```

### 2. Run with One Command

**On Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**On Linux / macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**With Docker Compose:**
```bash
docker compose up -d
```

### 3. Open in Browser
- **DMC Command Center**: `http://localhost:8080/dashboard.html`
- **VIP Guest Portal**: `http://localhost:8080/itinerary_portal.html`
- **n8n Automation Engine** *(if running Docker)*: `http://localhost:5678`

---

## 📖 Handover & Documentation

For complete architectural details, API specifications, operational runbooks, and production maintenance guidelines, please consult the **[Technical Handover Manual (HANDOVER.md)](HANDOVER.md)**.
