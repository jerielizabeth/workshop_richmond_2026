"""Render one source PDF to a PNG for visual transcription.

Reads source documents/ASR/ASR{year}.pdf without changing it and writes
data/images/asr_{year}_{dpi}dpi.png. Existing images require --force.
Run: .venv/bin/python scripts/render_pages.py --year 1871
"""

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
                        help="Also write a crop in rendered-image pixel coordinates.")
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error("--dpi must be positive")
    source = args.root / "source documents" / "ASR" / f"ASR{args.year}.pdf"
    destination = args.root / "data" / "images" / f"asr_{args.year}_{args.dpi}dpi.png"
    crop_destination = destination.with_stem(destination.stem + "_crop")
    if destination.exists() and not args.force:
        parser.error(f"Image already exists: {destination}. Use --force to rebuild it.")
    if args.crop and crop_destination.exists() and not args.force:
        parser.error(f"Crop already exists: {crop_destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with pdfium.PdfDocument(source) as document:
        if len(document) != 1:
            parser.error("Expected a single-page PDF; no image written.")
        page = document[0]
        bitmap = page.render(scale=args.dpi / 72)
        image = bitmap.to_pil()
        if args.crop:
            left, top, right, bottom = args.crop
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                parser.error("Crop must be inside the rendered image.")
        with destination.open("wb" if args.force else "xb") as stream:
            image.save(stream, format="PNG", dpi=(args.dpi, args.dpi))
        print(f"Rendered {source.name}: {image.width} × {image.height} pixels at {args.dpi} DPI")
        print(destination)
        if args.crop:
            with image.crop(args.crop) as crop:
                with crop_destination.open("wb" if args.force else "xb") as stream:
                    crop.save(stream, format="PNG", dpi=(args.dpi, args.dpi))
            print(f"Crop {args.crop}: {crop_destination}")
        image.close()
        bitmap.close()
        page.close()


if __name__ == "__main__":
    main()
