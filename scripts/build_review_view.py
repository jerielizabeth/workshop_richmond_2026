"""Build a local side-by-side PDF and CSV review page.

Reads the source PDF, transcription, validation checks, and human-review CSV.
Writes only a generated HTML page in data/validation/. It never changes a review
record. Browser edits can be downloaded as a new CSV draft and reopened later.
Run: .venv/bin/python scripts/build_review_view.py --year 1871 --run asr_1871_run01
Open the printed HTML path in a web browser. No server or network is required.
"""

import argparse
import base64
import csv
import json
import re
from pathlib import Path


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not re.fullmatch(rf"asr_{args.year}_run\d+", args.run):
        parser.error("Run ID must match the selected year.")
    review = read_csv(args.root / f"data/review/{args.run}_review.csv")
    cells = read_csv(args.root / f"data/transcriptions/{args.run}_cells.csv")
    checks = read_csv(args.root / f"data/validation/{args.run}_checks.csv")
    source = args.root / f"source documents/ASR/ASR{args.year}.pdf"
    image = args.root / f"data/images/asr_{args.year}_300dpi.png"
    payload = dict(run=args.run, year=args.year, review=review, cells=cells, checks=checks,
                   pdf=base64.b64encode(source.read_bytes()).decode(),
                   image=base64.b64encode(image.read_bytes()).decode())
    # JSON is data, never HTML. Escape characters that could terminate a script.
    encoded = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    template = Path(__file__).with_name("review_view.html").read_text(encoding="utf-8")
    output = args.root / f"data/validation/{args.run}_review_view.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w" if args.force else "x", encoding="utf-8") as stream:
        stream.write(template.replace("__REVIEW_DATA__", encoded))
    print(f"Created {output}")
    print("Open in your browser. Download review drafts to preserve edits; the original review CSV is never changed.")


if __name__ == "__main__":
    main()
