# cbam-egypt-data

CBAM product codes and EU default values for Egypt, with 2025 EU imports from Egypt, plus the certificate formula as a small tested Python module.

- Permanent DOI: https://doi.org/10.5281/zenodo.23898572
- Web version: https://omarhamdy.com/guides/cbam-egypt-exporters/codes/
- Calculator: https://omarhamdy.com/guides/cbam-egypt-exporters/

## Files
- `data/cbam-cn-codes-egypt-2026.csv` and `data/cbam-cn-codes-egypt-2026.json`: the dataset (260 lines). The JSON also carries the sources, mark-up schedule and notes per line.
- `cbam_egypt/`: the certificate formula (no dependencies, Python 3.9 or later).
- `tests/`: checks that the module gives the same results as the omarhamdy.com calculator.

## The formula
For an import year from 2026 to 2034, on the EU default value:

    certificates = max(0, tonnes x (default x (1 + mark-up) - benchmark_B x CBAM factor))

- default: total default value, tCO2e per tonne (column `total_tco2e_per_t`).
- mark-up: 10% in 2026, 20% in 2027, 30% from 2028 for cement, iron and steel, aluminium and hydrogen; 1% every year for fertilisers.
- benchmark_B: CBAM benchmark, Column B, Implementing Regulation (EU) 2025/2620, Annex, point 5.3, for the route the default table gives for Egypt. `BENCHMARK_B` covers 59 lines; `BENCHMARK_ROW` names the Annex row or rows for each line added on 3 November 2026.
- CBAM factor: Directive 2003/87/EC, Article 10a(1a): 97.5% in 2026 falling to 0 in 2034. Cross-sectoral correction factor 100% for 2026 to 2030 (Implementing Decision (EU) 2026/1862, Article 1), taken as 1 after.

No certificate price is assumed: cost is certificates times the price you supply. No carbon price paid in Egypt is deducted.

```python
import cbam_egypt as C
round(C.for_code("7601", 10_000, 2026))   # 6696 certificates, unwrought aluminium
round(C.for_code("7601", 10_000, 2034))   # 24310
C.path(10_000, 1.39, 0.902, "Fertilisers")  # urea 3102 10 19, 2026 to 2034
```

Run the checks: `python3 -m unittest discover -s tests`

Compiled by Omar Hamdy (ORCID 0009-0007-6613-8968), omarhamdy.com. Retrieved 2 November 2026.

## What it is
One row for each of the 260 CN or TARIC lines in the EU Carbon Border Adjustment Mechanism (CBAM) default value tables, covering cement, iron and steel, aluminium, fertilisers and hydrogen. For each line:
- the official description, sector and aggregated goods category;
- the default value that applies to goods from Egypt (direct, indirect and total, tCO2e per tonne), and whether it comes from the Egypt table or the "Other countries and territories" table;
- the production route, where the default depends on it;
- the mark-up schedule by year;
- EU imports from Egypt in 2025 (tonnes and EUR), from Eurostat Comext.

61 lines have an Egypt-specific default; 119 lines had EU imports from Egypt in 2025.

## Sources
- Commission Implementing Regulation (EU) 2025/2621, Annex I, as replaced by Implementing Regulation (EU) 2026/1740 of 20 July 2026 (OJ, 31 July 2026). EUR-Lex.
- Eurostat Comext, dataset DS-045409, EU imports with partner Egypt, 2025.
- Regulation (EU) 2023/956 as amended by Regulation (EU) 2025/2083.

## Notes
- Blanks are left blank on purpose: no value was estimated.
- Totals are as published in the regulation. Direct plus indirect can differ from the total by rounding (for example urea, 3102 10 19: 1.32 plus 0.08, total 1.39). The certificate count uses the total.
- The default_with_markup columns are the total multiplied by one plus that year's mark-up (10%, 20% and 30% from 2028 for cement, iron and steel, aluminium and hydrogen; 1% every year for fertilisers).
- Trade figures are at CN 8-digit level. The five TARIC (10-digit) lines have blank trade, because Comext does not publish below CN8.
- Comext sub-lines can differ slightly from heading totals because of rounding or confidential trade.
- Electricity is excluded; Egypt recorded no electricity exports to the EU.
- This is a compilation of published figures for information. It is not legal or tax advice for any shipment. Check the 8-digit code with your customs broker.

## Licence and credit
Data and compilation: CC BY 4.0 (`LICENSE-DATA`). Code in `cbam_egypt/` and `tests/`: MIT (`LICENSE`). Cite as: Omar Hamdy, "CBAM product codes and EU default values for Egypt, with 2025 EU imports from Egypt", 2026, Zenodo, https://doi.org/10.5281/zenodo.23898572. Web version: omarhamdy.com/guides/cbam-egypt-exporters/codes/. Underlying EU and Eurostat data follow their own reuse terms (Commission Decision 2011/833/EU; Eurostat copyright notice).

Views are the author's own and do not represent any institution.

Source data: © European Union. EU legal texts and the Commission's Excel file of defaults, reuse authorised under Commission Decision 2011/833/EU. Eurostat Comext, reuse with acknowledgement of the source under Eurostat's copyright notice.
