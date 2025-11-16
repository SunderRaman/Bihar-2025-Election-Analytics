import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

# Initialize Selenium real Chrome browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

BASE_URL = "https://results.eci.gov.in/ResultAcGenNov2025/candidateswise-S04{}.htm"



def parse_ac(ac_no):
    url = BASE_URL.format(ac_no)
    print(f"\nProcessing AC {ac_no}: {url}")

    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # ---- Correct AC Name Extraction ----
    h2 = soup.find("h2")
    if h2:
        text = h2.text.strip()
        # Example: "Assembly Constituency 1 - VALMIKI NAGAR (Bihar)"
        match = re.search(r"- (.*?)\s*\(", text)
        ac_name = match.group(1).strip() if match else ""
    else:
        ac_name = ""

    # ---- Candidate Cards ----
    cards = soup.find_all("div", class_="cand-box")
    if not cards:
        print("❌ No candidate cards found.")
        return None

    rows = []

    for card in cards:
        info = card.find("div", class_="cand-info")

        # Status (won/lost)
        status_div = info.find("div", class_="status")
        result_status = status_div.find("div").text.strip()

        # Votes and margin
        raw_votes = status_div.find_all("div")[1].text.strip().split()[0]

        # Margin in parentheses
        margin_span = status_div.find("span")
        raw_margin = margin_span.text.strip() if margin_span else "0"

        # Clean margin (remove parentheses, spaces)
        clean_margin = raw_margin.replace("(", "").replace(")", "").strip()
        clean_margin = clean_margin.replace("+", "").replace(" ", "")
        try:
            clean_margin = int(clean_margin)
        except:
            clean_margin = None

        # Candidate & Party
        name = info.find("h5").text.strip()
        party = info.find("h6").text.strip()

        rows.append({
            "AC_NO": ac_no,
            "AC_NAME": ac_name,
            "Candidate": name,
            "Party": party,
            "Votes": int(raw_votes),
            "Margin": clean_margin,
            "Status": result_status
        })

    # Compute total votes polled in this AC
    df_ac = pd.DataFrame(rows)
    df_ac["Total_Votes_Polled"] = df_ac["Votes"].sum()

    return df_ac

def extract_data_for_constituencies(start, end):
# ---- Run for first 5 ACs (increase later) ----
    all_rows = []
    for ac in range(start, end):
        df = parse_ac(ac)
        if df is not None:
            all_rows.append(df)
    final_df = pd.concat(all_rows, ignore_index=True)
    final_df.to_csv("bihar2025_cleaned_test.csv", index=False)
    driver.quit()
    return final_df

def merge_district_info(final_df):
    district_map = pd.read_csv("bihar_ac_district_mapping.csv")
    final_df["AC_NAME"] = final_df["AC_NAME"].str.strip().str.title()
    district_map["AC_NAME"] = district_map["AC_NAME"].str.strip().str.title()

    merged = final_df.merge(district_map, on=["AC_NO", "AC_NAME"], how="left")
    district_votes = (
        merged.groupby("DISTRICT")["Votes"].sum()
        .reset_index()
        .rename(columns={"Votes": "Total_Votes_Per_District"})
    )
    merged_final = merged.merge(district_votes, on="DISTRICT", how="left")
    return merged_final

def write_constituency_details_to_file(merged_final, output_file="bihar2025_results_with_district_metrics.csv"):
    
    try:
        # Load existing file if present
        existing_df = pd.read_csv(output_file)
        
        # Append new rows
        updated_df = pd.concat([existing_df, merged_final], ignore_index=True)
        
        # Remove duplicates (important!)
        updated_df.drop_duplicates(
            subset=["AC_NO", "Candidate", "Party"], 
            keep="first", 
            inplace=True
        )
        
        # Save updated file
        updated_df.to_csv(output_file, index=False)
        print("👉 Updated existing CSV with new constituencies.")
        
    except FileNotFoundError:
        # File does not exist → Create new file
        merged_final.to_csv(output_file, index=False)
        updated_df = merged_final
        print("👉 Created new CSV file as this is the first batch.")

    return updated_df

def analyze_data(df):
    # Total Votes Polled by Each party
    party_votes = df.groupby("Party")["Votes"].sum().reset_index()
    party_votes = party_votes.sort_values("Votes", ascending=False)
    # PErcentage Vote Share for each party
    total_votes_state = df["Votes"].sum()
    party_votes["Vote_Share_%"] = (party_votes["Votes"] / total_votes_state) * 100
    # Number of constituencies contested by each party
    party_constituencies = df.groupby("Party")["AC_NO"].nunique().reset_index()
    party_constituencies.columns = ["Party", "Constituencies_Contested"]
    # Seats won by each Party
    party_seats = df[df["Status"] == "won"].groupby("Party")["AC_NO"].count().reset_index()
    party_seats.columns = ["Party", "Seats_Won"]
    #Seat Conversion Ratio (Efficiency)
    scr = party_constituencies.merge(party_seats, on="Party", how="left")
    scr["Seats_Won"] = scr["Seats_Won"].fillna(0)
    scr["Conversion_Percentage"] = round(scr["Seats_Won"] / scr["Constituencies_Contested"]*100,2)

    # --- Combine analytics into a master dataframe ---

    analytics_df = party_votes.merge(party_constituencies, on="Party", how="left")
    analytics_df = analytics_df.merge(party_seats, on="Party", how="left")
    analytics_df = analytics_df.merge(scr[["Party", "Conversion_Percentage"]], on="Party", how="left")

    # Clean missing data
    analytics_df["Seats_Won"] = analytics_df["Seats_Won"].fillna(0).astype(int)
    analytics_df["Conversion_Percentage"] = analytics_df["Conversion_Percentage"].fillna(0)

    # Save to CSV
    analytics_df.to_csv("bihar2025_party_metrics.csv", index=False)

    print("Created → bihar2025_party_metrics.csv")

    # Winning margin Distributions:
    df_winners = df[df["Status"] == "won"].copy()

    bins = [0, 500, 2000, 10000, 25000, 50000, df_winners["Margin"].max()]
    labels = ["<500","0.5-2K", "2-10K", "10-25K", "25-50K", ">50K"]

    df_winners["Margin_Bucket"] = pd.cut(df_winners["Margin"], bins=bins, labels=labels,include_lowest=True)
    bucket_dummies = pd.get_dummies(df_winners["Margin_Bucket"])
    bucket_dummies = bucket_dummies.astype(int)
    bucket_dummies = bucket_dummies.rename(columns={
        "0-500":"0-500",
        "0.5-2K": "0.5-2K",
        "2-10K": "2_10K",
        "10-25K": "10_25K",
        "25-50K": "25_50K",
        ">50K": "50K_plus"
    })

    # Final merged DataFrame
    final_margin_df = pd.concat([df_winners, bucket_dummies], axis=1)

    # --- Multi-Cornered Contest Count ---
    multi_corner = df[df["Votes"] / df["Total_Votes_Polled"] > 0.10]
    multi_corner_count = (
        multi_corner.groupby("AC_NO")["Candidate"]
        .count()
        .reset_index()
        .rename(columns={"Candidate": "Multi_Cornered_Count"})
    )

    # Merge into winning candidate dataset
    final_margin_df = final_margin_df.merge(
        multi_corner_count,
        on="AC_NO",
        how="left"
    )

    # Clean NaN values
    final_margin_df["Multi_Cornered_Count"] = (
        final_margin_df["Multi_Cornered_Count"]
        .fillna(1)
        .astype(int)
    )

    # Save to CSV
    final_margin_df.to_csv("bihar2025_margin_buckets.csv", index=False)

    print("✔ Saved → bihar2025_margin_buckets.csv")


if __name__ == "__main__":
    final_df = extract_data_for_constituencies(1,35)
    merged_final = merge_district_info(final_df)
    output_file = "bihar2025_results_with_district_metrics.csv"
    updated_df = write_constituency_details_to_file(merged_final,output_file)
    analyze_data(updated_df)
