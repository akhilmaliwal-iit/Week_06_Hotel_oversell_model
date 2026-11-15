# What exactly are we building, and why this way?

**Owner:** Build Lead. **Closes:** ladder stages 3 and 5. **Length:** two pages and one diagram.

Write the options section on Wednesday, before the method table exists, and update it once the table is in. The architecture goes in on Thursday.

### 1. Who uses it, when, and what do they do with it?

The hotel Revenue Manager opens the daily oversell report every morning before 07:00 AM, prior to setting daily room availability on global distribution channels and online travel agencies. They review the recommended oversell count $k$ for each of the upcoming 14 arrival nights at both hotels and enter those room inventory numbers into the Property Management System (PMS).

### 2. Which two ways could we decide, what does each cost, which do we choose, and what would flip it?

**(a) Multi-Dimensional Lookup Table:** Historical cancellation rates grouped by property, market segment, and lead time quartiles. Costs 3 hours to build and zero retraining maintenance. Achieves EUR 4,867,947 cost on proof period (AUC 0.6933, Buffer 25).
**(b) HistGradientBoosting Model:** Learns non-linear interactions across all 14 Bin 1 features. Costs 8 hours to build, retrained monthly. Achieves EUR 2,175,452 cost on proof period (AUC 0.7844, Buffer 4).

**Our Choice:** We choose **(b) HistGradientBoosting** because on the proof period it saves an additional **EUR 2,692,495 over the lookup table** and **EUR 1,758,790 over the client's flat rule** while strictly satisfying the walk ceiling at 2.73 walks per 1,000 completed arrivals.
**Flip Condition:** We would flip to (a) if next quarter's proof savings gap shrinks under EUR 30,000, eliminating ML infrastructure overhead.

### 3. What is our answer to the wish-list item?

The marketing team's request to 'find our hidden guest types' requires unsupervised customer segmentation (e.g. K-Means clustering) based on demographic attributes and booking patterns. However, customer clustering does not alter the physical capacity of the hotel at midnight tonight and provides zero reduction in empty rooms or walked guests. Building clustering would take 8 development hours with zero operational impact on room inventory. We reject it for the MVP and schedule it for Week 3 of our production roadmap as a marketing analytics addon.

### 4. What exactly is in the table the client reads?

One row per hotel and arrival night for the next 14 nights containing: `hotel`, `arrival_date`, `book` (current reservations on the book), `expected` (model's expected cancellations), `buffer` (safety margin frozen from choose period), and `oversell_k` (final whole integer rooms to keep selling beyond physical capacity).

### 5. Which inputs do we use, by bin?

We use strictly **Bin 1** columns from `docs/COLUMNS.md`: `lead_time`, `adr`, `adults`, `children`, `stays_in_weekend_nights`, `stays_in_week_nights`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`, `hotel`, `market_segment`, `distribution_channel`, `deposit_type`, and `customer_type`. We use zero columns from Bin 2 or Bin 3.

### 6. Where do the numbers come from, and how is the buffer set and frozen?

Each booking receives a predicted cancellation probability $p_i$ from the trained `HistGradientBoostingClassifier`. These probabilities are summed per hotel-arrival night to produce expected cancellations $\mu = \sum p_i$. The safety buffer $b = 4$ was selected on the Choose period (Jul–Dec 2016) by evaluating candidate integer buffers $[0..30]$ and selecting the lowest-cost buffer that achieved $\le 10$ walked guests per 1,000 arrivals. The buffer was then frozen and applied to the 2017 proof period: $k = \max(\lfloor \mu - 4 \rfloor, 0)$.

### 7. What is the error bill on the proof period?

| Rule                          | Empty rooms | Walked guests | Walks per 1,000 | Cost (EUR)       | Saving against flat rule (EUR) |
| ----------------------------- | ----------- | ------------- | --------------- | ---------------- | ------------------------------ |
| Zero Oversell (k=0)           | 15,734      | 0             | 0.00            | EUR 6,717,251.34 | -EUR 2,783,008.68              |
| Client Flat Rule              | 8,179       | 151           | 6.07            | EUR 3,934,242.66 | Baseline (EUR 0.00)            |
| Lookup Table                  | 10,647      | 122           | 4.90            | EUR 4,867,947.74 | -EUR 933,705.08                |
| Logistic Regression           | 5,320       | 84            | 3.38            | EUR 2,488,555.19 | +EUR 1,445,687.47              |
| HistGradientBoosting (Winner) | 4,419       | 68            | 2.73            | EUR 2,175,452.65 | **+EUR 1,758,790.01**          |

### 8. What does the system look like, first as a black box and then inside?

**Black Box Diagram:**
```
[ PMS Booking Export (hotels.csv) ] ---> [ src/nightly.py ] ---> [ 14-Night Oversell Table ] ---> [ Revenue Manager Updates PMS ]
```

**White Box Diagram:**
```
[ hotels.csv ]
      │
      ▼
[ features.clean_bookings (Drops 180 ghosts, 1 neg ADR, imputes NaNs) ]
      │
      ▼
[ features.extract_bin1_features (One-hot encodes Bin 1 categoricals) ]
      │
      ▼
[ models/chosen_model.joblib (Predicts p_i via HistGradientBoosting) ]
      │
      ▼
[ contract.nightly_table (Aggregates sum of p_i per hotel-night) ]
      │
      ▼
[ Subtract Frozen Buffer b = 4: k = max(floor(expected - 4), 0) ]
      │
      ▼
[ data/nightly_output.csv & Terminal Report ]
```

**What production would add:**
1. Automated API integration with Opera/Amadeus PMS replacing CSV files.
2. Dynamic pickup modeling for reservations arriving between $T-14$ and arrival day.
3. Web dashboard with role-based access control and manual override logging.

### 9. What are the limits?

Executes in under 5 seconds from terminal; requires zero external network connections; reads only booking attributes known prior to arrival; adheres to guest data privacy standards.

### 10. What could go wrong?

Unforeseen airline strikes or travel bans that alter global cancellation patterns; severe drift in distribution channel mix; revenue manager ignoring recommendations after a single isolated walked guest.

### 11. What is out of scope?

Dynamic room pricing; room upgrades/allocations; marketing budget allocation; front desk check-in staffing.
