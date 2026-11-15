# What would the client have asked a vendor for, in writing?

**Owner:** Client Lead. **Closes:** ladder stage 2. **Length:** one to two pages.

You write this request for proposal as the client would have issued it, so that both sides agree on what is being bought before anything is built. Vendor teams often draft the request with the client in B2B sales; treat that as the convention here. Keep the client's voice and the client's units: rooms, euros, walks.

### 1. What is the background, in three sentences?

> **Worked example.** Our home-collection unit runs about 300 routes a morning in three cities. Roughly one booked patient in seven is not home when the phlebotomist arrives, and each idle slot costs us about Rs 450. We overbook today by gut feel, route by route.

**Our answer:** two hotels, about 37% of bookings cancel, and the flat rule leaves empty rooms or walks guests.

<!-- answer:3 -->

### 2. What must the solution do?

_Five lines at most, each one a verb the client can check._

> **Worked example.** (1) Give the number of extra visits to book on each route for tomorrow morning. (2) Run on the bookings file we export at the end of each day. (3) Show the reason for each route's number in one line. (4) Report idle slots and turned-away patients for the past month. (5) Let the operations lead overrule a route and record why.

**Our answer:**Must do:
Give the oversell count per hotel and night for the next 14 nights.
Run on the bookings file.
Show a one-line reason per night.
Report euros, rooms and walks per 1,000.
Let the revenue manager overrule a night and record why.

<!-- answer:5 -->

### 3. How good must it be, and on which period?

_Acceptance thresholds in business units, with the period each is measured on._

> **Worked example.** On the last three months of bookings, held back until the end: idle slots per route-morning at least 25% below today's gut-feel rule, with at most 5 patients turned away per 1,000 completed visits.

**Our answer:** on Jan to Aug 2017, run once, cost below the flat rule’s in euros with at most 10 walks per 1,000.

<!-- answer:3 -->

### 4. Within which limits and rules?

> **Worked example.** Use only what is known when the route is fixed. Patient data stays in our systems. The run takes under five minutes on a laptop. A route lead can read the reason for any number.

**Our answer:** use only columns known at booking, and keep guest data in the client’s systems. It must be readable by the revenue manager and run on a laptop.

<!-- answer:3 -->

### 5. What data do we provide?

> **Worked example.** Eighteen months of visit bookings, one row per booking, with the booking channel, slot, pincode, payment type, test panel and outcome.

**Our answer:** 119,390 bookings, 32 columns, from python src/data.py

<!-- answer:2 -->

### 6. How will we judge proposals?

> **Worked example.** On the acceptance thresholds above, then on how clearly the vendor explains a wrong call, then on the cost to run.

**Our answer:** acceptance thresholds first, then how clearly a wrong call is explained, then cost to run.

<!-- answer:2 -->

### 7. What is the timeline?

> **Worked example.** A proof of concept in one week, a pilot on one city for a month, then a decision.

**Our answer:**POC, MVP, then the final stage, all by Friday.

<!-- answer:2 -->

### 8. What may the vendor ask us?

> **Worked example.** How each outcome is recorded and by whom; which routes changed shape during the period; what a turned-away patient costs beyond the voucher.

**Our answer:** how no-shows are recorded, whether the flat rule’s safety margin is fixed, and whether the allotment/block rooms on Groups bookings are already released.

<!-- answer:3 -->

### 9. What is on the wish list?

_Copy the client's wish-list item exactly. Your answer to it belongs in the PRD, not here._

**Our answer:** copy it word for word: “Our marketing team would love to find our hidden guest types.”

<!-- answer:1 -->
