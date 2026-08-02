# Global WASH Coverage Dashboard — WHO/UNICEF JMP

A focused, end-to-end data analysis project on **water, sanitation and hygiene
(WASH)** access, built on the official **WHO/UNICEF Joint Monitoring Programme
(JMP)** world file - the UN's custodian dataset for WASH, covering 200+ countries
from 2000 to 2024, split by rural / urban / national service levels.

**Stack:** Python (pandas) for cleaning → one clean CSV → Power BI dashboard.

## What it does

1. Reads JMP's machine-readable tabs (`wat`, `san`, `hyg`) from the world file.
2. Selects, per country/year, the coverage figures JMP publishes directly -
   **"at least basic"** and **"safely managed"** - for rural (`_r`), urban (`_u`)
   and total/national (`_t`), converts `-` (no estimate) to missing, and reshapes
   everything into one tidy table.
3. Computes the **urban–rural gap** and writes one dashboard-ready CSV.
4. Feeds a single-page Power BI dashboard: coverage by country, progress over
   time, and the urban–rural inequality WASH work centres on.

## Data

WHO/UNICEF JMP household world file, free and openly licensed (CC BY 3.0 IGO),
from https://washdata.org/data (file `JMP_2025_WLD.xlsx`, updated Aug 2025).



## Run it

```bash
pip install pandas openpyxl
python src/clean_jmp.py        # reads data/raw/JMP_2025_WLD.xlsx -> data/clean/jmp_coverage_summary.csv
```

## Repo layout

```
wash-jmp-dashboard/
├── data/
│   ├── raw/     JMP_2025_WLD.xlsx            (download from washdata.org)
│   │            jmp_world_file_SAMPLE.xlsx   (synthetic; for testing only)
│   └── clean/   jmp_coverage_summary.csv     (dashboard source, you generate)
├── src/
│   ├── make_sample_raw.py                    (synthetic sample generator)
│   └── clean_jmp.py                          (the cleaning pipeline)
├── powerbi/     WASH_Dashboard.pbix         (one-page layout)
└── Output/ WASH_Dashboard.pdf
```

