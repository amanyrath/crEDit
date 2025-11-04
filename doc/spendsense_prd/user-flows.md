# User Flows

## Consumer: First-Time Login to Education

1. User navigates to app URL
2. Clicks "Login" (or "Sign Up")
3. Enters credentials → submits
4. **Consent Modal appears**
   - Reads explanation
   - Checks "I consent" checkbox
   - Clicks "Accept"
5. **Dashboard loads** (Transactions tab default)
   - Sees list of recent transactions
6. **Clicks "Insights" tab**
   - Views spending by category chart
   - Sees credit utilization trend (68% - in red zone)
   - Notices subscription breakdown
7. **Clicks "Education" tab**
   - Sees 4 education cards
   - First card: "Understanding Credit Utilization"
   - Reads rationale: "Your Visa ending in 4523 is at 68% utilization..."
   - Clicks "Learn More"
   - Reads full educational content
8. **Scrolls down to chat widget**
   - Clicks chat icon
   - Types: "Why is high credit utilization bad?"
   - Receives response citing their specific card data
9. **Clicks "Offers" tab**
   - Sees balance transfer card offer
   - Reads rationale about saving on interest
   - Sees eligibility: "You may be eligible"
   - Clicks "Learn More" (external link)

## Operator: Auditing a Recommendation

1. Operator logs in
2. **Lands on User List page**
   - Sees table of 3 users
   - Hannah Martinez has 🔴 High Utilization flag
3. **Clicks "View Details" for Hannah**
4. **User Detail page loads**
   - Section 1: Sees Hannah's profile, consent granted
   - Section 2: Reviews behavioral signals
     - Credit: 68% utilization, minimum payments
     - Subscriptions: 4 active, $62/month
     - Savings: $1,200, 1.2 months coverage
     - Income: Biweekly, $1,750/paycheck
5. **Scrolls to Section 3: Recommendations**
   - Sees list of 5 education items + 2 offers
   - First item: "Understanding Credit Utilization"
6. **Clicks "Decision Trace" button**
   - Modal opens with JSON
   - Reviews:
     - Persona match: high_utilization
     - Signals used: credit_utilization_visa_4523 = 0.68
     - Template ID: edu_credit_util_101
     - Guardrails passed: tone_check = true
7. **Closes modal**
8. **Clicks "Override Recommendation"**
   - Enters reason: "User already completed this module"
   - Confirms override
   - Action logged in operator_actions table

---
