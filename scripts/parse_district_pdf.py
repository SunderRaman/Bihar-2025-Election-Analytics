import camelot
import pandas as pd
import re

# Read all tables from the PDF
tables = camelot.read_pdf("../data/raw/bihar_ac_district_list.pdf", pages="all")
mapping_rows = []

for i, table in enumerate(tables):
    print(f"\n================== TABLE {i} ==================")
    df = table.df
    # Row 0 contains the actual header, remove newline characters
    df.columns = [col.replace("\n", " ").strip() for col in df.iloc[0]]

    # Drop the first two rows:
    # row 0 = header
    # row 1 = numbering row ("1 2 3")
    df = df[2:].reset_index(drop=True)

    # Now clean data rows (remove \n inside cells)
    df = df.map(lambda x: x.replace("\n", " ").strip() if isinstance(x, str) else x)

    # --- NORMALIZE COLUMN NAMES ---
    df.columns = [c.strip().replace("  ", " ") for c in df.columns]

    # Identify columns
    dist_col = [c for c in df.columns if "District" in c][0]
    ac_col   = [c for c in df.columns if "Constituencies" in c][0]

    # Forward-fill district name (because only first row has value)
    df[dist_col] = df[dist_col].replace("", pd.NA)
    df[dist_col] = df[dist_col].ffill()

    # Remove empty AC rows
    df = df[df[ac_col] != ""]

    # --- Extract AC_NO and AC_NAME ---
    for _, row in df.iterrows():
        district = str(row[dist_col]).strip()
        ac_entry = str(row[ac_col]).strip()

        if "-" not in ac_entry:
            continue

        ac_no_str, ac_name = ac_entry.split("-", 1)

        mapping_rows.append({
            "AC_NO": int(ac_no_str.strip()),
            "AC_NAME": ac_name.strip(),
            "DISTRICT": district
        })
    
district_df = pd.DataFrame(mapping_rows).drop_duplicates()
district_df = district_df.sort_values("AC_NO")
district_df.to_csv("../data/processed/bihar_ac_district_mapping.csv", index=False)
