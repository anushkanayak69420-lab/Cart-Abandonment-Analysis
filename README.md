# Cart Abandonment Analysis

**Question:** Where do customers drop off during checkout, and is the biggest drop-off a fixable problem?

**Finding:** Small orders (under Rs 800) that see a shipping fee late in checkout abandon at **87.5%**, versus **68.9%** for everyone else. The gap holds on Mobile, Desktop and Tablet, so it is a checkout-flow issue, not a device issue.

**Recommendation:** Show the shipping cost on the cart page, before checkout starts.

## Live links
- Interactive dashboard (web): PASTE_GITHUB_PAGES_LINK_HERE
- Power BI report: PASTE_POWER_BI_LINK_HERE

## What's in this repo
| File | What it is |
|---|---|
| `cart_abandonment_queries.sql` | 5 SQL queries that answer the project questions (funnel, abandonment rate, shipping-fee comparison, revenue lost, device check) |
| `generate_data.py` | Python script that builds 18,000 simulated checkout sessions |
| `checkout_sessions.csv` | The dataset it produces |
| `Cart_Abandonment_Analysis.xlsx` | Excel workbook: funnel, shipping-fee comparison (with pie chart), device cut. All live formulas |
| `index.html` | Interactive dashboard (filter by device) |
| `PowerBI_Build_Guide.md` | How the Power BI version is built |

## Tools
SQL, Excel, Power BI (Python only to generate the practice dataset)

## How to run the SQL
1. Install the free DB Browser for SQLite.
2. File > Import > Table from CSV file, choose `checkout_sessions.csv`, name the table `checkout_sessions`.
3. Open the Execute SQL tab, paste queries from `cart_abandonment_queries.sql`, and run them one at a time.

## How to regenerate the data (optional)
```
pip install pandas numpy
python generate_data.py
```

## Note on the data
The data is synthetically generated to demonstrate the method. It is not real company data.
