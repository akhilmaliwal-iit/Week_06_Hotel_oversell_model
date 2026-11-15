# Which questions did the grilling ask about the charter and the RFP skeleton, and what changed?

**Owner:** Client Lead. **When:** Tuesday, 45 minutes of grilling and then the edits. **Tool used:** _write it here_. **Full chat:** the file in `ai_logs/` it came from.

Write your own answer before you read the AI's recommended answer. When you accept a recommendation, say why in the last column. At least three rows must show a change to a document.

| Q | Question, as asked | AI's recommended answer | Our answer | Accepted, changed or rejected | What changed, in which document |
|---|---|---|---|---|---|
| 1 | If your model saves EUR 1.7M on paper, why can't the hotel owner bank that exact sum across the entire year? | Because hotel occupancy fluctuates seasonally. Overbooking savings only generate revenue on nights when demand exceeds physical capacity. | We recognized that empty room costs only matter on constrained nights, but had not calculated the exact share of constrained nights. | **Accepted** | Added the **Full-Night Caveat** to `docs/CHARTER.md` Section 5 with exact historical shares: City Hotel is near full on 37.9% of nights, Resort on 18.2%. |
| 2 | Why should the client trust your baseline when the brief claims 25% cancellations but your analysis uses a different number? | The brief contains an informal heuristic (25%), but empirical analysis of `data/hotels.csv` shows an actual mean cancellation rate of 37.04% (City: 41.73%, Resort: 27.76%). | We initially planned to ignore the discrepancy, but realized the client would question any mismatch. | **Changed** | Added explicit **Brief Fact-Check** row in `docs/CHARTER.md` Section 6 and updated baseline flat rule parameter to 37.04%. |
| 3 | Why is the decision unit the hotel-arrival night rather than individual guest bookings? | Because physical rooms are shared across all arrivals for that night; individual probabilities cannot prevent walk penalties unless aggregated to the room pool at check-in midnight. | We originally drafted the unit as "reservation", thinking per-booking cancellation probability was the primary output. | **Changed** | Rewrote `docs/CHARTER.md` Section 4 to mandate **hotel-arrival night** as the decision unit, and updated `src/contract.py` nightly summation. |

## What did we learn from being grilled?

The question that hurt most was challenging our euro savings claim against off-peak seasonal realities where rooms remain unconstrained. It exposed that quoting raw annual savings without occupancy conditioning is commercially deceptive. We now explicitly bound all revenue claims with the Portuguese seasonal full-night caveat (37.9% City, 18.2% Resort) and state net revenue impact honestly.