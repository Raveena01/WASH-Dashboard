"""
make_sample_raw.py
------------------
Generates a SMALL, clearly-labelled SYNTHETIC file matching the shape of the REAL
WHO/UNICEF JMP machine-readable tabs ('wat', 'san', 'hyg'): one flat header row,
decimal values, Rural/Urban/Total suffixes (_r/_u/_t), and the ladder columns JMP
provides directly. This exists ONLY so clean_jmp.py is runnable without the
download. It is NOT real data.
"""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)

COUNTRIES = [
    ("Afghanistan","AFG","Central and Southern Asia","Low income"),
    ("Kenya","KEN","Sub-Saharan Africa","Lower-middle income"),
    ("India","IND","Central and Southern Asia","Lower-middle income"),
    ("Germany","DEU","Europe and Northern America","High income"),
    ("Bolivia (Plurinational State of)","BOL","Latin America and the Caribbean","Lower-middle income"),
    ("Nigeria","NGA","Sub-Saharan Africa","Lower-middle income"),
]
YEARS = list(range(2000, 2025))

def series(base):
    r, u = [], []
    for i,_ in enumerate(YEARS):
        nat = np.clip(base + i*1.0 + rng.normal(0,2), 4, 99)
        r.append(np.clip(nat-12+rng.normal(0,2),1,99))
        u.append(np.clip(nat+8+rng.normal(0,2),1,100))
    return np.round(r,4), np.round(u,4)

def total(r,u,pu):  # population-weighted national
    return np.round(r*(1-pu/100)+u*(pu/100),4)

def maybe_dash(a):
    a=a.astype(object)
    for i in range(len(a)):
        if rng.random()<0.02: a[i]="-"
    return a

def build(service):
    rows=[]
    for name,iso,region,income in COUNTRIES:
        base={"Low income":28,"Lower-middle income":55,"High income":97}[income]
        pop0=rng.integers(5_000,210_000); pu0=rng.uniform(25,90)
        bas_r,bas_u=series(base); sm_r,sm_u=series(max(base-15,3))
        for i,yr in enumerate(YEARS):
            pop=round(pop0*(1.012)**(yr-2000),3); pu=round(np.clip(pu0+i*0.4,10,99),4)
            row={"name":name,"year":yr,"pop_t":pop,"prop_u":pu,
                 "iso3":iso,"region_sdg":region,"region_income":income}
            bt=total(np.array([bas_r[i]]),np.array([bas_u[i]]),pu)[0]
            st=total(np.array([sm_r[i]]),np.array([sm_u[i]]),pu)[0]
            if service=="wat":
                row.update({"wat_basal_r":bas_r[i],"wat_basal_u":bas_u[i],"wat_basal_t":bt,
                            "wat_sm_r":sm_r[i],"wat_sm_u":sm_u[i],"wat_sm_t":st})
            elif service=="san":
                row.update({"san_basal_r":bas_r[i],"san_basal_u":bas_u[i],"san_basal_t":bt,
                            "san_sm_r":sm_r[i],"san_sm_u":sm_u[i],"san_sm_t":st})
            else:
                row.update({"hyg_bas_r":bas_r[i],"hyg_bas_u":bas_u[i],"hyg_bas_t":bt})
            rows.append(row)
    df=pd.DataFrame(rows)
    for c in df.columns:
        if c not in {"name","year","iso3","region_sdg","region_income"}:
            df[c]=maybe_dash(df[c].to_numpy())
    return df

def main():
    out="data/raw/jmp_world_file_SAMPLE.xlsx"
    with pd.ExcelWriter(out,engine="openpyxl") as xw:
        for s in ["wat","san","hyg"]:
            build(s).to_excel(xw,sheet_name=s,index=False)
    print(f"Wrote synthetic sample -> {out}")

if __name__=="__main__":
    main()
