

CREATE TABLE IF NOT EXISTS customers (
    customer_id         INTEGER PRIMARY KEY,
    age                 INTEGER,
    income              INTEGER,
    occupation          TEXT,
    region              TEXT,
    acquisition_channel TEXT,
    signup_date         TEXT,
    age_group           TEXT
);

CREATE TABLE IF NOT EXISTS onboarding_events (
    event_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER REFERENCES customers(customer_id),
    onboarding_step     TEXT,
    onboarding_status   TEXT,
    conversion_flag     INTEGER   
);

CREATE TABLE IF NOT EXISTS transactions (
    tx_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id           INTEGER REFERENCES customers(customer_id),
    transaction_count     INTEGER,
    avg_transaction_value INTEGER,
    total_volume          INTEGER,
    transaction_intensity TEXT,
    high_value_flag       INTEGER
);

CREATE TABLE IF NOT EXISTS risk_profile (
    risk_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id       INTEGER REFERENCES customers(customer_id),
    credit_score      INTEGER,
    risk_band         TEXT,
    default_flag      INTEGER,
    fraud_flag        INTEGER,
    high_risk_flag    INTEGER,
    est_revenue       REAL,
    est_loss          REAL,
    net_value         REAL
);

CREATE INDEX IF NOT EXISTS idx_cust_channel   ON customers(acquisition_channel);
CREATE INDEX IF NOT EXISTS idx_cust_age_group ON customers(age_group);
CREATE INDEX IF NOT EXISTS idx_cust_occ       ON customers(occupation);
CREATE INDEX IF NOT EXISTS idx_onb_status     ON onboarding_events(onboarding_status);
CREATE INDEX IF NOT EXISTS idx_onb_step       ON onboarding_events(onboarding_step);
CREATE INDEX IF NOT EXISTS idx_risk_credit    ON risk_profile(credit_score);
CREATE INDEX IF NOT EXISTS idx_risk_default   ON risk_profile(default_flag);
CREATE INDEX IF NOT EXISTS idx_risk_band      ON risk_profile(risk_band);
CREATE INDEX IF NOT EXISTS idx_tx_hv          ON transactions(high_value_flag);


-- ============================================================
-- Q1: FUNNEL DROP-OFF ANALYSIS
-- PURPOSE  : Identify which onboarding step loses the most users
-- LOGIC    : Group by step; compare completed vs dropped counts
-- OPTIMIZE : idx_onb_status, idx_onb_step used in GROUP BY + WHERE
-- ============================================================

SELECT
    o.onboarding_step,
    COUNT(*)                                                                AS total_users,
    SUM(CASE WHEN o.onboarding_status = 'Completed' THEN 1 ELSE 0 END)     AS converted,
    SUM(CASE WHEN o.onboarding_status = 'Dropped'   THEN 1 ELSE 0 END)     AS dropped,
    ROUND(
        100.0 * SUM(CASE WHEN o.onboarding_status = 'Completed' THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                                                       AS conversion_pct,
    ROUND(
        100.0 * SUM(CASE WHEN o.onboarding_status = 'Dropped' THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                                                       AS drop_rate_pct
FROM onboarding_events o
GROUP BY o.onboarding_step
ORDER BY conversion_pct ASC;

-- INSIGHT: KYC and OTP_Verification steps have the highest drop rates.
-- ACTION: Simplify KYC UX; add progress indicators at OTP step.


-- ============================================================
-- Q2: CONVERSION RATE BY SEGMENT (Channel × Age Group)
-- PURPOSE  : Find which channel+segment combinations convert best
-- LOGIC    : JOIN customers + onboarding; aggregate by channel + age_group
-- OPTIMIZE : idx_cust_channel + idx_cust_age_group enable fast GROUP BY
-- ============================================================

SELECT
    c.acquisition_channel,
    c.age_group,
    COUNT(*)                                                    AS total_customers,
    SUM(o.conversion_flag)                                      AS converted,
    ROUND(100.0 * AVG(o.conversion_flag), 1)                    AS conversion_rate_pct,
    ROUND(AVG(r.net_value), 0)                                  AS avg_net_value
FROM customers c
JOIN onboarding_events o USING (customer_id)
JOIN risk_profile       r USING (customer_id)
GROUP BY c.acquisition_channel, c.age_group
ORDER BY conversion_rate_pct DESC;

-- INSIGHT: Referral channel converts best across all segments.
-- Gen Z via Ads is the worst performing combination (low conv + higher risk).


-- ============================================================
-- Q3: GEN Z vs OTHERS FULL COMPARISON
-- PURPOSE  : Quantify the Gen Z problem across all key metrics
-- LOGIC    : age_group flag derived during ingestion; join 3 tables
-- OPTIMIZE : idx_cust_age_group handles the GROUP BY efficiently
-- ============================================================

SELECT
    c.age_group,
    COUNT(*)                                                        AS total_customers,
    ROUND(AVG(c.age), 1)                                            AS avg_age,
    ROUND(AVG(c.income), 0)                                         AS avg_income,
    ROUND(100.0 * AVG(o.conversion_flag), 1)                        AS conversion_rate_pct,
    ROUND(100.0 * AVG(r.default_flag), 1)                           AS default_rate_pct,
    ROUND(100.0 * AVG(r.fraud_flag), 1)                             AS fraud_rate_pct,
    ROUND(AVG(r.credit_score), 0)                                   AS avg_credit_score,
    ROUND(AVG(t.transaction_count), 1)                              AS avg_tx_count,
    ROUND(AVG(t.avg_transaction_value), 0)                          AS avg_tx_value,
    ROUND(AVG(r.net_value), 0)                                      AS avg_net_value,
    ROUND(SUM(r.net_value), 0)                                      AS total_net_value
FROM customers c
JOIN onboarding_events o USING (customer_id)
JOIN transactions       t USING (customer_id)
JOIN risk_profile       r USING (customer_id)
GROUP BY c.age_group
ORDER BY total_net_value DESC;

-- INSIGHT: Gen Z converts at 46.7% vs 66.9% for older segments.
-- Despite lower conversion, Gen Z avg_net_value is HIGHER (₹226 vs ₹198)
-- because active Gen Z users transact more intensively.


-- ============================================================
-- Q4: RISK vs BEHAVIOR ANALYSIS
-- PURPOSE  : Understand how credit risk correlates with transaction behavior
-- LOGIC    : Join risk_profile + transactions; segment by risk_band
-- OPTIMIZE : idx_risk_band handles GROUP BY; idx_risk_credit supports ORDER BY
-- ============================================================

SELECT
    r.risk_band,
    COUNT(*)                                        AS customers,
    ROUND(AVG(r.credit_score), 0)                   AS avg_credit_score,
    ROUND(AVG(t.transaction_count), 1)              AS avg_tx_count,
    ROUND(AVG(t.avg_transaction_value), 0)          AS avg_tx_value,
    ROUND(AVG(t.total_volume), 0)                   AS avg_total_volume,
    ROUND(100.0 * AVG(r.default_flag), 1)           AS default_rate_pct,
    ROUND(AVG(r.net_value), 0)                      AS avg_net_value
FROM risk_profile r
JOIN transactions  t USING (customer_id)
GROUP BY r.risk_band
ORDER BY default_rate_pct DESC;

-- INSIGHT: Transaction count and value do NOT significantly differ by risk band.
-- Default risk is credit-score-driven, not behavior-driven in this dataset.
-- Implication: transaction monitoring alone won't catch defaulters early.


-- ============================================================
-- Q5: HIGH-RISK CUSTOMER IDENTIFICATION
-- PURPOSE  : Surface actionable high-risk customer list for review
-- LOGIC    : Filter on high_risk_flag (default OR fraud); sort by credit score
-- OPTIMIZE : idx_risk_default accelerates WHERE clause; LIMIT prevents full scan
-- ============================================================

SELECT
    c.customer_id,
    c.age,
    c.age_group,
    c.occupation,
    c.region,
    c.acquisition_channel,
    r.credit_score,
    r.risk_band,
    r.default_flag,
    r.fraud_flag,
    ROUND(t.total_volume, 0)    AS total_tx_volume,
    ROUND(r.net_value, 0)       AS net_value
FROM customers   c
JOIN risk_profile r USING (customer_id)
JOIN transactions  t USING (customer_id)
WHERE r.high_risk_flag = 1
ORDER BY r.credit_score ASC, r.default_flag DESC
LIMIT 25;

-- Use LIMIT for operational review lists.
-- Remove LIMIT for full export to risk management system.


-- ============================================================
-- Q6: CHANNEL PERFORMANCE (Full P&L view)
-- PURPOSE  : Evaluate each acquisition channel on conversion + profitability
-- LOGIC    : Aggregate revenue/loss/net across all three tables
-- OPTIMIZE : idx_cust_channel; single pass GROUP BY with aggregates
-- ============================================================

SELECT
    c.acquisition_channel,
    COUNT(*)                                        AS total_customers,
    SUM(o.conversion_flag)                          AS converted,
    ROUND(100.0 * AVG(o.conversion_flag), 1)        AS conversion_rate_pct,
    ROUND(100.0 * AVG(r.default_flag), 1)           AS default_rate_pct,
    ROUND(SUM(r.est_revenue), 0)                    AS total_revenue,
    ROUND(SUM(r.est_loss), 0)                       AS total_loss,
    ROUND(SUM(r.net_value), 0)                      AS total_net_value,
    ROUND(AVG(r.net_value), 0)                      AS avg_net_per_customer
FROM customers        c
JOIN onboarding_events o USING (customer_id)
JOIN risk_profile       r USING (customer_id)
GROUP BY c.acquisition_channel
ORDER BY total_net_value DESC;

-- INSIGHT: Referral generates most net value. Ads has lowest conversion
-- and similar default rate — worst ROI on acquisition spend.
-- ACTION: Shift budget from Ads to Referral incentive programs.


-- ============================================================
-- Q7: PROFITABILITY ESTIMATION BY OCCUPATION × REGION
-- PURPOSE  : Identify highest-value micro-segments for targeting
-- LOGIC    : Cross join occupation + region with profitability metrics
-- OPTIMIZE : Composite GROUP BY on two low-cardinality text columns
-- ============================================================

SELECT
    c.occupation,
    c.region,
    COUNT(*)                            AS customers,
    ROUND(AVG(r.credit_score), 0)       AS avg_credit_score,
    ROUND(100.0 * AVG(r.default_flag),1)AS default_rate_pct,
    ROUND(SUM(r.est_revenue), 0)        AS total_revenue,
    ROUND(SUM(r.est_loss), 0)           AS total_loss,
    ROUND(SUM(r.net_value), 0)          AS total_net_value,
    ROUND(AVG(r.net_value), 0)          AS avg_net_per_customer
FROM customers   c
JOIN risk_profile r USING (customer_id)
GROUP BY c.occupation, c.region
ORDER BY total_net_value DESC;

-- INSIGHT: Freelancer + Tier1 and Salaried + Tier1 are top micro-segments.
-- Tier2 cities have comparable avg net values but lower default rates.
-- ACTION: Launch Tier2-targeted campaigns with Referral channel.


-- ============================================================
-- Q8: BUSINESS TRADEOFF SIMULATION (Threshold = 650)
-- PURPOSE  : Show what happens to key metrics at recommended CS threshold
-- LOGIC    : Subquery filters approved customers; outer query aggregates
-- OPTIMIZE : idx_risk_credit makes the WHERE clause fast
-- ============================================================

SELECT
    'Credit Score ≥ 650 (Recommended)'          AS strategy,
    COUNT(*)                                     AS approved_customers,
    ROUND(100.0 * COUNT(*) / 1000.0, 1)         AS approval_rate_pct,
    ROUND(100.0 * AVG(r.default_flag), 1)        AS default_rate_pct,
    ROUND(SUM(r.net_value), 0)                   AS total_net_value,
    ROUND(AVG(r.net_value), 0)                   AS avg_net_per_customer
FROM risk_profile r
WHERE r.credit_score >= 650

UNION ALL

SELECT
    'Aggressive (CS ≥ 550)'                     AS strategy,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / 1000.0, 1),
    ROUND(100.0 * AVG(r.default_flag), 1),
    ROUND(SUM(r.net_value), 0),
    ROUND(AVG(r.net_value), 0)
FROM risk_profile r
WHERE r.credit_score >= 550

UNION ALL

SELECT
    'Conservative (CS ≥ 750)'                   AS strategy,
    COUNT(*),
    ROUND(100.0 * COUNT(*) / 1000.0, 1),
    ROUND(100.0 * AVG(r.default_flag), 1),
    ROUND(SUM(r.net_value), 0),
    ROUND(AVG(r.net_value), 0)
FROM risk_profile r
WHERE r.credit_score >= 750;

-- INSIGHT: CS≥650 captures ~75% of approvals with ~12% default rate.
-- CS≥750 = very safe but leaves 40%+ of net value on the table.
-- CS≥550 = marginal net value gain, default rate spikes to 25%+.


-- ============================================================
-- POWER BI / DASHBOARD — SUPPORTING QUERIES
-- ============================================================

-- KPI Card: Overall Conversion Rate
SELECT ROUND(100.0 * AVG(conversion_flag), 1) AS overall_conversion_pct
FROM onboarding_events;

-- KPI Card: Default Rate
SELECT ROUND(100.0 * AVG(default_flag), 1) AS default_rate_pct
FROM risk_profile;

-- KPI Card: Gen Z Conversion Gap
SELECT
    ROUND(100.0 * AVG(CASE WHEN c.age_group = 'Gen Z' THEN o.conversion_flag END), 1)  AS genz_conv,
    ROUND(100.0 * AVG(CASE WHEN c.age_group != 'Gen Z' THEN o.conversion_flag END), 1) AS others_conv,
    ROUND(
        100.0 * AVG(CASE WHEN c.age_group != 'Gen Z' THEN o.conversion_flag END) -
        100.0 * AVG(CASE WHEN c.age_group = 'Gen Z'  THEN o.conversion_flag END),
        1
    ) AS gap_pp
FROM customers c
JOIN onboarding_events o USING (customer_id);

-- KPI Card: Total Net Value
SELECT ROUND(SUM(net_value), 0) AS total_net_value FROM risk_profile;

-- Dashboard filter: Risk Band distribution
SELECT risk_band, COUNT(*) AS n, ROUND(100.0*COUNT(*)/1000,1) AS pct
FROM risk_profile GROUP BY risk_band ORDER BY pct DESC;

-- ============================================================
-- END OF QUERY PACK
-- ============================================================
