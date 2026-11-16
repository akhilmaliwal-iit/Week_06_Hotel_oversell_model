# How do we get from a first test to something the client can run?

**Owner:** Build Lead. **Closes:** ladder stages 4 and 6. **Length:** one page.

Three stages, each with an owner, an hour budget, a line that says when it is done, and the file that proves it. Fill the table on Wednesday morning and update the hours as you go.

| Stage | What is built                                                                                        | Owner             | Hours planned | Hours used | Done when                                                                                                                                                     | Evidence file |
| ----- | ---------------------------------------------------------------------------------------------------- | ----------------- | ------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| POC   | Flat rule baseline, lookup table, logistic regression, and HistGradientBoosting in `src/backtest.py` | Model Lead        | 8             | 9          | `python src/backtest.py` prints every method on the proof period, scored by `src/contract.py`, with the ceiling checked                                       |               |
| MVP   | `src/nightly.py` production pipeline reading only Bin 1 features and writing 14-night oversell table | Build Lead        | 6             | 6          | `python src/nightly.py --from 2017-08-18 --nights 14` writes the nightly table from a bookings file, reading only first-bin columns, signed by the challenger |               |
| Final | Uncertainty buffer comparison, full-night caveat, 3-week roadmap, slide deck, recordings             | Client Lead / All | 6             | 6          | The uncertainty buffer is compared with the rooms buffer, the full-night caveat is computed, and the roadmap is written                                       |               |

## What would production add that the MVP leaves out?

| Addition                      | Why it matters                                                                  | Owner      | Hours |
| ----------------------------- | ------------------------------------------------------------------------------- | ---------- | ----- |
| Automated PMS API connector   | Eliminates manual daily CSV export; connects live with Opera/Amadeus            | Data Lead  | 16    |
| Dynamic 14-day pickup curve   | Adjusts oversell numbers for bookings that arrive between T-14 and arrival date | Model Lead | 18    |
| Revenue Manager Web Dashboard | Allows one-click acceptance and tracks manual override reasons for compliance   | Build Lead | 16    |

## What did we cut, and why?

We cut customer persona clustering from the MVP. Although requested by the marketing department, unsupervised clustering does not alter the midnight physical room capacity of the hotel and provides zero reduction in empty rooms or walked guests. We cut it to protect our engineering hours and focus 100% of effort on the core revenue engine.
