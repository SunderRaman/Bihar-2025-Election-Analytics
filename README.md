# Bihar-2025-Election-Analytics
This project performs a comprehensive, constituency-level analysis of the Bihar Assembly Elections 2025, covering:
✔ Automated data extraction  
✔ PDF → CSV district mapping  
✔ Data cleaning & merging  
✔ Vote share, seat share, district-wise metrics  
✔ Margin buckets, multi-cornered contests  
✔ Interactive visualizations (Plotly + Matplotlib)  
✔ Master dataset for 2,859 candidate rows across 243 constituencies  

**1. Overview**

The Bihar 2025 Election Analytics project is a full end-to-end data project that:  
✔ Scrapes candidate-wise results from the ECI site (using Selenium)  
✔ Extracts district constituency mapping from an official PDF (using Camelot)  
✔ Cleans, merges, and enriches the dataset  
✔ Builds more than 20+ analytics metrics, including:  
  - Vote share %
  - Seat share %
  - Conversion ratio (Votes → Seats)
  - Wasted votes
  - Effective votes
  - Margin buckets
  - Multi-cornered contests
  - Winner vs Runner-Up comparison
  - District-wise seat distribution
  - Alliance-based performance  
✔ Provides rich visualizations:
  - Vote share bars
  - Seat share
  - Bubble charts
  - Heatmaps
  - Closest & widest victory tables  
    
All results are saved into CSV files for further analysis or reporting.

**2. Key Features**  

✔ Automated Data Extraction  
  - Scrapes 243 constituency result pages
  - Handles Chrome automation, waits, retries
  - Generates clean candidate-wise result table
✔ District Mapping via PDF Parsing  
  - Extracts district → AC mapping from official ECI PDF
  - Cleans multi-line text and malformed rows
  - Produces a clean mapping CSV  
✔ Master Dataset (Final Output)  
     Includes **28 columns**, such as:  
      - AC_NO, AC_NAME, DISTRICT,Candidate, Party, Votes, Margin, Status,GENERAL_SC reservation tag, Vote_Percent for winners, Wasted_Votes, Effective_Votes, Votes_per_Seat,Margin bucket flags: <500, 0.5-2K, 2_10K, etc.

**3. Analytics Performed**  
🟠 Vote & Seat Metrics
  - Party-wise total votes
  - Vote Share %
  - Seat Share %
  - Conversion ratio (efficiency)  
🔵 Margin Analysis  
  - Margin buckets  
  - Closest 15 contests  
  - Widest 15 contests  
  - Winner vs Runner-Up comparison with party acronyms   
🟣 District-Level Metrics
  - Total votes per district
  - District-wise seat share
  - Heatmap of party performance by district  
🟢 Contest Dynamics
  - Multi-cornered contests (3+ candidates >10% votes)
  - Candidate vote % and median vote %
  - Winners below/above median grouped by party    
🟡 Visualizations (Plotly + Matplotlib)
  - Alliance-colored bar charts
  - Bubble charts (Votes vs Seats vs Vote Share)
  - Heatmaps
  - Scatter plots
  - Annotated bar charts  

**4. How to Run**  
a) git clone https://github.com/sunderramanv/Bihar-2025-Election-Analytics.git  
b) cd Bihar-2025-Election-Analytics  
c) pip install -r requirements.txt  
d) jupyter notebook notebooks/Bihar_2025_Election_Analytics.ipynb  

**5. Data Sources**  
Election Commission of India – https://results.eci.gov.in  
Official district constituency PDF  
Candidate-wise HTML pages (Selenium extracted)  

**6. Technologies Used**  
Python 3.x  
Pandas  
Plotly  
Matplotlib  
Seaborn  
Jupyter Notebook  
Selenium (for scraping)  
Camelot (PDF parsing)  

**7. Future Enhancements**  
Alliance-wise trend analysis  
Voter turnout vs winning margins  
Compare 2025 vs 2020 elections  
Predictive modelling (margin predictions)  
Interactive dashboard via Streamlit  

**8. Author**
Sunder Raman V  
📍 India  
🔗 LinkedIn: https://www.linkedin.com/in/sunderramanv/  
