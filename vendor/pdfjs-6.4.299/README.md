# PDF.js 6.4.299

Source: Mozilla's official pdfjs-dist 6.4.299 npm distribution.
License: Apache 2.0; see LICENSE and the retained source notices.

pdf.js and pdf.worker.js are generated from build/pdf.mjs and build/pdf.worker.mjs
using esbuild 0.28.2 (IIFE format, ES2022 target, minified, legal comments retained).
The application loads these local classic scripts on demand. PDF.js's supported
same-thread worker fallback permits file:// use without a remote worker.
The application disables evaluation and WASM for this original PDF's rendering.

Reproduction command and input are documented in docs/gita-book.md.
No CDN, remote conversion, analytics or account credentials are involved.
