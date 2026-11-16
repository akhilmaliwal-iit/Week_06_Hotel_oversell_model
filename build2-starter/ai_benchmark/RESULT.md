# AI Benchmark — Final Results

## 1. Proof-period configuration

| Parameter | Selected value |
|---|---|
| Proof period | 2017-01-01 to 2017-08-31 |
| Selected model | Probability model |
| Selected model safety factor | 0 × nightly spread |
| Choose-period model cost | €1,206,379.91 |
| Selected flat-rule safety margin | 16 rooms |

The model safety factor was selected using the choose period, where the reported cost was €1,206,379.91.

A safety factor of zero means that no uncertainty adjustment is subtracted from the expected cancellation count. The model therefore bases its overbooking recommendation on expected cancellations without an additional nightly-spread buffer.

The flat-rule baseline uses a fixed safety margin of 16 rooms.

## 2. Proof-period results

| Metric | Probability model | Flat rule |
|---|---:|---:|
| Total cost (EUR) | 1,613,334.99 | 3,935,875.60 |
| Empty rooms | 3,421 | 8,186 |
| Walked guests | 168 | 155 |
| Walks per 1,000 arrivals | 6.74 | 6.21 |
| Walking ceiling met | True | True |
| Arrivals | 24,942 | 24,942 |
| Nights evaluated | 486 | 486 |

## 3. Financial comparison

**Savings against the flat rule: €2,322,540.61**

The probability model reduced the total proof-period cost compared with the flat-rule baseline.

It also resulted in:

- 4,765 fewer empty rooms.
- 13 additional walked guests.
- A walking rate of 6.74 per 1,000 arrivals, compared with 6.21 for the flat rule.

The probability model achieved a lower total cost while satisfying the contractual walking ceiling of 10 walked guests per 1,000 arrivals.

The financial savings calculation is:

€3,935,875.60 − €1,613,334.99 = **€2,322,540.61**

## 4. Business interpretation

The probability model performed better financially than the flat-rule baseline on the proof period.

Its total cost was approximately 59.0% lower than the flat-rule cost.

Although the model walked 13 more guests than the flat rule, its walking rate remained within the permitted business limit:

- Probability model: 6.74 walks per 1,000 arrivals.
- Flat rule: 6.21 walks per 1,000 arrivals.
- Maximum permitted: 10 walks per 1,000 arrivals.

Therefore, both approaches satisfied the contractual walking constraint, while the probability model achieved substantially lower total cost.

## 5. Generated 14-night overselling output

The model also generated an operational overselling table for the period:

**18 August 2017 to 31 August 2017**

Output file:

`ai_benchmark/oversell_2017-08-18_to_2017-08-31.csv`

The table contains recommended overbooking quantities by hotel and arrival date.

Expected columns:

| Column | Description |
|---|---|
| hotel | Hotel name |
| arrival_date | Arrival date |
| book | Number of bookings |
| expected | Expected cancellations |
| buffer | Nightly uncertainty adjustment |
| oversell | Recommended additional bookings |

The output covers 14 arrival dates for both hotels, giving 28 hotel-night recommendations.

## 6. Final benchmark conclusion

The AI-generated probability model achieved a proof-period cost of €1,613,334.99, compared with €3,935,875.60 for the flat-rule baseline.

It reduced empty rooms by 4,765 and generated savings of €2,322,540.61 while maintaining a walking rate of 6.74 per 1,000 arrivals, below the contractual maximum of 10.

The results demonstrate the value of using booking-level cancellation probabilities and aggregating them into hotel-arrival-night overbooking recommendations.

The model satisfied the business guardrail and achieved a substantial financial improvement over the flat-rule baseline.

## 7. Limitations and considerations

- The selected safety factor of zero means no additional uncertainty buffer was applied to expected cancellations.
- The model walked slightly more guests than the flat rule, even though it remained within the contractual limit.
- The evaluation uses the available historical booking dataset; actual booking-time snapshots would be needed to fully validate real-time operational performance.
- Results depend on the assumed empty-room and walked-guest cost calculations defined by the evaluation contract.
- Performance should be monitored over time because cancellation patterns may change.

