"""Take a bounded CC0 sample; never download the multi-gigabyte full database.

Authoring only: requires zstandard. Runtime puzzles are embedded in the HTML.
The integration step validates every line and applies the opponent's first move.
"""
import csv
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

import zstandard

ROOT = Path(__file__).resolve().parents[1]
URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
LIMITS = {1: 4000, 2: 4000, 3: 2000}


def main():
    counts = dict.fromkeys(LIMITS, 0)
    selected = []
    req = Request(URL, headers={"User-Agent": "StudyHub-OfflineChess/1.0"})
    with urlopen(req, timeout=45) as response:
        with zstandard.ZstdDecompressor().stream_reader(response) as reader:
            rows = csv.DictReader(io.TextIOWrapper(reader, encoding="utf-8"))
            for index, row in enumerate(rows):
                if index >= 500000:
                    raise RuntimeError("Bounded sample exhausted before all quotas")
                themes = row["Themes"].split()
                mate = next((n for n in LIMITS if f"mateIn{n}" in themes), None)
                if not mate or counts[mate] >= LIMITS[mate]:
                    continue
                rating = int(row["Rating"])
                if int(row["Popularity"]) < 80 or not 400 <= rating <= 2800:
                    continue
                selected.append([row["PuzzleId"], row["FEN"], row["Moves"], rating, mate])
                counts[mate] += 1
                if len(selected) % 2000 == 0:
                    print(f"Selected {len(selected)} puzzles: {counts}", flush=True)
                if counts == LIMITS:
                    break
    target = ROOT / "data/chess/puzzles-source.json"
    target.write_text(json.dumps({"source": URL, "license": "CC0-1.0", "puzzles": selected}, separators=(",", ":")), encoding="utf-8")
    print(f"Saved {len(selected)} source records; {counts}", flush=True)


if __name__ == "__main__":
    main()
