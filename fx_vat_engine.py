"""
DMC Multi-Currency FX Engine & European Travel Margin VAT Calculator
Implements:
1. Multi-Currency Spot Rates (EUR, USD, GBP, CHF, AUD) with a 2.5% Volatility Protection Buffer.
2. EU Special Travel Margin Scheme VAT (Directive 2006/112/EC Art. 306 / Italian Art. 74-ter).
"""

class FXandVATEngine:
    def __init__(self):
        # Base spot rates against 1 EUR (Base Currency)
        self.spot_rates = {
            "EUR": 1.00,
            "USD": 1.08,    # 1 EUR = 1.08 USD
            "GBP": 0.85,    # 1 EUR = 0.85 GBP
            "CHF": 0.96,    # 1 EUR = 0.96 CHF
            "AUD": 1.62,    # 1 EUR = 1.62 AUD
            "MZN": 69.50,   # 1 EUR = 69.50 MZN (Mozambique Metical)
            "ZAR": 19.80    # 1 EUR = 19.80 ZAR (South Africa Rand)
        }
        # Volatility Buffer: 2.5% safety margin on foreign currency quotes
        self.fx_buffer = 0.025
        # Standard EU/Italy VAT rate
        self.vat_rate = 0.22

    def convert_from_eur(self, amount_eur: float, target_currency: str, apply_buffer: bool = True) -> dict:
        """
        Converts EUR amount to target currency.
        If apply_buffer=True, adds the 2.5% FX risk buffer to protect against currency depreciation.
        """
        curr = target_currency.upper()
        if curr not in self.spot_rates:
            curr = "EUR"

        spot_rate = self.spot_rates[curr]

        if curr == "EUR":
            effective_rate = 1.0
            buffer_applied = 0.0
        else:
            # Buffer reduces purchasing power risk: effective_rate = spot_rate * (1 - buffer)
            effective_rate = spot_rate * (1 - self.fx_buffer) if apply_buffer else spot_rate
            buffer_applied = self.fx_buffer if apply_buffer else 0.0

        converted_amount = round(amount_eur * effective_rate, 2)

        return {
            "amount_eur": round(amount_eur, 2),
            "target_currency": curr,
            "spot_rate": spot_rate,
            "effective_rate": round(effective_rate, 4),
            "fx_buffer_applied": f"{int(buffer_applied * 100)}%",
            "converted_amount": converted_amount
        }

    def calculate_travel_margin_vat(self, net_supplier_cost: float, gross_selling_price: float, is_eu_service: bool = True) -> dict:
        """
        Calculates VAT under the EU Tour Operators Margin Scheme (TOMS / Italian Art. 74-ter).
        VAT is charged strictly on the gross margin, NOT on the total selling price.
        Formula:
          Gross Margin = Selling Price - Net Supplier Cost
          VAT on Margin = Gross Margin * (VAT_Rate / (1 + VAT_Rate))
          Net Profit after VAT = Gross Margin - VAT on Margin
        """
        gross_margin = round(gross_selling_price - net_supplier_cost, 2)

        if not is_eu_service or gross_margin <= 0:
            vat_amount = 0.0
            net_profit = gross_margin
            effective_tax_pct = 0.0
        else:
            # Art. 74-ter formula (VAT extracted from gross margin)
            vat_amount = round(gross_margin * (self.vat_rate / (1 + self.vat_rate)), 2)
            net_profit = round(gross_margin - vat_amount, 2)
            effective_tax_pct = round((vat_amount / gross_margin) * 100, 1)

        margin_pct = round((gross_margin / gross_selling_price) * 100, 1) if gross_selling_price > 0 else 0

        return {
            "gross_selling_price": round(gross_selling_price, 2),
            "net_supplier_cost": round(net_supplier_cost, 2),
            "gross_margin": gross_margin,
            "margin_percentage": f"{margin_pct}%",
            "vat_scheme": "EU TOMS / Italian Art. 74-ter" if is_eu_service else "Exempt (Non-EU Ground Service)",
            "vat_on_margin": vat_amount,
            "net_profit_after_vat": net_profit,
            "effective_vat_on_margin_pct": f"{effective_tax_pct}%"
        }

fx_vat_engine = FXandVATEngine()

if __name__ == "__main__":
    conversion = fx_vat_engine.convert_from_eur(7654.0, "USD", apply_buffer=True)
    vat_calc = fx_vat_engine.calculate_travel_margin_vat(5970.0, 7654.0)
    print("FX Conversion:", conversion)
    print("VAT on Margin:", vat_calc)
