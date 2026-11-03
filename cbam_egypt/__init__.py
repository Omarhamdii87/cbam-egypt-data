"""CBAM certificate arithmetic for goods from Egypt, on EU default values.

Same formula as the calculator on omarhamdy.com (CBAM product and CN code pages):

    certificates = max(0, tonnes x (default x (1 + mark-up) - benchmark_B x CBAM factor))

default      total default value, tCO2e per tonne: Implementing Regulation (EU) 2025/2621, Annex I,
             as replaced by Implementing Regulation (EU) 2026/1740 (column total_tco2e_per_t in data/).
mark-up      10% in 2026, 20% in 2027, 30% from 2028 for cement, iron and steel, aluminium and hydrogen;
             1% every year for fertilisers (2026/1740, Annex I).
benchmark_B  CBAM benchmark, Column B (used with default values), Implementing Regulation (EU) 2025/2620.
CBAM factor  Directive 2003/87/EC, Article 10a(1a). Cross-sectoral correction factor taken as 1:
             100% for 2026 to 2030 under Implementing Decision (EU) 2026/1862, Article 1, and assumed 1 after.

No price is assumed. Cost is certificates times the price you supply. No carbon price paid in Egypt is
deducted. Illustrative arithmetic on public figures, not legal or tax advice for any shipment.
"""
import csv, json, os

__version__ = "2026.11.03"

CBAM_FACTOR = {2026: 0.975, 2027: 0.95, 2028: 0.90, 2029: 0.775, 2030: 0.515,
               2031: 0.39, 2032: 0.265, 2033: 0.14, 2034: 0.0}

# Column B benchmarks, tCO2e per tonne: Implementing Regulation (EU) 2025/2620, Annex, point 5.3, Column B (used with
# default values), for the route that the default table gives for Egypt (Annex, point 5.1). One figure per CN line; a
# code that covers several CN8 rows is listed only when every row gives the same value (BENCHMARK_ROW says which).
# Rebar figures here are on the default only; the site models the steel precursor chain for actual data.
BENCHMARK_B = {
    "2523 10 00 10": 0.859, "2523 10 00 90": 0.666, "2523 21 00": 0.859, "2523 29 00": 0.666,
    "2814 10 00": 1.522, "2814 20 00": 0.457, "3102 10 12": 0.304, "3102 10 15": 0.503,
    "3102 10 19": 0.902, "3102 10 90": 0.882, "3102 21 00": 0.414, "3102 30 90": 0.767,
    "3102 40 10": 0.688, "3102 60 00": 0.633, "3102 80 00": 0.625, "3102 90 00": 0.847,
    "3105 30 00": 0.339, "3105 40 00": 0.173, "3105 90 80": 0.248, "7202 11": 1.361,
    "7207 20 15": 1.364, "7207 20 17": 1.364, "7208": 1.37, "7209": 1.458,
    "7210": 1.491, "7211 19 00": 1.37, "7211 23": 1.458, "7211 29 00": 1.458,
    "7212": 1.491, "7213": 1.364, "7214 20 00": 1.364, "7214 99": 1.364,
    "7215": 1.364, "7216": 1.364, "7217 10": 1.364, "7217 90": 1.397,
    "7226 91": 1.577, "7301": 1.458, "7307 29": 1.173, "7307 99": 1.383,
    "7308": 1.491, "7309": 1.491, "7326 20 00": 1.397, "7326 90 98": 1.491,
    "7601": 1.423, "7604 10 10": 1.485, "7604 10 90": 1.493, "7604 21 00": 1.493,
    "7604 29 10": 1.485, "7604 29 90": 1.493, "7605": 1.485, "7606": 1.485,
    "7607": 1.599, "7608": 1.493, "7610 90": 1.493, "7610 90 90": 1.493,
    "7612": 1.594, "7614": 1.485, "7616 99 90": 1.485,
}
# Where the Annex gives a second Column B figure, indicator (2), for production years 2028 to 2030.
BENCHMARK_B_2028 = {
    "7202 11": 1.277, "7226 91": 1.409, "7307 29": 1.135,
}

# The Annex row or rows each benchmark is read from, and the route used (lines from the site's calculator keep their own source).
BENCHMARK_ROW = {
    "2523 21 00": "2523 21 00",
    "2523 29 00": "2523 29 00",
    "2814 10 00": "2814 10 00",
    "3102 10 12": "3102 10 12",
    "3102 10 15": "3102 10 15",
    "3102 10 19": "3102 10 19",
    "3102 10 90": "3102 10 90",
    "3102 21 00": "3102 21 00",
    "3102 30 90": "3102 30 90",
    "3102 40 10": "3102 40 10",
    "3102 60 00": "3102 60 00",
    "3102 80 00": "3102 80 00",
    "3102 90 00": "3102 90 00",
    "3105 30 00": "3105 30 00",
    "3105 40 00": "3105 40 00",
    "3105 90 80": "3105 90 80",
    "7202 11": "7202 11 20 to 7202 11 80",
    "7207 20 15": "7207 20 15, route (C)",
    "7207 20 17": "7207 20 17, route (C)",
    "7208": "7208 10 00 to 7208 90 80, route (C)",
    "7209": "7209 15 00 to 7209 90 80, route (C)",
    "7210": "7210 11 00 to 7210 90 80, route (C)",
    "7211 19 00": "7211 19 00, route (C)",
    "7211 23": "7211 23 20 to 7211 23 80, route (C)",
    "7211 29 00": "7211 29 00, route (C)",
    "7212": "7212 10 10 to 7212 60 00, route (C)",
    "7213": "7213 10 00 to 7213 99 90, route (C)",
    "7214 20 00": "7214 20 00, route (C)",
    "7214 99": "7214 99 10 to 7214 99 95, route (C)",
    "7215": "7215 10 00 to 7215 90 00, route (C)",
    "7216": "7216 10 00 to 7216 99 00, route (C)",
    "7217 10": "7217 10 10 to 7217 10 90, route (C)",
    "7217 90": "7217 90 20 to 7217 90 90, route (C)",
    "7226 91": "7226 91 20 to 7226 91 99, route (F)",
    "7301": "7301 10 00 to 7301 20 00, route (C)",
    "7307 29": "7307 29 10 to 7307 29 80",
    "7307 99": "7307 99 10 to 7307 99 80, route (C)",
    "7308": "7308 10 00 to 7308 90 98, route (C)",
    "7309": "7309 00 10 to 7309 00 90, route (C)",
    "7326 20 00": "7326 20 00, route (C)",
    "7326 90 98": "7326 90 98, route (C)",
    "7601": "7601 10 10 to 7601 20 80, route (K)",
    "7604 10 90": "7604 10 90, route (K)",
    "7604 21 00": "7604 21 00, route (K)",
    "7604 29 10": "7604 29 10, route (K)",
    "7604 29 90": "7604 29 90, route (K)",
    "7605": "7605 11 00 to 7605 29 00, route (K)",
    "7606": "7606 11 30 to 7606 92 00, route (K)",
    "7607": "7607 11 11 to 7607 20 99, route (K)",
    "7608": "7608 10 00 to 7608 20 89, route (K)",
    "7610 90": "7610 90 10 to 7610 90 90, route (K)",
    "7610 90 90": "7610 90 90, route (K)",
    "7612": "7612 10 00 to 7612 90 80, route (K)",
    "7614": "7614 10 00 to 7614 90 00, route (K)",
    "7616 99 90": "7616 99 90, route (K)",
}

FERTILISERS = "Fertilisers"
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cbam-cn-codes-egypt-2026.json")


def markup(sector, year):
    """Mark-up on the default value for a CBAM sector and import year."""
    if sector == FERTILISERS:
        return 0.01
    return 0.10 if year == 2026 else 0.20 if year == 2027 else 0.30


def certificates(tonnes, default, benchmark_b, year, sector):
    """CBAM certificates to surrender on the default value. Never below zero."""
    if year not in CBAM_FACTOR:
        raise ValueError("year must be 2026 to 2034")
    if tonnes < 0 or default < 0 or benchmark_b < 0:
        raise ValueError("inputs must be 0 or more")
    per_t = default * (1 + markup(sector, year)) - benchmark_b * CBAM_FACTOR[year]
    return max(0.0, tonnes * per_t)


def path(tonnes, default, benchmark_b, sector, b_2028=None):
    """Certificates for each year 2026 to 2034."""
    return {y: certificates(tonnes, default, b_2028 if (b_2028 and 2028 <= y <= 2030) else benchmark_b, y, sector)
            for y in CBAM_FACTOR}


def load(path_=DATA):
    """The dataset rows, keyed by CN code as printed (for example '3102 10 19')."""
    with open(path_, encoding="utf-8") as fh:
        return {c["cn_code"]: c for c in json.load(fh)["codes"]}


def for_code(cn_code, tonnes, year, rows=None):
    """Certificates for a CN line in the dataset that has a Column B benchmark here."""
    rows = rows or load()
    c = rows[cn_code]
    b = BENCHMARK_B[cn_code]
    if year >= 2028 and year <= 2030 and cn_code in BENCHMARK_B_2028:
        b = BENCHMARK_B_2028[cn_code]
    return certificates(tonnes, c["default_values"]["total_tco2e_per_t"], b, year, c["sector"])
