"""
clean_jmp.py
------------
Cleans the REAL WHO/UNICEF JMP world file into ONE dashboard-ready CSV, reading
the machine-readable tabs ('wat', 'san', 'hyg') that hold flat, decimal data.

Input : the JMP world file, e.g. JMP_2025_WLD.xlsx, in data/raw/
Output: data/clean/jmp_coverage_summary.csv   <- the single source for the dashboard
        data/clean/jmp_tidy_long.csv          <- optional per-residence detail

Switch between the real file and the synthetic sample by editing RAW_PATH.
"""
import numpy as np, pandas as pd

# --- config -----------------------------------------------------------------
RAW_PATH = "data/raw/JMP_2025_WLD.xlsx"          # real file; use the SAMPLE name to test
# RAW_PATH = "data/raw/jmp_world_file_SAMPLE.xlsx"

# service -> (machine tab, "at least basic" prefix, "safely managed" prefix or None)
SERVICES = {
    "Water":      ("wat", "wat_basal", "wat_sm"),
    "Sanitation": ("san", "san_basal", "san_sm"),
    "Hygiene":    ("hyg", "hyg_bas",   None),
}
RESIDENCE = {"r": "Rural", "u": "Urban", "t": "National"}   # Total = national
META = {"name": "country", "iso3": "iso3", "region_sdg": "region",
        "region_income": "income_group", "year": "year",
        "pop_t": "population_000s"}


def _num(s):
    """JMP unformatted tabs are decimals but use '-' for no estimate."""
    return pd.to_numeric(s.replace({"-": np.nan, "": np.nan}), errors="coerce")


def _load_service(path, service):
    tab, basal, sm = SERVICES[service]
    df = pd.read_excel(path, sheet_name=tab, dtype=object)
    df = df.rename(columns=META)

    frames = []
    for suf, res in RESIDENCE.items():
        block = df[list(META.values())].copy()
        block["service"] = service
        block["residence"] = res
        block["at_least_basic_pct"] = _num(df[f"{basal}_{suf}"])
        block["safely_managed_pct"] = _num(df[f"{sm}_{suf}"]) if sm else np.nan
        frames.append(block)
    out = pd.concat(frames, ignore_index=True)
    return out


def main():
    parts = [_load_service(RAW_PATH, s) for s in SERVICES]
    summary = pd.concat(parts, ignore_index=True)

    # tidy the metadata
    summary["country"] = summary["country"].astype(str).str.strip()
    summary["iso3"] = summary["iso3"].astype(str).str.strip().str.upper()
    summary["region"] = summary["region"].astype(str).str.strip()
    summary["income_group"] = summary["income_group"].astype(str).str.strip()
    summary["year"] = pd.to_numeric(summary["year"], errors="coerce").astype("Int64")
    summary["population_000s"] = pd.to_numeric(summary["population_000s"], errors="coerce")

    # drop non-country / empty rows (regional footers, blanks)
    summary = summary[summary["iso3"].str.match(r"^[A-Z]{3}$", na=False)]
    summary = summary.dropna(subset=["year"])
    summary = summary.dropna(subset=["at_least_basic_pct", "safely_managed_pct"], how="all")

    for c in ("at_least_basic_pct", "safely_managed_pct"):
        summary[c] = summary[c].clip(0, 100).round(1)

    # urban - rural gap in "at least basic", carried on every row of that country/year/service
    piv = summary.pivot_table(index=["country", "year", "service"],
                              columns="residence", values="at_least_basic_pct")
    if {"Urban", "Rural"}.issubset(piv.columns):
        gap = (piv["Urban"] - piv["Rural"]).round(1).rename("urban_rural_gap_pct").reset_index()
        summary = summary.merge(gap, on=["country", "year", "service"], how="left")

    summary = summary.sort_values(["service", "country", "year", "residence"]).reset_index(drop=True)

    cols = ["country", "iso3", "region", "income_group", "year", "population_000s",
            "service", "residence", "at_least_basic_pct", "safely_managed_pct", "urban_rural_gap_pct"]
    summary = summary[[c for c in cols if c in summary.columns]]

    summary.to_csv("data/clean/jmp_coverage_summary.csv", index=False)
    summary.to_csv("data/clean/jmp_tidy_long.csv", index=False)

    yr = f'{int(summary["year"].min())}-{int(summary["year"].max())}'
    print("Cleaning complete.")
    print(f"  rows                      : {len(summary):,}")
    print(f"  countries / years covered : {summary['country'].nunique()} countries, {yr}")
    print(f"  services                  : {', '.join(summary['service'].unique())}")
    print("  output                    : data/clean/jmp_coverage_summary.csv (dashboard source)")


if __name__ == "__main__":
    main()
