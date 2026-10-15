# Original Study Hub Sudoku

The game uses **200 original puzzle layouts**, 50 each at Easy (40 clues), Medium (34), Hard (29) and Expert (25). Each has exactly one solution. Levels refer to clue counts; logical difficulty can vary. Digit permutations, valid row/column permutations and transposition create fresh variations without changing uniqueness.

`scripts/sudoku-bank.cjs` generates and checks the bank locally. `tests/sudoku-rules.cjs` additionally verifies every layout and a transformed variant with a separate solver. The delivered app embeds everything in `study-hub.html`; no server, embed, CDN, API key or runtime download is required.

The user-provided [Sudoku100 documentation](https://www.sudoku100.com/api) and [YouDoSudoku documentation](https://you-do-sudoku-api.vercel.app/) were inspected as references. Their images, branding, source code and puzzle banks are not copied. No provided credential is stored or transmitted.

## Saved progress

One additive `DB.sudoku` field holds `game` and `completed`:

* `game`: ID, level, givens, solution, current values, pencil notes, last-change timestamp, hint count and assisted status.
* `completed`: completion records by puzzle variation ID, including level, timestamp and assisted status.

The same existing `studyHubData_v1` backup/import/Gist sync carries these fields. Union merges preserve completion records and choose the game with the newer timestamp. Independent completion takes precedence over an assisted completion of the same variation. Old backups receive defaults. Chess data remains in its existing `DB.chess` field.

## Authoring

```
node scripts/sudoku-bank.cjs
node scripts/chess-integrate.cjs
node scripts/games-integrate.cjs
```

The bank only needs regenerating when its content is changed. Both embedding commands write the HTML atomically after parsing its executable scripts. Chess embedding preserves the Games additions; Games embedding preserves the existing curriculum and chess assets.

The Games folder is a navigation view, with Chess and Sudoku as child views. A shared fit function sizes the boards from viewport height, their actual top offset and controls beneath them. Focus view temporarily hides surrounding navigation and restores it on exit, Escape or navigation to another section.
