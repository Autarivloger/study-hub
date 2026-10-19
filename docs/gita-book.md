# Gita Book in Yoga & Meditation

Open **Yoga & Meditation → Book**.
The supplied 1,296-page PDF contains Swami Ramsukhdas's illustrated
Sadhak-Sanjivani Hindi commentary. Its outer cover and internal title page differ;
the reader preserves every original byte, including that cover.

## Reading and pencil

- Resume restores the last PDF page and vertical reading position.
- Use the page field, previous/next buttons or the eighteen chapter entries.
- The floating pencil enables drawing. Drag under a sentence; turn it off to
  scroll normally. Undo/redo apply to that page.
- The bookmark icon explicitly saves the current page and position.
- Page notes reuse the existing heading-note component.
- Zoom and different screen widths retain normalised annotation coordinates.
- Download original PDF reconstructs the exact supplied bytes. It does not bake
  personal marks into the PDF; existing Study Hub backup/export preserves them.

The PDF's legacy Chanakya fonts render correctly but do not extract reliable
Unicode text. Consequently pencil marks are graphical overlays, not text-range
annotations. The book is rendered one page at a time. The original PDF is never
edited. Its SHA-256 is:

    b444867d9721b826f63a20a2806ca25c13a264e141ca3c20c7a3121d0cb3dd1c

## Offline and privacy

The book and PDF.js load from the local books/ and vendor/ folders. Keep these
beside study-hub.html when opening the downloaded project without a server.
On the hosted app, open Book online once and wait for its offline status.
The existing service worker caches these same-origin assets. Its verified status
indicates when those files are cached. No external PDF service receives the book.

Reading state, bookmark and individual pencil strokes use JSON strings in
namespaced headNotes entries. Existing data defaults/schema and export remain
unchanged. A narrowly scoped merge branch selects newer timestamped Gita records.
Undo uses a timestamped tombstone, so a merged older mark does not resurrect it.
Existing ordinary notes retain their original merge behaviour.

## Study guidance

The chapter guide uses original Nepali summaries: context, a central interpretive
point, practical application and a reflection question. PDF page targets were
checked against this edition's contents and chapter openings. Chapter 13 numbering
follows the supplied 34-verse edition.

There are 37 rotating daily reflections with a verse reference, original Nepali
line, simple meaning and one practical action. A reflection is clearly labelled as
an interpretation, not a verbatim Sanskrit verse or the publisher's translation.
The local calendar date selects the same reflection for that day. On return to the
tab or after midnight while open, the daily card refreshes.

The study support connects action, discernment, meditation and devotion. It is not
a verse-by-verse replacement for the entire 1,296-page commentary and makes no
claim of a teacher's human credentials. Read the surrounding passage slowly.

## Source preparation

All pages were extracted locally for structural analysis. Legacy character
decoding was compared with rendered pages; no extracted text or conversion tool
is shipped as a replacement for the source. The book's title, contents, chapter
introductions and selected teaching passages were examined. Chapter guide and
reflections are original interpretations of the relevant passages.

PDF.js 6.4.299 comes from Mozilla's official npm package. The reader's classic
bundles are built using esbuild 0.28.2:

    node scripts/build-gita-assets.cjs <supplied-PDF> <build-node_modules>
    node scripts/add-gita-book.cjs

The first command requires those pinned build dependencies in the given tools
directory. The second embeds only the reader, study guidance and scoped Yoga/
merge/navigation hooks. Re-running either preserves the existing courses.

Primary technical references:

- [Mozilla PDF.js](https://mozilla.github.io/pdf.js/getting_started/)
- [PDFWorker API](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib-PDFWorker.html)
- [PDF.js source/API](https://mozilla.github.io/pdf.js/api/draft/api.js.html)

The source PDF is user-supplied. Its text, illustrations and publisher attribution
remain with their respective rights holders.
