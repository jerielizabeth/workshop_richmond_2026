# AGENTS.md

Instructions and context for AI coding agents (and the people working with them) on this project. Read this file in full before starting work. If something here conflicts with a direct request from the researcher, ask before proceeding.

> **Status:** working draft. Remaining questions for the researcher are listed under §9, Open decisions.

---

## 1. Project overview

**Research goal.** Turn historical membership and financial statistics of the Seventh-day Adventist (SDA) denomination into structured, spreadsheet-ready data, so that change over time can be tracked and analysed.

**Sources.** Annual Statistical Reports (ASR) from [adventistarchives.org](https://www.adventistarchives.org). Each ASR file is a single **typescript page** that retypes a statistics table first printed in the *Review and Herald*, the denomination's weekly periodical. Each page covers one General Conference session. Each table lists conferences and missions with counts of ministers, licentiates, churches, and members, plus Systematic Benevolence (S.B.) giving figures.

**The core problem.** The PDFs are images only. They have no text layer, so the numbers cannot be copied or searched. Every value has to be transcribed. This project uses an **AI vision model** to do the transcription, with structured checks and human review.

**Scope.**
- *Current sample:* report years 1867–1876 (10 files). 1874 contains no table ("No Reports available."), so there are 9 tables.
- *Long-term goal:* a **reusable, documented** process that can be extended to further years without redesign.

**Audience.** This repository is used in a teaching workshop. Participants will read this file, the code, and the outputs. Write everything (code, comments, documentation, commit messages) so that a researcher who is new to programming can follow it.

---

## 2. Repository layout

```
richmond-workshop/
├── AGENTS.md                  ← this file
├── CLAUDE.md                  ← points Claude Code to this file
├── source documents/
│   └── ASR/                   ← original PDFs (READ-ONLY)
├── data/
│   ├── images/                ← page images rendered from the PDFs (generated; can be rebuilt)
│   ├── transcriptions/        ← verbatim model output and run metadata, one set per run
│   ├── validation/            ← validation reports
│   ├── processed/             ← cleaned, structured tables ready for analysis
│   └── reference/             ← source register and lookup tables (units, measures)
├── prompts/                   ← versioned prompts sent to the vision model
├── scripts/                   ← Python scripts, one per pipeline stage
└── docs/
    └── source_notes.md        ← year-by-year observations about the source pages
```

Folders that don't exist yet will be created as the pipeline is built. Update this tree when the layout changes.

**Rules**
- Never modify, rename, move, or delete anything in `source documents/`.
- Generated files (`data/images/`, `data/validation/`) must be reproducible from scripts. Never hand-edit them.
- Never overwrite a transcription in `data/transcriptions/`. Write a new run instead. The run used downstream is recorded in `data/reference/source_register.csv` (column `current_run_id`).

---

## 3. Source documents

**Naming convention:** `ASR{YYYY}.pdf`, where `YYYY` is the year in the page title. Example: `ASR1871.pdf`.

**Current holdings:** `ASR1867.pdf` – `ASR1876.pdf`. Each file is a **single page**.

**Source register:** `data/reference/source_register.csv` has one row per source file, recording where it came from and what it contains (see §5.4).

**Adding a new year**
1. Download the PDF from adventistarchives.org.
2. Rename it to `ASR{YYYY}.pdf` and place it in `source documents/ASR/`.
3. Add a row to the source register with the source URL and download date.
4. Look at the page and add a section to `docs/source_notes.md` describing anything new: the column layout, unit names, number format, or visual hazards.
5. Run the pipeline for that year only (see §8.1).

**Known quirks (summary).** See [docs/source_notes.md](docs/source_notes.md) for year-by-year details.
- **Two layers of possible error:** the original printing in the *Review and Herald*, and the later retyping.
- **"Year" is ambiguous:** the title year doesn't always match the session date. The page titled 1872 records a December 1871 session.
- **Columns change:** four layouts across 1867–1876, and 1876 has only one money column.
- **Units change:** conferences merge, split, and get renamed. The same name can cover different territory in different years.
- **Number formats change:** `1275.00` up to 1875, but `1,275 00` in 1876.
- **Visual hazards:** mirrored bleed-through from neighbouring pages (including a ghost table behind the empty 1874 page), later pencil annotations, totals with no space between columns, and values sitting between rows.
- **Carried-forward data:** some figures repeat unchanged from the previous year, and the 1876 notes say some reports were "given as last year".

---

## 4. Data processing conventions

These rules exist so that every number in the final dataset can be **trusted, traced, and checked**.

### 4.1 Pipeline stages

Each stage writes its output to disk so it can be inspected on its own.

| Stage | Input | Output | Notes |
|---|---|---|---|
| 1. Render | PDF | page image (PNG, 300 DPI) in `data/images/` | Deterministic; safe to re-run |
| 2. Transcribe | page image + prompt | cell table (CSV) + metadata (JSON) in `data/transcriptions/` | AI vision model; see §4.3 |
| 3. Validate | transcription | report in `data/validation/` | Arithmetic, format, and narrative checks; see §4.5 |
| 4. Structure | validated transcription + reference tables | per-year tidy table | Interpretation and normalisation happen here, not earlier |
| 5. Combine | per-year tidy tables | `data/processed/asr_statistics.csv` | Adds cross-year checks (e.g. carried-forward values) |

### 4.2 Faithfulness: transcribe first, interpret later

- Transcriptions record **exactly what is printed**: original spelling, abbreviations, punctuation, ditto marks, place names, and column headings.
- Do not correct, standardise, or "fix" anything during transcription. That belongs in stage 4, and every change made there must be documented.
- If the source contains an apparent error (e.g. a total that doesn't add up), transcribe it as printed and **flag** it. Do not correct it.
- Text outside the table goes into the run metadata, not the table. This includes the title, subtitle, notes, citation, session line, archive page number, and any pencil annotations.

### 4.3 AI vision transcription

- **Run metadata:** every transcription run records, in its metadata file:
  - the exact model ID
  - the prompt file and version used (from `prompts/`)
  - the date and time of the run
  - the source file and image settings
- **Prompts:** prompts live in `prompts/` as versioned files (e.g. `transcribe_v1.md`). Edit a prompt by creating a new version, never by overwriting the old one.
- **What the prompt must tell the model:**
  - Transcribe only the dark foreground text. Ignore faint, mirrored bleed-through.
  - Report pencil annotations separately; never put them in the table.
  - Split run-together values using the column positions.
  - Flag values whose row or column position is ambiguous.
  - Keep number formats exactly as printed (including `1,275 00` and `$`).
  - Ignore stray dots or specks in cells. They are scan artifacts, not content.
  - Mark uncertainty instead of guessing (see §4.4).
  - Return "no table" for pages without one, such as 1874.
- **One run per page.** Each page is transcribed once. Errors are caught by validation (§4.5) and human review (§8.3). A page is re-run only if review finds a serious problem, and the re-run becomes a new run (it never overwrites the old one).

### 4.4 Uncertainty and special values

Transcription markers (stage 2):

| Situation | How to record it | Meaning |
|---|---|---|
| Cell is blank | *(empty)* | Nothing printed |
| Lone dot or speck in a cell (`.`, `•`) | *(empty)* | Scan artifact, not content; treat the cell as blank |
| Ditto mark in a name (`"`) | `"` | Transcribed as printed; expanded in stage 4 |
| Cannot be read | `[illegible]` | Do not guess |
| Readable but unsure | value + flag `uncertain` | Best reading, needs review |
| Unclear which row/column it belongs to | value + flag `misaligned` | Position needs review |
| Visibly overtyped or corrected | value + flag `corrected_in_source` | Note the competing reading in `note` |

Flags added later in the pipeline (stages 3–5):

| Flag | Meaning |
|---|---|
| `total_mismatch` | Row values don't add up to the printed total |
| `carried_forward_suspected` | Identical to the same unit's value in the previous year |
| `source_error_suspected` | Reviewer believes the source itself is wrong; explain in `note` |

A cell can carry several flags, separated by `;`.

### 4.5 Validation

- **Arithmetic checks:** where the source prints totals, recompute them from the rows and report mismatches. A mismatch may be a transcription error *or* an error in the original. Check the image before assuming either.
- **Format checks:** numbers parse as numbers, money values have valid dollars and cents, and no unexpected blank cells.
- **Narrative checks:** where the page text states figures (e.g. the 1876 note on gains since last year), compare them with the table.
- **Human spot-check:** a person compares a sample of transcribed values with the page image. Record who checked what, and when, in the validation report.

### 4.6 Provenance

Every row in a processed table must be traceable to its source. At a minimum, include:
- `source_file` (e.g. `ASR1871.pdf`)
- `run_id` of the transcription that produced it
- `unit_name_printed` and `value_printed`, the original text before normalisation

### 4.7 Change over time

Organisational units (conferences, missions, states) split, merge, and get renamed. Do not silently treat two differently named units as the same unit. Do not assume a unit is the same just because its name is.
- Map each **printed name** to a **stable unit ID** in `data/reference/unit_names.csv`. Define each unit, with its predecessors and successors, in `data/reference/units.csv`.
- Map each **printed column heading** to a **stable measure ID** in `data/reference/measures.csv`.
- Any decision about whether two units or columns are "the same" across years is a **historical judgement**: ask the researcher, then record the decision in §9.
- Keep the processed data at the level the source reports (e.g. "Wisconsin & Illinois" stays one unit in 1867–70). Combining units for comparisons across years happens in analysis, not in the processed dataset.

### 4.8 Formats

- **File format:** CSV, UTF-8, comma-delimited, header row, one table per file. CSVs open directly in Excel or Google Sheets; do not produce `.xlsx` files.
- **Tidy ("long") format** for processed data: one row per observation (one unit × one report year × one measure).
- **Money:** store as a decimal number in dollars (e.g. `1275.00`). The 1876 format `1,275 00` becomes `1275.00` in stage 4. Do not store `$` or commas in numeric columns.
- **Dates:** ISO 8601 (`YYYY-MM-DD`, or `YYYY` when only the year is known).
- **File names:** lowercase, no spaces, words separated by underscores (e.g. `asr_1871_run01_cells.csv`).
- **IDs:** lowercase with underscores (e.g. `wisconsin_illinois`, `sb_pledged`).

---

## 5. Data dictionary

### 5.1 Transcription cells: `data/transcriptions/asr_{year}_run{NN}_cells.csv`

One row per table cell, including the name column and the Total row. This long format makes it easy to attach a flag and a note to any individual cell.

| Column | Type | Definition |
|---|---|---|
| `run_id` | text | e.g. `asr_1871_run01` |
| `source_file` | text | e.g. `ASR1871.pdf` |
| `row_index` | integer | Row position from top, starting at 1 (Total row included) |
| `column_index` | integer | Column position from left, starting at 0 (0 = name column) |
| `row_label` | text | Name-column text for this row, verbatim |
| `column_heading` | text | Column heading, verbatim (line breaks become single spaces) |
| `value` | text | Cell contents, verbatim (see §4.4) |
| `flags` | text | Zero or more flags, separated by `;` |
| `note` | text | Free-text explanation of any flag |

### 5.2 Run metadata: `data/transcriptions/asr_{year}_run{NN}_meta.json`

Contains `run_id`, `source_file`, `image_file`, `image_dpi`, `model_id`, `prompt_file`, `run_datetime`, `has_table` (true/false), and `page_text`. `page_text` holds, verbatim: `title`, `subtitle`, `intro`, `notes`, `citation`, `session`, `archive_page_number`, and `annotations` (a list of pencil or handwritten additions).

### 5.3 Processed dataset: `data/processed/asr_statistics.csv`

| Column | Type | Definition |
|---|---|---|
| `report_year` | integer | Year in the page title (matches the file name) |
| `unit_id` | text | Stable unit ID (from `units.csv`) |
| `unit_name_printed` | text | Name as printed, with ditto marks expanded |
| `measure_id` | text | Stable measure ID (see below) |
| `value` | number | Cleaned numeric value; empty if not reported or illegible |
| `value_printed` | text | Value exactly as transcribed |
| `flags` | text | All flags from every stage, separated by `;` |
| `note` | text | Explanation of flags or interpretation decisions |
| `source_file` | text | e.g. `ASR1871.pdf` |
| `run_id` | text | Transcription run the value came from |

Session and citation details live in the source register (join on `report_year`). They are not repeated on every row.

**Measures**

| `measure_id` | Unit | Printed headings | Years |
|---|---|---|---|
| `ministers` | count | Ministers | 1867–76 |
| `licentiates` | count | Licentiates | 1867–76 |
| `churches` | count | Churches | 1867–76 |
| `members` | count | Members | 1867–76 |
| `sb_pledged` | dollars | S. B. Fund Pledged; S.B. Pledges (1876) | 1867–76 |
| `sb_used_by_churches` | dollars | Used by Ch.; S.B. Fund used by the Ch('s). | 1867–75 |
| `sb_pledged_to_conference` | dollars | Pledged to conf.; S.B. Fund Pledged to Conf('s).; … to St.Conf. | 1867–75 |
| `sb_pledged_to_general_conference` | dollars | Pledged to General Conf.; S.B. Fund Pledged to Gen. Conf. / to the G. C. | 1868–75 |
| `sb_on_hand` | dollars | Funds on hand; S.B. Fund on hand | 1867–75 |
| `sb_pledged_to_state_conference_1867` | dollars | Pledged to State Conf. | 1867 only |

The 1867 "Pledged to State Conf." column is its own measure. Do not merge it with `sb_pledged_to_conference` (also printed in 1867) or with the 1868 "Pledged to General Conf." column, even though the later "to St.Conf." heading looks similar.

### 5.4 Reference tables: `data/reference/`

- **`source_register.csv`:** one row per source file, including files with no table (e.g. 1874, recorded with `has_table` = false). Columns: `source_file`, `report_year`, `archive_url`, `download_date`, `archive_page_number`, `has_table`, `session_number`, `session_date`, `rh_volume`, `rh_issue`, `rh_page`, `rh_date`, `current_run_id`, `note`. Blank citation parts stay blank; don't fill them in from other sources without recording that in `note`.
- **`units.csv`:** one row per stable unit. Columns: `unit_id`, `standard_name`, `description` (territory covered), `first_year`, `last_year`, `predecessor_ids`, `successor_ids`, `note`.
- **`unit_names.csv`:** maps printed names to units. Columns: `printed_name`, `first_year`, `last_year`, `unit_id`, `note`. The same printed name may map to different units in different years.
- **`measures.csv`:** maps printed headings to measures. Columns: `printed_heading`, `first_year`, `last_year`, `measure_id`, `note`.

---

## 6. Coding conventions

### 6.1 Environment
- **Language:** Python 3.14, using the project virtual environment in `.venv/`.
- **Dependencies:** listed with pinned versions in `requirements.txt`. If you add a package, add it there and explain why it's needed.
- Keep dependencies few. Prefer the standard library and well-known packages (e.g. `pandas`).

### 6.2 Writing scripts
- **One script per pipeline stage**, named for what it does (e.g. `scripts/render_pages.py`, `scripts/transcribe.py`).
- **No hard-coded years or file paths.** Scripts take command-line arguments (e.g. `--year 1871`) so they work for any year.
- **Safe to re-run:** scripts must not overwrite or destroy existing outputs unless explicitly told to (e.g. a `--force` flag). Transcription scripts are never allowed to overwrite.
- **Paths contain spaces** (`source documents/`). Always handle them correctly, and quote them in shell commands.
- Secrets such as API keys come from environment variables and are never written into code or committed.

### 6.3 Readability (for workshop participants)
- Start every script with a docstring that explains, in plain language: what it does, what it reads, what it writes, and how to run it (with an example command).
- Comment the *why*, not just the *what*, especially for anything that encodes a data decision.
- Prefer clear, explicit code to clever or compact code. Use descriptive variable names (`membership_total`, not `mt`).
- Print short progress messages so a user can see what the script is doing.

### 6.4 Notebooks vs scripts
- **Scripts** are for the pipeline: anything that produces data other work depends on.
- **Notebooks** (if used) are for exploration and analysis only. They read from `data/processed/` and never write to `data/`.

---

## 7. Conversation and collaboration style

How agents should work with the researcher and workshop participants:

- **Explain the code you write.** After writing or changing code, say in plain language what it does, why it's built that way, and how to run it. Assume the reader is a capable researcher who may be new to programming.
- **Plain language first.** Define technical terms the first time you use them, and avoid unexplained jargon.
- **Be explicit about uncertainty.** Say when you're unsure, when a value is a guess, or when you haven't verified something.
- **Ask before making historical or interpretive decisions.** For example, whether two differently labelled columns measure the same thing, or how to treat an ambiguous entry. Offer options and your reasoning, but let the researcher decide.
- **Never invent or silently correct data.** If a value is missing or unreadable, say so.
- **Confirm before bulk or destructive actions**, such as re-running transcription across all years, deleting files, or overwriting outputs.
- **Work in small, reviewable steps.** Show results for one year before scaling to all of them.
- **Report outcomes honestly.** If a check fails or a step was skipped, say so clearly.

---

## 8. Workflows

*Planned. Script names are placeholders until the scripts exist; update these steps as they are built.*

### 8.1 Add a new year
1. Follow "Adding a new year" in §3: download, name, register, and write source notes.
2. Render the page: `python scripts/render_pages.py --year YYYY`
3. Transcribe: `python scripts/transcribe.py --year YYYY` (each run gets a new run number). If the page has no table, the run records `has_table: false` and steps 4–6 are skipped.
4. Validate: `python scripts/validate.py --year YYYY`
5. Review the validation report. Check every flagged cell against the image, and record your decisions in the cell `note` or §9.
6. If the year introduces new unit names or column headings, add them to `unit_names.csv` / `measures.csv`. Ask the researcher about any new mapping.
7. Set `current_run_id` in the source register.
8. Rebuild the processed dataset: `python scripts/build_dataset.py`

### 8.2 Re-run the pipeline for one year
1. Rendering is safe to repeat. Transcription always creates a new run and never replaces an old one.
2. If a prompt changed, record the new prompt version and why, in §9.
3. Validate the new run, then decide whether it becomes `current_run_id`.
4. Rebuild the processed dataset.

### 8.3 Review a transcription
1. Open the page image next to the validation report.
2. Check every flagged cell, then a random sample of at least 10 unflagged cells.
3. For each problem, record the correct reading and the reason in `note`. Never edit the original run file. Corrections are applied in stage 4 from the review record.
4. Add the reviewer's name, the date, and the cells checked to the validation report.

---

## 9. Decisions log

Record significant decisions here, newest first, with the date, the decision, and the reasoning. This includes data interpretation choices, schema changes, and changes to conventions in this file.

| Date | Decision | Reasoning |
|---|---|---|
| 2026-11-07 | 1874 is recorded as a year with no data: listed in the source register with `has_table` = false, with no rows in the processed dataset | The page states "No Reports available."; listing it documents the gap rather than hiding it |
| 2026-11-07 | One transcription run per page | Validation and human review are the error checks; a second run adds cost and complexity for the demo |
| 2026-11-07 | Carried-forward values are kept as observations, flagged `carried_forward_suspected` | Keeps the record complete; analysts can choose to exclude flagged values |
| 2026-11-07 | Lone dots or specks in cells are scan artifacts; record the cell as blank | Researcher's reading of the sources: they carry no meaning |
| 2026-11-07 | 1876 "S.B. Pledges" is the same measure as earlier "S.B. Fund Pledged" (`sb_pledged`) | Researcher confirmed |
| 2026-11-07 | 1867 "Pledged to State Conf." is a separate measure, not merged with "Pledged to conf." or the 1868 "Pledged to General Conf." | Researcher's decision: the columns are recorded separately |
| 2026-11-07 | Year-by-year source details kept in `docs/source_notes.md`, not in this file | Keeps this file short enough for agents to read in full; source notes will grow with each year |
| 2026-11-07 | Processed data keeps units as reported (no merging of units across years) | Merging is an analytical choice; keeping the reported level preserves the evidence |
| 2026-11-07 | Output CSV only; no Excel files | CSVs open in any spreadsheet tool, and one format avoids version drift |
| 2026-11-07 | Use an AI vision model for transcription | Sources are image-only PDFs; manual transcription doesn't scale beyond the sample |
| 2026-11-07 | Scope limited to ASR series; *Review and Herald* PDFs excluded from this demo | Keeps the workshop demo focused on one consistent source series |

### Open decisions (researcher to decide)
1. **Which "year" to use for analysis.** The proposal is to key on `report_year` (the title year) and keep session dates in the source register. Alternatives are the session date or the *Review and Herald* publication date. This matters for 1871–72 (two sessions in calendar 1871) and the 1873→1875 gap.
