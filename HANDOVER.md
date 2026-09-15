# DMC Operations Platform - Technical Handover Manual

## 1. Executive Summary

The **Destination Management Company (DMC) Operations Platform** is a full-stack, modular automation suite engineered to eliminate operational bottlenecks in high-touch travel logistics.

It automates four critical operational handover points:
1. **Inquiry-to-Quotation Turnaround**: Compresses 48-hour manual tariff lookups and day-by-day itinerary builds into under 10 minutes using AI structured extraction, dynamic contract matching, and automated markup calculations.
2. **Supplier Operations & Booking Confirmations**: 1-Click WhatsApp and Email booking pings with unique secure tokens for local chauffeurs, guides, hotels, and boat charters, automatically issuing client vouchers upon confirmation.
3. **Daily Ground Dispatch**: Automated evening compilation of next-day run-sheets grouped by driver vehicle plate and licensed guide, with real-time aviation radar delay monitoring.
4. **Financial Operations & FX Risk**: Real-time multi-currency conversions with a 2.5% volatility protection buffer, automated Stripe 30% deposit sessions, and European Travel Margin VAT calculation (EU Directive 2006/112/EC Art. 306 / Italian Art. 74-ter).

---

## 2. System Architecture & Inventory

```mermaid
graph TD
    subgraph ClientLayer ["Client & Partner Touchpoints"]
        Agent[B2B Tour Operator / Client]
        GuestPortal[Mobile Itinerary Portal]
        SupplierWA[Supplier WhatsApp / Email]
        DriverWA[Driver WhatsApp Run-Sheet]
    end

    subgraph AppLayer ["DMC Command Center (Python 3.13 stdlib)"]
        Dashboard[Command Dashboard (HTML5/Tailwind)]
        REST_API[server.py REST API (Port 8080)]
        PDF_Gen[pdf_exporter.py (Native Headless Engine)]
    end

    subgraph ServiceModules ["Core Business Modules"]
        CommGW[comm_gateway.py (Twilio / Meta / SMTP)]
        FlightTrack[flight_tracker.py (Aviation Radar Delay Check)]
        PayCheckout[payment_checkout.py (Stripe Deposit Session)]
        FX_VAT[fx_vat_engine.py (Hedging Buffer & TOMS VAT)]
    end

    subgraph DataLayer ["Data & Workflow Engines"]
        SQLite[(dmc_operations.db)]
        DB_Layer[db.py (Schema & Seed Loader)]
        n8n[n8n Workflow Blueprints (workflows/)]
    end

    Agent -->|Email / RFP| REST_API
    GuestPortal -->|View Trip & Pay Deposit| PayCheckout
    REST_API --> CommGW --> SupplierWA
    REST_API --> CommGW --> DriverWA
    REST_API --> FlightTrack
    REST_API --> PayCheckout
    REST_API --> FX_VAT
    REST_API --> DB_Layer --> SQLite
    REST_API --> PDF_Gen
    Dashboard <--> REST_API
```

### Component Inventory

| File | Purpose | Key Dependencies |
|---|---|---|
| `server.py` | Primary REST API server & static file host | Python standard library (`http.server`, `socketserver`, `json`, `urllib`) |
| `db.py` | Database initialization, migrations, and seed loading | Python standard library (`sqlite3`, `csv`, `os`) |
| `dmc_operations.db` | Persistent relational SQLite database | SQLite 3 |
| `dashboard.html` | Operations Command Dashboard SPA | Tailwind CSS (CDN / local), Vanilla JavaScript |
| `itinerary_portal.html` | Client-facing luxury mobile guest portal | Tailwind CSS, Responsive Web Standards |
| `pdf_exporter.py` | Headless vector PDF document generator | Microsoft Edge or Google Chrome CLI (`--headless=new`) |
| `comm_gateway.py` | Multi-channel WhatsApp & Email communication gateway | Twilio REST API / SMTP (with built-in simulation fallback) |
| `flight_tracker.py` | Aviation radar delay detector & transfer rescheduler | AviationStack / OpenSky API (with built-in simulation fallback) |
| `payment_checkout.py` | Stripe deposit checkout session builder & webhook handler | Stripe REST API (with sandbox simulator fallback) |
| `fx_vat_engine.py` | Multi-currency converter (+2.5% buffer) & TOMS VAT engine | Pure mathematical formulas (EU Art. 306 / Italian Art. 74-ter) |
| `test_runner.js` | Node.js end-to-end simulation runner | Node.js 18+ stdlib (`fs`, `path`) |
| `templates/` | Jinja/Handlebars compatible HTML proposal & voucher templates | Clean semantic HTML5 / CSS3 |
| `workflows/` | Production-ready n8n workflow blueprints (JSON) | n8n v1.0+ |
| `sample_data/` | Seed CSV files for suppliers, tariffs, and sample RFPs | RFC 4180 CSV |

---

## 3. Installation & Local Setup

### Prerequisites
- Python 3.10+ (Recommended: Python 3.13)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- Git 2.30+
- *(Optional)* Microsoft Edge or Google Chrome (required for headless PDF generation)
- *(Optional)* Docker & Docker Compose (for containerized deployment)

### Setup Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-organization/dmc-workflow-automation.git
   cd dmc-workflow-automation
   ```

2. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys (Twilio, Stripe, AviationStack, OpenAI). If left blank, the platform operates in full **Sandbox Simulation Mode**.

3. **Initialize the Database:**
   ```bash
   python db.py
   ```
   *Seeds suppliers, tariffs, and sample bookings automatically.*

4. **Start the Server:**
   ```bash
   python server.py
   ```
   *Launches the server at `http://localhost:8080` and opens `dashboard.html`.*

---

## 4. API Reference

### 1. KPI Metrics
- **Endpoint**: `GET /api/kpis`
- **Response**:
  ```json
  {
    "active_inquiries": 2,
    "suppliers_confirmed": "1 / 4",
    "manifest_runs": "4 Runs",
    "avg_margin": "21.0%"
  }
  ```

### 2. Inquiries & Quoting
- **Endpoint**: `POST /api/inquiries/parse-and-quote`
- **Payload**:
  ```json
  {
    "rfp_text": "VIP couple traveling to Amalfi Sept 20 to 24. Needs airport transfer and Capri yacht.",
    "margin": 0.22
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "inquiry_id": "INQ-2026-1420",
    "destination": "Amalfi Coast & Capri",
    "pax_adults": 2,
    "total_net": 5970.0,
    "margin_pct": 22,
    "gross_price": 7654.0,
    "profit": 1684.0
  }
  ```

### 3. Supplier Confirmations
- **Endpoint**: `POST /api/suppliers/confirm`
- **Payload**:
  ```json
  {
    "item_id": "ITM-2026-001-D2",
    "action": "accept"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "item_id": "ITM-2026-001-D2",
    "status": "Confirmed",
    "voucher_number": "VOUCH-2026-89124"
  }
  ```

### 4. Flight Delay Tracking & Rescheduling
- **Endpoint**: `POST /api/flights/check-and-reschedule`
- **Payload**:
  ```json
  {
    "item_id": "ITM-2026-001-D1",
    "flight_number": "AZ 1284"
  }
  ```
- **Response**:
  ```json
  {
    "flight_status": "Delayed",
    "delay_minutes": 45,
    "original_pickup_time": "14:30",
    "new_pickup_time": "15:15",
    "rescheduled": true
  }
  ```

### 5. Stripe Deposit Link Generator
- **Endpoint**: `POST /api/payments/create-deposit-link`
- **Payload**:
  ```json
  {
    "inquiry_id": "INQ-2026-001",
    "deposit_percent": 0.30
  }
  ```
- **Response**:
  ```json
  {
    "inquiry_id": "INQ-2026-001",
    "deposit_amount": 1976.92,
    "currency": "EUR",
    "checkout_url": "https://checkout.stripe.com/c/pay/..."
  }
  ```

### 6. FX Hedging & TOMS VAT
- **Endpoint**: `POST /api/pricing/convert-currency`
  - **Payload**: `{"amount_eur": 7654.0, "target_currency": "USD", "apply_buffer": true}`
  - **Response**: Effective rate with 2.5% buffer applied (`1.053`), USD total `$8,059.66`.
- **Endpoint**: `POST /api/pricing/calculate-vat`
  - **Payload**: `{"net_cost": 5970.0, "gross_price": 7654.0}`
  - **Response**: `{"vat_scheme": "EU TOMS / Italian Art. 74-ter", "vat_on_margin": 303.67, "net_profit_after_vat": 1380.33}`

---

## 5. Production Deployment Guide

### Option A: Docker Compose (Recommended)
Deploy the DMC Platform and n8n orchestration engine together:
```bash
docker compose up -d
```
- DMC Dashboard & REST API: `http://your-server-ip:8080`
- n8n Workflow Automation: `http://your-server-ip:5678`

### Option B: Linux VPS (Systemd Service)
1. Copy code to `/var/www/dmc-platform`:
   ```bash
   sudo mkdir -p /var/www/dmc-platform
   sudo cp -r . /var/www/dmc-platform/
   ```
2. Create systemd unit `/etc/systemd/system/dmc.service`:
   ```ini
   [Unit]
   Description=DMC Operations Command Server
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/var/www/dmc-platform
   ExecStart=/usr/bin/python3 server.py --no-browser
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now dmc
   ```

### Option C: Reverse Proxy with SSL (Caddy / Nginx)
Using Caddyfile:
```caddy
dmc.yourdomain.com {
    reverse_proxy localhost:8080
}

workflows.yourdomain.com {
    reverse_proxy localhost:5678
}
```

---

## 6. Maintenance & Backup

1. **Database Backup**:
   The SQLite database is stored in `dmc_operations.db`. Create daily automated snapshots:
   ```bash
   sqlite3 dmc_operations.db ".backup 'backups/dmc_$(date +%Y%m%d).db'"
   ```
2. **Rate Expirations**:
   Periodically review `tariffs` table validities (`valid_to` column) before high/low season transitions.
3. **Log Monitoring**:
   Monitor standard output logs via `journalctl -u dmc -f` or Docker logs `docker compose logs -f dmc-app`.
