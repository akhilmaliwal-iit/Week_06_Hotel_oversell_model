# Which columns did the hotel know on the day of booking?

**Owner:** Data Lead. **Closes:** part of ladder stage 1. **Used by:** `src/features.py`, the PRD and slide 4.

Put every column in exactly one bin, by when the hotel learns its value:

1. **Fixed at booking**: known on the day the booking is made, and it does not change.
2. **Amendable**: known at booking but it can change before arrival, or it is only partly known at booking.
3. **After the fact**: written at check-in, during the stay, or when the outcome is already known.

Only the first bin feeds the MVP. A second-bin column may be tried with its caveat written beside it. A third-bin column never feeds a method. The dataset article (Antonio, de Almeida and Nunes, 2019) says how several columns were recorded; cite it where it settles a bin.

The evidence column holds the number or the source that settled the bin, for example a rate you computed, or a sentence from the dataset article.





| Column | Bin (1, 2 or 3) | Why | Evidence |
|---|---:|---|---|
| `hotel` | 1 | Identifies the hotel selected when the booking is made. | Booking-time hotel identifier. |
| `is_canceled` | 3 | This is the cancellation outcome and the target label (`y`), not an input feature. | Dataset target/outcome; known only after the booking outcome. |
| `lead_time` | 1 | Number of days between booking date and arrival date; known when the booking is created. | Dataset definition; explicitly listed as a Bin 1 example in the project checkpoint. |
| `arrival_date_year` | 2 | Scheduled arrival year can change if the arrival date is amended. | Scheduled arrival information; treat as amendable. |
| `arrival_date_month` | 2 | Scheduled arrival month can change if the arrival date is amended. | Scheduled arrival information; treat as amendable. |
| `arrival_date_week_number` | 2 | Scheduled arrival week can change if the arrival date is amended. | Scheduled arrival information; treat as amendable. |
| `arrival_date_day_of_month` | 2 | Scheduled arrival day can change before arrival. | Scheduled arrival information; treat as amendable. |
| `stays_in_weekend_nights` | 2 | Planned weekend-night count can change if the length of stay is modified. | Stay detail; amendable before arrival. |
| `stays_in_week_nights` | 2 | Planned weekday-night count can change if the length of stay is modified. | Stay detail; amendable before arrival. |
| `adults` | 1 | Number of adults is treated as a booking-time party-size attribute for this project. | Project checkpoint explicitly names `adults` as Bin 1; verify the stored value is the booking-time value. |
| `children` | 1 | Number of children is treated as a booking-time party-size attribute for this project. | Project classification assumption; verify booking-time availability because party size can be amended. |
| `babies` | 1 | Number of babies is treated as a booking-time party-size attribute for this project. | Project classification assumption; verify booking-time availability because party size can be amended. |
| `meal` | 2 | Selected meal plan can be changed before arrival. | Booking preference; potentially amendable. |
| `country` | 1 | Represents the guest's country of origin as captured in booking information. | Dataset booking attribute. |
| `market_segment` | 1 | Identifies the market segment through which the booking was made. | Booking acquisition information; explicitly listed as a Bin 1 example in the project checkpoint. |
| `distribution_channel` | 1 | Identifies the channel through which the booking was distributed. | Booking acquisition information. |
| `is_repeated_guest` | 1 | Indicates whether the guest has made a previous booking; this historical fact does not change for the current booking. | Historical customer information. |
| `previous_cancellations` | 1 | Counts cancellations made by the guest before the current booking. | Historical booking information. |
| `previous_bookings_not_canceled` | 1 | Counts previous bookings that were not cancelled. | Historical booking information. |
| `reserved_room_type` | 2 | The room type initially reserved may be changed before arrival. | Initial booking room preference; potentially amendable. |
| `assigned_room_type` | 3 | Represents the room type actually assigned through hotel operations; it may reflect decisions made after the original booking. | Operational assignment; not safe as a booking-time predictor. |
| `booking_changes` | 2 | Counts changes made to the booking and can increase as amendments happen before arrival. | Project checkpoint explicitly lists it as amendable. Use only a snapshot available at the prediction cutoff. |
| `deposit_type` | 1 | Indicates the deposit arrangement associated with the booking. | Booking/payment-condition attribute; explicitly listed as a Bin 1 example in the project checkpoint. |
| `agent` | 1 | Identifies the travel agent associated with the booking, if applicable. | Booking distribution information; missing values may indicate no associated agent. |
| `company` | 1 | Identifies the company associated with the booking, if applicable. | Booking/business information; missing values may indicate no associated company. |
| `days_in_waiting_list` | 2 | Waiting-list duration can accumulate over time before confirmation or arrival. | Project checkpoint explicitly lists it as amendable; use only a cutoff-time snapshot. |
| `customer_type` | 1 | Identifies the customer type associated with the booking. | Booking classification information. |
| `adr` | 1 | Treated as a booking-time rate feature for this project. | Project checkpoint explicitly lists `adr` as Bin 1. Verify that the value is the rate available at booking, not a realized-stay calculation. |
| `required_car_parking_spaces` | 2 | Number of requested parking spaces can change before arrival. | Guest requirement; potentially amendable. |
| `total_of_special_requests` | 2 | Number of special requests can increase or change before arrival. | Guest requirements; potentially amendable. |
| `reservation_status` | 3 | Indicates the reservation outcome, such as Check-Out, Canceled, or No-Show. | Outcome field; direct target-leakage risk. |
| `reservation_status_date` | 3 | Records the date on which the reservation status was updated and may reveal the outcome timing. | Outcome-related timestamp; target-leakage risk. |

## What happens to a method when the late columns go in?

_Train the same method twice on the same split, once with first-bin columns only and once with the second and third bins added. Then run the first version once more on a random split. Record the three AUCs here and say which one the client should believe._

| Run | Columns | Split | AUC on the proof period |
|---|---|---|---|
| A | First bin only | Time |0.8199 |
| B | All three bins | Time | 1.0|
| C | First bin only | Random |0.8381 |
