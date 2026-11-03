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

__version__ = "2026.11.02"

CBAM_FACTOR = {2026: 0.975, 2027: 0.95, 2028: 0.90, 2029: 0.775, 2030: 0.515,
               2031: 0.39, 2032: 0.265, 2033: 0.14, 2034: 0.0}

# Column B benchmarks (2025/2620), tCO2e per tonne, for the dataset lines the site's calculator covers.
# Rebar figures here are on the default only; the site models the steel precursor chain for actual data.
BENCHMARK_B = {
    "3102 10 19": 0.902, "3102 10 90": 0.882, "3102 10 15": 0.503, "3102 10 12": 0.304,
    "2814 10 00": 1.522, "2814 20 00": 0.457,
    "7601": 1.423, "7604 10 10": 1.485, "7604 10 90": 1.493, "7605": 1.485, "7606": 1.485,
    "7607": 1.599, "7608": 1.493,
    "7214 20 00": 1.364,
    "2523 29 00": 0.666, "2523 10 00 90": 0.666, "2523 21 00": 0.859, "2523 10 00 10": 0.859,
}
# Where 2025/2620 gives a second Column B figure for production years 2028 to 2030 (none of the lines above).
BENCHMARK_B_2028 = {}

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
