# ASR visual transcription, version 1

Transcribe the supplied page image faithfully. Record only dark foreground text;
ignore faint or mirrored bleed-through, even if it resembles a complete table
or another session heading. Do not use arithmetic or earlier notes to correct
what is printed. Preserve spelling, punctuation, abbreviations, ditto marks,
currency signs, decimal points, spaces within numbers, and blank cells.

Include every table cell, including name cells, blank cells, and printed totals.
Row indices start at 1; column indices start at 0 for the name column. Preserve
headings, replacing line breaks with single spaces. Split run-together values
using column positions. Treat lone dots and specks as blank scan artifacts.
Do not interpret blank cells as zero.

Use [illegible] if a value cannot be read. For a best reading that remains unsure,
add uncertain; for unclear row or column placement add misaligned; for visible
overtyping or source correction add corrected_in_source and explain competing
readings in note. Multiple flags are separated by semicolons. Do not silently
resolve ambiguous row placement or repair apparent source errors.

Keep all text outside the table in page_text: title, subtitle, intro, notes,
citation, session, archive_page_number, and annotations. Annotations is a list
of later pencil or handwritten additions; do not put these in the table.
Handwritten column headings that identify columns belong in the table headings.
If there is no foreground table, return has_table=false and cells=[].

Return JSON with has_table (boolean), page_text (the fields above as strings,
except annotations as a string list), and cells (an array). Each cell contains
row_index (integer), column_index (integer), row_label (string), column_heading
(string), value (string), flags (string), and note (string). No normalisation,
unit mapping, or historical interpretation belongs in this transcription.
