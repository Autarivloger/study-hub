# Study Hub Sokoban

40 original levels in four packs: First steps, Plan ahead, Think in boxes, and Warehouse craft. Every level is open from the start. The first warehouse introduces two simple pushes; later rooms use two, three and four crates.

## Reference and original work

The user provided [paskhaver/sokoban](https://github.com/paskhaver/sokoban), whose README, board structure, entry page and repository/license metadata were inspected on 2026-10-16. That repository uses Easel.js and other external libraries; no explicit license was found in its repository tree or GitHub metadata. Study Hub implements its own rules, solver, CSS/SVG artwork, interface and level layouts. No source, sprites or level data from that repository are distributed here.

## Levels and correctness

`scripts/sokoban-levels.cjs` creates rooms by reversing legal box pushes from solved positions, then solves the resulting room in the forward direction. It adds an original fixed introductory room. The bank records a verified solution and a minimum push count for every level. `tests/sokoban-rules.cjs` replays every solution with a separate forward interpreter and tests blocked movement, single-box pushes, no pulling, goals and deadlocks. Level maps and solutions are embedded in `study-hub.html`, so runtime gameplay makes no network requests.

The push-space BFS solver groups equivalent reachable player regions and skips static dead squares. In-game hints run in a disposable worker with time/state limits. A solved result provides one next direction. An exhausted search reports an impossible position; a resource limit reports that a quick hint was unavailable, rather than claiming the position is impossible. Moving, restarting, changing levels or leaving the game cancels pending hints. Hints mark the attempt as assisted; Undo never clears that flag.

## Saved progress

One additive `DB.sokoban` field is included in the existing `studyHubData_v1` object:

```
sokoban: {
  game: {level, moves, assisted, at} | null,
  completed: {levelId: {moves, pushes, assisted, at}}
}
```

The active route is a string of successful U/D/L/R moves. It is replayed to restore the board, push count and Undo history after reopening. Invalid moves do not increment counters. Restart/level changes ask before replacing an unfinished route. Completions remain saved across retries; independent results take precedence over assisted results, then fewer pushes, then fewer moves. Backup/import and Gist sync include this field; union merges keep all valid completions and the newer active route. Older backups get defaults. Invalid entries in this new field are isolated from existing course data.

## Authoring and layout

```
node scripts/sokoban-levels.cjs
node scripts/games-integrate.cjs
node tests/sokoban-rules.cjs
node tests/sokoban-browser.cjs
```

Regenerate the bank only when changing its levels. Embedding validates all 40 routes and all executable inline scripts, then atomically replaces the HTML with bounded retries for Windows file watchers. Existing chess, Sudoku and learning content are preserved.

Sokoban uses the existing Games and Focus controls. Tile size is computed from the actual rows, columns, viewport and space for controls. On short landscape screens in Focus, the board stays left and the HUD/buttons stay right. The movement pad has larger targets in Focus. Exit focus, Escape and navigating away restore the normal layout. Keyboard bindings operate only while Sokoban is active and never intercept text fields or modals.
