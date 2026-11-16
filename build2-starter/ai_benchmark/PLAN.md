I’ll ground the plan only in the four named project files and `data/hotels.csv`, without downloading anything or changing files.

"Read" failed
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\BRIEF.md"
}
Tool execution failed: Path does not exist

"Read" failed
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\docs\\EVALUATION_CONTRACT.md"
}
Tool execution failed: Path does not exist

"Read" failed
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\src\\data.py"
}
Tool execution failed: Path does not exist

"Read" failed
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\src\\contract.py"
}
Tool execution failed: Path does not exist

Ran terminal command: $p = 'C:\Users\Dharmen\Desktop\ML_project\Week_06_Hotel_oversell_model\data\hotels.csv'; Get-Item $p | Select-Object FullName, Length; Get-Content -LiteralPath $p -TotalCount 6
Tool execution failed with exit code 1

The supplied workspace path doesn’t resolve in this session. I’ll check the active working directory and its immediate entries only, then read the requested paths if present.

Ran terminal command: Get-Location; Get-ChildItem -Force | Select-Object Name, FullName, Mode

Ran terminal command: Get-ChildItem -Force -LiteralPath 'C:\Users\Dharmen\Desktop\ML_project\Week_06_Hotel_oversell_model\build2-starter' | Select-Object Name, FullName, Mode; Get-ChildItem -Force -LiteralPath 'C:\Users\Dharmen\Desktop\ML_project\Week_06_Hotel_oversell_model\build2-starter\data' -ErrorAction SilentlyContinue | Select-Object Name, FullName, Mode
Tool execution failed with exit code 1

Read 
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\build2-starter\\BRIEF.md"
}

Read 
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\build2-starter\\docs\\EVALUATION_CONTRACT.md"
}

Read 
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\build2-starter\\src\\data.py"
}

Read 
Completed with input: {
  "path": "C:\\Users\\Dharmen\\Desktop\\ML_project\\Week_06_Hotel_oversell_model\\build2-starter\\src\\contract.py"
}

Ran terminal command: $p = 'C:\Users\Dharmen\Desktop\ML_project\Week_06_Hotel_oversell_model\build2-starter\data\hotels.csv'; if (Test-Path -LiteralPath $p) { Get-Item -LiteralPath $p | Select-Object FullName, Length; Get-Content -LiteralPath $p -TotalCount 6 } else { Write-Output "Not found: $p" }

## Proposed evaluation plan

1. **Prediction target:** Estimate each booking’s probability of cancellation (`is_canceled`), where cancellation includes no-shows as specified in the brief.

2. **Columns:** Use `hotel`, `lead_time`, arrival-date fields, stay-length fields, guest counts, `meal`, `country`, `market_segment`, `distribution_channel`, `is_repeated_guest`, prior cancellation/booking counts, `reserved_room_type`, `booking_changes`, `deposit_type`, `days_in_waiting_list`, `customer_type`, parking requests, special requests, and `adr` as potential predictors. They describe the hotel, booking timing, guest, or stay. Use `adr` and stay length to calculate the contract’s room value as well. Exclude `is_canceled` from predictors, and exclude `reservation_status` and `reservation_status_date` because they reveal the outcome; omit `assigned_room_type` because assignment may happen after booking. I’ll confirm the available columns and any cleaning needs once the CSV is available.

3. **Bookings to score:** Score every booking for each hotel and arrival night, using the final-book interpretation in the contract—not just bookings that would have been visible on a particular morning. The fourteen-night table will therefore treat each night’s final book as already present, as the contract specifies.

4. **Time split:** Use arrival dates before July 1, 2016 to fit candidate models; July 1–December 31, 2016 to select the model and its safety setting; and January 1–August 31, 2017 for one final proof run. Freeze the choices before that proof run.

5. **Comparisons:** Compare the selected probability model against the required flat rule: each hotel’s cancellation rate from the train period, multiplied by that night’s bookings, less a fixed safety margin. Choose the flat rule’s margin on the choose period under the same walk ceiling. Report savings against this rule, not against selling no extra rooms.

6. **Turning probabilities into oversell counts:** For each hotel/night, sum booking cancellation probabilities to estimate cancellations and use their uncertainty to set a conservative oversell count. Tune a safety setting on the choose period to minimize cost while meeting the ceiling of at most 10 walked guests per 1,000 arrivals; convert the result to a nonnegative whole-room count. The contract’s nightly scoring will determine costs, empty rooms, walks, and ceiling compliance.

7. **What to report:** Provide the next-fourteen-night table with hotel, night, bookings on the book, expected cancellations, buffer, and oversell count. For the proof period, compare the model and flat rule in euros, empty rooms, walked guests, walks per 1,000 arrivals, and ceiling status.

**Data availability:** I found the requested project files under `build2-starter`, including `BRIEF.md`, `EVALUATION_CONTRACT.md`, `data.py`, and `contract.py`. But `data/hotels.csv` is not present at the stated location or under that folder, so I could not verify its schema. I have not downloaded anything. I’ll stop here and wait for your approval; the CSV will need to be made available before implementation.