const fs = require('fs');
const path = require('path');

console.log('================================================================');
console.log('🚀 DMC AUTOMATION SUITE: END-TO-END SIMULATION RUNNER');
console.log('================================================================\n');

// 1. Load Tariffs from CSV
const tariffsCsv = fs.readFileSync(path.join(__dirname, 'sample_data', 'tariffs_sample.csv'), 'utf8');
const tariffLines = tariffsCsv.trim().split('\n').slice(1);
const tariffs = tariffLines.map(line => {
  const cols = line.split(',');
  return {
    tariff_id: cols[0],
    supplier_id: cols[1],
    service_title: cols[2],
    category: cols[3],
    pricing_unit: cols[4],
    currency: cols[5],
    net_rate: parseFloat(cols[6])
  };
});
console.log(`✓ Loaded ${tariffs.length} contracted supplier tariffs from CSV.`);

// 2. Incoming Sample RFP
const mockRFP = {
  inquiry_id: "INQ-2026-001",
  client_name: "Sarah Jenkins (Signature Travel Network)",
  client_email: "sjenkins@signatureluxury.mock",
  destination: "Amalfi Coast & Capri",
  travel_start_date: "2026-09-20",
  travel_end_date: "2026-09-24",
  pax_adults: 2,
  pax_children: 0,
  service_tier: "Ultra-VIP",
  special_requests: "25th Anniversary celebration. Needs Mercedes V-Class, luxury sea view hotel, private Pompeii guide, and private Capri Riva yacht."
};

console.log('\n--- SIMULATING WORKFLOW 1: QUOTATION & PROPOSAL GENERATION ---');
console.log(`Processing RFP for: ${mockRFP.client_name}`);
console.log(`Destination: ${mockRFP.destination} | Dates: ${mockRFP.travel_start_date} to ${mockRFP.travel_end_date}`);

// Tariff Matcher Logic
const itinerarySchedule = [
  { day: 1, date: "2026-09-20", tariff_id: "TAR-TRN-01", type: "Arrival Transfer" },
  { day: 2, date: "2026-09-21", tariff_id: "TAR-GDE-01", type: "Private Archaeology Guide" },
  { day: 3, date: "2026-09-22", tariff_id: "TAR-ACT-01", type: "Private Yacht Charter" },
  { day: 4, date: "2026-09-24", tariff_id: "TAR-TRN-02", type: "Departure Transfer" }
];

let totalNet = 0;
const enrichedItems = itinerarySchedule.map(s => {
  const tariff = tariffs.find(t => t.tariff_id === s.tariff_id);
  totalNet += tariff.net_rate;
  return {
    day_number: s.day,
    service_date: s.date,
    service_title: tariff.service_title,
    service_type: s.type,
    service_description: `Exclusive private service for ${mockRFP.pax_adults} guests. Supplier reference: ${tariff.supplier_id}.`,
    net_cost: tariff.net_rate
  };
});

// Add 3 nights accommodation (TAR-HTL-02)
const hotelTariff = tariffs.find(t => t.tariff_id === "TAR-HTL-02");
const hotelNights = 3;
const hotelTotalNet = hotelTariff.net_rate * hotelNights;
totalNet += hotelTotalNet;

const margin = 0.22; // 22% margin
const grossPrice = Math.round(totalNet / (1 - margin));

console.log(`-> Total Net Supplier Cost: €${totalNet.toLocaleString()}`);
console.log(`-> Target Margin: 22%`);
console.log(`-> Gross Selling Price: €${grossPrice.toLocaleString()}`);

// Render Proposal HTML
let proposalTemplate = fs.readFileSync(path.join(__dirname, 'templates', 'itinerary_proposal.html'), 'utf8');
proposalTemplate = proposalTemplate
  .replace(/{{inquiry_id}}/g, mockRFP.inquiry_id)
  .replace(/{{destination}}/g, mockRFP.destination)
  .replace(/{{client_name}}/g, mockRFP.client_name)
  .replace(/{{travel_start_date}}/g, mockRFP.travel_start_date)
  .replace(/{{travel_end_date}}/g, mockRFP.travel_end_date)
  .replace(/{{pax_adults}}/g, mockRFP.pax_adults)
  .replace(/{{pax_kids_info}}/g, "")
  .replace(/{{service_tier}}/g, mockRFP.service_tier)
  .replace(/{{currency}}/g, "EUR")
  .replace(/{{total_price}}/g, grossPrice.toLocaleString());

// Replace items loop
let itemsHtml = '';
enrichedItems.forEach(item => {
  itemsHtml += `
  <div class="day-card">
    <div class="day-header">
      <span class="day-tag">Day ${item.day_number}</span>
      <span class="day-date">${item.service_date}</span>
    </div>
    <h3 class="day-title">${item.service_title}</h3>
    <p class="day-description">${item.service_description}</p>
    <span class="service-badge">${item.service_type}</span>
  </div>`;
});

proposalTemplate = proposalTemplate.replace(/\{\{#each itinerary_items\}\}[\s\S]*?\{\{\/each\}\}/, itemsHtml);

const proposalOutputPath = path.join(__dirname, 'output_sample_proposal.html');
fs.writeFileSync(proposalOutputPath, proposalTemplate, 'utf8');
console.log(`✓ Branded proposal generated: ${proposalOutputPath}`);


console.log('\n--- SIMULATING WORKFLOW 2: SUPPLIER 1-CLICK CONFIRMATION & VOUCHERS ---');
const sampleToken = 'tok_amalfi_948123';
const sampleVoucherNum = 'VOUCH-2026-98144';
console.log(`-> Generated 1-Click WhatsApp confirmation links for suppliers.`);
console.log(`-> Simulated Supplier click: ACCEPTED by Amalfi Luxury Chauffeurs (SUP-TRN-001)`);

let voucherTemplate = fs.readFileSync(path.join(__dirname, 'templates', 'service_voucher.html'), 'utf8');
voucherTemplate = voucherTemplate
  .replace(/{{voucher_number}}/g, sampleVoucherNum)
  .replace(/{{inquiry_id}}/g, mockRFP.inquiry_id)
  .replace(/{{service_date}}/g, "2026-09-20")
  .replace(/{{service_time}}/g, "14:30")
  .replace(/{{client_name}}/g, mockRFP.client_name)
  .replace(/{{pax_adults}}/g, mockRFP.pax_adults)
  .replace(/{{pax_children}}/g, "0")
  .replace(/{{supplier_name}}/g, "Amalfi Luxury Chauffeurs")
  .replace(/{{service_title}}/g, "Private Mercedes V-Class Airport Transfer")
  .replace(/{{service_description}}/g, "Meet & greet at Naples Airport (NAP) arrivals hall with name board, luggage handling, direct transfer to Sorrento.")
  .replace(/{{meeting_location}}/g, "Naples Airport Arrivals Hall")
  .replace(/{{resource_details}}/g, "Mercedes V-Class Extra Long (Chauffeur: Antonio De Luca)")
  .replace(/{{flight_details}}/g, "AZ 1284 (FCO -> NAP), Scheduled arrival 14:15");

const voucherOutputPath = path.join(__dirname, 'output_sample_voucher.html');
fs.writeFileSync(voucherOutputPath, voucherTemplate, 'utf8');
console.log(`✓ Ground service voucher generated: ${voucherOutputPath}`);


console.log('\n--- SIMULATING WORKFLOW 3: DAILY OPERATIONS MANIFEST ---');
const manifestText = `📋 DAILY DISPATCH MANIFEST - 2026-09-20
Driver: Antonio De Luca | Vehicle: Mercedes V-Class (FX 892 TR)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stop #1: 14:30 - Airport Transfer
• Lead Guest: Sarah Jenkins (2 Pax)
• Flight: AZ 1284 (FCO -> NAP) - STATUS: ON TIME
• Pickup: Naples International Airport (NAP) - Arrivals Gate
• Dropoff: Grand Hotel Excelsior Vittoria, Sorrento
• Notes: VIP 25th anniversary guests. Provide chilled water and wet towels.

📞 24/7 Operations Desk: +39 081 555 9999`;

const manifestOutputPath = path.join(__dirname, 'output_sample_manifest.txt');
fs.writeFileSync(manifestOutputPath, manifestText, 'utf8');
console.log(`✓ Daily dispatch manifest compiled: ${manifestOutputPath}`);
console.log('\n================================================================');
console.log('✅ ALL SIMULATION STEPS COMPLETED SUCCESSFULLY');
console.log('================================================================\n');
