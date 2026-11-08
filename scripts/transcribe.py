"""Save a session model's visual transcription as a new, permanent run.

This script does not call a model or require an API key. After the session model
reads prompts/transcribe_v1.md and the image, save its JSON reply, then run:
.venv/bin/python scripts/transcribe.py --year 1871 --response /tmp/reply.json --model-label Sol
Reads that reply and the rendered image; writes cells, metadata, and the exact
reply bytes to data/transcriptions/. Never overwrites a previous run.
"""

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

CELL_FIELDS = ["row_index", "column_index", "row_label", "column_heading", "value", "flags", "note"]
PAGE_FIELDS = {"title", "subtitle", "intro", "notes", "citation", "session", "archive_page_number", "annotations"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--model-id", help="Exact runtime ID, only if actually exposed by the session")
    parser.add_argument("--prompt", default="prompts/transcribe_v1.md")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    raw = args.response.read_bytes()
    reply = json.loads(raw)
    if type(reply.get("has_table")) is not bool or not isinstance(reply.get("cells"), list):
        parser.error("Reply must contain has_table (boolean) and cells (list).")
    page_text = reply.get("page_text", {})
    if set(page_text) != PAGE_FIELDS:
        parser.error("Page-text fields do not match the documented schema.")
    for key, value in page_text.items():
        if key == "annotations":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                parser.error("annotations must be a list of strings")
        elif not isinstance(value, str):
            parser.error(f"page_text.{key} must be a string")
    positions = set()
    for cell in reply["cells"]:
        if set(cell) != set(CELL_FIELDS):
            parser.error("Cell fields do not match the documented schema.")
        for key in CELL_FIELDS[:2]:
            if type(cell[key]) is not int:
                parser.error(f"{key} must be an integer")
        if cell["row_index"] < 1 or cell["column_index"] < 0:
            parser.error("Invalid cell position")
        if not all(isinstance(cell[key], str) for key in CELL_FIELDS[2:]):
            parser.error("Cell text fields must be strings")
        if set(cell["flags"].split(";")) - {"", "uncertain", "misaligned", "corrected_in_source"}:
            parser.error("Unsupported transcription flag")
        position = (cell["row_index"], cell["column_index"])
        if position in positions:
            parser.error(f"Duplicate cell: {position}")
        positions.add(position)
    if not reply["has_table"] and reply["cells"]:
        parser.error("A no-table reply must contain no cells.")
    source = args.root / "source documents" / "ASR" / f"ASR{args.year}.pdf"
    image = args.root / "data/images" / f"asr_{args.year}_{args.dpi}dpi.png"
    prompt = args.root / args.prompt
    with Image.open(image) as picture:
        image_size = list(picture.size)
    output = args.root / "data/transcriptions"
    output.mkdir(parents=True, exist_ok=True)
    run_number = 1
    while list(output.glob(f"asr_{args.year}_run{run_number:02d}*")):
        run_number += 1
    run_id = f"asr_{args.year}_run{run_number:02d}"
    metadata = {
        "run_id": run_id, "source_file": source.name,
        "image_file": str(image.relative_to(args.root)), "image_dpi": args.dpi,
        "image_size": image_size, "model_id": args.model_id,
        "model_label": args.model_label, "model_label_source": "researcher-selected session model",
        "model_id_note": "Exact runtime ID supplied" if args.model_id else "Exact runtime model ID not exposed to this session; not inferred from model label.",
        "execution_mode": "in_session_visual_transcription", "token_usage": None,
        "token_usage_note": "Not exposed by the session; no API call made.",
        "prompt_file": args.prompt, "prompt_version": prompt.stem,
        "prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
        "run_datetime": datetime.now(timezone.utc).isoformat(),
        "has_table": reply["has_table"], "page_text": page_text,
        "output_contract": "Session-authored JSON; checked locally, not API-constrained structured output.",
        "response_note": "Exact bytes of the session-authored structured reply supplied to this script; not an API response.",
    }
    # Exclusive creation protects the audit trail, including on interrupted runs.
    with (output / f"{run_id}_response.json").open("xb") as stream:
        stream.write(raw)
    with (output / f"{run_id}_cells.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["run_id", "source_file"] + CELL_FIELDS)
        writer.writeheader()
        for cell in reply["cells"]:
            writer.writerow({"run_id": run_id, "source_file": source.name, **cell})
    with (output / f"{run_id}_meta.json").open("x", encoding="utf-8") as stream:
        json.dump(metadata, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"Saved {run_id}: {len(reply['cells'])} cells. No API call made.")


if __name__ == "__main__":
    main()
