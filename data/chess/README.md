# Study Hub offline chess puzzles

10,000 distinct positions from the [Lichess open puzzle database](https://database.lichess.org/#puzzles), retrieved on 2026-10-16. The database is released under **CC0-1.0**. Study Hub does not copy Lichess server code, branding or lesson text.

* 4,000 mate-in-one puzzles
* 4,000 mate-in-two puzzles
* 2,000 mate-in-three puzzles

`puzzles-source.json` retains the original database records, as compact tuples `[PuzzleId, FEN, Moves, Rating, MateLength]`. The FEN is **before** the opponent's setup move. The first UCI move belongs to the opponent, not the learner. Each ID links back to `https://lichess.org/training/ID`.

The authoring script `scripts/chess-integrate.cjs` applies that first move, checks all remaining moves with chess.js, rejects duplicate IDs/positions, requires exactly `2 * MateLength - 1` solution plies, and verifies final checkmate before embedding the playable records in `study-hub.html`. Source ratings are training filters, not ratings assigned to the learner or the computer opponent.

The bounded sampling script `scripts/chess-puzzles.py` stops after these quotas; it does not download the full database. It requires the authoring-only `zstandard` Python package. Rebuilding from the checked-in sample requires only Node:

```
node scripts/chess-integrate.cjs
```

The delivered website makes **no chess network requests**. Rules, puzzles, worker source and styles are embedded in the existing HTML so double-clicking the file and the existing service-worker offline cache both work. There is no CDN, Python runtime, npm installation or server requirement for players.

## Rules library and original bot

`vendor/chess.js/chess.cjs` is the CommonJS distribution of **chess.js 1.4.0**, obtained from its npm release, with indentation tabs expanded to spaces. Its BSD-2-Clause notice is retained in `vendor/chess.js/LICENSE` and in the embedded rules script. The source-map comment is omitted only in the embedded copy because the map is not distributed.

The original Study Hub bot uses a disposable worker, iterative depth-limited negamax with alpha-beta pruning, capture ordering, bounded capture search, and a short time limit. It is a practice opponent, not Stockfish and not assigned an Elo rating. Leaving Chess, undoing, changing mode or starting another game cancels pending work. Browsers that block workers receive an explicitly labelled simple legal-move fallback.

## Saved data

The existing `studyHubData_v1` object receives one additive `chess` field:

```
chess: {
  game: {at, mode, side, level, moves: [UCI, ...]} | null,
  solved: {PuzzleId: {solvedAt: ISO | null, assistedAt: ISO | null}}
}
```

Normal games persist their full move sequence, retaining castling rights, repetition history, en passant and undo after reopening. Puzzles never overwrite a normal match. Hints and revealed solutions count as assisted reviews; an independent completion can subsequently be earned. Existing export, replace import and Gist sync carry this field. Union import merges puzzle completions and keeps the match with the newer timestamp. Missing fields in old backups get safe defaults. No passwords or tokens are added.
