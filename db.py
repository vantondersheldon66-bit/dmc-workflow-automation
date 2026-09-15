"""
DMC Operations Database Layer (SQLite stdlib)
Initializes tables and seeds with contract tariffs, suppliers, and inquiries.
"""

import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dmc_operations.db")
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Suppliers Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT,
        contact_person TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        whatsapp_number TEXT,
        payment_terms TEXT,
        rating INTEGER
    )
    """)

    # 2. Tariffs Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tariffs (
        tariff_id TEXT PRIMARY KEY,
        supplier_id TEXT REFERENCES suppliers(supplier_id),
        service_title TEXT NOT NULL,
        category TEXT NOT NULL,
        pricing_unit TEXT,
        currency TEXT DEFAULT 'EUR',
        net_rate REAL NOT NULL,
        valid_from TEXT,
        valid_to TEXT,
        cancellation_policy TEXT
    )
    """)

    # 3. Inquiries Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        inquiry_id TEXT PRIMARY KEY,
        client_name TEXT NOT NULL,
        client_email TEXT,
        client_country TEXT,
        pax_adults INTEGER DEFAULT 2,
        pax_children INTEGER DEFAULT 0,
        travel_start_date TEXT,
        travel_end_date TEXT,
        destination TEXT NOT NULL,
        budget_currency TEXT DEFAULT 'EUR',
        service_tier TEXT DEFAULT 'Luxury',
        special_requests TEXT,
        status TEXT DEFAULT 'New RFP',
        net_total_cost REAL DEFAULT 0,
        margin_percentage REAL DEFAULT 0.22,
        gross_selling_price REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. Itinerary Items Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS itinerary_items (
        item_id TEXT PRIMARY KEY,
        inquiry_id TEXT REFERENCES inquiries(inquiry_id),
        day_number INTEGER,
        service_date TEXT,
        service_time TEXT,
        tariff_id TEXT REFERENCES tariffs(tariff_id),
        supplier_id TEXT REFERENCES suppliers(supplier_id),
        service_title TEXT NOT NULL,
        service_type TEXT,
        service_description TEXT,
        quantity INTEGER DEFAULT 1,
        unit_cost_net REAL NOT NULL,
        net_total_cost REAL NOT NULL,
        supplier_status TEXT DEFAULT 'Pending Dispatch',
        confirmation_token TEXT,
        voucher_number TEXT
    )
    """)

    # Seed Suppliers if empty
    cur.execute("SELECT COUNT(*) FROM suppliers")
    if cur.fetchone()[0] == 0:
        sup_csv = os.path.join(SAMPLE_DIR, "suppliers_sample.csv")
        if os.path.exists(sup_csv):
            with open(sup_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                    INSERT INTO suppliers (supplier_id, name, category, location, contact_person, contact_email, contact_phone, whatsapp_number, payment_terms, rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (row['supplier_id'], row['name'], row['category'], row['location'], row['contact_person'], row['contact_email'], row['contact_phone'], row['whatsapp_number'], row['payment_terms'], int(row['rating'])))

    # Seed Tariffs if empty
    cur.execute("SELECT COUNT(*) FROM tariffs")
    if cur.fetchone()[0] == 0:
        tar_csv = os.path.join(SAMPLE_DIR, "tariffs_sample.csv")
        if os.path.exists(tar_csv):
            with open(tar_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                    INSERT INTO tariffs (tariff_id, supplier_id, service_title, category, pricing_unit, currency, net_rate, valid_from, valid_to, cancellation_policy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (row['tariff_id'], row['supplier_id'], row['service_title'], row['category'], row['pricing_unit'], row['currency'], float(row['net_rate']), row['valid_from'], row['valid_to'], row['cancellation_policy']))

    # Seed Inquiries & Items if empty
    cur.execute("SELECT COUNT(*) FROM inquiries")
    if cur.fetchone()[0] == 0:
        inq_csv = os.path.join(SAMPLE_DIR, "inquiries_sample.csv")
        if os.path.exists(inq_csv):
            with open(inq_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                    INSERT INTO inquiries (inquiry_id, client_name, client_email, client_country, pax_adults, pax_children, travel_start_date, travel_end_date, destination, budget_currency, service_tier, special_requests, status, net_total_cost, margin_percentage, gross_selling_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (row['inquiry_id'], row['client_name'], row['client_email'], row['client_country'], int(row['pax_adults']), int(row['pax_children']), row['travel_start_date'], row['travel_end_date'], row['destination'], row['budget_currency'], row['service_tier'], row['special_requests'], row['status'], float(row['net_total_cost']), float(row['margin_percentage']), float(row['gross_selling_price'])))

        # Insert default sample items for INQ-2026-001
        sample_items = [
            ("ITM-2026-001-D1", "INQ-2026-001", 1, "2026-09-20", "14:30", "TAR-TRN-01", "SUP-TRN-001", "Private Mercedes V-Class Airport Transfer", "Private Transport", "Meet & greet at Naples Airport (NAP) arrivals hall.", 1, 180.0, 180.0, "Confirmed", "tok_01", "VOUCH-2026-98144"),
            ("ITM-2026-001-D2", "INQ-2026-001", 2, "2026-09-21", "09:30", "TAR-GDE-01", "SUP-GDE-001", "Private VIP 3-Hour Guided Tour of Pompeii Ruins", "Licensed Guide", "Certified archaeologist guide for private ruins walk.", 1, 280.0, 280.0, "Pending Dispatch", "tok_02", None),
            ("ITM-2026-001-D3", "INQ-2026-001", 3, "2026-09-22", "10:00", "TAR-ACT-01", "SUP-ACT-001", "Full Day Private Riva Yacht Charter around Capri Island", "Boat Charter", "Private boat charter with prosecco, captain, and fuel.", 1, 1900.0, 1900.0, "Pending Dispatch", "tok_03", None),
            ("ITM-2026-001-D4", "INQ-2026-001", 4, "2026-09-24", "11:00", "TAR-TRN-02", "SUP-TRN-001", "Sorrento to Naples Airport Transfer", "Private Transport", "Mercedes chauffeur transfer from hotel to airport.", 1, 160.0, 160.0, "Pending Dispatch", "tok_04", None),
        ]
        for itm in sample_items:
            cur.execute("""
            INSERT OR IGNORE INTO itinerary_items (item_id, inquiry_id, day_number, service_date, service_time, tariff_id, supplier_id, service_title, service_type, service_description, quantity, unit_cost_net, net_total_cost, supplier_status, confirmation_token, voucher_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, itm)

    conn.commit()
    conn.close()
    print("[OK] SQLite database initialized and seeded successfully.")

if __name__ == '__main__':
    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    init_db()
