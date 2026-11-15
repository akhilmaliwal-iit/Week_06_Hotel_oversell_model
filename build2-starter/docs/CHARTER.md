# What is the project, in one page?

**Owner:** Client Lead. **Closes:** ladder stages 0 and 1. **Length:** one page. **Version 0** is written on paper on Tuesday, with no AI, and typed in here before any AI tool is opened.

Answer each question in one to three sentences. The worked example comes from a different business on purpose (home sample collection at a diagnostics chain, with made-up numbers), so it shows the standard of an answer without giving you the hotel's.

### 1. Who is the client, and who pays whom?

> **Worked example.** The client is the home-collection unit of a diagnostics chain. Patients pay per test (B2C); partner hospitals and corporate health camps pay on monthly invoices (B2B). We are the analytics vendor, and the unit head renews us only if idle phlebotomist slots fall.

**Our answer:**The client is a two-hotel group in Portugal (a Lisbon city hotel and an Algarve resort). Guests pay per stay (B2C), and tour operators, travel agents and groups pay in volume (B2B). RateGain is the vendor, paid by the hotel, so the work has to pay for itself in the hotel's euros.

<!-- answer:3 -->

### 2. Who decides, how often, and what does one wrong call cost in each direction?

> **Worked example.** The city operations lead fixes each route's bookings every evening for the next morning. An empty slot costs about Rs 450 of phlebotomist time and fuel. A patient we cannot reach in time costs about Rs 600 in a voucher and a rebooking, plus a complaint.

**Our answer:**The revenue manager decides each night. An empty room costs that night's average booked stay (adr × nights), about EUR 319 at the City Hotel and EUR 435 at the Resort. A walked guest costs EUR 300.

<!-- answer:3 -->

### 3. What is decided, from what is known when, about which outcome?

> **Worked example.** How many extra visits to book on each route for tomorrow morning, from the bookings known at the end of today, about how many booked patients will not be there when the phlebotomist arrives.

**Our answer:**How many rooms beyond capacity to keep selling for each arrival night, using only what the hotel knew at booking, about how many of that night's bookings will cancel.

<!-- answer:3 -->

### 4. What is the unit of decision, and why that unit?

> **Worked example.** The route-morning: one phlebotomist, one morning, about 12 slots. The overbooking is set per route, so per-patient answers are only useful once they are added up per route.

**Our answer:**One hotel on one arrival night. Overselling is set per night, so per-booking probabilities only matter once they are summed per night.

<!-- answer:2 -->

### 5. What are the north star and the guardrail?

_Give each one a numerator, a denominator, a window and the exclusions. Draw the metric tree underneath: the north star at the top, the two costs below it, the guardrail beside it._

> **Worked example.** North star: idle slots per route-morning, averaged over a calendar month, excluding routes the lab cancelled. Guardrail: patients turned away per 1,000 completed visits, per calendar month, all routes, at most 5.

**Our answer:**
North star: empty rooms per night, averaged over a calendar month, per hotel. The numerator is rooms left empty by cancellations, the denominator is nights, and bookings with no usable adr are excluded.
Guardrail: walked guests per 1,000 arrivals over the period, at most 10. Arrivals are non-cancelled bookings, and the ceiling is checked on the choose period.
Metric tree: the north star at the top, empty rooms × stay value and walks × EUR 300 as the two costs below it, and the ceiling beside it.


<!-- answer:4 -->

### 6. Which numbers in the brief did we check, and what did the data say?

_Every number in the brief gets a row. A number you could not check gets a question to the client instead._

> **Worked example.**
>
> | Number in the brief | What we checked | What the data said | What we do about it |
> |---|---|---|---|
> | "A home visit takes 20 minutes" | Median time from arrival to sample scan | 26 minutes; 20 is the planned slot length | Plan on the record, not the plan |

| Number in the brief | What we checked | What the data said | What we do about it |
|---|---|---|---|
| About 1 booking in 4 is cancelled | Share of all 119,390 bookings with is_canceled = 1, overall and per hotel. | 37.0% overall. City is 41.7%, Resort is 27.8%. Only the Resort is near one in four. | The brief is wrong for the group. Use the per-hotel rates in the charter.
| 119,390 bookings, 32 columns | Row and column count of the raw file as loaded. | The row count matches. The raw file read in as 34 columns because I had added arrival_date and nights, so recount on the raw file before logging it. | Log the checked value.
| Arrivals July 2015 to August 2017 | Earliest and latest arrival date, built from the year, month and day columns. | 1 Jul 2015 to 31 Aug 2017, confirmed. | None. |
| Finance: most non-refundable bookings never become stays (the brief says this "cannot be right") | Cancellation rate by deposit_type, overall and per hotel. | Finance is right. 99.4% of Non Refund bookings cancel (99.8% at the City Hotel, 96.0% at the Resort). | This is observation 1. Don't assume prepaid means guaranteed.
| Walk ceiling of 1 in 100 | Converted 1 in 100 to walks per 1,000 and compared it with the scoring rule's ceiling. | Equals 10 per 1,000, which is consistent with the scoring rule. | None.

### 7. What is out of scope?

> **Worked example.** Pricing of home visits, phlebotomist hiring, and routes outside the three metro cities.

**Our answer:**
Room pricing, marketing guest segments (the wish list), channel strategy, hotels other than these two, and any column not known at booking.
<!-- answer:2 -->

### 8. Who owns what on this team?

| Role | Name | Owns |
|---|---|---|
| Client Lead | Harshit Agrawal `docs/CHARTER.md`, `docs/RFP.md`, business frame, metric tree, presentation slides 1-2 & 10, client defense |
| Data Lead | Malav Modi |`docs/COLUMNS.md`, `docs/DECISIONS.md`, `src/features.py`, leakage audit, AI comparison `docs/COMPARISON.md` |
| Model Lead | Chetan | `src/backtest.py`, 5 model comparison table, buffer tuning on Choose, `models/chosen_model.joblib`|
| Build Lead | Akhil | `AGENTS.md`, `docs/PRD.md`, `docs/BUILD_PLAN.md`, `docs/ROADMAP.md`, `src/nightly.py`, automated tests|

### 9. What is the one question we are sending the client?

> **Worked example.** "Is a no-show recorded by the phlebotomist at the door, or by the call centre the next day?"

**Our answer:**
Is a no-show recorded as cancelled by the desk at check-in time, or later?" This matters because is_canceled includes no-shows.
