# Source notes: Annual Statistical Reports (ASR), 1867–1876

Year-by-year observations about the source pages. General rules for handling these quirks are in [AGENTS.md](../AGENTS.md) §3 and §4. Add a section for each new year as it is processed.

> These notes come from a visual review of the page images on 2026-11-07 (by Claude, before any systematic transcription). Treat specific numbers quoted here as **to be verified** against the transcriptions.

---

## What these pages are

Each PDF is a **single typescript page** that copies a statistics table from the *Review and Herald*, the denomination's weekly periodical. Each page covers one General Conference session. The pages are not scans of the periodical itself. That means two layers of possible error: the original printing, and the later retyping.

Features shared by most pages:
- A typed title (e.g. "SEVENTH-DAY ADVENTIST STATISTICS, 1869"), and in later years a subtitle ("General Conference Summary for the Year …").
- One table: one row per conference or mission, followed by a **Total** row.
- A citation line, "Copied from: Review and Herald, Battle Creek, Mich., Vol. …, No. …, p. …, [date]".
- A session line (e.g. "Seventh Annual Session / May 18, 1869").
- A red page number in the top-right corner (2–11). This is the archive compilation's page number, not part of the original.

## Year-by-year summary

| Report year | File | Session | Session date | *Review and Herald* citation (as typed) | Column layout |
|---|---|---|---|---|---|
| 1867 | ASR1867.pdf | Fifth | May 14, 1867 | Vol. 29, No. 24, p. 283, 1867 | A |
| 1868 | ASR1868.pdf | "Six" (sic) | May 12, 1868 | Vol. 31, p. 356, 1868 *(no issue no.)* | B |
| 1869 | ASR1869.pdf | Seventh | May 18, 1869 | Vol. 33, No. 22, p. 172, May 25, 1869 | C |
| 1870 | ASR1870.pdf | Eighth | March 15, 1870 | Vol. 35, No. 14, p. 109, 1870 | C |
| 1871 | ASR1871.pdf | Ninth | February 7, 1871 | Vol. 37, No. [blank], p. 68, Feb. 14, 1871 | C |
| 1872 | ASR1872.pdf | Tenth | Dec. 29, **1871** | Vol. 39, No. [blank], p. 20, Jan. 2, 1872 | C |
| 1873 | ASR1873.pdf | Eleventh | March 11, 1873 | Vol. 41, No. 14, March 18, 1873, p. 108 | C |
| 1874 | ASR1874.pdf | — | — | — | **No table** |
| 1875 | ASR1875.pdf | Fourteenth | August 15, 1875 | Vol. 45, No. [blank], p. 59, Aug. 26, 1875 | C |
| 1876 | ASR1876.pdf | Fifteenth | September 19, 1876 | Vol. 48, No. 14, p. 105, October 5, 1876 | D |

**The "year" is ambiguous.** The year in the page title doesn't always match the session date. The page titled 1872 records a session held in December 1871, so calendar year 1871 has two sessions (February and December). The 12th and 13th sessions don't appear at all: the numbering jumps from the Eleventh (March 1873) to the Fourteenth (August 1875).

## Column layouts

S.B. = **Systematic Benevolence**, the denomination's pledged-giving plan (the 1876 page spells it out).

| Layout | Years | Columns after the name column |
|---|---|---|
| A | 1867 | Ministers · Licentiates · Churches · Members · S. B. Fund Pledged · Used by Ch. · Pledged to conf. · Pledged to State Conf. · Funds on hand. |
| B | 1868 | Same as A, except "Pledged to **General** Conf." replaces "Pledged to State Conf." |
| C | 1869–1873, 1875 | Ministers · Licentiates · Churches · Members · S.B. Fund Pledged · S.B. Fund used by the Ch.('s) · S.B. Fund Pledged to Conf('s). *(1869–71)* / to St.Conf. *(1872–75)* · S.B. Fund Pledged to Gen. Conf. / to the G. C. *(1870)* · S.B. Fund on hand |
| D | 1876 | Ministers · Licentiates · Churches · Members · S.B. Pledges |

Other heading details:
- The name column is headed "Names." (1867), "Names" (1868), "Names of Conferences" (1869–72, 1875–76), or "Name of Conferences" (1873).
- 1867–1872: the four count headings (Ministers, Licentiates, Churches, Members) are **handwritten**, written vertically. From 1873 on they are typed, still vertical.

## Conference and mission names

Names change, merge, and split over the period. The same printed name can also cover a different territory in different years (e.g. "Michigan" before and after Indiana is reported separately). As printed:

| Unit | Printed names by year |
|---|---|
| Michigan | "Mich. Conf." (1867–68), "Michigan" (1869–70), "Mich.& Ind." (1871–72), "Michigan" (1873, 1875–76) |
| Indiana | inside "Mich.& Ind." (1871–72); "Indiana" (1873, 1875–76) |
| New York & Pennsylvania | "N.Y. & Pa." (1867–68, 1875), "N.Y. & Penn." (1869–71, 1873), "New York" (1872), "New York and Pennsylvania" (1876) |
| Wisconsin & Illinois | "Wis.& Ill." (1867–68), "Wis.& Illin." (1869–70); separate "Wisconsin" and "Illinois" from 1871 |
| Iowa | "Iowa" (1867–72), "Iowa & Nebr." (1873, 1875), "Iowa and Nebraska" (1876) |
| New England | "N.E.Mission" (1867–70), "New England" (1871, 1875–76), "N.E.Conf." (1872–73) |
| Maine | from 1868 |
| California | "Calif.Mis'n" (1869–71), "California" (1872 on) |
| European / Swiss | "Europ.Mis'n" (1870), "Swiss Mis'n" (1871), "Swiss Miss." (1872, 1875), "Swiss Mission" (1873, 1876) |
| Kansas & Missouri | "Kansas & Mo." (1871–75); separate "Missouri" and "Kansas" in 1876 |
| Kentucky | 1876 only |
| Ohio, Vermont, Minnesota | every year (spelled "Minesota" in 1869) |

This table groups printed names by rough geography to make them easy to find. It does **not** say which names are the same unit; those decisions are in `data/reference/unit_names.csv` and the AGENTS.md §9 decisions log. For example, "Mich.& Ind." is listed beside Michigan above but is a separate unit (`michigan_indiana`, decided 2026-11-07).

In 1867–68 the name column uses **ditto marks** (`"`) to repeat "Conf." from the first row (e.g. `Iowa "`).

The order of rows varies from year to year, so don't rely on row position to identify a unit.

## Number formatting

- **1867–1875:** decimal point, no thousands separator (`6143.00`). A `$` appears only on the first row of the first money column.
- **1876:** comma thousands separator with a **space instead of a decimal point** (`1,275 00`, `$ 43,998 47`). `$` on the first row and the total.
- **Dots** (`.` or `•`) appear in some count cells (e.g. 1868 Iowa licentiates, 1876 Swiss Mission licentiates). These are scan artifacts, not content, so the cells are recorded as blank (decided 2026-11-07).
- **Blank cells** are common, especially in the money columns.
- On a typewriter, the digit 1 can look like a lowercase `l`, and 0 like a capital `O`.

## Visual hazards for transcription

- **Bleed-through:** every page shows faint, mirrored text from the next or previous page. It often looks like a complete table. **Only the dark foreground text is the source.**
- **1874:** the page reads only "No Reports available." Behind it is a faint but almost complete ghost table, which must **not** be transcribed.
- **Pencil annotations** were added later: 1871 ("Feb", "Feb. 1871"), 1872 ("Dec. 1871", with the 1872 in the subtitle circled), and 1873 ("as of Mar 1873"). Record them in the metadata, not in the table.
- **Run-together totals:** in some Total rows, neighbouring columns have no space between them (1871: `1110.003959.25`; 1872: `2150.003894.94`). Split them by column position.
- **Values between rows:** some values sit halfway between two rows (e.g. 1871–1872 Churches and Members for Kansas & Mo. and California, and 1873 Indiana). Flag them as `misaligned`.
- **Corrections in the typescript:** some digits are overtyped or smudged (e.g. 1868 Funds on hand total; 1873 Michigan "used by the Ch's").

## Content issues to check (candidate source errors)

These are things noticed on a first look. Each one needs checking against the transcription, and possibly the original periodical, before anything is concluded.

- **1869 Minnesota:** "used by the Ch." reads 3959.34, the same as Michigan's "S.B. Fund Pledged". Michigan's own "used" and "pledged to Conf." cells are blank. Values may have slipped one row down.
- **Repeated figures across years:** identical fund figures for N.Y. & Penn. in 1869, 1870 and 1871; Ohio in 1869 and 1870; and several units (Mich.& Ind., Iowa, Minnesota, California) in 1871 and 1872. These look like reports carried forward from the previous year, not new data.
- **1876 notes:** the text says the Michigan report is incomplete, and that New England, New York and Illinois are "given as last year with a few known changes". It also mentions companies in Texas, Virginia and Maryland that aren't in the table.
- **1876 stated gains vs. totals:** the text claims gains of 2,012 members and $11,079.85 over 1875. On a first reading, the printed totals give 2,022 members and $11,379.85. To verify.
- **1870:** the Total row has no value for "S.B. Fund on hand".

## 1871 pilot findings (2026-11-07; human review pending)

The first Sol session transcription is `asr_1871_run01`: 140 cells, including
blanks and the Total row. The 300 DPI PDF render is 2319 × 3438 pixels (one pixel
larger in each direction than the plan's preliminary dimensions). A table crop
at [130, 700, 1940, 1980] was also inspected without resizing. Both can be rebuilt
with `scripts/render_pages.py`; see the run's inspection JSON for the command.

Generated validation finds eight matching numeric totals and one mismatch:
S.B. Fund Pledged sums to 23066.33, while the transcribed printed total is
23066.42. The difference is -0.09 (sum minus printed total). This remains an
unresolved finding, not an established error in the source. Six Churches/Members
cells in the Kansas & Mo. / Calif.Mis'n. / Swiss Mis'n. block carry `misaligned`
flags, including ambiguous blank assignments. The run-together totals were read
as 1110.00 and 3959.25 by column position.

No human review has been recorded. Accuracy and the cause of the mismatch are
unknown. The source register's current run remains blank, and no processed
dataset has been built. Unit mappings other than the researcher's already
approved Michigan & Indiana mapping remain pending. Wait for human review before
recommending changes to the prompt or scaling to additional years.
