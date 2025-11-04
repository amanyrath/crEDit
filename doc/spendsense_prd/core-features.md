# Core Features

## 1. Authentication & Authorization

**Requirements:**
- Real authentication via AWS Cognito User Pools
- Role-based access control (consumer vs operator)
- Pre-seeded demo accounts for testing
- Session management and token refresh

**User Flows:**

**Consumer Login:**
1. User navigates to app
2. Enters email/password
3. If first login → consent modal appears
4. User must grant consent before accessing dashboard
5. Redirects to consumer dashboard

**Operator Login:**
1. User navigates to app
2. Enters email/password with operator role
3. Redirects to operator user list
4. No consent required (viewing aggregated data)

**Demo Accounts:**
- `hannah@demo.com` / `demo123` (Consumer - High Utilization persona)
- `sam@demo.com` / `demo123` (Consumer - Subscription-Heavy persona)
- `operator@demo.com` / `demo123` (Operator access)

**Technical Details:**
- AWS Cognito User Pools with JWT tokens
- Application-layer security enforces data access (users can only access their own data, operators can access all data based on role)
- Consent tracked in `consent_records` table with timestamps
- IP address logging for consent audit trail

---

## 2. Consumer Dashboard

**Layout:**
4-tab navigation with persistent chat widget

### Tab 1: Transactions

**Purpose:** Allow users to review their spending history

**Features:**
- Table view with columns:
  - Date
  - Merchant Name
  - Amount (color-coded: red for debit, green for credit)
  - Category (with icon)
  - Account (last 4 digits)
- Filters:
  - Date range (30/90 days)
  - Category dropdown
  - Search by merchant name
- Sort by date (default: newest first) or amount
- Pagination (50 transactions per page)

**Edge Cases:**
- Empty state: "No transactions found for this filter"
- Pending transactions marked with badge
- Large amounts (>$1000) highlighted

---

### Tab 2: Insights 🌟 *Showcase Feature*

**Purpose:** Visualize spending patterns and key financial metrics

**Features:**

**Chart 1: Monthly Spending by Category**
- Type: Horizontal bar chart
- X-axis: Amount ($)
- Y-axis: Categories (Food & Drink, Shopping, Bills, etc.)
- Time period toggle: 30d / 90d
- Hover: Show exact amount + % of total

**Chart 2: Credit Utilization Trend**
- Type: Line chart
- X-axis: Date (weekly buckets)
- Y-axis: Utilization % (0-100%)
- Reference lines: 30% (green), 50% (yellow), 80% (red)
- Tooltip: "Week of [date]: 65% utilization ($3,400 / $5,000)"
- Only shown if user has credit accounts

**Chart 3: Subscription Breakdown**
- Type: Donut chart
- Inner: Total monthly recurring ($)
- Segments: Individual subscriptions by merchant
- Legend: Merchant name + amount
- Click segment → filter transactions to that merchant

**Summary Cards (above charts):**
- Total Spending (period)
- Average Daily Spend
- Top Category
- Savings Rate (if applicable)

**Explanation Boxes:**
Each chart has a "What this means" expandable section with plain-language explanation.

---

### Tab 3: Education

**Purpose:** Deliver personalized financial education content

**Features:**

**Content Cards (3-5 per user):**
Each card displays:
- Icon (matched to category: credit, savings, budgeting, etc.)
- Title (e.g., "Understanding Credit Utilization")
- Brief description (2-3 sentences)
- **Rationale box** (highlighted background):
  - "We're showing you this because [specific data point]"
  - Example: "...your Visa ending in 4523 is at 65% utilization ($3,400 of $5,000 limit)"
- "Learn More" button (expands full content in modal)
- Tags: #Credit #DebtManagement

**Content Mapping:**
- High Utilization persona → Credit utilization explainer, debt paydown strategies, minimum payment dangers
- Subscription-Heavy persona → Subscription audit checklist, negotiation tips, cancellation workflows
- Savings Builder persona → Goal-setting frameworks, HYSA explainers, CD basics

**Card Sorting:**
- Priority order based on persona match and signal strength
- Most urgent/relevant at top
- Color-coded by topic area

**Disclaimer:**
At bottom of tab: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."

---

### Tab 4: Offers

**Purpose:** Present relevant partner products with eligibility transparency

**Features:**

**Offer Cards (2-3 per user):**
Each card displays:
- Partner logo
- Product name (e.g., "Balance Transfer Credit Card")
- Brief description
- Eligibility status:
  - ✅ "You may be eligible" (green badge)
  - ⚠️ "Requirements not met" (yellow badge) + explanation
- **Rationale:**
  - "This might help because [data-driven reason]"
  - Example: "...you're currently paying $87/month in interest on your Visa"
- "Learn More" external link
- **Disclosure:** "SpendSense may receive compensation. This is not a recommendation."

**Eligibility Logic:**
- Balance transfer card: High utilization (>50%) + no recent late payments
- HYSA: Building savings + current savings APY < 2%
- Budgeting app: Variable income detected OR subscription-heavy
- Subscription manager: ≥5 active subscriptions

**Filtering:**
- Don't show products user already has
- Don't show products with income requirements not met
- Never show predatory products (payday loans, high-fee accounts)

---

### Chat Widget

**Purpose:** Answer user questions about their financial data

**Features:**
- Fixed position: bottom-right corner
- Expandable/collapsible
- Chat history (session-based)
- Typing indicator when processing

**Example Queries:**
- "What's my credit utilization?"
- "How much do I spend on subscriptions?"
- "Why am I seeing this education content?"
- "What can I do to improve my credit score?"

**Response Format:**
- Cites specific data points
- Includes numbers from actual transactions
- Links back to relevant tabs ("See Insights tab for more")
- Always includes disclaimer at end

**Guardrails:**
- No financial advice (only education)
- No shaming language
- PII scrubbing in logs
- Error handling for unclear questions
- Rate limiting (10 messages per minute)

**Technical Implementation:**
- OpenAI GPT-4 or Claude API
- System prompt with strict guidelines
- Retrieval of user's computed features + recent transactions
- Response validation before displaying

---

## 3. Operator Dashboard

**Layout:**
2-page application

### Page 1: User List

**Purpose:** Overview of all users for monitoring and selection

**Features:**

**Table View:**
- Columns:
  - Full Name
  - Email
  - Primary Persona (30-day)
  - Risk Flags (badges: 🔴 High Utilization, ⚠️ Overdue, etc.)
  - Last Active
  - Actions (View Details button)
- Sort by any column
- Search by name or email
- Filter by persona type
- Filter by risk flags

**Summary Stats (top of page):**
- Total Users
- Users by Persona (bar chart)
- Active Users (last 7 days)
- Flagged Users Requiring Review

---

### Page 2: User Detail

**Purpose:** Deep dive into individual user's data and recommendations

**Layout:**

**Section 1: User Overview**
- Name, email, member since
- Consent status + timestamp
- Connected accounts (number + types)
- Persona assignments:
  - 30-day: [Persona Name]
  - 90-day: [Persona Name]
  - 180-day: [Persona Name] (if different, shows evolution)

**Section 2: Behavioral Signals**
Display all detected signals with time windows:

**Credit Signals:**
- Visa ****4523: 65% utilization ($3,400 / $5,000)
- Last payment: $50 (minimum only)
- Interest charged: $87 last statement
- Status: Current (no overdues)

**Subscription Signals:**
- 8 active recurring merchants
- Monthly total: $203
- Top subscriptions: Netflix ($15), Spotify ($10), ...
- Subscription share: 15% of total spend

**Savings Signals:**
- Emergency fund: $1,200
- Monthly net inflow: $150
- Growth rate: 3.2% over 90 days
- Coverage: 1.2 months expenses

**Income Signals:**
- Payroll frequency: Biweekly
- Average paycheck: $1,750
- Last deposit: Oct 28, 2025
- Cash-flow buffer: 0.8 months

**Section 3: Recommendations Review**
Table of all education items + offers shown to user:
- Columns:
  - Type (Education / Offer)
  - Title
  - Shown At (timestamp)
  - Clicked? (boolean)
  - Decision Trace (button)
- Click "Decision Trace" → Opens modal with JSON view

**Decision Trace Format:**
```json
{
  "recommendation_id": "rec_123",
  "type": "education",
  "title": "Understanding Credit Utilization",
  "rationale": "User's Visa ****4523 is at 65% utilization",
  "decision_logic": {
    "persona_match": "high_utilization",
    "signals_used": [
      "credit_utilization_visa_4523: 0.65",
      "minimum_payment_only: true",
      "interest_charged: 87.00"
    ],
    "eligibility_checks_passed": true,
    "tone_validation_passed": true,
    "timestamp": "2025-11-03T10:30:00Z"
  }
}
```

**Section 4: Operator Actions**
- Button: "Override Recommendation" (logs action)
- Button: "Flag for Review" (adds to queue)
- Audit log of past operator actions on this user

---

## 4. Behavioral Signal Detection

**Purpose:** Compute features from transaction data to drive personalization

**Implementation:** Background job runs on user data update

**Signals to Detect:**

### Subscription Detection
- Logic: Recurring merchant (≥3 occurrences in 90 days with monthly/weekly cadence)
- Cadence detection: ±3 days tolerance for monthly, ±1 day for weekly
- Outputs:
  - List of recurring merchants
  - Monthly recurring spend total
  - Subscription share of total spend

### Credit Utilization
- For each credit card account:
  - Utilization % = balance / limit
  - Flag: High (≥50%), Medium (30-50%), Low (<30%)
- Minimum payment detection:
  - Compare last_payment_amount to minimum_payment_amount
  - Flag if equal within $5
- Interest detection:
  - Check for interest charges in transaction categories
- Overdue status from liability data

### Savings Behavior
- Net inflow = deposits to savings-like accounts - withdrawals
- Growth rate = (current_balance - balance_90d_ago) / balance_90d_ago
- Emergency fund coverage:
  - Average monthly expenses from transactions
  - Coverage = savings_balance / avg_monthly_expenses
  - Flag: Excellent (≥6mo), Good (3-6mo), Building (1-3mo), Low (<1mo)

### Income Stability
- Payroll detection:
  - Look for ACH deposits with "PAYROLL" or employer names
  - Identify recurring pattern
- Frequency: Weekly, biweekly, semi-monthly, monthly
- Variability: Coefficient of variation of paycheck amounts
- Cash-flow buffer = checking_balance / avg_monthly_expenses

**Time Windows:**
Compute signals for:
- 30-day (short-term, reactionary)
- 90-day (medium-term, trend detection)
- 180-day (long-term, stability assessment)

---

## 5. Persona Assignment

**Purpose:** Categorize users based on behavioral signals for targeted education

**Assignment Logic:** Hierarchical (higher priority first)

**Persona 1: High Utilization**
- **Priority:** 1 (highest)
- **Criteria:**
  - ANY card utilization ≥50% OR
  - Interest charges > $0 OR
  - Minimum payment only detected OR
  - Overdue status = true
- **Primary Focus:**
  - Reduce credit utilization
  - Understand interest impact
  - Payment planning strategies
  - Autopay setup education

**Persona 2: Subscription-Heavy**
- **Priority:** 2
- **Criteria:**
  - Recurring merchants ≥3 AND
  - (Monthly recurring spend ≥$50 in 30d OR subscription share ≥10%)
- **Primary Focus:**
  - Subscription audit checklist
  - Negotiation tactics
  - Cancellation workflows
  - Bill alerts setup

**Persona 3: Variable Income Budgeter**
- **Priority:** 3
- **Criteria:**
  - Median pay gap >45 days OR irregular frequency AND
  - Cash-flow buffer <1 month
- **Primary Focus:**
  - Percentage-based budgeting
  - Emergency fund basics
  - Income smoothing strategies
  - Expense forecasting

**Persona 4: Savings Builder**
- **Priority:** 4
- **Criteria:**
  - Savings growth rate ≥2% over 90-day window OR
  - Net savings inflow ≥$200/month AND
  - All card utilizations <30%
- **Primary Focus:**
  - Goal-setting frameworks
  - Savings automation
  - HYSA/CD education
  - Investment readiness quiz

**Assignment Rules:**
- One primary persona per time window
- User can have different personas across windows (30d vs 90d)
- If multiple criteria met, highest priority wins
- If no criteria met → "General Financial Wellness" default

---

## 6. Recommendation Engine

**Purpose:** Generate personalized education content and partner offers

**Process Flow:**
1. Retrieve user's persona and behavioral signals
2. Select 3-5 education items from content catalog
3. Select 2-3 partner offers with eligibility filtering
4. Generate rationales for each recommendation
5. Apply tone guardrails
6. Store recommendations with decision traces
7. Return to frontend

**Education Content Catalog:**

Structured as:
```json
{
  "id": "edu_credit_util_101",
  "title": "Understanding Credit Utilization",
  "category": "credit",
  "personas": ["high_utilization"],
  "trigger_signals": ["credit_utilization_high"],
  "content": "...",
  "rationale_template": "Your {card_name} is at {utilization}% utilization ({balance} of {limit} limit). Bringing this below 30% could improve your credit score."
}
```

**Rationale Generation:**
- Template-based with variable substitution
- Always cite specific data (account numbers, amounts, dates)
- Use plain language, no jargon
- Format: "We're showing you this because [concrete observation]"

**Tone Guardrails:**
- **No shaming:** Avoid "you're overspending", "bad habits", "poor choices"
- **Empowering:** Use "opportunity to", "you might consider", "here's what you can do"
- **Neutral observations:** "We noticed", "your data shows", "based on your activity"
- Validation: Check generated text against prohibited phrase list

**Partner Offer Filtering:**
```python
def filter_offers(user_signals, offers):
    eligible = []
    for offer in offers:
        # Check eligibility criteria
        if offer.type == "balance_transfer_card":
            if user_signals.credit_utilization >= 0.5:
                if not user_signals.has_late_payments:
                    eligible.append(offer)
        
        # Check doesn't already have product
        if offer.product_id in user_signals.existing_products:
            continue
        
        # Check minimum requirements
        if offer.min_income and user_signals.income < offer.min_income:
            continue
        
        eligible.append(offer)
    
    return eligible[:3]  # Top 3 most relevant
```

**Decision Trace Schema:**
```json
{
  "recommendation_id": "rec_abc123",
  "user_id": "user_xyz",
  "type": "education",
  "title": "Understanding Credit Utilization",
  "selected_reason": "Persona match: high_utilization",
  "signals_used": [
    {"signal": "credit_utilization_visa_4523", "value": 0.65, "threshold": 0.50},
    {"signal": "interest_charged", "value": 87.00, "threshold": 0}
  ],
  "template_id": "edu_credit_util_101",
  "rationale_generated": "Your Visa ending in 4523 is at 65% utilization...",
  "guardrails_passed": {
    "tone_check": true,
    "eligibility_check": true,
    "no_shaming": true
  },
  "timestamp": "2025-11-03T10:30:00Z"
}
```

---

## 7. Consent Management

**Purpose:** Respect user privacy and meet compliance requirements

**Requirements:**
- Explicit opt-in before processing any data
- Clear explanation of what data is used and why
- Easy revocation mechanism
- Audit trail of consent events

**Consent Modal (First Login):**

**Content:**
```
Welcome to SpendSense!

We'll analyze your transaction data to provide personalized financial education.

What we access:
- Your transaction history
- Account balances and types
- Payment patterns and subscriptions

What we don't do:
- Share your data with third parties (except partner offers you click)
- Provide financial advice (only education)
- Access your login credentials

You can revoke consent anytime in Settings.

[Checkbox] I consent to SpendSense analyzing my financial data

[Button: Accept] [Button: Decline]
```

**If Declined:**
- User cannot access dashboard
- Show message: "SpendSense requires consent to provide personalized education. You can grant consent anytime in Settings."

**Revocation Flow:**
- Settings → Privacy → "Revoke Consent" button
- Confirmation modal with consequences
- On revoke: Stop all processing, hide all recommendations, show consent modal again

**Database Tracking:**
```sql
consent_records (
  id uuid,
  user_id uuid,
  granted_at timestamptz,
  revoked_at timestamptz,
  version text,  -- "1.0" for MVP
  ip_address text
)
```

---
