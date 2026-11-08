# Pilot plan: running the full pipeline on 1871

**Status:** 1871 session transcription and validation completed (2026-11-07); full human review pending. Setup, rendering, prompt, and initial reference files exist. Unit mappings are incomplete. No processed dataset has been built.

**Decided so far (2026-11-07):**
- The pipeline runs with **the available Sol model in the Codex session**, by the researcher's updated instruction. No API key or separate API call is used. Exact runtime ID and token usage are unavailable and recorded as null rather than invented.
- The **researcher checks every cell by hand** (C3), and the review record goes in **`data/review/`** (B1).
- **"Mich.& Ind." is a different unit from Michigan** (C1): `michigan_indiana`.

**Goal.** Run every workflow in [AGENTS.md](../AGENTS.md) §8 once, end to end, on a single year (`ASR1871.pdf`), so that we can:

1. build the first version of each pipeline script, prompt and reference table;
2. see how accurate the AI transcription is on a real page;
3. find gaps or contradictions in the conventions *before* we scale up to all ten years.

This follows the rule in AGENTS.md §7 to work in small, reviewable steps and show results for one year before running all of them.

---

## Why 1871 is a good pilot year

The 1871 page (archive page 6, Ninth Annual Session, February 7, 1871) is typical of layout C (1869–75) and contains most of the hazards listed in [source_notes.md](source_notes.md):

| Hazard | Where on the 1871 page |
|---|---|
| Handwritten, vertical column headings | Ministers, Licentiates, Churches, Members |
| Pencil annotations (later additions) | "Feb" beside the title, "Feb. 1871" beside the subtitle |
| Run-together totals | Total row: `1110.003959.25` (two columns with no space between them) |
| Values sitting between rows | Churches and Members for Kansas & Mo., Calif.Mis'n and Swiss Mis'n |
| Bleed-through from the next page | Faint ghost table, plus "Tenth Annual Session / Dec. 29, 1871" under the session line |
| Blank citation part | "Vol. 37, No. [blank] p. 68" |
| Blank cells | Ohio ministers; many money cells |
| Suspected carried-forward figures | N.Y. & Penn. funds (same as 1869–70, per source notes) |

It is also small enough to check completely: **13 unit rows + 1 Total row, × 10 columns = 140 cells.**

**A preliminary arithmetic check** (Claude, by eye, not yet verified): eight of the nine printed totals match the column sums. **S.B. Fund Pledged** may not: the rows appear to sum to 23,066.33, while the Total row reads 23,066.42. That could be a misreading by Claude, a transcription error, or an error in the original. The pilot should show how the pipeline handles this case.

---

## Decisions needed before starting

These are the researcher's to make (AGENTS.md §7: "Ask before making historical or interpretive decisions"). Each has a recommendation, but nothing will be built on an assumption.

### A. Practical setup

| # | Question | Recommendation |
|---|---|---|
| A1 | **API access.** Superseded by researcher instruction: use the session model. | No key or API spending limit required. |
| A2 | **Model.** Sol, as selected by the researcher. | Record the selected label; exact runtime ID is null unless exposed by the session. |
| A3 | **Image inspection.** Actual 300 DPI render: 2319 × 3438 px. | Keep the full PNG and inspect a native-resolution table crop. Record source dimensions, viewer resizing, and crop coordinates; internal model processing is unknown. |
| A4 | **Structured output.** Session model authors JSON, validated locally on import. | This is not API-constrained structured output. Keep the exact submitted reply bytes for audit. |
| A5 | **PDF rendering library.** | `pypdfium2` + `Pillow` (both installable with pip and pinned in `requirements.txt`), so participants don't need to install system tools. `pdftoppm` is already on this machine but would be an extra, unpinned dependency. |
| A6 | **Source register details.** The register needs `archive_url` and `download_date` for `ASR1871.pdf`. | Researcher supplies these. Until then, they stay blank, and `note` says why. |

### B. Gaps or conflicts found in AGENTS.md

| # | Issue | Recommendation |
|---|---|---|
| B1 | **Where does the human review record live?** §8.3 says to add the reviewer's name and decisions to the *validation report*, but §2 says `data/validation/` is generated and must never be hand-edited. Stage 4 also needs a machine-readable list of corrections. | **Decided: `data/review/`.** Hand-written review files, e.g. `asr_1871_run01_review.csv`, one row per checked cell: reviewer, date, row and column, verdict, corrected reading, reason. Validation reports stay fully generated. AGENTS.md §2, §4.5 and §8.3 updated to match. |
| B2 | **Printed Total rows in the processed dataset.** AGENTS.md doesn't say whether the Total row becomes rows in `asr_statistics.csv`. If it does, anyone summing the data would count everything twice. | Keep printed totals **out** of `asr_statistics.csv`. Write them to a separate `data/processed/asr_printed_totals.csv` (same columns), so they are preserved and can be compared but can't be summed by mistake. |
| B3 | **Where does the per-year tidy table go?** (Stage 4 output.) | `data/processed/by_year/asr_1871.csv`. |
| B4 | **Blank cells in the tidy data.** | One row per unit × measure, even when the cell is blank (`value` and `value_printed` empty). This makes "not reported" explicit rather than invisible. This seems to be what §5.3 intends; please confirm. |
| B5 | **Script names.** §8 lists `build_dataset.py` but no separate stage-4 script. | `scripts/structure.py --year YYYY` (stage 4, one year) and `scripts/build_dataset.py` (stage 5, combines every year). |

### C. Historical judgements for 1871

**C1. Stable unit IDs.** Every printed name on the 1871 page needs a `unit_id`. Proposed IDs:

| Printed name (1871) | Proposed `unit_id` | Open question |
|---|---|---|
| Maine | `maine` | |
| New England | `new_england` | Is it the same unit as "N.E.Mission" (1867–70) and "N.E.Conf." (1872–73), or does the change from mission to conference make it a new unit? |
| Vermont | `vermont` | |
| N.Y. & Penn. | `new_york_pennsylvania` | Same unit as "New York" (1872)? |
| Ohio | `ohio` | |
| Mich.& Ind. | `michigan_indiana` | *Decided:* a **different unit** from `michigan` (researcher, 2026-11-07). Predecessor and successor links still to be decided. |
| Wisconsin | `wisconsin` | New unit in 1871; predecessor `wisconsin_illinois`? |
| Illinois | `illinois` | New unit in 1871; predecessor `wisconsin_illinois`? |
| Minnesota | `minnesota` | |
| Iowa | `iowa` | |
| Kansas & Mo. | `kansas_missouri` | |
| Calif.Mis'n | `california` | Same unit as "California" (1872 on), or is `california_mission` a separate unit? |
| Swiss Mis'n | `swiss_mission` | Same unit as "Europ.Mis'n" (1870)? |

For the pilot, only the IDs need to be decided. Predecessor and successor links can stay blank, with a note, until 1870 and 1872 are processed.

**C2. Measures.** These are already decided in AGENTS.md §5.3. Recording them here for completeness:
"S.B. Fund Pledged" → `sb_pledged`; "S.B. Fund used by the Ch's." → `sb_used_by_churches`; "S.B. Fund Pledged to Conf's." → `sb_pledged_to_conference`; "S.B. Fund Pledged to Gen. Conf." → `sb_pledged_to_general_conference`; "S.B. Fund on hand" → `sb_on_hand`; plus `ministers`, `licentiates`, `churches`, `members`.

**C3. How thorough should the human check be?** *Decided:* the researcher checks **every cell by hand** (all 140 for 1871). That gives a real accuracy figure for the method, which helps decide how much checking later years need.

---

## Step-by-step plan

Each step has a review checkpoint. The researcher's updated instruction authorizes the Sol session transcription without the earlier paid-API checkpoint. The full human-review checkpoint remains required before structuring the data.

### Step 0. Setup

- Create `requirements.txt` with pinned versions: `pandas` (already installed), `pypdfium2` (to render PDFs), `Pillow` (to resize or crop images). Each gets a comment explaining why it's needed. The previously installed `openai` package is no longer required; it has been removed from requirements without uninstalling packages from the environment.
- Create the folders from AGENTS.md §2 (`data/images/`, `data/transcriptions/`, `data/validation/`, `data/review/`, `data/processed/`, `data/reference/`, `prompts/`, `scripts/`).
- Decide what git tracks: generated images (`data/images/`) can be rebuilt, so ignore them. Commit transcriptions, review files, reference tables and processed data.

**Checkpoint:** environment installs cleanly; Sol is selected. No API key is required.

### Step 1. Reference tables (1871 rows only)

Create, in `data/reference/`:
- `source_register.csv` with the `ASR1871.pdf` row: session number 9, session date `1871-02-07`, R&H vol. 37, issue blank, p. 68, R&H date `1871-02-14`, archive page 6, `has_table` = true, `current_run_id` blank for now. URL and download date per A6.
- `measures.csv` with the 1871 headings exactly as printed (C2).
- `units.csv` and `unit_names.csv` with the 1871 names, once C1 is decided.

**Checkpoint:** researcher reviews the four files.

### Step 2. Render (stage 1)

Write `scripts/render_pages.py --year 1871`:
- reads `source documents/ASR/ASR1871.pdf` (read-only);
- writes `data/images/asr_1871_300dpi.png`;
- refuses to overwrite unless `--force` is given;
- prints the image size so we can check it matches the native scan (2318 × 3437).

**Checkpoint:** open the PNG and compare it with the PDF.

### Step 3. Write the prompt

Write `prompts/transcribe_v1.md`, covering every point in AGENTS.md §4.3:
- transcribe only dark foreground text; ignore mirrored or faint bleed-through, including the ghost "Tenth Annual Session" text;
- put pencil annotations in `annotations`, never in the table;
- split run-together values by column position;
- flag `misaligned`, `uncertain` and `corrected_in_source` as defined in §4.4; use `[illegible]` rather than guessing; treat lone dots as blank;
- keep number formats exactly as printed (`$ 950.00` stays `$ 950.00`);
- return `has_table: false` for pages with no table;
- describe the JSON shape to return (cells and page text).

The prompt is written to work for any year, not just 1871.

**Checkpoint:** researcher reads the prompt. This is the main place where the research conventions turn into instructions for the model.

### Step 4. Transcribe (stage 2): Sol session, no API call

Use the session model to read the prompt and page images and author the JSON reply.
Import it with `scripts/transcribe.py --year 1871 --response /path/to/reply.json --model-label Sol`:
- reads the session-authored reply and checks its documented fields, types, unique cell positions, and allowed transcription flags;
- does not call a model or require an API key;
- assigns the next free run number (`asr_1871_run01`) and **never overwrites** an existing run;
- writes three files to `data/transcriptions/`:
  - `asr_1871_run01_cells.csv`: the cell table (AGENTS.md §5.1);
  - `asr_1871_run01_meta.json`: run metadata and page text (§5.2), including the selected model label, null exact ID and token usage when unavailable, prompt file and hash, source and image hashes, timestamp, and image size;
  - `asr_1871_run01_response.json`: exact bytes of the session-authored JSON reply, kept for audit. An additional inspection JSON records viewer image sizes and crop coordinates.

**Checkpoint:** inspect the cell table and page text. No separate API payment or key is involved.

### Step 5. Validate (stage 3)

Run `scripts/validate.py --year 1871 --run asr_1871_run01 --expected-rows 14 --expected-columns 10`. It writes a generated report to `data/validation/asr_1871_run01_validation.md` (readable) and `…_checks.csv` (one row per check). The report covers:
- **Completeness:** 14 rows × 10 columns present; every row has a label; headings recorded.
- **Format:** count cells are whole numbers; money cells have valid dollars and cents (`$` allowed only where printed); lists any non-blank cell that doesn't parse.
- **Arithmetic:** each of the 9 numeric columns summed and compared with the Total row; mismatches flagged `total_mismatch` with the size of the difference. (Expected: at least S.B. Fund Pledged, see above.)
- **Narrative:** 1871 has no notes giving figures, so this check is recorded as "not applicable", not silently skipped.
- **Review list:** every cell the model flagged and every cell involved in a failed check, listed first so the reviewer looks at them with particular care. Every other cell is still checked (C3).
- **Review template:** a blank `data/review/asr_1871_run01_review.csv` with one row per cell (all 140), pre-filled with the cell position and transcribed value, ready for the reviewer to complete. The script writes it only if it doesn't already exist, so a review in progress is never overwritten.

**Checkpoint:** show the report.

### Step 6. Human review (researcher, all cells)

The researcher opens the page image next to the validation report and completes the review file in `data/review/`, checking all 140 cells. Particular attention to:
- the Kansas & Mo. / Calif.Mis'n / Swiss Mis'n block, where Churches and Members sit between rows. Which row does each value belong to? This may need the original *Review and Herald* page;
- the split of `1110.003959.25`;
- the S.B. Fund Pledged total. Is the difference a misreading, a retyping error, or in the original?

The reviewer records findings in the review file only; the run files are never edited. Then set `current_run_id = asr_1871_run01` in the source register (unless the review finds a serious problem; see AGENTS.md §4.3 on re-runs).

**Checkpoint:** a completed review file. This is also where we measure accuracy: how many of the 140 cells the model got exactly right.

### Step 7. Structure (stage 4)

Write `scripts/structure.py --year 1871`. Using the current run, the review file and the reference tables, it:
- applies reviewer corrections, recording each one in `note`;
- maps printed names to `unit_id` and headings to `measure_id`, and stops with a clear message if a name or heading is missing from the reference tables (it never guesses);
- converts values to numbers (`$ 950.00` → `950.00`, blank → empty) while keeping `value_printed`;
- carries every flag through;
- writes `data/processed/by_year/asr_1871.csv` (13 units × 9 measures = 117 rows) and the printed totals separately (B2).

**Checkpoint:** spot-check a few rows against the image.

### Step 8. Combine (stage 5)

Write `scripts/build_dataset.py`. It combines all per-year tables into `data/processed/asr_statistics.csv` and runs the cross-year **carried-forward check**. With only 1871 processed, that check has no earlier year to compare against. The script should say so plainly ("1870 not available; carried-forward check not run for 1871"), not report a false "no problems found".

**Checkpoint:** final dataset for 1871.

### Step 9. Lessons and updates

- Update AGENTS.md: replace placeholder script names in §8, add the decisions from this plan to the §9 log, and update the §2 layout tree.
- Add a "Pilot findings" section to `docs/source_notes.md` for 1871: what the model got wrong, what review found, and the accuracy figure.
- Recommend whether the prompt or image settings (A4) should change before running the other years.

---

## Deliberately out of scope for the pilot

- Other years, including the no-table year 1874. The no-table path will be tested when 1874 is run.
- Unit predecessor and successor links (need neighbouring years).
- Re-running transcription. One run only, per the decisions log.
- Checking against the original *Review and Herald* printing, unless the reviewer decides it's needed for the misaligned values.
