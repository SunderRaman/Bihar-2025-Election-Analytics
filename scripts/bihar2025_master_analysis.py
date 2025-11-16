import pandas as pd

def load_all_data():
    df_results = pd.read_csv("../data/processed/bihar2025_results_with_district_metrics.csv")
    df_margin = pd.read_csv("../data/processed/bihar2025_margin_buckets.csv")
    df_party = pd.read_csv("../data/processed/bihar2025_party_metrics.csv")

    return df_results, df_margin, df_party

def merge_results_and_margins(df_results, df_margin):

    merged = df_results.merge(
        df_margin[
            [
                "AC_NO", "Candidate", "Party", 
                "Margin_Bucket",
                "<500","0.5-2K","2_10K","10_25K","25_50K","50K_plus",
                "Multi_Cornered_Count"
            ]
        ],
        on=["AC_NO", "Candidate", "Party"],
        how="left"
    )

    # Add binary flag for multi-cornered
    merged['Vote_Percent'] = round(merged["Votes"]/merged["Total_Votes_Polled"]*100,2)
    merged["Is_Multi_Cornered"] = (merged["Multi_Cornered_Count"] >= 3).astype(int)

    return merged

def merge_party_metrics(master_df, df_party):

    df_party = df_party.rename(columns={
        "Votes": "Party_Total_Votes",
        "Vote_Share_%": "Party_Vote_Share_%",
        "Constituencies_Contested": "Party_Constituencies_Contested",
        "Seats_Won": "Party_Seats_Won",
        "Conversion_Percentage": "Party_Conversion_Percentage"
    })

    master = master_df.merge(df_party, on="Party", how="left")

    return master

def compute_wasted_effective_efficiency_votes(master):
    master["Wasted_Votes"] = master.apply(
        lambda row: row["Votes"] if row["Status"] != "won" else 0,
        axis=1
    )
    master["Effective_Votes"] = master.apply(
        lambda r: r["Votes"] if r["Status"] == "won" else 0, axis=1
    )
    master["Votes_per_Seat"] = (
    master["Party_Total_Votes"] / master["Party_Seats_Won"]
    )
    return master

def calculate_party_level_median_details(master):
    median_winner_vote_percent = (
        master[master["Status"] == "won"]["Vote_Percent"].median()
    )
    winners = master[master["Status"] == "won"]
    winners = winners.copy()
    winners['Below_Median'] = winners["Vote_Percent"] < median_winner_vote_percent

    summary = winners.groupby("Party").agg(
        Below_Median_Percent=("Below_Median", lambda x: x.sum()),
        Above_Median_Percent=("Below_Median", lambda x: (~x).sum())
    ).reset_index()
   
    print(f"Median of Winner Vote percentage is: {median_winner_vote_percent}")
    print(f"Summary:\n {summary}")

    
    # return master
   
def build_master_dataset():

    df_results, df_margin, df_party = load_all_data()

    # 1. Merge Results + Margin buckets
    master = merge_results_and_margins(df_results, df_margin)

    # 2. Merge with party metrics
    master = merge_party_metrics(master, df_party)

    # 3. Add wasted / effective vote indicators
    master = compute_wasted_effective_efficiency_votes(master)

    #4. Calculate party level metrics
    calculate_party_level_median_details(master)

    # Final output
    master.to_csv("../data/processed/bihar2025_master_dataset.csv", index=False)

    print("🎉 MASTER DATASET CREATED: ../data/processed/bihar2025_master_dataset.csv")
    print(f"Total Rows: {len(master)}")
    print(f"Total Columns: {master.shape[1]}")
    

    return master

if __name__ == "__main__":
    master_df = build_master_dataset()
