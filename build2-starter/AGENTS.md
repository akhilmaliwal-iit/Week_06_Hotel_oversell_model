# Which rules must a coding agent follow in this repository?

## Which rules has our team set?

1. **Strict Chronological Splits Only:** Never use random train/test splits (`train_test_split` with shuffle). All models must train on arrivals before 2016-07-01, choose buffers on 2016-07-01 to 2016-12-31, and evaluate on the proof period starting 2017-01-01.
2. **Zero Post-Booking Leakage:** Never use Bin 3 columns (`reservation_status`, `reservation_status_date`, `assigned_room_type`) in any feature pipeline or model. Only use Bin 1 features known on the day of booking.
3. **The Unit is the Night:** Never stop at per-booking classification probabilities. All probabilities must be aggregated per hotel and arrival night using `contract.nightly_table()`, and scored as an integer oversell count $k$.
4. **Hard Walk Ceiling Constraint:** Any oversell policy that produces > 10 walked guests per 1,000 arrivals on the choose or proof period is unacceptable and must be rejected, regardless of euro savings.
5. **Preserve Data Contract Integrity:** Never modify `src/contract.py` or the evaluation scoring formulas. Every data cleaning step must be documented with row counts in `docs/DECISIONS.md`.

## Which general coding guidelines apply?

1. **Think Before Coding:** State assumptions, outline data structures, and consider edge cases before writing code.
2. **Simplicity First:** Write simple, readable functions over clever, nested abstractions. Avoid unnecessary dependencies.
3. **Surgical Changes:** Make minimal, focused diffs that touch only the intended logic. Never rewrite working modules wholesale.
4. **Goal-Driven Execution:** Every script must have a clear verification test that proves correctness in terminal output.
# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
