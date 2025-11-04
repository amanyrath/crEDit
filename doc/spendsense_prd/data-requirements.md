# Data Requirements

## Synthetic Data Generation

**Seed 3 Demo Users:**

**User 1: Hannah Martinez (High Utilization)**
- Age: 29, Income: $48,000/year
- Accounts:
  - Checking: $850 balance
  - Savings: $1,200 balance
  - Visa Credit Card: $3,400 balance / $5,000 limit (68% utilization)
- Transactions (90 days):
  - ~200 transactions
  - Categories: 40% necessities, 30% discretionary, 20% bills, 10% subscriptions
  - Recurring: Netflix, Spotify, Planet Fitness, Adobe
  - Credit card interest charges: $87/month
  - Minimum payments only
- Persona: High Utilization
- Key behaviors: High utilization, interest charges, minimum payments

**User 2: Sam Patel (Subscription-Heavy)**
- Age: 34, Income: $65,000/year
- Accounts:
  - Checking: $2,400 balance
  - Savings: $5,000 balance
  - Credit Card: $800 balance / $8,000 limit (10% utilization)
- Transactions (90 days):
  - ~180 transactions
  - 8 active subscriptions totaling $203/month
  - Recurring: Netflix, Hulu, Disney+, Spotify, Apple iCloud, NYT, Peloton, HelloFresh
  - Subscription share: 15% of total spend
- Persona: Subscription-Heavy
- Key behaviors: Multiple subscriptions, good credit habits

**User 3: Sarah Chen (Savings Builder)**
- Age: 26, Income: $55,000/year
- Accounts:
  - Checking: $3,200 balance
  - High-Yield Savings: $8,500 balance (growing)
  - Credit Card: $400 balance / $3,000 limit (13% utilization)
- Transactions (90 days):
  - ~150 transactions
  - Automatic savings transfer: $500/month
  - Low discretionary spending
  - Pays credit card in full monthly
- Persona: Savings Builder
- Key behaviors: Consistent saving, low utilization, automated transfers

**Data Format:**
- CSV files: `accounts.csv`, `transactions.csv`
- JSON structure following Plaid schema
- No real PII - use faker library for names, addresses

---

## Content Catalog

**Education Items (15 total, 3-5 per persona):**

**High Utilization:**
1. Understanding Credit Utilization
2. The Real Cost of Minimum Payments
3. Debt Avalanche vs. Debt Snowball
4. How to Set Up Autopay
5. Building a Debt Paydown Plan

**Subscription-Heavy:**
1. The $200 Question: Are You Using All Your Subscriptions?
2. How to Negotiate Lower Bills
3. Subscription Cancellation Made Easy
4. Setting Up Bill Alerts

**Variable Income:**
1. Budgeting with Irregular Income
2. Building a Cash-Flow Buffer
3. The 50/30/20 Rule (Adapted)

**Savings Builder:**
1. From Savings to Investing: When Are You Ready?
2. High-Yield Savings Accounts Explained
3. Setting SMART Financial Goals
4. CD Laddering Basics

**Partner Offers (8 total):**
1. Balance Transfer Credit Card (0% APR for 18 months)
2. High-Yield Savings Account (4.5% APY)
3. Budgeting App (Mint alternative)
4. Subscription Management Tool (Truebill)
5. Credit Monitoring Service
6. Financial Planning Consultation
7. Debt Consolidation Loan
8. Cashback Credit Card

---
