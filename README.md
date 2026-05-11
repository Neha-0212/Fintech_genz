# Fintech GenZ Customer Intelligence & Risk Analytics

> **1,000 Gen Z fintech customers. 8 SQL-powered business questions. 1 clear product recommendation.**  
> This project diagnoses why Gen Z converts 20pp below older cohorts, quantifies credit risk by segment, and delivers a data-driven credit threshold strategy — packaged as a production-style analytics case study.

---

## Business Problem

Fintech platforms targeting Gen Z face a paradox: **the most digitally native cohort converts at the lowest rates.**

This project investigates that gap across three dimensions:

| Dimension | Business Question |
|---|---|
| **Onboarding** | Where exactly does the funnel break — and for whom? |
| **Risk** | Which customer segments generate net value vs. net loss? |
| **Acquisition** | Which channels produce profitable, low-risk customers? |

Without answers, product and marketing teams over-invest in leaky funnels, approve high-risk segments at scale, and misallocate channel spend — all of which erode unit economics.

---

## Objectives

- **Funnel drop-off analysis** — identify highest-friction onboarding steps by conversion rate
- **Segment conversion benchmarking** — compare Gen Z vs. older cohorts by channel and occupation
- **Credit risk profiling** — model default and fraud rates across risk bands
- **Channel P&L analysis** — evaluate acquisition ROI by conversion rate, default rate, and net value
- **Micro-segment targeting** — identify occupation × region combos with highest net value potential
- **Credit threshold simulation** — quantify business trade-offs at CS 550 / 650 / 750 approval thresholds
- **High-risk customer flagging** — surface actionable review lists for risk operations teams

---

## Dataset

| Attribute | Detail |
|---|---|
| **Source** | Synthetic fintech platform data (production-representative schema) |
| **Scale** | 1,000 customers, 4 relational tables |
| **Format** | Structured CSV + SQLite database |
| **Scope** | Jan 2024 customer cohort, Gen Z focus (ages 20–34, avg 27.3) |
| **Tables** | `customers`, `onboarding_events`, `transactions`, `risk_profile` |
| **Key Fields** | age_group, acquisition_channel, onboarding_step, credit_score, default_flag, fraud_flag, est_revenue, net_value |

---

## Tech Stack

| Layer | Tools |
|---|---|
| **Analytics & Querying** | SQL (SQLite), Python (pandas, csv) |
| **Visualization / Reporting** | Power BI (dashboard queries packaged), PowerPoint (strategy deck) |
| **Database** | SQLite (indexed, normalized relational schema) |
| **Notebook** | Jupyter Notebook (EDA + insight validation) |
| **Simulation** | SQL UNION-based threshold modeling |

---

## Data Pipeline & Workflow

```
Raw CSV (1,000 customers)
    │
    ▼
Schema Design & Indexing
  └─ 4 normalized tables + 9 composite indexes for query optimization
    │
    ▼
SQL Analysis Layer (8 core queries)
  └─ Funnel analysis → Segmentation → Risk profiling → P&L → Simulation
    │
    ▼
Insight Extraction
  └─ Per-query business findings + recommended actions
    │
    ▼
Dashboard Query Pack
  └─ Pre-built KPI card queries for Power BI integration
    │
    ▼
Executive Strategy Deck (PowerPoint)
  └─ Business recommendations with supporting data
```

---

## Key Features

**SQL Query Pack (8 production-ready queries)**
- Q1: Funnel drop-off by onboarding step with conversion % and drop rate %
- Q2: Conversion rate matrix — channel × age group × net value
- Q3: Gen Z vs. non-Gen Z profitability comparison
- Q4: Risk band vs. transaction behavior correlation
- Q5: High-risk customer identification list (operational output)
- Q6: Full channel P&L — revenue, loss, net value, default rate
- Q7: Occupation × Region micro-segment profitability ranking
- Q8: Credit threshold simulation (CS 550 / 650 / 750 UNION comparison)

**Database Engineering**
- 9 indexed columns (`acquisition_channel`, `age_group`, `credit_score`, `default_flag`, `risk_band`) — each query comments explain which index it uses and why
- Normalized schema eliminates redundancy and enables efficient multi-table JOINs

**Dashboard-Ready KPI Queries**
- Overall conversion rate card
- Default rate card
- Gen Z conversion gap (in percentage points)
- Total portfolio net value
- Risk band distribution for slicer/filter

---

## KPIs & Metrics Tracked

| KPI | Value |
|---|---|
| Overall Conversion Rate | 60.1% |
| Gen Z Conversion Rate | ~46.7% |
| Non-Gen Z Conversion Rate | ~66.9% |
| Gen Z Conversion Gap | ~20 percentage points |
| Portfolio Default Rate | 19.1% |
| Fraud Rate | 2.8% |
| CS ≥ 650 Approval Rate | ~75% of customers |
| CS ≥ 650 Default Rate | ~12% |
| CS ≥ 750 Approval Rate | ~60% |
| Avg Customer Net Value (Gen Z active) | ₹226 vs ₹198 (older cohorts) |

---

## Key Insights

1. **KYC and OTP Verification are the primary funnel killers.** These two steps account for the majority of drop-offs. Simplifying KYC UX and adding progress indicators at OTP could materially lift conversion.

2. **Gen Z converts 20pp below older cohorts — but active Gen Z users generate higher net value (₹226 vs ₹198).** The problem is funnel friction, not customer quality. Fix onboarding, not the audience.

3. **Referral is the highest-ROI acquisition channel.** It delivers the best net value and similar or lower default rates versus Ads, which has the worst conversion-to-default trade-off.

4. **Transaction behavior does not predict default risk.** Default rates are credit-score-driven in this dataset, not behavior-driven — meaning transaction monitoring alone won't catch defaulters early. Credit scoring must remain the primary risk gate.

5. **Credit Score ≥ 650 is the optimal approval threshold.** It captures ~75% of approvals at ~12% default rate. CS ≥ 750 leaves 40%+ of portfolio net value unrealized; CS ≥ 550 spikes default rates to 25%+ with marginal net value gain.

6. **Freelancer + Tier1 and Salaried + Tier1 are the top-value micro-segments.** Tier2 cities show comparable average net values with lower default rates — a high-potential, underserved market.

7. **Ads channel has the lowest ROI.** It has the worst conversion rate and similar default rates to other channels — suggesting budget reallocation to Referral incentive programs would improve acquisition efficiency.

---

## Dashboard / Visualizations

The Power BI query pack supports:

- **Funnel waterfall chart** — conversion % by onboarding step
- **Segment heatmap** — channel × age group conversion rates
- **Risk band donut chart** — portfolio distribution with default/fraud overlays
- **Channel P&L bar chart** — total revenue, loss, and net value per channel
- **Micro-segment table** — occupation × region ranked by net value
- **Credit threshold comparison table** — approval rate, default rate, net value at 3 thresholds
- **KPI cards** — conversion rate, default rate, Gen Z gap, total net value

---

## Business Impact

| Area | Impact |
|---|---|
| **Onboarding** | Identified two high-friction steps; UX fix could recover 15–20% of dropped users |
| **Risk Management** | Credit threshold recommendation (CS ≥ 650) reduces default exposure while preserving ~75% of approvals |
| **Marketing Spend** | Referral-first channel strategy could improve acquisition ROI by reallocating Ads budget |
| **Targeting** | Tier2 + Freelancer/Salaried micro-segments identified as high-value, low-risk expansion opportunity |
| **Operations** | High-risk customer list (Q5) ready for direct integration into risk review workflows |
| **Product Strategy** | Gen Z paradox framing gives product team a clear mandate: fix the funnel, not the audience |

---

## Challenges & Solutions

| Challenge | Solution |
|---|---|
| Multi-table joins without performance degradation | 9 targeted indexes on GROUP BY and WHERE columns; each query documents which index it uses |
| Threshold comparison requiring multiple aggregations | SQL UNION ALL pattern to compare 3 strategies in a single query result set |
| Avoiding double-counting in funnel metrics | Separate `conversion_flag` field in `onboarding_events` used for clean aggregation |
| Keeping business context in SQL | Inline `-- INSIGHT` and `-- ACTION` comments on every query |
| Micro-segment explosion (occupation × region cross join) | Low-cardinality columns kept the GROUP BY performant without partitioning |

---

## Future Improvements

- **Predictive churn model** — logistic regression on drop-off probability by step + segment
- **LTV forecasting** — time-series projection of net value per cohort
- **Anomaly detection** — flag sudden spikes in fraud_flag or default_flag by region
- **Vector search / semantic segmentation** — cluster customers by behavioral profiles beyond rule-based bands
- **Streaming ingestion** — replace batch CSV with Kafka or Pub/Sub for real-time risk scoring
- **Cloud deployment** — migrate SQLite to BigQuery or Redshift for scale beyond 1M records
- **A/B test framework** — structure onboarding experiments to measure UX interventions statistically

---

## Project Structure

```
Fintech_genz-main/
├── fintech_genz_case.csv          # Raw dataset (1,000 customers, 14 fields)
├── fintech_genz.db                # SQLite database (normalized, indexed schema)
├── fintech_genz_queries.sql       # 8 core analysis queries + dashboard query pack
├── fintech_genz_analysis.ipynb    # EDA notebook (Python/pandas)
└── fintech_genz_strategy.pptx     # Executive strategy deck with recommendations
└── fintech_genz_dashboard.py      # Dashboard 
```

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/fintech-genz-analytics.git
cd fintech-genz-analytics

# Run SQL analysis (SQLite)
sqlite3 fintech_genz.db < fintech_genz_queries.sql

# Or explore interactively
sqlite3 fintech_genz.db
sqlite> .tables
sqlite> SELECT * FROM customers LIMIT 5;

# Python EDA
pip install pandas jupyter
jupyter notebook fintech_genz_analysis.ipynb

# Dashboard
pip install streamlit
streamlit run fintech_genz_dashboard.py
```

---

## Why This Project Stands Out

**Business clarity over technical noise.** Every query answers a specific business question, with the insight and recommended action written inline — not buried in a notebook cell.

**Production-grade SQL discipline.** Indexed schema, documented query optimization notes, and modular query structure that mirrors how analytics engineers write for data warehouses.

**Product-minded framing.** The Gen Z paradox insight — lower conversion but higher net value — is the kind of counterintuitive finding that changes product roadmap decisions. That's the goal of analytics.

**End-to-end ownership.** Schema design → SQL analysis → dashboard query pack → executive deck. Covers the full analyst-to-stakeholder workflow.

**Actionable, not academic.** No generic conclusions. Every insight maps to a specific product, marketing, or risk action.

---

*Built as a production-style portfolio case study demonstrating SQL analytics, business problem framing, and data-driven decision-making for fintech product and analytics roles.*
