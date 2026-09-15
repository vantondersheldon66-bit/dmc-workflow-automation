"""
Enhanced DMC Command Server with SQLite-backed REST API
Zero external dependencies (Python 3 stdlib: http.server, sqlite3, json)
"""

import http.server
import socketserver
import os
import sys
import json
import re
import urllib.parse
from datetime import datetime, timedelta
import db
from comm_gateway import gateway
from flight_tracker import flight_tracker
from payment_checkout import payment_engine
from fx_vat_engine import fx_vat_engine

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DMCRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/kpis':
            self.handle_get_kpis()
        elif path == '/api/inquiries':
            self.handle_get_inquiries()
        elif path == '/api/tariffs':
            self.handle_get_tariffs()
        elif path == '/api/suppliers/items':
            self.handle_get_supplier_items()
        elif path.startswith('/api/proposals/'):
            inquiry_id = path.split('/')[-1]
            self.handle_get_proposal_html(inquiry_id)
        elif path.startswith('/api/vouchers/'):
            item_id = path.split('/')[-1]
            self.handle_get_voucher_html(item_id)
        else:
            # Fall back to standard static file serving
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(length) if length > 0 else b'{}'
        try:
            body = json.loads(body_bytes.decode('utf-8'))
        except Exception:
            body = {}

        if path == '/api/inquiries/parse-and-quote':
            self.handle_parse_and_quote(body)
        elif path == '/api/suppliers/confirm':
            self.handle_supplier_confirm(body)
        elif path == '/api/manifests/dispatch':
            self.handle_manifest_dispatch(body)
        elif path == '/api/flights/check-and-reschedule':
            item_id = body.get("item_id", "ITM-2026-001-D1")
            flight_num = body.get("flight_number", "AZ 1284")
            result = flight_tracker.auto_reschedule_transfer(item_id, flight_num)
            self.send_json(result)
        elif path == '/api/payments/create-deposit-link':
            inquiry_id = body.get("inquiry_id", "INQ-2026-001")
            deposit_pct = float(body.get("deposit_percent", 0.30))
            result = payment_engine.create_deposit_session(inquiry_id, deposit_pct)
            self.send_json(result)
        elif path == '/api/payments/simulate-success':
            inquiry_id = body.get("inquiry_id", "INQ-2026-001")
            result = payment_engine.process_successful_payment(inquiry_id)
            self.send_json(result)
        elif path == '/api/pricing/convert-currency':
            amount = float(body.get("amount_eur", 0))
            curr = body.get("target_currency", "USD")
            buf = body.get("apply_buffer", True)
            result = fx_vat_engine.convert_from_eur(amount, curr, buf)
            self.send_json(result)
        elif path == '/api/pricing/calculate-vat':
            net = float(body.get("net_cost", 0))
            gross = float(body.get("gross_price", 0))
            result = fx_vat_engine.calculate_travel_margin_vat(net, gross)
            self.send_json(result)
        else:
            self.send_json({"error": "Endpoint not found"}, status=404)

    # --- API HANDLERS ---

    def handle_get_kpis(self):
        conn = db.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM inquiries")
        total_inq = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM itinerary_items WHERE supplier_status = 'Confirmed'")
        confirmed_sup = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM itinerary_items")
        total_sup = cur.fetchone()[0]

        cur.execute("SELECT AVG(margin_percentage) FROM inquiries WHERE margin_percentage > 0")
        avg_margin_row = cur.fetchone()[0]
        avg_margin = round((avg_margin_row or 0.22) * 100, 1)

        conn.close()
        self.send_json({
            "active_inquiries": total_inq,
            "suppliers_confirmed": f"{confirmed_sup} / {total_sup}",
            "manifest_runs": f"{total_sup} Runs",
            "avg_margin": f"{avg_margin}%"
        })

    def handle_get_inquiries(self):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM inquiries ORDER BY created_at DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        self.send_json({"inquiries": rows})

    def handle_get_tariffs(self):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tariffs ORDER BY category, net_rate")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        self.send_json({"tariffs": rows})

    def handle_get_supplier_items(self):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT i.*, s.name as supplier_name, s.whatsapp_number, s.category as supplier_category, q.client_name
        FROM itinerary_items i
        LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
        LEFT JOIN inquiries q ON i.inquiry_id = q.inquiry_id
        ORDER BY i.service_date, i.service_time
        """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        self.send_json({"items": rows})

    def handle_parse_and_quote(self, body):
        rfp_text = body.get("rfp_text", "")
        margin = float(body.get("margin", 0.22))

        # Basic NLP / rule-based extraction from RFP
        client_name = "VIP Client"
        client_match = re.search(r"(?:regards|thanks|from)[\s,:]+([A-Za-z\s]+)", rfp_text, re.IGNORECASE)
        if client_match:
            client_name = client_match.group(1).strip().split('\n')[0]

        pax_adults = 2
        pax_match = re.search(r"(\d+)\s*(?:pax|guests|adults|people)", rfp_text, re.IGNORECASE)
        if pax_match:
            pax_adults = int(pax_match.group(1))

        destination = "Amalfi Coast & Capri"
        if "sorrento" in rfp_text.lower():
            destination = "Sorrento & Amalfi"
        elif "capri" in rfp_text.lower():
            destination = "Amalfi Coast & Capri"

        conn = db.get_connection()
        cur = conn.cursor()

        # Query relevant tariffs
        cur.execute("SELECT * FROM tariffs")
        all_tariffs = {t['tariff_id']: dict(t) for t in cur.fetchall()}

        # Match services
        matched_items = []
        # Airport transfer
        if "TAR-TRN-01" in all_tariffs:
            t = all_tariffs["TAR-TRN-01"]
            matched_items.append((1, "2026-09-20", "14:30", t, "Private Mercedes V-Class Airport Transfer"))
        # Guide
        if "TAR-GDE-01" in all_tariffs:
            t = all_tariffs["TAR-GDE-01"]
            matched_items.append((2, "2026-09-21", "09:30", t, "Private VIP 3-Hour Pompeii Archaeology Guide"))
        # Yacht or excursion
        if "TAR-ACT-01" in all_tariffs:
            t = all_tariffs["TAR-ACT-01"]
            matched_items.append((3, "2026-09-22", "10:00", t, "Full Day Private Riva Yacht Charter (Capri)"))
        # Hotel 3 nights
        if "TAR-HTL-02" in all_tariffs:
            t = all_tariffs["TAR-HTL-02"]
            matched_items.append((1, "2026-09-20", "15:00", t, "3 Nights Deluxe Sea View Suite"))

        total_net = sum(item[3]['net_rate'] for item in matched_items)
        gross_price = round(total_net / (1 - margin))

        inquiry_id = f"INQ-2026-{datetime.now().strftime('%M%S')}"
        cur.execute("""
        INSERT INTO inquiries (inquiry_id, client_name, client_email, destination, pax_adults, travel_start_date, travel_end_date, status, net_total_cost, margin_percentage, gross_selling_price, special_requests)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (inquiry_id, client_name, "advisor@luxurytravel.mock", destination, pax_adults, "2026-09-20", "2026-09-24", "Proposal Drafted", total_net, margin, gross_price, rfp_text[:250]))

        # Insert items
        for idx, itm in enumerate(matched_items, 1):
            item_id = f"{inquiry_id}-D{idx}"
            cur.execute("""
            INSERT INTO itinerary_items (item_id, inquiry_id, day_number, service_date, service_time, tariff_id, supplier_id, service_title, service_type, service_description, quantity, unit_cost_net, net_total_cost, supplier_status, confirmation_token)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (item_id, inquiry_id, itm[0], itm[1], itm[2], itm[3]['tariff_id'], itm[3]['supplier_id'], itm[4], itm[3]['category'], f"Contracted service for {pax_adults} guests.", 1, itm[3]['net_rate'], itm[3]['net_rate'], "Pending Dispatch", f"tok_{item_id}"))

        conn.commit()
        conn.close()

        self.send_json({
            "success": True,
            "inquiry_id": inquiry_id,
            "client_name": client_name,
            "destination": destination,
            "pax_adults": pax_adults,
            "total_net": total_net,
            "margin_pct": round(margin * 100),
            "gross_price": gross_price,
            "profit": gross_price - total_net,
            "items_count": len(matched_items)
        })

    def handle_supplier_confirm(self, body):
        item_id = body.get("item_id")
        action = body.get("action", "accept")

        status = "Confirmed" if action == "accept" else "Declined"
        voucher_num = f"VOUCH-2026-{datetime.now().strftime('%f')[:5]}" if action == "accept" else None

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
        UPDATE itinerary_items
        SET supplier_status = ?, voucher_number = ?
        WHERE item_id = ?
        """, (status, voucher_num, item_id))
        conn.commit()
        conn.close()

        self.send_json({
            "success": True,
            "item_id": item_id,
            "status": status,
            "voucher_number": voucher_num
        })

    def handle_manifest_dispatch(self, body):
        date = body.get("date", "2026-09-20")
        msg = f"""📋 *DAILY DISPATCH MANIFEST - {date}*
Driver: Antonio De Luca | Vehicle: Mercedes V-Class (FX 892 TR)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stop #1: 14:30 - Airport Transfer
• Lead Guest: Sarah Jenkins (2 Pax)
• Flight: AZ 1284 (FCO -> NAP) - STATUS: ON TIME
• Pickup: Naples Int'l Airport (NAP) Arrivals Gate
• Dropoff: Grand Hotel Excelsior Vittoria, Sorrento
• Notes: VIP 25th anniversary. Provide chilled water and cold towels.

📞 24/7 Operations Duty Desk: +39 081 555 9999"""
        self.send_json({
            "success": True,
            "dispatched_count": 2,
            "manifest_text": msg
        })

    def handle_get_proposal_html(self, inquiry_id):
        # Serve the generated proposal HTML
        path = os.path.join(DIRECTORY, "output_sample_proposal.html")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_json({"error": "Proposal not found"}, status=404)

    def handle_get_voucher_html(self, item_id):
        path = os.path.join(DIRECTORY, "output_sample_voucher.html")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_json({"error": "Voucher not found"}, status=404)


if __name__ == '__main__':
    db.init_db()
    with socketserver.TCPServer(("", PORT), DMCRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/dashboard.html"
        print("=" * 65)
        print("🚀 DMC OPERATIONS COMMAND SERVER + REST API (SQLITE)")
        print("=" * 65)
        print(f"Web Dashboard: {url}")
        print(f"REST API Endpoints:")
        print(f"  - GET  /api/kpis")
        print(f"  - GET  /api/inquiries")
        print(f"  - GET  /api/tariffs")
        print(f"  - GET  /api/suppliers/items")
        print(f"  - POST /api/inquiries/parse-and-quote")
        print(f"  - POST /api/suppliers/confirm")
        print(f"  - POST /api/manifests/dispatch")
        print("=" * 65)
        print("Press Ctrl+C to terminate.")

        if "--no-browser" not in sys.argv:
            import webbrowser
            webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()
